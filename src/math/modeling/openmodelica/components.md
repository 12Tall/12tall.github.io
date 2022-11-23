---  
title: 组件 components 
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


> `Model` + `Coneector` = `Component`。模型加上引脚就可以构成组件。  

通过封装，可以将模型从一堆公式编程一个简单的带接口的图形组件。使用组件开发可以提高效率、减少错误和维护成本。  

## 传热组件  
一般连接器的使用都是成对出现的，一个流出端口对应着一个流入端口，为了区别流入流出端口，我们可以给它们设置不同的图标（尽管内部的变量都是一样的）。  
```modelica{3-8}
within Modelica.Thermal.HeatTransfer;
package Interfaces "Connectors and partial models"
  // 部分定义的类，只能被继承，不能直接使用
  partial connector HeatPort "Thermal port for 1-dim. heat transfer"
    Modelica.SIunits.Temperature T "Port temperature";
    flow Modelica.SIunits.HeatFlowRate Q_flow
      "Heat flow rate (positive if flowing from outside into the component)";
  end HeatPort;

  // 端口A，填充红色
  connector HeatPort_a "Thermal port for 1-dim. heat transfer (filled rectangular icon)"
    extends HeatPort;

    annotation(Icon(coordinateSystem(preserveAspectRatio=true,
                            extent={{-100,-100},{100,100}}),
                            graphics={Rectangle(
                              extent={{-100,100},{100,-100}},
                              lineColor={191,0,0},
                              fillColor={191,0,0},
                              fillPattern=FillPattern.Solid)}));
  end HeatPort_a;

  // 端口B，无填充
  connector HeatPort_b "Thermal port for 1-dim. heat transfer (unfilled rectangular icon)"
    extends HeatPort;

    annotation(Icon(coordinateSystem(preserveAspectRatio=true,
                            extent={{-100,-100},{100,100}}),
                            graphics={Rectangle(
                              extent={{-100,100},{100,-100}},
                              lineColor={191,0,0},
                              fillColor={255,255,255},
                              fillPattern=FillPattern.Solid)}));
  end HeatPort_b;
end Interfaces;
```  

### 热容模型  

现实生活中，每个物体都可以看作为一个热的容器。对于集总（频率无关、不随位置分布变化、可以理想化地抽象为一个点）热容模型，理想的公式是：  
$$C \dot{T} = Q_{flow}$$  
即，物体温度的变化率正比于热量流入/流出的速率。于是我们可以建立模型：  
```modelica
within ModelicaByExample.Components.HeatTransfer;
model ThermalCapacitance "A model of thermal capacitance"
  parameter Modelica.SIunits.HeatCapacity C "Thermal capacitance";  // 热容
  parameter Modelica.SIunits.Temperature T0 "Initial temperature";  // 初始温度  
  Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_a node          // 添加一个端口
    annotation (Placement(transformation(extent={{-10,-10},{10,10}})));
initial equation
  node.T = T0;  // 初始化端口温度
equation
  C*der(node.T) = node.Q_flow;  // 模型方程  
  // 其实这里如果再加上一个内部变量（物体温度T）就更好理解了  
  // T = node.T // 物体温度等于端口温度  
end ThermalCapacitance;
```  

### 环境导热模型  
首先我们需要看一个公式，傅里叶导热公式：  
$$Q = \lambda A (T_h -T_c ) / \delta$$  
其中：  
$A$ 是垂直热量传递方向的面积  
$T_h, T_c$ 分别为高温和低温面的温度  
$\delta$ 为两个面之间的距离  
$\lambda$ 为材料的导热系数，单位是$W/(m\degree C)$  

于是我们可以构建简单的模型：  
```modelica  
within ModelicaByExample.Components.HeatTransfer;
model ConvectionToAmbient "An overly specialized model of convection"
  parameter Modelica.SIunits.CoefficientOfHeatTransfer h;  // λ/δ
  parameter Modelica.SIunits.Area A;  // 截面积
  parameter Modelica.SIunits.Temperature T_amb "Ambient temperature";  // 环境温度，为常量
  Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_a port_a
    annotation (Placement(transformation(extent={{-110,-10},{-90,10}})));
equation
  port_a.Q_flow = h*A*(port_a.T-T_amb) "Heat transfer equation";
end ConvectionToAmbient;
```  

