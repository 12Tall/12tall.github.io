---
title: Wechat QRCode 二维码扫描
date: 2026-01-28 08:37:31  
description: 六年前的模块，依然好使
tags:
    - python
    - 神经网络  
    - 机器视觉

prev: 
    text: Docker 基本操作  
    link: '../docker-basic'
next: 
    text: Todo
    link: '.'
---  

做OCR 识别时，发现物体标签上有二维码信息，用手机微信是可以扫描出来，但是用`pyzbar` 却无法识别。搜索后发现这篇文章[微信AI设计了一种超分辨率技术，让扫二维码更方便](https://mp.weixin.qq.com/s/ZEthIoGsIm1KsHheWUviZg)，进一步搜索后发现`opencv` 中已经集成了该功能。真的是踏破铁鞋无觅处，得来全不费工夫。  

理论知识不多赘述，核心的思路是：  
1. 通过超分辨率模型使得原本模糊的二维码变得清晰可识别  
2. 通过模型蒸馏，大幅缩小模型体积并提高效率  

虽然大模型的准确率高，但是消耗资源多，在边缘计算设备中，蒸馏后的小模型反而更有优势。  

## 安装使用  

有时系统会有`python-opencv` 库，但是因为版本原因可能没有`WechatQRCode` 模块，这时候需要手动更新库：  

```bash
# 先卸载opencv 相关库
pip3 uninstall -y opencv-python opencv-contrib-python opencv-python-headless opencv-contrib-python-headless

# 重新安装最新的 opencv-contrib-python
pip3 install opencv-contrib-python
```

安装后还需要[下载模型和权重文件](https://github.com/WeChatCV/opencv_3rdparty)，是基于`CAFFE`框架的，可以通过一些工具转化为torch 或者tf 格式。不过对于一般使用来说不影响。  

使用方法如下：  
```python{3-7,10}
import cv2

detector = cv2.wechat_qrcode.WeChatQRCode(
    "detect.prototxt",
    "detect.caffemodel", 
    "sr.prototxt", 
    "sr.caffemodel")

img = cv2.imread("123.png")
res, points = detector.detectAndDecode(img)
print(res, points)

# 得到结果如下（假设包含两个二维码）：
# (
#     '二维码1 包含的文本', 
#     '二维码1 包含的文本'
# ) 
# (
#     array([[232.75479 ,  88.500145],
#        [227.90897 ,  19.418858],
#        [296.88034 ,  21.399696],
#        [301.46844 ,  89.96361 ]], dtype=float32), 
#     array([[318.8573 , 805.2406 ],
#        [313.44568, 742.3865 ],
#        [372.53503, 732.10156],
#        [377.7074 , 794.7845 ]], dtype=float32)
# )
```

经过测试，灰度处理后的图像能容易识别出来二维码信息：  
```python{7,11-12}
import cv2
import numpy as np

img = cv2.imread("多个二维码.jpg", cv2.IMREAD_GRAYSCALE)

# 计算图像平均亮度
mean_brightness = np.mean(img)

# 如果平均亮度小于128（偏暗，说明是黑色背景），则进行反色
if mean_brightness < 128:
    img = cv2.bitwise_not(img)
    print("检测到黑色背景，已进行反色处理")
else:
    print("检测到白色背景，保持原样")

# 保存结果图片
# cv2.imwrite("output.png", img)

res, points = detector.detectAndDecode(img)
print(res, points)
```

## 参考资料 
1. [微信AI设计了一种超分辨率技术，让扫二维码更方便](https://mp.weixin.qq.com/s/ZEthIoGsIm1KsHheWUviZg)  
2. [微信二维码引擎OpenCV开源！3行代码让你拥有微信扫码能力 | 知乎](https://mp.weixin.qq.com/s/AknsKNqVmvr8aohV25_ZcQ)