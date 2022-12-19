import math


class State():
    def __init__(self, name="state", func=lambda: 0, init_value=0, get_h=lambda: 0.01, get_index=lambda: 1) -> None:
        self.name = name
        self.init_value = init_value   # 变量初始值
        self.curr_value = init_value   # 暂存计算结果
        self.k = [.0, .0, .0, .0, .0]  # k0 = (k1+2*k2+2*k3+k4)/6
        self.get_index = get_index             # 当前需要计算k?: 1,2,3,4
        self.get_h = get_h                 # 迭代步长，不要手动修改
        self.func = func           # 方程右边的算法，是一个lambda 函数，参数是一个模块

    # 根据k_n 计算状态值，并将该状态值作为求解k_{n+1} 的参数返回给lambda 函数
    def val(self):
        temp_value = 0             # 该方法容易扩展到更高阶
        if self.get_index() == 1:
            temp_value = self.curr_value
        elif self.get_index() == 2:
            temp_value = self.curr_value + 0.5*self.get_h()*self.k[1]
        elif self.get_index() == 3:
            temp_value = self.curr_value + 0.5*self.get_h()*self.k[2]
        elif self.get_index() == 4:
            temp_value = self.curr_value + self.get_h()*self.k[3]
        return temp_value

    def calc(self):                # 计算最终斜率存储到k0，并利用k0 算出最终结果
        self.k[0] = (self.k[1]+2*self.k[2]+2*self.k[3]+self.k[4])/6
        self.curr_value = self.curr_value + self.get_h()*self.k[0]

    def reset(self):               # 重置状态，在重启计算时需要
        self.curr_value = self.init_value


# Module 对象可以扩展，进行递归运算
class Module():
    def __init__(self, name="module", get_h=lambda: 0.01, get_index=lambda: 0) -> None:
        self.get_h = get_h  # 模块的步长最终（必须）会更新到到所有状态变量中
        self.get_index = get_index
        self.name = name

    def create_sub_module(self, name="module"):
        module_name = self.name+"/"+name
        module = Module(module_name, get_h=self.get_h,
                        get_index=self.get_index)
        setattr(self, module_name, module)
        return module

    def create_state(self,  name="state", func=lambda: 0, init_value=0):     # 创建状态变量
        state_name = self.name+"/"+name
        state = State(name=state_name, func=func, init_value=init_value,
                      get_h=self.get_h, get_index=self.get_index)
        setattr(self, state_name, state)
        return state

    def reset(self):  # 重置计算过程，依次重置所有状态变量
        for prop_name in dir(self):
            prop = getattr(self, prop_name)
            if (isinstance(prop, State) or isinstance(prop, Module)):
                prop.reset()

    def calc_k1_to_k4(self):
        for prop_name in dir(self):
            # 遍历所有属性，筛选State 类型用于计算，似乎是按属性名排序的
            prop = getattr(self, prop_name)
            if (isinstance(prop, State)):
                prop.k[self.get_index()] = prop.func()  # 将计算结果暂存到对应的状态变量中

            if (isinstance(prop, Module)):
                prop.calc_k1_to_k4()  # 将计算结果暂存到对应的状态变量中

    def calc_k0(self):
        # 根据上面计算的k1~k4 数据，计算这一步的k0 和结果，并以数组的形式返回
        for prop_name in dir(self):
            # 遍历所有属性，筛选State 类型用于计算，似乎是按属性名排序的
            prop: State = getattr(self, prop_name)
            if (isinstance(prop, State)):
                prop.calc()
            if (isinstance(prop, Module)):
                prop.calc_k0()  # 将计算结果暂存到对应的状态变量中


# 1. 将步长信息统一存放到System 下
# 2. 龙哥-库塔的迭代过程也由System 完成
# 3. System 包含多个子模块，且至少包含一个时间（time）模块
#    3.1 模块间可以不存在任何关系
#    3.2 但是模块间的所有关系需要用户手动设置
#    3.3 模块并没有对输入输出状态要求特殊的命名规范
# 4. 不再自动记录仿真数据，需要用户手动设置存储方法
class System():
    def __init__(self, h=0.01) -> None:
        self.h = h
        self.index = 1
        self.create_timer()
        pass

    def get_h(self):
        return self.h

    def create_module(self, name="module"):
        module_name = "/"+name
        module = Module(module_name, get_h=lambda: self.h,
                        get_index=lambda: self.index)
        setattr(self, module_name, module)
        return module

    def create_timer(self):  # system 的timer 是一个状态的引用，如果是一个模块的引用的话，将会导致该timer 被计算两次
        timer = self.create_module("timer")
        self.timer = timer.create_state(
            "time", lambda: 1, init_value=0)

    def calc_k1_to_k4(self):
        for index in range(1, 5):  # 计算每个属性的 k1,k2,k3,k4
            self.index = index
            for module_name in dir(self):
                # 遍历所有属性，筛选State 类型用于计算，似乎是按属性名排序的
                module: Module = getattr(self, module_name)
                if (isinstance(module, Module)):
                    module.index = index  # 更新状态变量的阶数，使得prop.val() 函数能返回正确的值
                    module.calc_k1_to_k4()

    def calc_k0(self):
        # 根据上面计算的k1~k4 数据，计算这一步的k0 和结果，并以数组的形式返回
        for module_name in dir(self):
            # 遍历所有属性，筛选State 类型用于计算，似乎是按属性名排序的
            module: Module = getattr(self, module_name)
            if (isinstance(module, Module)):
                module.calc_k0()

    def reset(self):
        for module_name in dir(self):
            module: Module = getattr(self, module_name)
            if (isinstance(module, Module)):
                module.reset()

    def calc(self):
        self.calc_k1_to_k4()
        self.calc_k0()

    def simulate(self):
        pass
    pass


##### Test #####
# u = 5v
# r = 1 Ω
# c = 1 H
# 三种元件串联，得：
# 1. du_vol = 0, u_vol_0 = 5
# 2. dc_vol = i/c  = r_vol/r/c,  c_vol_0 = 0  # 流入为正
# 3. dr_vol = -i/c = -r_vol/r/c, r_vol = -5

sys = System(0.01)
U = 5
R = 1
C = 1


u = sys.create_module("u")  # 电源模型
u_h = u.create_state("u_h", func=lambda: U*math.cos(sys.timer.val()), init_value=0)
u_l = u.create_state("u_l", func=lambda: 0, init_value=0)

r = sys.create_module("r")  # 电阻模型
r_i = r.create_state("r_i", func=lambda: (
    u_h.func()-r_l.func())/R, init_value=0)  # lambda 函数中可以通过.fun()调用其他状态的微分 # 初始值在某种程度上决定了电路的运行状态

c = sys.create_module("c")  # 电容模型
c_h = c.create_state("c_h", func=lambda: u_l.func() +
                     r_i.val()/C)

# 连接点处电压相同
r_h = u_h
c_l = u_l
r_l = c_h
# 环路电流处处相等
u_i = c_i = r_i

for i in range(3200):
    sys.calc()
    print(i*0.01,c_h.curr_value, c_i.curr_value)
