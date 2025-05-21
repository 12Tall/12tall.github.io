---
title: 使用gettext 进行国际化
date: 2025-05-15 14:27:44
tags:  
    - gettext  
    - 多语言  
    - 国际化
---


一般来说，使用`gettext` 为程序添加多语言支持时，需要遵循一些标准的步骤。另外就是，对于在`main()` 函数之前就初始化的变量需要特殊处理。
为此，特整理笔记备忘。  

<!-- more -->


## 最小可用示例  

该示例代码仅保证多语言功能可用：  
```cpp
#include <iostream>
#include <locale.h>
#include <libintl.h>

#define _(STRING) gettext(STRING)

int main() {
    setlocale(LC_ALL, "");  // 指定语言，例如en_US，zh_CN，zh_CN.UTF-8 等
    bindtextdomain("myapp", "./locale"); // .locale 是语言包的路径，可以是相对路径也可以是绝对路径
    textdomain("myapp");
    // 上面的myapp 可以改成自己喜欢的名字，但是文件路径需要遵循以下规则  
    // ./locale/{zh_CN}/LC_MESSAGES/{myapp}.mo  
    // 其中.mo 可以通过以下步骤生成

    std::cout << _("Hello, world!") << std::endl;
    return 0;
}
```

### 提取、翻译   
```bash  
# 从main.cpp 中提取待翻译的内容
xgettext --from-code=UTF-8 -k_ main.cpp -o messages.pot

# 同时提取多个文件
find . -name "*.cpp" | xargs xgettext --from-code=UTF-8 -k_ -o messages.pot
```

通过[poedit](https://poedit.net/) 可以打开.pot 文件，并将翻译结果保存到相应的路径下。  

## 静态变量翻译
上面内容不太重要，多试试就好了。但是静态变量的翻译就很有意思了。  
```c++
#include <iostream>
#include <locale.h>
#include <libintl.h>

#define _(STRING) gettext(STRING)

const char * bye = _("Goodbye!");

int main() {
    setlocale(LC_ALL, "");  // 指定语言，例如en_US，zh_CN，zh_CN.UTF-8 等
    bindtextdomain("myapp", "./locale"); // .locale 是语言包的路径，可以是相对路径也可以是绝对路径
    textdomain("myapp");

    std::cout << _("Hello, world!") << std::endl;  // 可以正常显示对应语言
    std::cout << bye << std::endl;  // 无法正常显示对应语言
    return 0;
}
```

因为`bye` 是在`main()` 之前初始化的，所以在`main()` 执行时就获取不到对应的译文了。为此，可以封装一个函数：  
```cpp
#define _(STRING) _translate(STRING)
void _translate(const char* msg) {
    setlocale(LC_ALL, "");  // 指定语言，例如en_US，zh_CN，zh_CN.UTF-8 等
    bindtextdomain("myapp", "./locale"); // .locale 是语言包的路径，可以是相对路径也可以是绝对路径
    textdomain("myapp");

    return gettext(msg);
}
```

### 多语言初始化标识符
每次运行`_()` 前都设置下语言就好了。但是这样会造成额外的开销，为此我们可以通过一个全局的标识符`gettext_initialized` 来表示语言是否初始化过了。
```cpp
#define _(STRING) _translate(STRING)

bool gettext_initialized = false;

void ensure_gettext_initialized() {
    if (!gettext_initialized) {
        setlocale(LC_ALL, "");
        bindtextdomain("gmsh", "./locale");
        textdomain("gmsh");
        gettext_initialized = true;
    }
}
const char* _translate(const char* msg) {
    ensure_gettext_initialized();
    return gettext(msg);
}
```

### 多线程安全  
其实上面的代码在大部分情况下已经可用了，但是多线程的情况下可能会有一丢丢的问题（但仔细想想其实无关紧要，最多是多初始化几次而已）。为此，可以添加线程锁，以下是完整代码（未作验证）：  
```cpp
#include <iostream>
#include <locale.h>
#include <libintl.h>
#include <mutex>

#define _(STRING) _translate(STRING)
std::mutex gettext_mutex;
bool gettext_initialized = false;

void ensure_gettext_initialized() {
    std::lock_guard<std::mutex> lock(gettext_mutex);
    if (!gettext_initialized) {
        setlocale(LC_ALL, "");  // 也可用export LC_MESSAGES=zh_CN.UTF-8 指定语言
        bindtextdomain("myapp", "./locale");
        textdomain("myapp");
        gettext_initialized = true;
    }
}

const char* _translate(const char* msg) {
    ensure_gettext_initialized();
    return gettext(msg);
}


const char* messages[] = {
    _("Hello"),
    _("Goodbye!")
};
const char * bye = _("Goodbye!");

int main() {
    std::cout << _("Hello, world!") << std::endl;
    
    std::cout << bye << std::endl; 
    for (auto key : messages) {
        std::cout << key << std::endl;  // 运行时翻译
    }
    return 0;
}
```

该操作甚至可以翻译数组`messages[]` 中的字符串。😮

## 其他  
### 修改FLTK 支持字体  
默认显示汉语乱码，可以修改`FlGui::FlGui()` 构造函数，添加：
```cpp
FlGui::FlGui(int argc, char **argv, bool quitShouldExit,
             void (*error_handler)(const char *fmt, ...))
  : _quitShouldExit(quitShouldExit), lastContextWindow(0)
{
  Fl::set_font(FL_HELVETICA, "Noto Sans CJK SC"); // 确保系统已安装该字体

  // ...
}
```

### 批量替换文件内容  
在vscode 中，使用`ctrl+shift+f` 可以全局查询，并按正则表达式替换内容：  
```txt
Msg::Error\s*\(\s*"((?:[^"\\]|\\.)*)"\s*\)

匹配"" 中的字符串，支持转义字符。并替换为

Msg::Error(_("$1"))
```
在`Msg` 中常见的消息类型有：`Warning`、`Debug`、`Error`、`Info`、`StatuBar`，其他例如窗口图标，则需要具体考虑了。

### CMAKE  
添加了`I18n.h` 之后，要记得在对应的`.cpp` 文件中实现方法，并且在同级的`CMAKELIST.txt` 中检查是否将文件添加进去，否则可能造成编译时找不到定义的错误。
