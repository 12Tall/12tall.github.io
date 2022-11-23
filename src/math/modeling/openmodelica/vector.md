---
title: 向量与数组 vector  
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

> 简单的用法：可以把向量或数组当成一次声明许多个变量，并且向量和矩阵的运算在`Modelica` 语言中也已经封装的非常完善了。  

## 状态空间  
状态空间的一般形式：  
$$
\begin{array}{l}
  \dot{\vec{x}}(t) = A(t)\vec{x}(t) + B(t)\vec{u}(t) \\ 
  \vec{y}(t) = C(t)\vec{x}(t) + D(t)\vec{u}(t)
\end{array}
$$  

在线性时不变（LTI，linear-time-invariant）系统中，ABCD 为常数矩阵：  
$$
\begin{array}{l}
  \dot{\vec{x}}(t) = A\vec{x}(t) + B\vec{u}(t) \\ 
  \vec{y}(t) = C\vec{x}(t) + D\vec{u}(t)
\end{array}
$$   

于是我们可以对LTI 系统进行定义：  
```modelica
model LTI
  "Equations written in ABCD form where matrices are also time-invariant"
  parameter Integer nx=0 "Number of states"; // 状态数量
  parameter Integer nu=0 "Number of inputs"; // 输入维度
  parameter Integer ny=0 "Number of outputs";// 输出维度

  parameter Real A[nx,nx]=fill(0,nx,nx);  // 参数矩阵
  parameter Real B[nx,nu]=fill(0,nx,nu);  // 默认值都为0
  parameter Real C[ny,nx]=fill(0,ny,nx);
  parameter Real D[ny,nu]=fill(0,ny,nu);

  parameter Real x0[nx]=fill(0,nx) "Initial conditions";  // 初始状态  

  Real x[nx] "State vector";  // 内部变量
  Real u[nu] "Input vector";
  Real y[ny] "Output vector";
initial equation
  x = x0 "Specify initial conditions";  // 初始化
equation
  der(x) = A*x+B*u;  // 空间状态方程
  y = C*x+D*u;       // 矩阵可以直接加减乘除，唯一的要求就是维度要一致
end LTI;
```  
#### 简单一阶系统
通过继承`LTI` 模型，就可以创建简单的一阶系统：  
$$\dot{x} = 1- x$$
```modelica{2,12}
model FirstOrder "Represent der(x) = 1-x"
  extends LTI(nx=1,nu=1,A=[-1], B=[1]);  // 初始化
  /** 矩阵的初始化：
  * A= [
  *  0,d,1,0; 
  *  c,0,0,1; 
  *  0,1,0,a; 
  *  1,0,b,0; 
  * ]
  * */
equation
  u = {1};  // 输入u 总是1，因为其是内部变量，所以在每次计算中都要计算
  // u =  {1, 2, 3*4, 5*sin(time)}; 表示一个向量
end FirstOrder;
```  
其实LTI 模型也可以用来计算非线性或者时变的系统，只是碍于命名的意义，不宜引起混乱。  

### 子部件  
虽然可以通过继承重用部分代码，但是通过将LTI 作为子组件创建模型会更加简洁清晰：  
```modelica{6-10,12}
model RLC "State space version of an RLC circuit"
  parameter Real Vb=24;
  parameter Real L=1;
  parameter Real R=100;
  parameter Real C=1e-3;
  LTI rlc_comp(nx=2, nu=1, ny=2, x0={0,0},  // 使用LTI 子组件
               A=[-1/(R*C), 1/C; -1/L, 0],  // 矩阵（parameter）初始化
               B=[0; 1/L],
               C=[1/R, 0; -1/R, 1],
               D=[0; 0]);
equation
  rlc_comp.u = {Vb};  // 计算子组件输入
end RLC;
```

### 循环  
> 常用的是for 循环，还有while 循环，但不常用
```modelica
equation
  for i in 1:n loop
    for j in 1:n loop
      // equation
    end for;
  end for;
```  

## 函数
首先看函数的定义：  
```modelica  
function Line "Compute coordinates along a line"
  // 输入参数 
  input Real x     "Independent variable";   
  input Real p0[2] "Coordinates for one point on the line";
  input Real p1[2] "Coordinates for another point on the line";  

  // 输出参数
  output Real y    "Value of y at the specified x";
protected

  // 中间变量
  Real m = (p1[2]-p0[2])/(p1[1]-p0[1])        "Slope";
  Real b = (p1[2]+p0[2]-m*(p1[1]+p0[1]))/2.0  "Offset";
algorithm

  // 实现算法，注意赋值的符号是`:=`
  y := m*x+b;
end Line;
```  

### 计算多项式的值  
以4 阶多项式为例：  
$$p(x,\vec{c}) = ((c_1x+c_2)x+c_3)x+c_4$$  
函数定义：  
```modelica   
function Polynomial "Create a generic polynomial from coefficients"
  input Real x     "Independent variable";  // 自变量
  input Real c[:]  "Polynomial coefficients";// 系数向量
  output Real y    "Computed polynomial value";// 返回值
protected
  Integer n = size(c,1);  // 中间变量：循环的次数，即系数的个数
algorithm
  y := c[1];
  for i in 2:n loop
    y := y*x + c[i];
  end for;
end Polynomial;
```  

需要注意的是，我们这样定义的函数并不能被直接求导，需要手动在`annotation(derivative=xxx)` 指定导数函数（需要提前定义）。  