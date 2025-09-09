---
title: Yolo 学习笔记 -- 概览  
date: 2025-09-09 14:33:00
tags:
    - yolo
    - python
---

记录一些学习yolo 过程中的知识点。零基础。  

<!-- more -->

## 安装  
YOLO 系列对Python 和PyTorch 的版本都有要求，故而采用miniconda 安装，Python 和Torch 的版本尽量选择最低小版本的最新release。因为小版本号可以保证API 兼容而最新release 可以保证代码较新。总有刁库这儿不兼容或者那儿不兼容。  

### 安装miniconda  
按照[Conda官网说明](https://www.anaconda.com/docs/getting-started/miniconda/install)安装miniconda，然后创建环境：  
```bash
conda create --name yolov5s python==3.8
conda activate yolov5s  # 激活环境  
```

### 安装yolo 与pytorch  
在[yolov5 入门手册](https://docs.ultralytics.com/zh/yolov5/quickstart_tutorial/)中，推荐从github 克隆仓库下来，但是在v8 或者更新版本中，便取消了这一过程。仿照v8 的教程，直接从pip 安装也是可以的：
```bash
pip install -U ultralytics  # v5 其实指的是预训练权重的版本，代码是向后兼容（新代码能跑旧权重）的
```

值得注意的是，`ultralytics` 在首次运行时会创建一个[配置文件](https://github.com/ultralytics/ultralytics/issues/807)，用于指定数据集的保存目录等。可以通过`yolo setting` 命令查看配置文件：  
```js
// /home/username/.config/Ultralytics/settings.json
{
  "settings_version": "0.0.6",
  "datasets_dir": "datasets",  // 可以是绝对路径，但是推荐写成相对路径，以便和项目共存
  "weights_dir": "weights",
  "runs_dir": "runs",
  "uuid": "********",
  "sync": true,
  "api_key": "",
  "openai_api_key": "",
  "clearml": true,
  "comet": true,
  "dvc": true,
  "hub": true,
  "mlflow": true,
  "neptune": true,
  "raytune": true,
  "tensorboard": false,
  "wandb": false,
  "vscode_msg": true,
  "openvino_msg": false
}
```

### 运行  
```python
import cv2
from ultralytics import YOLO

# 加载模型权重文件，如果文件不存在则下载（至项目根目录）。
model = YOLO("yolov5s.pt")

# 显示模型信息（非必须）
model.info()

# 通过示例数据集训练，数据集不存在则下载。目录即通过上面配置文件指定
results = model.train(data="coco08.yaml", epochs=100, imgsz=640)

# 通过训练后的模型处理文件
results = model("test.jpg")

# 结果分析
annotated = results[0].plot()  

cv2.imshow("YOLOv8 Detection", annotated)
cv2.waitKey(0)
cv2.destroyAllWindows()
```

相比克隆项目要清晰许多。很多示例文件和代码在git 仓库里面，可以自行参考。

### OpenXLab 数据集下载  
上海人工智能实验室开放了许多数据集可供下载使用，需要在[openxlab.org.cn](https://openxlab.org.cn) 注册账号才能使用：  
```bash
pip install -U openxlab 
```
示例代码如下：  
```python
import openxlab
from openxlab.dataset import info, get, download
openxlab.login(ak=<Access Key>, sk=<Secret Key>) # 通过密钥登录验证

info(dataset_repo='cvnet/6WEED') #数据集信息查看（非必须）
# 下载文件记得修改目录
get(dataset_repo='cvnet/6WEED', target_path='6weed') # 整个数据集下载，
download(dataset_repo='cvnet/6WEED',source_path='/README.md', target_path='6weed') # 下载数据集中的某个文件
```

## 数据集
yolo 通过`.yaml` 文件来描述一个数据集，其中主要包含以下元素：  
```yaml
# dataset.yaml 
path: 'datasets/coco128'  # 包含数据集根目录，可以是绝对路径或者相对路径
train: 'images/train2017' # 相对于path 的相对路径的文本文件，训练数据（图片）集  
val: 'images/train2017 '   # 相对于path 的相对路径，验证数据（图片）集，样本太小训练验证一样
# test: ''  # 相对于path 的相对路径，测试数据（图片）集（非必须）

# 下面这种写法也是支持的，更适合大数据集
# train: /home/ge/datasets/6WEED/train.txt  #  1390train images (relative to 'path')
# val: /home/ge/datasets/6WEED/val.txt      #  396val images (relative to 'path')
# test: /home/ge/datasets/6WEED/test.txt    #  204test images (optional)

# 分类，也可以用数组的形式
# 类别数量
# nc: 3 
# names: [person, bicycle, car]
names:
  0: person
  1: bicycle
  2: car
  # ...

# 下载数据集（可选，适合小数据集方便演示）
download: https://github.com/ultralytics/assets/releases/download/v0.0.0/coco128.zip
```

实际文件目录如下：
```text
datasets/coco128/
├── images/
│   └── train2017/   # 图片
│       ├── 000000000009.jpg
│       └── ...
└── labels/
    └── train2017/   # 标签
        ├── 000000000009.txt
        └── ...
```
YOLO 在扫描图片目录时，会自动到同级的`labels/` 目录下去找对应的`.txt` 文件。

实际通过标注工具可以自动生成YAML 文件。  

yolo 的标注文件有如下特点：  
- 图片名称与标注文件名称一一对应  
- 图片位于images、标注文件位于labels  
- 标注文件txt 的每一行代表一个物体（一般）
- 标注数值一般是相对图片尺寸的比例，~~可能也有像素值~~

### 目标检测  
目标检测一般使用竖直的矩形表示，标注值为矩形的中心点和尺寸：  
```txt
<class-index> x_center y_center width hight 
0 0.48 0.63 0.69 0.71
1 0.481719 0.634028 0.690625 0.713278
```

### OBB 定向盒  
与目标检测类似，只不过是通过四个点确定一个矩形：  
```txt
<class-index> x1 y1 x2 y2 x3 y3 x4 y4 
0 0.780811 0.743961 0.782371 0.74686 0.777691 0.752174 0.776131 0.749758
```

### 语义分割  
语义分割使用的是多边形，因此每一行的列数不固定（至少要有三个点）：  
```txt
<class-index> <x0> <y0> <x1> <y1> ... <xn> <yn>  
0 0.681 0.485 0.670 0.487 0.676 0.487
1 0.504 0.000 0.501 0.004 0.498 0.004 0.493 0.010 0.492 0.0104
```

### 姿态检测  
姿态检测需要同时用到矩形和观点特征，每一类物体的关键点维度应该是相同的，不同物体可以不同。根据关键点的可见性，可以分成以下两种格式：  
#### Dim=2  
默认所有点都是可见：
```txt
<class-index> <x> <y> <width> <height> <px0> <py0> <px1> <py1> ... <pxn> <pyn>
```
#### Dim=3
可见性有下面三种：0 不存在、1 不可见、2 可见。
```txt
<class-index> <x> <y> <width> <height> <px0> <py0> <p0-visibility> <px1> <py1> <p1-visibility> <pxn> <pyn> <pn-visibility>
```
反映在`.yaml` 中，主要有以下属性需要添加：
```yaml
# 关键点维度：[所有关键点类别数量, Dim]
kpt_shape: [17, 3]
# 是否存在对称点对称
flip_idx: [0, 2, 1, 4, 3, 6, 5, 8, 7, 10, 9, 12, 11, 14, 13, 16, 15]
```

### 分类问题 
分类问题并没有对txt 有要求，但是要求图片按照一定结构组织：  
```txt
root/
|
|-- train/
|   |-- airplane/
|   |   |-- 10008_airplane.png
|   |   |-- ...
|   |
|   |-- automobile/
|   |   |-- 1000_automobile.png
|   |   |-- ...
|   |
|   |-- ...
|
|-- test/
|   |-- 同上
|
|-- val/ (optional)
|   |-- 同上
```

### 多目标追踪  
尚未更新

## 标注工具  
| 工具 | 类型 | 特点 | YOLO 支持 |
| --- | --- | --- | --- |
| **LabelImg** | 桌面 GUI | 轻量，经典标注工具，支持矩形框 | 支持直接导出 YOLO `.txt` |
| **Label Studio** | Web / 桌面 | 可标注图片/视频/音频，灵活，支持多人协作 | 支持 YOLO 格式导出（需配置模板） |
| **CVAT** | Web | 企业级标注平台，可多人协作、视频标注 | 支持 YOLOv5/YOLov8 格式导出 |
| **Roboflow** | 云平台 | 自动生成训练/验证集划分，自动生成 `data.yaml` | 支持 YOLOv5/v8，自动生成 YAML 和标签 |
| **makesense.ai** | 在线免费 | 无需安装，支持导出多种格式 | 支持 YOLO |

### label-studio  
```bash
pip install -U label-studio # 安装
label-studio 
```
支持多种标注方式，但是导出的文件和yolo 并不完全一致。

### labelme  
labelme 的标注结果是json 文件，需要通过脚本或者工具转换成yolo 格式，如果要转换成姿态检测功能兼容的，一般需要包含矩形（用于分类）和关键点（用于姿态检测）两种元素。对于元素重叠、遮挡的情况，则需要通过`group_id` 或者`flags` 进行设置： 
```bash
# group_id 可以用于区分重合或者包含的元素是否是同一分组  
# flags 比较特殊，只能在启动labelme 时传入，并且分为文件级和标签级，姿态检测时常用到标签级
uvx labelme --labels=flag1,flag2 --labelflags='{.*: [occluded, truncated], person: [male]}'
# 或者  
uvx labelme --labels image_labels.txt --labelflags label_flags.json
```
以下是`image_labels.txt` 和`label_flags.json` 的内容示例：  
- image_labels.txt  
```text
__ignore__
boat
bottle
bus
car
cat
tv/monitor
```

- label_flags.json  
```json
// ".*" 对应所有标签的共同属性  
// "person" 仅对person 标签生效 
{
    ".*": [
        "occluded",
        "truncated"
    ],
    "person": [
        "male"
    ]
}
```

在标注结果`json` 文件中，各种可能的`flag` 会组成一个字典，通过`get()` 方法获取最为妥当。 

### labelme 标注文件  
```json
{
  "version": "4.5.6",  // 版本号
  "flags": {},         // 全局标签
  "shapes": [          // 所有形状
    {
      "shape_type": "rectangle",// 标签类型
      "label": "black-bishop",  // 标签名
      "points": [               // 两点定矩形
        [ 250.5, 44.0],
        [ 285.0, 112.5]
      ],
      "group_id": null,         // 组名，只对该json 生效
      "description": "",
      "flags": {},              // 形状标签
      "mask": null              // 不知道有啥用
    },
    {
      "label": "p1",
      "points": [
        [426.77570093457945,388.4423676012461]
      ],
      "group_id": 1,
      "description": "",
      "shape_type": "point",
      "flags": {
        "hidden": true
      },
      "mask": null
    },
    {
      "label": "l",
      "points": [
        [ 317.0626349892009, 438.22894168466524 ],
        [ 427.64578833693304, 434.9892008639309 ,
        [ 429.58963282937367, 431.10151187904967 ]
      ],
      "group_id": null,
      "description": "",
      "shape_type": "polygon",
      "flags": {},
      "mask": null
    },
     {
      "label": "circle",
      "points": [
        // 圆心
        [ 241.24352331606218, 138.4455958549223 ],
        // 圆上一点
        [ 281.6580310880829, 172.12435233160622 ]
      ],
      "group_id": null,
      "description": "",
      "shape_type": "circle",
      "flags": {},
      "mask": null
    },
    {
      "label": "line-stripe",
      "points": [
        [ 331.39896373056996, 125.49222797927462 ],
        // ... 
        [ 321.55440414507774, 300.10362694300517 ]
      ],
      "group_id": null,
      "description": "",
      "shape_type": "linestrip",
      "flags": {},
      "mask": null
    }

  ],
  "imagePath": "0af.jpg",
  "imageData": "/9j/4AAQ...",   // base64
  "imageHeight": 512,
  "imageWidth": 765
}
```

## 训练  
```python
# model = YOLO("yolov5s.pt")  # 加载预训练权重和网络结构
model = YOLO("yolov5s.yaml")  # 仅加载网络结构，不加载权重信息，从头训练
results = model.train(data="coco08.yaml", epochs=100, imgsz=640)
# imgsz=640: 图片会被转化成640*640 的正方形，越大越精确、越耗时
# batch=16: 批次大小  
# epochs=100: 训练轮数
# data: 指定数据集配置文件
# weights: 初始权重，如yolov5s.pt，也可以为空，表示从头开始训练
```

尽量在预训练权重基础上进行微调，而不是从头开始，更多参数请参考[参数配置](https://docs.ultralytics.com/zh/usage/cfg/#train-settings)。

## 导出  
导出结果可以参考官方[文档](https://docs.ultralytics.com/zh/yolov5/tutorials/model_export/#exported-model-usage-examples)或者[新版文档](https://docs.ultralytics.com/zh/modes/export/#usage-examples)，下面是两个简单的示例：
```python
# 导出结果在runs/detect/tain??/weights/，不支持自定义文件名好像
# 默认会导出best.pt 和last.pt 一般用best 会好一些，last 可能会过拟合
model.export(format='onnx', dynamic=True)  # 允许处理不同尺寸的图片文件
model.export()  # 默认pt 格式  
model.export(format='engine')  # TensorRT 格式会更快
```