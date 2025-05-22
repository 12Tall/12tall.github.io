---
title: 变量 variable  
date: 2022-08-25
tags:   
    - OpenModelica  
    - 建模
---

> 模式包含一系列的变量作为其特征。  
<!-- more -->
1. 无限定词：模型中的变量默认为连续变量（内部变量）  
2. `parameter` 限定词：表示该变量是先验已知的，可以该模型的输入数据、可以是不随时间变化的常数  
3. `protect` 限定词：保护变量，表示此变量是模型/类内部的一个局部变量  
4. `constant` 限定词：表示是常数、且不能随着模拟而改变，如$\pi$  
5. `discrete` 限定词：表示离散变量，暂无示例    
6. `flow` 限定词：流变量。在连接器中用到  
7. `cross` 限定词：势变量

## 变量类型  
首先`Modelica` 语言自带以下内建类型：  
- Real： 实数  
- Integer： 整数  
- Boolean： 布尔值  
- String： 字符串   

### 派生类型  
内置类型可以进行“特殊化”。这个特性主要是用于修改与属性相关的值，比如unit。用于创建派生类型的语法是：
```modelica  
type NewTypeName = BaseTypeName(/* attributes to be modified */);  

// 可以无限派生哦
type Temperature = Real(unit="K"); // Could be a temperature difference
type AbsoluteTemperature = Temperature(min=0); // Must be positive
```

### 枚举类型  
语法很像派生，但是使用上和C 语言的枚举类似、一般可以用整数替代：  
```modelica  
type AssertionLevel = enumeration(warning, error);  
type StateSelect = enumeration(never, avoid, default, prefer, always);
```

### 属性  
- `quantity`: `String`; `""` 描述变量含义  
- `start`: `Real`; `0.0` 主要用于提供`parameter` 的默认值（备用）    
- `fixed`: `Boolean`; `false` 在`parameter` 中为`true`，强制使用`start`     
- `min`: `Real`; `-inf` 最小值  
- `max`: `Real`; `inf` 最大值    
- `unit`: `String`; `""` 单位，`"1"` 表示没有物理单位  
- `displayUnit`: `String`; `""` 显示单位      
- `nominal`: `Real`; `0.0` 额定值      
- `stateSelect`: `StateSelect`; `default` 仿真时是否被选为状态量：never（从不）、avoid（避免）、default（默认）、prefer（偏向）、always（总是）   

### Record 类型  
`Record` 类型只包含变量，不包含方程。如：  
```modelica  
record FirstOrder_Record
Real x;
end FirstOrder_Record;  

// 或者  
record Vector "A vector in 3D space"
  Real x;
  Real y;
  Real z;
end Vector;
```

在使用上，`Record` 可以当作一个普通的数据类型作为模型的参数：  
```modelica  
parameter Vector v(x=1.0, y=2.0, z=0.0);
```

也可以在`Model` 中继承`Record`，就可以比较灵活地重写方程或初始值了：  
```modelica
model FirstOrder_Extends  
  extends FirstOrder_Record;  // 继承Record
  
initial equation              // 重写方程
  x = .4;
equation
  der(x) = 1-x;

end FirstOrder_Extends;
```