---
title: Rime 输入法在Debian 上的安装过程
date: 2026-03-19 13:32:01  
description: Rime 输入法在Debian 上的安装过程
tags:
    - ibus
    - fcitx5  
    - rime

prev: 
    text: PaddleOCR 微调过程笔记
    link: '../ppocr-fine-tuning'
next: 
    text: Lark websocket 长连接监听事件
    link: '../lark-ws'
---  

# Rime 输入法在Debian 上的安装过程  

```bash
# 先卸载ibus 如果有需要的话
sudo apt-get remove --purge ibus ibus-*
sudo apt autoremove

# 安装fcitx5 rime
sudo apt update && apt install --install-recommends fcitx5 fcitx5-chinese-addons
sudo apt install fcitx5-rime

im-config  # 该命令可以配置默认输入法
```

一般按`F4` 可以切换简/繁/五笔等不同的输入模式，Rime 的配置项存在于`.local/share/fcitx5/rime/build/default.yaml` 
1. 修改完成后右键点击输入法图标：重启输入法，即可生效
2. 有些软件需要退出重开才能生效，例如Zed 编辑器
3. 如果还是有问题，就可以重启系统再试


## 参考资料  
1. [在 Debian 上透過 Fcitx 5 使用中州韻輸入法引擎](https://blog.fernvenue.com/zh/archives/configure-fcitx5-and-rime-on-debian/)  
2. [Ubuntu系统下安全卸载或替换IBus输入法框架指南](https://comate.baidu.com/zh/page/pzmn0gp8wvk)
3. [Rime 输入法中的快捷键 ](https://blog.einverne.info/post/2021/10/rime-shortcut.html)
