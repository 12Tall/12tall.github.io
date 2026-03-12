---
title: PaddleOCR 微调过程笔记
date: 2026-03-12 09:08:30  
description: PaddleOCR 微调过程笔记
tags:
    - python
    - conda
    - ocr

prev: 
    text: Wechat QRCode 二维码扫描
    link: '../wechat-qrcode'
next: 
    text: Todo
    link: '.'
---  

# PaddleOCR 微调过程笔记  

在做OCR 项目时，发现除了带有视觉功能的大模型外，PaddleOCR/PPOCR 的效果是最好的，但是其对于某些特殊工况下的精度不够。为了适应我们的特殊工况，故对该模型进行微调（仅展示`rec` 部分）。

## 数据集标注  
采用[XAnyLabeling](https://github.com/CVHub520/X-AnyLabeling) 进行标注，最新的版本可以调用PPOCR-V5 的模型自动识别字符串，只需要人工做些微调就可以了，并且可以导出PPOCR 可用的格式。（不是重点）

## 环境配置（重点）
按照官网的教程（没有一个统一的教程）或者问ChatGPT，他们会给一个过时的答案。经过测试之后，下面这个步骤能够较好的用于PPOCR-V5 的微调，但是需要conda 配合（因为用uv 跟宿主环境有时候不好区分）：
```bash
conda create -n ppocr python=3.12  # 创建Python 3.12 环境（3.10版本太低了）
conda activate ppocr  # 激活环境  

conda config --add channels nvidia  # 添加Nvidia 的源

# 安装paddlepaddle-gpu。2.6.* 版本的不兼容H100 GPU，其他显卡训练时还会有内存泄漏的问题
# 这一步会自动安装合适的CUDA 依赖
conda install paddlepaddle-gpu==3.0 --channel https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/Paddle/ 

# 克隆项目
git clone https://github.com/PaddlePaddle/PaddleOCR
cd PaddleOCR/

# 安装依赖
python -m pip install -r requirements.txt
python -m pip install -e .

# 下载别人做好的数据集
wget https://paddle-model-ecology.bj.bcebos.com/paddlex/data/ocr_rec_dataset_examples.tar
tar -xf ocr_rec_dataset_examples.tar
# 下载预训练参数
wget https://paddle-model-ecology.bj.bcebos.com/paddlex/official_pretrained_model/PP-OCRv5_server_rec_pretrained.pdparams
```

之后修改配置文件就可以执行训练过程了。  

## 配置文件  
下面是配置文件以及对应的注释，尽量按照以下要求去做：
1. 每个数据集都包含自己的配置文件；  
2. 配置文件尽量只改动文件路径和批次大小；  
```yaml
# 不要照抄该文件，请在官方文件上进行修改！！！
Global:
  model_name: PP-OCRv5_server_rec # 静态模型名
  debug: false  # 是否开启调试模式
  use_gpu: true # 是否使用GPU
  epoch_num: 75 # 训练轮数 // [!code focus] 
  log_smooth_window: 20  # 日志平滑窗口
  print_batch_step: 10  # 每多少批打印一次日志
  save_model_dir: ./output/my_model  # 结果保存位置 // [!code focus] 
  save_epoch_step: 1  # 多少轮保存一次
  eval_batch_step: [0, 2000]  # 每多少step 进行一次评估
  cal_metric_during_train: true  # 训练过程中计算指标
  calc_epoch_interval: 1  # 每多少轮计算指标
  pretrained_model:   # 预训练模型路径
  checkpoints:  # 恢复训练checkpoint
  save_inference_dir: # 导出推理模型路径
  use_visualdl: false # 是否使用VisualDL 可视化
  infer_img: doc/imgs_words/ch/word_1.jpg # 测试图片【没搞懂什么用】
  character_dict_path: ./ppocr/utils/dict/ppocrv5_dict.txt # 字符字典文件【重要，如果训练与预测不一致会识别出乱码】
  max_text_length: &max_text_length 25  # 最大文本长度
  infer_mode: false # 禁用推理模式
  use_space_char: true  # 包含空白字符
  distributed: true # 分布式训练
  save_res_path: ./output/rec/my_model.txt  # 结果保存路径
  d2s_train_image_shape: [3, 48, 320] # 训练图像尺寸3通道


Optimizer:  # 优化器
  name: Adam
  beta1: 0.9
  beta2: 0.999
  lr:
    name: Cosine
    learning_rate: 0.0005
    warmup_epoch: 1
  regularizer:
    name: L2
    factor: 3.0e-05


Architecture: # 网络结构
  model_type: rec
  algorithm: SVTR_HGNet
  Transform:
  Backbone:
    name: PPHGNetV2_B4
    text_rec: True
  Head:
    name: MultiHead
    head_list:
      - CTCHead:
          Neck:
            name: svtr
            dims: 120
            depth: 2
            hidden_dims: 120
            kernel_size: [1, 3]
            use_guide: True
          Head:
            fc_decay: 0.00001
      - NRTRHead:
          nrtr_dim: 384
          max_text_length: *max_text_length

Loss: # 损失函数
  name: MultiLoss
  loss_config_list:
    - CTCLoss:
    - NRTRLoss:

PostProcess:    # 后处理
  name: CTCLabelDecode

Metric: # 评价指标
  name: RecMetric
  main_indicator: acc

Train:  # 训练数据
  dataset:
    name: MultiScaleDataSet
    ds_width: false
    data_dir: ./train_data/  # // [!code focus] 
    ext_op_transform_idx: 1
    label_file_list:
    - ./train_data/train.txt  # // [!code focus] 
    transforms:
    - DecodeImage:
        img_mode: BGR
        channel_first: false
    - RecAug:
    - MultiLabelEncode:
        gtc_encode: NRTRLabelEncode
    - KeepKeys:
        keep_keys:
        - image
        - label_ctc
        - label_gtc
        - length
        - valid_ratio
  sampler:
    name: MultiScaleSampler
    scales: [[320, 32], [320, 48], [320, 64]]
    first_bs: &bs 256 # 定义批大小为128【重要，视显卡能力确定】 // [!code focus] 
    fix_bs: false
    divided_factor: [8, 16] # w, h
    is_training: True
  loader:
    shuffle: true
    batch_size_per_card: *bs
    drop_last: true
    num_workers: 16
Eval:
  dataset:
    name: SimpleDataSet
    data_dir: ./train_data/  # // [!code focus] 
    label_file_list:
    - ./train_data/val.txt  # // [!code focus] 
    transforms:
    - DecodeImage:
        img_mode: BGR
        channel_first: false
    - MultiLabelEncode:
        gtc_encode: NRTRLabelEncode
    - RecResizeImg:
        image_shape: [3, 48, 320]
    - KeepKeys:
        keep_keys:
        - image
        - label_ctc
        - label_gtc
        - length
        - valid_ratio
  loader:
    shuffle: false
    drop_last: false
    batch_size_per_card: 128
    num_workers: 4
```

## 训练过程  
仅记录几个重要步骤，避免踩坑（假设数据集在`./train_data`，配置文件是`./train_data/PP-OCRv5_server_rec.yml`）：  
```bash
# 通过配置文件进行训练(我这里直接借用了原版的配置文件)
python3 tools/train.py -c train_data/PP-OCRv5_server_rec.yml  -o Global.pretrained_model=./PP-OCRv5_server_rec_pretrained.pdparams 

# 通过训练过程效果最好的参数进行一波预测
python3 tools/infer_rec.py -c ./train_data/PP-OCRv5_server_rec.yml -o Global.infer_img='./train_data/images/train_word_1.png' Global.pretrained_model='./output/my_model/latest'
## 以上结果还是正确的 ##  

# 导出模型
python3 tools/export_model.py -c ./train_data/PP-OCRv5_server_rec.yml -o Global.pretrained_model='./output/my_model/latest' Global.save_inference_dir="./PP-OCRv5_server_rec_infer/"

# 验证导出的模型  
python3 tools/infer/predict_rec.py --image_dir=./train_data/images/test.jpg --rec_model_dir=./PP-OCRv5_server_rec_infer/
## 结果可能会出现乱码 ##  

## 导出onnx 模型  
# python3 -m pip install paddle2onnx onnx onnxruntime
# paddlex --paddle2onnx --paddle_model_dir ./inference/my_model --onnx_model_dir ./inference/my_model/onnx  
```

## 调用
```python
from paddleocr import PaddleOCR

ocr = PaddleOCR(
    text_recognition_model_dir="./PP-OCRv5_server_rec_infer",
    use_doc_orientation_classify=False, # 通过 use_doc_orientation_classify 参数指定不使用文档方向分类模型
    use_doc_unwarping=False, # 通过 use_doc_unwarping 参数指定不使用文本图像矫正模型
    use_textline_orientation=False, # 通过 use_textline_orientation 参数指定不使用文本行方向分类模型
    device="CPU",
    text_det_unclip_ratio=1.5,  # 检测框扩大，一般2.0 就比较大了
    text_det_limit_side_len=960, # 图像长边限制，提高远距离小字的识别率
    text_det_box_thresh=0.6, # 如果有漏检，则调低
    text_det_thresh=0.3, # 减小保留更多微弱文字区域
)

result = ocr.predict("./test.jpg")
for res in result:
    res.print()
    res.save_to_img("output")
    res.save_to_json("output")
```
识别结果将会保存在`./output` 文件夹下。  

如果不希望调用全流程，则需要通过`TextRecognition` 模块实现。
 
## 参考资料  
1. [PP-OCRv5:4.2.1 通过参数指定本地模型路径](https://www.paddleocr.ai/main/version3.x/pipeline_usage/OCR.html#421)  
2. [PP-OCRv5_server_rec.yml](https://github.com/PaddlePaddle/PaddleOCR/blob/main/configs/rec/PP-OCRv5/PP-OCRv5_server_rec.yml)
3. [Bash 随机拆分TXT](https://chatgpt.com/s/t_69b27608cc148191b06616bcaa77a558)  
4. [PPOCR 文本识别模块](https://www.paddleocr.ai/main/version3.x/module_usage/text_recognition.html#42)
5. [转换模型后识别结果乱码](https://github.com/PaddlePaddle/PaddleOCR/issues/10992)