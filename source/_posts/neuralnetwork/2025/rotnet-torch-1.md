---
title: 通过pytorch 理解RotNet（上）
date: 2025-12-14 13:12:08
tags:
    - RotNet  
    - torch  
    - CNN  
---

RotNet 是一个可以判断图片旋转角度的CNN 网络，作者有着非常详细的[文章](https://d4nst.github.io/2017/01/12/image-orientation/)解释，用来理解CNN 以及如何复用现有的申请网络模型都非常有好处。这里先记录下如何通过MNIST 数据集训练识别手写数字的方向。  

<!-- more -->

## 数据集准备  
因为torchvision 提供了MNIST 数据集，假设MNIST 数据集中的图片都是但是我们需要对该数据集做一些随机旋转工作，并以旋转角度替换掉文本标签。  

### Dataset 类  
Dataset 类负责提供单个样本的读取逻辑，必须实现两个接口：  
- `__len__()`：数据集的总长度  
- `__getitem__(index:int)`：获取具体样本和标签    

例如，可以继承torchvision 的MNIST 类：  
```python
from torchvision import datasets, transforms

class RotMNIST(datasets.MNIST):
    """
    继承MNIST 数据集，并将随机旋转角度(间隔45度)设置为标签
    """

    def __init__(self, 
            root="./data",
            train=True, 
            download=True
        ):
        super().__init__(root, train, download=download)
        # 可以使用torchvision 提供的一些现成图片变换方法
        self.to_tensor = transforms.ToTensor()

    def __getitem__(self, index):
        """每次获取的数据都不一样"""
        img, _ = super().__getitem__(index)
        angle = random.randint(0, 359)  # 随机旋转的角度
        # 对图片进行旋转操作
        img = torchvision.transforms.functional.rotate(img, angle)
        img = self.to_tensor(img)  # 要将图片转换成Tensor 对象返回
        return img, angle//45
```

### DataLoader 类  
DataLoader 类负责批量化、打乱、并行加载数据，但并不关心数据的具体含义：  
```python
from torch.utils.data import DataLoader

# 初始化数据集对象
train_dataset_rotated = RotMNIST()
# 加载数据集，随机打乱、每个批次包含64 个样本
train_loader = DataLoader(train_dataset_rotated, batch_size=64, shuffle=True)

# 查看数据格式
img, angle = train_dataset_rotated[0]
print(f"\n单个样本:")
print(f"图片形状: {img.shape}")  
# 图片形状: torch.Size([1, 28, 28])
# 单通道（灰度图），28px × 28px
print(f"标签（旋转角度）: {angle:.2f}")
```

## 神经网络模型  
torch 模型建立的主要步骤有两个：  
1. 在`__init__(self,)` 中定义层  
2. 在`forward(self,x)` 中去连接层（也可以复用，因为复用会共享权重，所以一般会重用ReLU、Sigmoid 这种激活函数）  

参考[RotNet-MNIST](https://github.com/d4nst/RotNet/blob/master/train/train_mnist.py) 模型，卷积部分的模型结构如下：  
![](model.svg)

下面是详细的代码实现：
```python
class RotCNN(torch.nn.Module):

    def __init__(self,):
        super(RotCNN, self).__init__()
        # torch 不需要显示指定输入层，但是MNIST 输入是28×28的PIL 图片
        # 输入1 通道，32个卷积核/输出通道数，卷积核尺寸3×3, padding=1 表示保持原尺寸
        self.conv_1 = torch.nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.conv_2 = torch.nn.Conv2d(32, 64, kernel_size=3, padding=1)
        # self.conv_3 = torch.nn.Conv2d(64, 128, kernel_size=3, padding=1)
        # 池化层会缩小每个通道的尺寸
        self.max_pooling_1 = torch.nn.MaxPool2d(2)
        self.dropout_1 = torch.nn.Dropout2d(0.25)  # 随机dropout
        # 展平
        self.flatten_1 = torch.nn.Flatten()
        # Linear 表示全连接层
        self.fc_1 = torch.nn.Linear(64*14*14, 128)  # 通道参数×池化后的尺寸
        # 全连接层用普通的Dropout 而不是Dropout1d
        self.dropout_2 = torch.nn.Dropout(0.25)
        self.fc_2 = torch.nn.Linear(128, 8)

        self.reLu = torch.nn.ReLU()
        # 不需要在模型中定义softmax！训练时用CrossEntropyLoss会自动处理
        # self.softmax = torch.nn.Softmax()

    def forward(self, x):
        x = self.reLu(self.conv_1(x))
        x = self.reLu(self.conv_2(x))
        x = self.max_pooling_1(x)
        x = self.dropout_1(x)
        x = self.flatten_1(x)
        x = self.reLu(self.fc_1(x))
        x = self.dropout_2(x)
        x = self.fc_2(x)
        return x
```

## 训练  
pytorch 没有一键训练的方法，需要自己手工控制这个过程。整体来说也不算太复杂：  
1. 初始化模型  
2. 定义损失函数与优化器  
3. 开启训练模式，训练n 个epochs：  
    1. 从数据集获取数据  
    2. 正向过程  
    3. 反向过程  
    4. 更新参数  
5. 计算准确度和损失值  

具体训练过程代码如下：  
```python
import torch

# 使用CUDA 初始化模型
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = RotCNN().to(device)

# 多分类单标签的损失函数CrossEntropyLoss，已经包含了softmax
criterion = torch.nn.CrossEntropyLoss()
# 根据损失函数值更新模型的参数，一般用Adam  
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
# 正向过程->损失函数->反相过程->更新参数  

# 将模型切换到训练模式  
model.train()

# 训练100 个epochs
for epoch in range(100):
    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in train_loader:  # 每次获取64 张图片及标注结果
        images = images.to(device)
        labels = labels.to(device)

        # 前向传播
        outputs = model(images)  # [batch_size, num_classes]
        # 计算误差
        loss = criterion(outputs, labels)

        # 反向传播
        optimizer.zero_grad()  # 将模型中所有参数的梯度清零，为当前 batch 的反向传播做准备。
        loss.backward()  # 反向过程，结果会存放在model.grad 参数中  
        optimizer.step()  # 更新模型参数

        # loss 与 model 没有 Python 对象层面的直接连接；
        # 它们通过 outputs 以及 outputs.grad_fn 中记录的运算依赖，
        # 间接但完整地连接到 model.parameters()

        # 统计准确率
        _, predicted = torch.max(outputs.data, 1)  # 求每一行的最大值及其对应的索引
        total += labels.size(0)  # 所有文件数
        correct += (predicted == labels).sum().item()  # 正确结果数量
        running_loss += loss.item()  # 损失值

    accuracy = 100 * correct / total  # 准确率
    avg_loss = running_loss / len(train_loader)  # 平均损失
    print(  # 打印结果
        f'Epoch [{epoch+1}/100], Loss: {avg_loss:.4f}, Accuracy: {accuracy:.2f}%')

```
这里仅理清实现思路和流程，没有接入提前停止等工程化的实践。

## 保存结果与验证  
可以将训练结果保存到`.pth` 文件：  
```python
# 保存模型
torch.save({
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
}, 'rotation_model.pth')
print("\n模型已保存到 rotation_model.pth")
```

### 加载模型并验证  
```python
model = RotCNN()          # 结构必须和保存时完全一致
model.to(device)

checkpoint = torch.load('rotation_model.pth', map_location=device)
model.load_state_dict(checkpoint['model_state_dict'])

# 开启验证模式
model.eval()

# 加载测试集
test_dataset = RotMNIST()
test_loader = DataLoader(test_dataset, batch_size=128,
                         shuffle=False, num_workers=2)

# 关闭梯度计算（节省计算资源）
with torch.no_grad():
    for i in range(5):  # 只测试前5 个样本
        img, true_angle = test_dataset[i]  # 实际值
        img = img.unsqueeze(0).to(device)

        outputs = model(img)  # 预测值
        # 预测的可能性
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        # 最大可能行的角度范围（最大概率的那个）
        predicted_angle = torch.argmax(probabilities, dim=1).item()
        # 相应的置信度
        confidence = probabilities[0, predicted_angle].item()

        # 计算误差（考虑循环）
        error = abs(predicted_angle - true_angle)
        error = min(error, 360 - error)

        print(f"样本 {i+1}: 真实={true_angle}, 预测={predicted_angle}, "
              f"误差={error}, 置信度={confidence:.2%}")

```


## 改进  
测试结果，如果按1 度作为标签间隔进行划分的话，训练准确度变化不明显，尤其是准确度到达60% 之后上升就比较慢了。但是如果以45度或者30度的角度区间划分的话，则精确度提高的非常快。因此，在工程条件允许的情况下，可以尽量减少标签种类。  

因为数据集每次被调用都会随机旋转图片，故而效率较低。在真正的训练中可以预先设定好旋转角度，这样训练效率会高很多。

pytorch 的实现封装程度整体不如tensorflow，因为训练过程部分还需要自己手工控制。也许后面多学学就能掌握更高级的用法了:(

## 参考资料  
1. [Correcting Image Orientation Using Convolutional Neural Networks](https://d4nst.github.io/2017/01/12/image-orientation/)