然后再新建一个冷却系统的模型，通过`connect` 函数将上面两个组件连接起来：  
```modelica{11-14}  
within ModelicaByExample.Components.HeatTransfer.Examples;
model CoolingToAmbient "A model using convection to an ambient condition"

  ThermalCapacitance cap(C=0.12, T0(displayUnit="K") = 363.15)
    "Thermal capacitance component"
    annotation (Placement(transformation(extent={{-30,-10},{-10,10}})));
  ConvectionToAmbient conv(h=0.7, A=1.0, T_amb=298.15)
    "Convection to an ambient temprature"
    annotation (Placement(transformation(extent={{20,-10},{40,10}})));
equation
  connect(cap.node, conv.port_a) annotation (Line(
      points={{-20,0},{20,0}},
      color={191,0,0},
      smooth=Smooth.None));
end CoolingToAmbient;
```  

`connect` 函数会建立两个方程：  
- `cap.node.T = conv.port_a.T "Equating across variables";`  
- `cap.node.Q_flow + conv.port_a.Q_flow = 0 "Sum of heat flows must be zero";`  
注意流入量与流出量的符号约定。  

> 连接器面向的对象不是本模型，而是其他模型，至少是本模型的其他部分。  

## 电气部件  
在连接器部分简单设计了一点，因为电气部件很多都是二端口网络，于是我们可以使用一个`partitial` 的模型来表示一个抽象的二端口网络：  
```modelica  
within ModelicaByExample.Components.Electrical.DryApproach;
partial model TwoPin "Common elements of two pin electrical components"
  Modelica.Electrical.Analog.Interfaces.PositivePin p
    annotation (Placement(transformation(extent={{-110,-10},{-90,10}})));
  Modelica.Electrical.Analog.Interfaces.NegativePin n
    annotation (Placement(transformation(extent={{90,-10},{110,10}})));
protected
  Modelica.SIunits.Voltage v = p.v-n.v;  // 端口电压
  Modelica.SIunits.Current i = p.i;      // 流经电流
equation
  p.i + n.i = 0 "Conservation of charge";// KCL 
end TwoPin;
```  

### 电阻模型  
通过继承二端口网络，我们可以很方便的创建电阻的模型：  
```modelica  
within ModelicaByExample.Components.Electrical.DryApproach;
model Resistor "A DRY resistor model"
  parameter Modelica.SIunits.Resistance R;
  extends TwoPin;
equation
  v = i*R "Ohm's law";
  // 需要自定义ICON
end Resistor;
```  

关于方程数量的问题：  
- 每个引脚`Pin` 有两个变量  
- 二端口网络还有两个保护变量  
一共有6 个变量    
- 二端口网络有3 个方程（包含保护变量的定义）  
- 每个connector 的流变量隐含了一个方程
共计有5 个方程    

### 机械模型  
对于有转动惯量的模型，两侧的扭矩差会让物体加速或减速转动，以存储或释放能量。但是对于理想弹簧、阻尼等器件，则不会以转动的形式存储角动量（如果两边的扭矩不一样，弹簧会被拉长或者压缩）：  
```modelica  
// No storage of angular momentum
flange_a.tau + flange_b.tau = 0;
```  
于是可以发现，Modelica 语言对使用者最残酷的要求就是：使用者必须真正理解要建模的事物！  


### 连接集  
如果两条连接语句内有一个共同的连接器，它们就属于相同的连接集。如果一个连接器未连接到任何其他连接器，那么它就属于一个仅包含其本身的连接集。对于同一连接集中有n 个连接器，则会自动核算：  
- 所有横跨变量的值都应该相同（n-1个方程）  
- 所有穿越变量的值总和为0（1个方程）