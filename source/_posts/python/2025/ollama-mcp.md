---
title: 结合Ollama 实现的MCP 服务器/客户端
date: 2025-11-08 17:18:48
tags:
    - llm
    - ollama  
    - mcp
    - agent
---

本周用`Qwen3-vl` 做了一个发票识别的玩具，忽然想到了之前`deepseek-r1` 不支持`function call` 的事情。于是琢磨通过MCP 服务实现，简单记录下实现过程。  

<!-- more -->

## MCP 服务器
实现MCP 服务器的代码很简单，主体结构如下：
```python
from fastmcp import FastMCP
mcp = FastMCP("Test Server")  # 初始化

@mcp.tool(tags=['math'])    # 指定函数标签，在函数比较多的时候可以用来帮助定位所需的函数
async def multiply(a: float, b: float) -> float:
    """两个浮点数相乘，返回二者的积"""
    return a * b


@mcp.prompt  # 这段代码也可以放在客户端每次启动客户端都更新下列表
async def prompt() -> float:
    """prompt 只能返回user/assistant 类型的消息，擅自拆解消息并不是很专业，但是好用"""
    tools = await mcp.get_tools()
    res = (
        "你是一个支持调用 MCP 工具的智能助手。\n"
        "你可以根据需要调用以下工具。\n"
        "调用规则非常严格，请务必遵守：\n"
        "当你需要调用工具时，只能输出：\n"
        '{"type":"tool", "name":"工具名", "params": {参数JSON}}\n'
        "不要添加其他说明，不要添加额外文字，不要加标点。\n"
        "不要解释，不要回答用户内容，不要换行解释。\n"
        "只要你决定调用工具，输出格式必须完全符合示例。\n\n"
        "以下是你可以使用的工具列表：\n"
    )

    for key in tools.keys():
        tool = tools[key]
        # 服务端的模型需要转换成客户端模型才能JSON 格式化
        res += "\n".join(tool.to_mcp_tool().model_dump_json())

    return res

if __name__ == "__main__":
    # 启动服务
    mcp.run(transport="http", port=9999)
```

## MCP 客户端  

### 初始化Ollama 客户端

```python
import json
from ollama import ChatResponse, Client

HOST = "http://127.0.0.1:11434"
QWEN3_VL = "qwen3-vl:32b"
model = Client(HOST)

def mcp_chat(messages):
    resp: ChatResponse = model.chat(
        QWEN3_VL,
        messages=messages
    )
    
    return json.loads(resp.message.content)
```

### MCP 调用
通过客户端也可生成可用工具列表，~~不要太早考虑优化~~。  
```python
from typing import Any, Dict, List
from fastmcp import Client
import asyncio
from mcp.types import Tool

from llm import mcp_chat

# 通过客户端生成可用工具列表
def get_sys_prompt(tools: List[Tool]) -> str:
    prompt = (
        "你是一个支持调用 MCP 工具的智能助手。\n"
        "你可以根据需要调用以下工具。\n"
        "调用规则非常严格，请务必遵守：\n"
        "当你需要调用工具时，只能输出：\n"
        '{"type":"tool", "name":"工具名", "params": {参数JSON}}\n'
        "不要添加其他说明，不要添加额外文字，不要加标点。\n"
        "不要解释，不要回答用户内容，不要换行解释。\n"
        "只要你决定调用工具，输出格式必须完全符合示例。\n\n"
        "以下是你可以使用的工具列表：\n"
    )

    prompt += "\n".join([tool.model_dump_json() for tool in tools])

    return prompt


async def main():
    async with Client("http://127.0.0.1:9999/mcp") as cli: # 通过http 连接MCP 服务器
        tools = await cli.list_tools()  # 获取可用工具（函数）清单
        messages = [
            {
                "role": "system",
                "content": get_sys_prompt(tools)  # 生成系统提示词模板
            },   {
                "role": "user",
                "content": "问候 Tom"
            },
        ]

        json_obj:Dict[str, Any] = mcp_chat(messages)  # 获取将要调用的函数
        print(json_obj)
        # {'type': 'tool', 'name': 'greeting', 'params': {'name': 'Tom'}}
        if json_obj.get('type', '') == 'tool':
            # 调用函数
            res = await cli.call_tool(name=json_obj.get('name'), arguments=json_obj.get('params'))
            # 打印结果
            print(res.data)

if __name__ == '__main__':
    # 启动服务
    asyncio.run(main())
```

## 结论  
我似乎走了一条最笨的道路，上面代码应该还有可以改善的地方：
1. 预设`system` 提示词，然后获取MCP 服务器的`prompt` 直接`extend(prompt.messages)`  
2. 添加工具清单的缓存，无论是客户端还是服务端，虽然意义不大，因为最耗时的工作不在这儿；
3. 在任务比较复杂的时候可以组合多个提示词和工具清单，分成多个小任务进行（比如我们的发票包含各式各样的，写在一次对话中容易忽略重点）。
