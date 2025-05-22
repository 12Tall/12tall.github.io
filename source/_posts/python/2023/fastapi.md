---
title: FastAPI 工程化  
date: 2023-10-12
tags:   
    - fastapi   
    - router  
    - asgi 
    - jinja2  
    - lulu-ui
---    

> 从asp.NET 到前后分离，到vue+koa2，兜兜转转又到了模板渲染。以前开发看逼格，现在开发看速度。SSR 有啥不好的，又不是不能用只要把内容展示出来就好了呗。  
<!-- more -->
## FastAPI  
`Koa2` 有各种灵活的插件，`FastAPI` 继承了路由和参数解析的功能，并且还附带了文档的功能，这样省了接口测试的功夫。并且如果配合`Jinja2` 和`lulu-ui` 完全能做出不错的页面出来。下面是一个最基本的后端代码：  
```python{22}
import uvicorn
from fastapi import FastAPI, Request, templating, staticfiles

app = FastAPI()

# 挂载静态资源，前后端的绝对路径能够保持一致
app.mount("/static", staticfiles.StaticFiles(directory="static"), name="static")

# Jinja2 模板的目录
templates = templating.Jinja2Templates(directory='templates')


@app.get('/')
# @app.post('/alias')  ## 多个路由可以匹配同一个处理函数
def index(request: Request):
    return templates.TemplateResponse('index.html', {
        'request': request,
        'warning_text': 'hello world'
    })

if __name__ == "__main__":
    """main 函数与官方写法不一样是为了方便使用Nuitka 打包"""
    uvicorn.run(app, port=9000, host='0.0.0.0')
```

项目的文件结构如下：  
![Alt text](file-structure.png)     

这样组织`static` 文件夹，可以让前后端引用js 的路径一致，便于开发时预览页面效果。     

### 路由  
FastAPI 的路由写法还不算反人类，只是需要很多的`import`，不过要注意路由匹配顺序是自上而下的  
> `from . import ***` 这种写法不能用在`main` 模块中，不然会报错  

![Alt text](router.png)  

### 中间件  
> FastAPI 中间件本质上是一个异步函数，包含`request, call_next` 两个参数。  

中间件可以在`main` 模块定义：  
```python{6}
@app.middleware("http")
# 必须用 async
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    # 必须用 await
    response = await call_next(request)
    process_time = time.time() - start_time
    # 自定义请求头
    response.headers["X-Process-Time"] = str(process_time)
    # 返回响应
    return response
```

也可以在单独的文件中定义（此方法的执行效率似乎更高一些）：  
```python{11-20}
import time
from fastapi import Request

class TimerMiddleware:
    def __init__(
            self,
            attrs
    ):
        self.attrs = attrs  # 一些可选的属性数据

    async def __call__(self, request: Request, call_next):
        start_time = time.time()
        # 必须用 await
        response = await call_next(request)
        process_time = time.time() - start_time
        # 自定义请求头
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Attrs"] = self.attrs
        # 返回响应
        return response
```
使用`app.add_middleware` 启用中间件：  
```python
from fastapi import FastAPI, Request, templating, staticfiles
from middleware.mw import TimerMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI()
app.add_middleware(BaseHTTPMiddleware, dispatch=TimerMiddleware("attrs"))
```

