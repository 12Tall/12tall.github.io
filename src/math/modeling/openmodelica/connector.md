---  
title: 连接器 connector  
date: 2022-08-25   
timeLine: true
sidebar: false  
icon: superscript
category:  
    - 数学    
tag:   
    - OpenModelica  
    - 建模
---  

以前建模是基于方程的，需要知道完整的系统/模型的本构方程（反应系统宏观性质的数学模型）。现在我们可以通过连接器，创建可重用的模型或组件，有了连接器，就可以让模型与模型进行交互了。

## 非因果连接  
这个名字怪怪的，但是只要记住两个概念：  
- 横跨变量（cross，势）。是让部件运动的原因，如温度、压力、电压等；  
- 穿越变量（flow，流）。代表一些保守量（守恒量，如电荷量、体积等）对于时间的微分，如电流、流量等。  

> 关于流量的正负号，我们定义流入部件为正，流出为负。  

## 简单领域  
简单领域是指connector 仅带有一个穿越量以及一个横跨量的工程领域。也就是说该连接器只涉及一个保守量。常见的简单领域如下：  

| 领域         | 穿越变量            | 横跨变量 | 保守量     |
| ------------ | ------------------- | -------- | ---------- |
| 电气         | 电流/A              | 电压/V   | 电荷守恒   |
| 热学         | 热/W                | 温度/K   | 能量守恒？ |
| 平移         | 力/N                | 位置/m   | 动量守恒   |
| 旋转         | 力矩/Nm             | 角/rad   | 角动量守恒 |
| 不可压缩流体 | 流量/$m^3s^{-1}$    | 压强/Pa  | 体积守恒   |
| 压缩流体     | 质量流率/$Kgs^{-1}$ | 压强/Pa  | 质量守恒   |

### 两个约束条件  
1. 要求穿越变量应为某个守恒量的时间导数。这样做的原因是穿越变量会被用于建立系统的广义守恒方程。因此，穿越变量为守恒量的导数便至关重要。  
2. 要求横跨变量应为领域内所有本构方程和经验公式内的最低阶导数。我们希望横跨变量不要经过太多次微分。  

## 热流体建模  
有时连接器需要涉及不止一个保守量，那么就可以在其中添加更多的穿越变量和跨越变量：  
```modelica  
connector ThermoFluid
    Modelica.SIunits.Pressure p;
    flow Modelica.SIunits.MassFlowRate m_dot;
    Modelica.SIunits.Temperature T;
    flow Modelica.SIunits.HeatFlowRate q;
  end ThermoFluid;
```  

## 框图连接器  
除了非因果性的连接器外，Modelica 还可以用来建模系统的信息流。这就是框图连接器，框图连接器包含输入信号和输出信号：  
```modelica
within ModelicaByExample.Connectors;
package BlockConnectors "Connectors for block diagrams"
  connector RealInput = input Real;
  connector RealOutput = output Real;
  connector IntegerInput = input Integer;
  connector IntegerOutput = output Integer;
  connector BooleanInput = input Boolean;
  connector BooleanOutput = output Boolean;
end BlockConnectors;
```  

## 图标标注  
通过图标标注，可以给连接器创建图形，这样就不用通过代码建模了。  

### Icon  
`Icon` 主要表示模型的图标，由以下几种元素选择性地组合而成：  
- `Ellipse`，圆  
- `Rectangle`，矩形  
- `Text`，文本    

其中，各元素都包含以下属性：  
- `extent`，位置、大小    
- `fillColor`，填充颜色     
- `fillPattern`，填充模式    
- `pattern`，框线模式    
- `lineColor`，框线颜色  
- `textString`，Text 专属  


## 连接器的标准写法  
```modelica  
connector PositivePin
    Modelica.SIunits.Voltage v;
    flow Modelica.SIunits.Current i;  
    // input ...; 
    // output ...;
    // parameter ...;

annotation (...);
end PositivePin;
```  

光有连接器，还不足以应用到实际建模中，我们还需要将其与模型结合起来。  

## 电阻模型  
可以将连接器理解为电子元器件的引脚，或者其他系统组件的接口。以电阻模型为例：  
```modelica  
within ModelicaByExample.Components.Electrical.VerboseApproach;
model Resistor "A resistor model"  // 电阻模型
  parameter Modelica.SIunits.Resistance R;  // 有一个属性R  
  Modelica.Electrical.Analog.Interfaces.PositivePin p  // 正极引脚（连接器）
    annotation (Placement(transformation(extent={{-110,-10},{-90,10}})));
  Modelica.Electrical.Analog.Interfaces.NegativePin n  // 负极引脚（连接器）
    annotation (Placement(transformation(extent={{90,-10},{110,10}})));
protected
  Modelica.SIunits.Voltage v = p.v-n.v;  // 保护变量，引脚间的电压
equation
  p.i + n.i = 0 "Conservation of charge";  // KCL 基尔霍夫电流定律
  v = p.i*R "Ohm's law";  // 欧姆定律  
  // 本来四个变量需要四个方程的，现在已经有两个了，另外两个由系统的其他组件给出（通过接线的方式）
end Resistor;
```

## 参考资料  
1. [连接器-Modelica by Example](http://modelicabyexample.globalcrown.com.cn/components/connectors/)