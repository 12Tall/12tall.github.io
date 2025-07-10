---
title: Python 处理HTML 格式的剪切板内容
date: 2025-07-10 13:37:42
tags:
    - html  
    - 剪切板
---

在开发AI 翻译工具时，有一个功能是读取剪切板内容，像txt 内容没有问题，但是若是Office 文件这种带有格式的内容则需要特殊处理。  
<!-- more -->

## HTML 剪切板格式  
剪贴板的官方名称（`RegisterClipboardFormat`使用的字符串）是`HTML Format`，描述符是`CF_HTML`。在Python 的Win32 库中却不能使用`CF_HTML`。
HTML 剪切板始终使用utf-8 编码，格式如下：  
```html
Version:1.0
StartHTML:0121
EndHTML:0272
StartFragment:0006
EndFragment:0106
StartSelection:0180
EndSelection:0225
<html><!--StartFragment--><body>This is normal. <b>This is bold.</b> <i><b>This is bold italic.</b> This is italic.</i></body><!--EndFragment--></html>
```

### 字段说明  
- `Version` 版本号，起始版本是0.9，现在版本是1.0  
- `StartHTML/EndHTML` 从剪切板开头到`上下文` 起止的字节数；  
- `StartFragment/EndFragment` 从剪切板开头到`片段` 起止的字节数  
- `StartSelection/EndSelection` 从剪切板开头到`所选内容` 起止的字节数（可选）  
- 偏移量左边可以填充任意数量的`0`，一般总长为10位  

**上下文**  
上下文是一个最小的但是格式正确的html 文档，提供完整的结构，确保格式、样式等正确。  

**片段**  
剪切板中实际被复制或剪切的 HTML 内容，是用户选择的那部分 DOM 内容。正常片段是在`<body/>` 标签内的。也就是上面的官方说明与实际表现有出入。下面是实际剪切板内容： 
```html
Version:0.9
StartHTML:0000000105
EndHTML:0000000244
StartFragment:0000000141
EndFragment:0000000208
<html>
<body>
<!--StartFragment--><a href="https://qiita.com/timeline">タイムライン - Qiita</a><!--EndFragment-->
</body>
</html>
```
**选择**
此项留作分段选取用，实际使用中一般忽略。  

## win32clipboard 使用   

`win32clipboard` 使用一般流程如下（打开-操作-保存）：  
```python
import win32clipboard

# 打开剪切板
win32clipboard.OpenClipboard()
# 获取剪切板内容（纯文本）
data = win32clipboard.GetClipboardData()
# 打印结果
print(data)

# 清空剪切板
win32clipboard.EmptyClipboard()	

data = 'test'
# 向剪切板写入内容，但是要注意字符编码
win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, clipdata.encode('UTF-8'))

# 关闭剪切板
win32clipboard.CloseClipboard()
```

### 读写HTML 内容  
因为`CF_HTML` 在该库中没有定义，所以在读写HTML 内容时需要用`win32clipboard.RegisterClipboardFormat('HTML Format')` 作为参数。  
在写入剪切板时，不同格式的内容互不影响，所以写入之前最好先清空剪切板。  
```python
data = win32clipboard.GetClipboardData(win32clipboard.RegisterClipboardFormat('HTML Format')) # 可能会报异常
print(data)
data = """Version:0.9
StartHTML:0000000105
EndHTML:0000000244
StartFragment:0000000141
EndFragment:0000000208
<html>
<body>
<!--StartFragment--><a href="https://qiita.com/timeline">タイムライン - Qiita</a><!--EndFragment-->
</body>
</html>"""

win32clipboard.SetClipboardData(win32clipboard.RegisterClipboardFormat('HTML Format'), data.encode('UTF-8'))
```

### 拼接剪切板内容  

从上文可以看出，我们只需要向`<!--StartFragment--><!--EndFragment-->` 中间添加html 内容，然后再修改偏移量就好了。但实际上偏移量似乎对一般剪切板内容也没啥影响：    
```python
import win32clipboard

def html_to_clipboard(html:str):
  """
  根据html 字符串生成剪切板内容
  """
  header_template = (
        "Version:0.9\n"
        "StartHTML:{start_html:010d}\n"
        "EndHTML:{end_html:010d}\n"
        "StartFragment:{start_frag:010d}\n"
        "EndFragment:{end_frag:010d}\n"
    )
  segment_start = '<html><body><!--StartFragment-->'
  segment_end = '<!--EndFragment--></body></html>'
  # 占位头部：先构建出 header，便于偏移量计算
  header_placeholder = header_template.format(
        start_html=0, end_html=0, start_frag=0, end_frag=0
    )
  offset_start_html = len(header_placeholder.encode())
  offset_start_segment = offset_start_html + len(segment_start.encode())
  offset_end_segment = offset_start_segment + len(html.encode())
  offset_end_html = offset_end_segment+len(segment_end.encode())

  header = header_template.format(
        start_html=offset_start_html,
        end_html=offset_end_html,
        start_frag=offset_start_segment,
        end_frag=offset_end_segment
    )
  return header + segment_start + html + segment_end

data = '<a href="https://www.gushiwen.cn/mingju/juv_ee31a5dc434b.aspx">娉娉袅袅十三余，豆蔻梢头二月初。</a>'
clipdata = html_to_clipboard(clipdata)

win32clipboard.OpenClipboard()
win32clipboard.EmptyClipboard()	
# win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, "毫不相干的内容")
win32clipboard.SetClipboardData(win32clipboard.RegisterClipboardFormat('HTML Format'), clipdata.encode('UTF-8'))
win32clipboard.CloseClipboard()
```

最后，设置了HTML 之后纯TEXT 内容依然为空，这可能导致部分应用无法粘贴。


## 参考资料  
1. [Pythonでクリップボードをリンク付き(HTML形式)加工する。](https://qiita.com/tapitapi/items/d0a1df5f9f74aefa97d3)  
2. [HTML 剪贴板格式](https://learn.microsoft.com/zh-cn/windows/win32/dataxchg/html-clipboard-format)
