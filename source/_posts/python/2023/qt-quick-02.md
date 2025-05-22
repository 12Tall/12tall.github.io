---
title: Qt Quick 的学习笔记（二） 
date: 2023-09-29   
tags:   
    - python    
    - qt  
    - pyside 
    - qml
---  

> 和Electron 类似，PyQt 与PySide 也支持向QML 的前端暴露对象以实现前后端的通信；但是呢，似乎QML 可以往任意子元素暴露对象变量  
<!-- more -->
本笔记中的所有内容均摘自[Feng Misaka - 博客园](https://www.cnblogs.com/linuxAndMcu/)。重点在于前后端的通信与动态组件的绘制。    

## 通信  
前后端通信是所有做用户界面不可避免的问题，说简单也简单，无非就是函数的调用与数据的传输罢了。但是怎么做得高效优雅就是一门学问了。PySide 中也使用了向前端暴露对象变量的方法。  

### 前端调用后端  
前端调用后端，需要后端向前端暴露一个槽函数（`@Slot()`），槽函数装饰器的签名如下：  
```python
class Slot(
    *types: type,  # 参数类型
    name: str | None = ...,  # 函数名，默认与Python 函数同名
    result: str | None = ...  # 结果类型
)
```
示例代码如下：  
```python{18,20-23,30}  
# main.py  
import sys

from PySide6.QtCore import QObject, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine


class Api(QObject):
    '''
    1. 暴露的变量对象必须继承自QObject
    '''

    def __init__(self, parent=None) -> None:
        '''
        2. 并且需要通过父类方法进行初始化
        '''
        super().__init__(parent)  #

    @Slot(str, result=str)  # 装饰器用于告诉QML 该函数的签名
    def clickme(self, arg):  # 真正的函数定义
        print(f"{arg} clicked")
        return "123"


app = QGuiApplication(sys.argv)
engine = QQmlApplicationEngine()
engine.quit.connect(app.quit)
# 暴露该对象到rootContext
engine.rootContext().setContextProperty('api', Api(app))
# 也可以暴露到某个组件，但是不如直接放在全局简单粗暴
# engine.rootObjects()[0].setProperty('backend', backend)
engine.load('main.qml')

sys.exit(app.exec_())
```
```qml
import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    visible: true
    // ...
    Button {
        id: btn
        text: "'click me'"
        onClicked:{
            var res = api.clickme("123")?1:2
            console.log(res)
        }
    }    
}
```

## 后端调用前端   
正常后端可以通过同步的方法修改。也可以通过以事件的形式进行。这时就需要后台向前端发送信号`Signal()`。然后在前端监听信号的变化：  
```python{16,18,25}
from PySide6.QtCore import QObject, Slot, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine


class Api(QObject):
    '''
    1. 暴露的变量对象必须继承自QObject
    '''
    def __init__(self, parent=None) -> None:
        '''
        2. 并且需要通过父类方法进行初始化
        '''
        super().__init__(parent)  #
        # 不能将信号定义为实例变量
        # self.sig = Signal(str, arguments=['arg1'])
    # 只能将信号定义为类变量，不然的话会找不到emit 方法
    sig = Signal(str, arguments=['arg1'])
    

    @Slot(str, result=str)  # 装饰器用于告诉QML 该函数的签名
    def clickme(self, arg):  # 真正的函数定义
        print(f"{arg} clicked")
        # 在槽方法中发送信号
        self.sig.emit(arg)
        return "123"
# ...        
```
在前端则需要`Connect` 到`api` 变量，并且使用`onSig` 监听`sig` 信号：
```qml{9-11}
import QtQuick 2.2
import QtQuick.Controls 2.2

ApplicationWindow {
    // ...
    Connections{
        target: api  
        
        function onSig(arg1) {
            btn.text = arg1
        }
    }
}
```

`Signal` 构造参数及意义：  
```python
```python
class Signal(
    *types: type,  # 参数类型
    name: str | None = ...,  # 函数名，默认与Python 对象同名
    arguments=[str] | None = ...  # 形参名
)
```
```

## 动态元素  
QML 中提供了`ListView` 和`GridView` 来展示数据，并且提供了相应的`*Model` 容器来管理数据，以实现实时更新的效果。下面的代码取自[QML中动态与静态模型应用详解](https://zhuanlan.zhihu.com/p/639430500)，仅作部分删减修改并添加注释：  
```qml{13-17,42,45-53,71-75}
import QtQuick 2.2
import QtQuick.Window 2.2
Window {
    visible: true
    width: 640
    height: 480
    title: qsTr("动态添加和删除元素")
    Rectangle{
        width: 480
        height: 300
        color: "white"
        // 初始化数据模型
        ListModel{
            id: theModel
            ListElement{number:0}
            ListElement{number:1}
        }
        Rectangle{
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.margins: 20
            height: 40
            color: "darkGreen"
            Text {
                anchors.centerIn: parent
                text: "add item"
            }
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    theModel.append({"number": parent.count++})
                }
            }
            property int count: 2
        }
        GridView{
            anchors.fill: parent
            anchors.margins: 20
            anchors.bottomMargin: 80
            clip: true
            model: theModel // 绑定模型
            cellWidth: 45
            cellHeight: 45
            delegate: numberDelegate  // 子元素模板
            add: Transition {  // 添加元素的动画，最新的写法
                    NumberAnimation { properties: "x,y"; from: 100; duration: 1000 }
                }
            remove: Transition {
                        ParallelAnimation {
                            NumberAnimation { property: "opacity"; to: 0; duration: 1000 }
                        }
                }
        }

        // 子元素的模板
        Component{
            id:numberDelegate
            Rectangle{
                id: wrapper
                width: 40
                height: 40
                color: "lightGreen"
                Text {
                    anchors.centerIn: parent
                    font.pixelSize: 10
                    text: number  // 模型的number 属性
                }
                MouseArea{
                    anchors.fill: parent
                    onClicked: {  // 子元素的事件监听
                            // 这里要判断元素是否已经被移除，所以仅凭index 还是不够的
                            // 默认index 属性
                            theModel.remove(index)
                        }
                }
                //模型元素移除时候的动画
            }
        }
    }
}
```

关于动画的部分，以后有时间在学习吧。总之学了数据的增删改查一般的小项目就足够用了。而且比web 和qtdesigner 考虑的都要单纯些。  


## 参考资料  
1. [Feng Misaka - 博客园](https://www.cnblogs.com/linuxAndMcu/)  
2. [QML 在线预览](https://qmlonline.kde.org/)  
3. [QML 在线预览的仓库](https://github.com/patrickelectric/qmlonline)  
4. [Connect python signal to QML ui slot with PySide2](https://stackoverflow.com/a/54011163) 包含退出程序前清理线程的代码    
5. [Is there a cleaner way for backend in PySide6 for QML?](https://stackoverflow.com/a/68613783)  
6. [QML中动态与静态模型应用详解](https://zhuanlan.zhihu.com/p/639430500) 文中关于动画的写法过时了    
7. [QML - GrideView - Attached Signals](https://doc.qt.io/qt-6/qml-qtquick-gridview.html#attached-signals)
