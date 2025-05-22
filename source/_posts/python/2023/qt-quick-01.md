---
title: Qt Quick 的学习笔记（一） 
date: 2023-09-27  
tags:   
    - python    
    - qt  
    - pyside 
    - qml
---  

> 很难找到集成度高、配置简单、上手又快的GUI 框架，看起来QML 似是不错：  
> - 跨平台  
> - 语法简单：类似JS+JSON 的语法  
> - 前后分离：通过信号与槽的机制进行通信，又不用自己定义各种API  
> - PySide6 也支持     
<!-- more -->
本笔记中的所有内容均摘自[Feng Misaka - 博客园](https://www.cnblogs.com/linuxAndMcu/)。大致记录如何绘制静态窗口。下一篇记录如何绘制动态窗口。    

## QML 的语法  
QML 的语法兼容JS，变量与函数的定义也是一致的，并且对象的动态属性也是一致的。而且`this` 在函数中的指向也保持一致：  
```js  
// 具名函数中的this 指向调用者
person.printInfo = function printlnfo(){
	console.log(`name - ${this.name}, year - ${this.year}`)
}
person.printlnfo()

// 匿名函数中的this 指向调用者
person2.printInfo = function (){
	console.log("name -", this.name, "year -", this.year)
}
person2.printlnfo()

// 箭头函数中this 指向定义时的this  
person3.printInfo = ()=>{
	console.log("name -", this.name, "year -", this.year)
}
person3.printlnfo()
```
并且，QML 中创建出来的对象会有垃圾收集器负责管理，而不用手动清理内存。但是需要提前取消引用。  

### 全局宿主对象Qt  
在QML 中，全局宿主对象`Qt` 的位置类似于前端的`window` 对象，其具有以下常用的属性：  
1. `application` 用来访问应用的全局状态  
2. `platform` 顾名思义，运行平台  
3. 非常多的枚举类型，如键值、窗口模态、应用状态等  
4. 用于创建宿主类型的方法：  
   1. `Qt.rect()` 创建 rect 实例  
   2. `Qt.point()` 创建 point 实例  
   3. `Qt.size()` 创建 size 实例  
   4. `Qt.rgba()`、`Qt.hsla()`、`Qt.darker()`、`Qt.lighter()`、`Qt.tint()` 等创建`color` 类型的颜色值  
   5. `Qt.font()` 创建字体  
   6. `Qt.vector2d()` 创建 vector2d  
5. 格式化日期时间函数  
   1. `string Qt.formatDateTime(datetime date, variant format)`  
   2. `string Qt.formatDate(datetime date, variant format)` 
   3. `string Qt.formatTime(datetime date, variant format)`  
6. 创建组件的函数  
   1. `object Qt.createComponent(url)`  
   2. `object Qt.createQmlObject(string qml, object parent, string filepath)`  
7. 其他方法  
   1. `Qt.quit()` 退出应用   
   2. `String Qt.md5(string)` 计算字符串的MD5  
   3. `string Qt.resolvedUrl(url)` 将传入的相对路径转换为全路径

### QML 语法示例   
QML 通过组合不同的组件来获取想要的界面，用户也可以自己定义组件在不同的文件中来引用，下面是一个简单的示例：  
```qml
// rectangle.qml  //注释

import QtQuick 2.0

// 根元素
Rectangle {
    id: root  // 在qml 中可以通过id 来引用元素

    // 属性 - properties: <name>: <value>
    width: 120; height: 240  // 如果属性在同一行可以用; 隔开
    // color property(颜色属性)
    color: "#D8D8D8"

    Image {  // 子元素
        id: rocket

        // 相对parent的x坐标（会随父元素的宽度变化而刷新）
        x: (parent.width - width)/2; y: 40

        source: 'assets/rocket.png'
    }

    // root的另一个子元素：文本元素
    Text {
        // 根据id对应元素的属性，设置y坐标
        y: rocket.y + rocket.height + 20

        width: root.width

        horizontalAlignment: Text.AlignHCenter
        text: 'Rocket'
    }
}
```

> 花括号`{}` 可以表示元素块，但是跟在`on<Property><Event>` 的属性后面，则相当于函数体。因为在QML 中事件的处理函数也是以属性的形式定义在元素中的。  

## QML 对象  
可以通过以下方式定义QML 对象  
1. 通过文件名：类似于`.vue` 文件，可以直接使用导入的`.qml` 文件  
2. 通过`Component` 类型定义，类似于通过js 创建DOM 元素  
3. 通过C++ 定义，暂不了解，因为后端代码用的是python    

> 通过文件定义QML 组件时，如果组件位于`main.qml` 同级目录则不需要多于操作，如果位于其他目录则属要`import '/path/to/folder'`，导入组件所在的文件夹。而文件名就是组件名！ 

QML 对象可以包含各式各样的属性：  
```qml{12-14}  
import QtQuick 2.0

Text {
    id: thisLabel

    x: 24; y: 16
    height: 2 * width  // 动态刷新

    // 自定义属性的定义：property type name: value
    property int times: 24

    // 属性的别名
    // 通过别名可以将子组件的属性暴露在父组件上，用于外部元素访问
    property alias anotherTimes: thisLabel.times

    text: "Greetings " + times

    // 属性分组
    // 也可以写作 font { pixelSize: 18; bold: true; }
    font.family: "Ubuntu"
    font.pixelSize: 24

    // 按键导航：按下tab 键时聚焦到哪个元素
    KeyNavigation.tab: otherLabel

    // 信号（事件）处理函数
    onHeightChanged: console.log('height:', height)

    // 自动获取焦点
    focus: true

    // 设置前景色
    color: focus?"red":"black"  

    // 附加属性  
    keys.enabled: false
}
```

### 锚布局  
通过与其他元素关联来确定本元素的**位置**信息：  
```qml  
import QtQuick 2.9
import QtQuick.Window 2.2
import QtQuick.Controls 2.4

Window {
    // ...
    Rectangle {
        id: rect1
        // ...
        anchors.left: parent.left
    }

    Rectangle {
        id: rect2
        // ...
        anchors.left: rect1.right
        anchors.leftMargin: 60
        anchors.top: parent.top
        anchors.topMargin: 40
    }
}
```

### 定位器与布局管理器  
定位器相当于指定子元素的排列方式，与布局管理器的作用大同小异：  
- `Row[Layout]` 行定位器，横向排列  
- `Column[Layout]` 列定位器，纵向排列  
- `Grid[Layout]` 表格定位器   
- `Flow[Layout]` 流式定位器，会自动换行  

有一点区别就是布局管理器`*[Layout]` 会修改子控件大小，让其自适应。  

## QML 基本元素  
可以被绘制在屏幕上的元素被称为可视化元素，如标签、文本框等；不可见的元素如计时器、鼠标区域和按键元素则被称作非可视化元素。而`Item` 元素本身是不可见的，却是所有可视化元素的基类，作用类似于`<div><div/>`。    

### 非可视化元素  
1. `MouseArea` 一个矩形区域，用来捕捉鼠标事件。其事件处理函数会有一个`mouse` 对象作为参数。  
   ```qml{6}   
    Rectangle {
        // ...
        MouseArea {
            // ...
            onClicked: {
                if (mouse.button == Qt.RightButton)
                    parent.color = 'blue';
                else
                    parent.color = 'red';
            }
        }
    }
   ```
2. `keys` 按键元素，与`MouseArea` 不同，按键元素并不能单独存在，而是作为其他`Item` 子类的属性来定义：  
   ```qml{5-15}  
    import QtQuick 2.0

    Rectangle {
        // ...
        Keys.onEscapePressed: Qt.quit()
        Keys.onPressed: {
            switch(event.key) {
            case Qt.Key_0:
            // ...
            case Qt.Key_9:
                event.accept = true
                keyView.text = event.key - Qt.Key_0;
                break;
            }
        }
    }
   ```
3. `Timer` 定时器
   ```qml
    import QtQuick 2.2
    import QtQuick.Controls 1.1
    
    Rectangle {
        // ...
        Timer {
            id: countDown;
            interval: 1000;
            repeat: true;
            triggeredOnStart: true;
            onTriggered:{
                countShow.text = attrs.counter;
                attrs.counter -= 1;
                if(attrs.counter < 0)
                {
                    countDown.stop();
                    countShow.text = "Clap Now!";
                }
            }
        }
        
        Button {
            id: startButton;
            // ...
            onClicked: {
                countDown.start();
            }
        }
    }

   ```






## 参考资料  
1. [Feng Misaka - 博客园](https://www.cnblogs.com/linuxAndMcu/)  
2. [QML 在线预览](https://qmlonline.kde.org/)  
3. [QML 在线预览的仓库](https://github.com/patrickelectric/qmlonline)  
4. [【前端】js匿名函数和箭头函数的this](https://juejin.cn/post/6844904066456223752)  
5. [QML 组件与对象动态创建详解-转载](https://blog.51cto.com/u_15329836/3402684)  
6. [Create applications with QtQuick](https://www.pythonguis.com/tutorials/pyside6-qml-qtquick-python-application/)

