---  
title: 初识Modelica    
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


> 笔记摘自：[Modelica by Example 的中文翻译](http://modelicabyexample.globalcrown.com.cn/)，因为`Modelica` 语言是一种规范，所以无论哪种实现在使用上是不应有区别的！  


## Modelica 是一种描述语言  
> 因为Prism 插件还未支持Modelica 语言，所以代码块暂时无法高亮显示 :(

Modelica 是一种用来描述模型、系统的语言，而描述是基于方程的、变量在等式左右两边的位置对模型没有影响：  
$$\dot{x} = 1-x$$
```modelica  
model FirstOrder  // 定义一个模块
    Real x;       // 模块中的属性
equation          // 描述模块属性的方程（组）
    der(x) = 1-x;  
end FirstOrder;   // 结束


///// 另一种定义方式 /////
model FirstOrder2  // 定义一个模块
    Real x = 1 - der(x);       // 同时定义变量和方程
equation          
    // 可以少写一条equation  
    // 不推荐这样做，因为这样会让你的模型变得不清晰  
    // 但是看到这样的用法要明白
end FirstOrder;   // 结束
```  
上面代码的含义就是：我们有一个模型`FirstOrder`，模型内有一个状态变量`x`、并且`x` 与它对时间的导数`x'`之和为`1`。我们关注的**重点并不是如何去求解微分方程，而是如何去建立这个微分方程**  
> 需要注意的是Modelica 语法要求严格，千万不要忘记结尾的分号！  

## 模型 model  
`Modelica` 的建模是基于物理模型的，也就是说，计算应基于`model`。而模型的定义，大致就是上面代码的样子。  

### 方程  
在Modelica 中，变量的数量要等于方程的数量（`initial equation` 不算），方程可以是带有条件的：  
```modelica  
if a>b then
  x = 5*time;
else
  x = 3*time;
end if;
```  
但是最终方程的有效数量应该是一致的。  

### 注释与说明  
还是以上面的代码为例：  
```modelica
// '//' 后面跟的是注释  
// '""' 内部填充的是说明，说明只能紧跟在模型、属性、方程等有意义的符号后面
model FirstOrderDocumented "A simple first order differential equation"
  Real x "State variable";
equation
  der(x) = 1-x "Drives value of x toward 1.0";
end FirstOrderDocumented;
```  

### 初始值  
因为求解微分方程一般会用到各个状态量的初始值，在Modelica 语言中可以在`initial equation` 部分去初始化某些变量：    
$$
\begin{array}{ll}    
    \dot{x} = 1-x;  \\  
    x(0) = 2
\end{array}
$$
```modelica  
model FirstOrderInitial "First order equation with initial value"
  Real x "State variable";
initial equation
  x = 2 "在计算之前初始化x";  
  // der(x) = 2 "同样地，也可以初始化x'" ;
equation
  der(x) = 1-x "Drives value of x toward 1.0";
end FirstOrderInitial;
```  

### 继承  
既然是面向对象的，那么模型自然可以继承其他模型。继承采用`extends` 关键字：  
```modelica  
model FirstOrder_Extends  
  extends FirstOrder;  /* 继承会继承所有的属性和方法 */
  
initial equation    // 设置初始值（如果原先没有的话）
  x = .5;
equation
  // der(x) = 2;    // 不能重写父类模型中的方程
end FirstOrder_Extends;
```  
继承的概念在Modelica 中不如在其它语言中那么灵活。 

### 标注  
当搭建模型时，建模人员可能希望为模型关联特定的试验条件。这可以通过应用`annotation（标注）`来完成。如仿真的开始时间、结束时间和容差范围等。以`experiment` 标注为例：  
```modelica  
model FirstOrder  // 定义一个模块
    Real x;        // 模块中的属性
equation          // 描述模块属性的方程（组）
    der(x) = 1-x;  
    annotation(
      experiment(StartTime=2,StopTime=8),
      Documentation(info="<html>
        <p>以html 写一些说明文档:</p>
        <pre>
          x' = 1-x;
        </pre>
        </html>"));  // 设置实验的起始时间和终止时间
end FirstOrder;    // 结束
```  

同时，在标注中还可以添加模型的样式、说明等信息，以`,` 分隔。  
> 虽然experiment标注在建立模型时被广泛的应用，但是也要注意到，一般情况下，建模工具是可以忽略任何或者全部标注内容的。Openmodelica 不会忽略！

需要注意的是，一般模型的说明文档和位置、图标等信息都是通过标注实现的。标注可以有自己的命名空间：  
```modelica  
annotation(XogenyIndustries(PartNumber="FF78-E4B879"),
           experiment(StartTime=0,StopTime=8));

// XogenyIndustries 就相当于命名空间
```

## 物理模型  
> 现实世界中，我们在使用数学计算时还会关心它的单位`unit`。  

有了变量的基础，我们就可以在建模时添加单位或者其他限制属性了。以牛顿冷却定律为例：  
$$m c_p \dot{T} = h A (T_{\infty} - T)$$  

```modelica  
model NewtonCoolingWithTypes "Cooling example with physical types"
  // 首先由Real 派生各种带有单位的数值类型
  type Temperature=Real(unit="K", min=0) "开尔文，最小为0";
  type ConvectionCoefficient=Real(unit="W/(m2.K)", min=0);
  type Area=Real(unit="m2", min=0);
  type Mass=Real(unit="kg", min=0);
  type SpecificHeat=Real(unit="J/(K.kg)", min=0);

  // 然后根据派生类型定义实际的变量
  parameter Temperature T_inf=298.15 "Ambient temperature";
  parameter Temperature T0=363.15 "Initial temperature";  // 变量初始值，写在这里的好处就是可以随时修改
  parameter ConvectionCoefficient h=0.7 "Convective cooling coefficient";
  parameter Area A=1.0 "Surface area";
  parameter Mass m=0.1 "Mass of thermal capacitance";
  parameter SpecificHeat c_p=1.2 "Specific heat";

  // 内部变量
  Temperature T "Temperature";
initial equation
  T = T0 "Specify initial value for T";  // 变量的初始化
equation
  // 牛顿冷却定律的公式描述  
  m*c_p*der(T) = h*A*(T_inf-T) "Newton's law of cooling";
end NewtonCoolingWithTypes;
```  