也可以让中间件类直接继承`BaseHTTPMiddleware`，但是这样似乎会存在一些内存泄露的问题。参见[How to write a custom FastAPI middleware class](https://stackoverflow.com/a/71526036)。所以还是有必要像路由一样统一管理中间件。  

## 前端  

前端采用`lulu-ui`，因为他采用的是`is` 方法重新定义组件，相比于`vue` 或者其他框架来说，它的用法更接近于原生的`html+js+css`。所见即所得：  

![Alt text](lulu-ui.png)  

不太好的地方是后端通过表单获取数据时写法有点复杂，但是可以通过拦截`submit` 或者其他的手段来曲线救国。   

### Jinja2   
虽然专业的前端设计很漂亮，但是打包工具未免也太复杂了些。而后端渲染的方式简单粗暴，深得我心。尤其是`jinja2` 既可以实现继承（`extend`）又可以实现组件化（`import/include`）。看起来也还挺方便的，只是还不知道使用起来感觉怎么样。  

1. 通过`include` 导入模板文件     
![Alt text](include.png)  
2. 通过`import` 导入模板文件的部分内容  
![Alt text](import.png)  
3. 通过`extends` 继承模板文件  
![Alt text](extends.png)  


## 数据库   
一般的教程都会推荐`SQLAlchemy`，但是这个框架着实不好理解。好在`FastAPI` 的作者基于`SQLAlchemy` 封装了一个新的库`SQLModel`，和其他静态语言的数据库组件设计思路很像。如果不考虑数据库迁移的的话，模型和引擎可以不定义在同一个文件中。  
![Alt text](sqlmodel.png)  

并且支持`SQLAlchemy` 的[查询语法](https://docs.sqlalchemy.org/en/14/tutorial/data_select.html#)：  
```python
from sqlmodel import SQLModel, Session, select, func, desc
from model.node import Node
from model.db import engine

with Session(engine) as s:
    statement = select(Node.id, 
                       Node.data,
                       func.count(Node.parent_id).label('count')
                       ).group_by(
                           Node.parent_id
                        )
    nodes = s.exec(statement) 
    print(nodes.all())
    s.commit()
```

定义树状的数据结构：  
```python
from typing import Optional
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine


class Node(SQLModel, table=True):
    __tablename__ = 'node'  # 显式声明数据表

    id: Optional[int] = Field(default=None, primary_key=True)
    data: str
    parent_id: Optional[int] = Field(
        foreign_key='node.id',  # 小写的n 表示外键连
        default=None,
        nullable=True
    )
    parent: Optional['Node'] = Relationship(
        back_populates='children',
        sa_relationship_kwargs=dict(
            remote_side='Node.id'  # 大写的N 表示本表中的字段
        )
    )
    children: list['Node'] = Relationship(back_populates='parent')
```

递归查询：可以通过`remote_side` 来实现自递归，项目结构如下：  
![Alt text](sqlmodel2.png)



### 异步  
参考[Add documentation about how to use the async tools (session, etc)](https://github.com/tiangolo/sqlmodel/issues/626#issuecomment-1669841104)。
或者[FastAPI with Async SQLAlchemy, SQLModel, and Alembic](https://testdriven.io/blog/fastapi-sqlmodel/)：  
```python
import os

from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession, AsyncEngine

from sqlalchemy.orm import sessionmaker


DATABASE_URL = os.environ.get("DATABASE_URL")

engine = AsyncEngine(create_engine(DATABASE_URL, echo=True, future=True))

async def init_db():
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

################################################################################

from fastapi import Depends, FastAPI
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session, init_db
from app.models import Song, SongCreate

app = FastAPI()


@app.on_event("startup")
async def on_startup():
    await init_db()


@app.get("/ping")
async def pong():
    return {"ping": "pong!"}


@app.get("/songs", response_model=list[Song])
async def get_songs(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Song))
    songs = result.scalars().all()
    return [Song(name=song.name, artist=song.artist, id=song.id) for song in songs]


@app.post("/songs")
async def add_song(song: SongCreate, session: AsyncSession = Depends(get_session)):
    song = Song(name=song.name, artist=song.artist)
    session.add(song)
    await session.commit()
    await session.refresh(song)
    return song        
```




另外，一个好玩的点：  
```python  
from typing import TYPE_CHECKING  

if TYPE_CHECKING:  
    '''
    代码块里面的代码并不会被执行，但是可以为编辑器提供类型提示
    '''
    import libs  
```

这篇笔记记录的都是一些可行性的问题，具体项目中的代码肯定还需要很多细节性的问题需要解决。


## 参考资料  
1. [Live Preview](https://marketplace.visualstudio.com/items?itemName=ms-vscode.live-server) 实时预览html 的vscode 插件  
2. [How To Format Form Data as JSON](https://www.section.io/engineering-education/how-to-format-form-data-as-json/) 通过监听表单的`submit` 事件来自定义处理函数    
3. [lulu-ui](https://l-ui.com/)    
4. [How to use macros in a included file](https://stackoverflow.com/a/45024799)  
5. [SQLModel](https://sqlmodel.tiangolo.com/) FastAPI 作者开发的ORM 库，应该是见过的最简洁的Python ORM 库了    
6. [Pydantic](https://docs.pydantic.dev/latest/) 一个比较好用的数据校验工具，尤其是对于JSON 到对象、对象到对象的类型转换非常友好  
7. [How to write a custom FastAPI middleware class](https://stackoverflow.com/a/71526036)  
8. [How do I construct a self-referential/recursive SQLModel](https://stackoverflow.com/a/73420019)  
9. [Aggregate functions with GROUP BY / HAVING](https://docs.sqlalchemy.org/en/14/tutorial/data_select.html#aggregate-functions-with-group-by-having)

-----  

其实有一个问题： `ORM` 要不要承担创建表和数据迁移的工作呢？如果不要的话，代码的逻辑应该会非常简单；如果要的话，一不小心就会出现循环导入的问题。
