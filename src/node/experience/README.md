---
title: 零星经验     
date: 2023-06-09    
timeLine: true
sidebar: false  
icon: nodeJS  
category:  
    - 开发  
    - Javascript     
tag:  
    - JSDoc  
    - 注释         
---    

## 复杂功能简单化   
（仅针对自己）在复杂的功能中，很多时候一个函数或者一条`SQL` 虽然可以完成任务，但是需要考虑的情况很多且不利于扩展，这个时候不要想着非得将所有功能塞在一起，比如：  
- `SQL` 插入去重：先`SELECT` 记录是否存在，没有再插入   
- 项目管理：先添加项目，再给项目添加负责人或成员  

## Koa2 中利用JSDoc 实现代码类型提示  
koa2 中的事件处理函数接收`ctx, next` 参数，但是在自定义函数在VSCode 中没有参数类型提示
```js
// 这样写没有类型提示
async function editTeam(ctx, next) {  
    let body = ctx.request.body
    ctx.body = Msg.success(team)
}
```  

于是可以封装一个新的函数，并通过JSDoc 注释来让VSCode 能够解析参数类型：  
```js{5}
const { Context } = require('koa');
/**
 * Wrap controller with try catch
 * 
 * @param {function(Context): Promise<object>} func 
 * @returns 
 */
function defineController(func) {

    /**
     * @param {Context} ctx
     */
    return async (ctx) => {
        try {
            ctx.body = await func(ctx)
        } catch (e) {
            ctx.body = Msg.internalError(e)
            log(ctx, `internal error: ${JSON.stringify(ctx.body)}`)
        }
    }
}

// 使用方法  
const defaultController = defineController(async (ctx) => {
    // 这里编译器便可以自动提示ctx 中定义的属性
    return "hello world!"
});


module.exports = { defaultController, defineController};
```
