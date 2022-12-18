class State():
    def __init__(self, func=lambda module: 0, init_value=0, h=0.001) -> None:
        self.init_value = init_value   # 变量初始值
        self.curr_value = init_value   # 暂存计算结果  
        self.k = [.0, .0, .0, .0, .0]  # k0 = (k1+2*k2+2*k3+k4)/6
        self.index = 1             # 当前需要计算k?: 1,2,3,4
        self.h = h                 # 迭代步长，不要手动修改
        self.func = func           # 方程右边的算法，是一个lambda 函数，参数是一个模块

    def val(self):                 # 根据k_n 计算状态值，并将该状态值作为求解k_{n+1} 的参数返回给lambda 函数  
        temp_value = 0             # 该方法容易扩展到更高阶
        if self.index == 1:
            temp_value = self.curr_value
        elif self.index == 2:
            temp_value = self.curr_value + 0.5*self.h*self.k[1]
        elif self.index == 3:
            temp_value = self.curr_value + 0.5*self.h*self.k[2]
        elif self.index == 4:
            temp_value = self.curr_value + self.h*self.k[3]
        return temp_value

    def calc(self):                # 计算最终斜率存储到k0，并利用k0 算出最终结果
        self.k[0] = (self.k[1]+2*self.k[2]+2*self.k[3]+self.k[4])/6
        self.curr_value = self.curr_value + self.h*self.k[0]

    def reset(self):               # 重置状态，在重启计算时需要  
        self.curr_value = self.init_value

class Module():
    def __init__(self, h=0.01) -> None:
        self.h = h  # 模块的步长最终（必须）会更新到到所有状态变量中
        self.res = []
        self.time = self.create_state(lambda m: 1)  # 创建一个默认状态变量time  

    def create_state(self, func, init_value=0):     # 创建状态变量  
        return State(func=func, init_value=init_value, h=self.h)

    def reset(self):  # 重置计算过程，依次重置所有状态变量
        for prop_name in dir(self):
            prop = getattr(self, prop_name)
            if (isinstance(prop, State)):
                assert type(prop) == State
                prop.reset()

    def calc(self):
        res = []
        for index in range(1, 5):  # 计算每个属性的 k1,k2,k3,k4
            for prop_name in dir(self):
                prop = getattr(self, prop_name)  # 遍历所有属性，筛选State 类型用于计算，似乎是按属性名排序的
                if (isinstance(prop, State)):
                    assert type(prop) == State
                    prop.index = index  # 更新状态变量的阶数，使得prop.val() 函数能返回正确的值
                    prop.k[index] = prop.func(self)  # 将计算结果暂存到对应的状态变量中

        # 根据上面计算的k1~k4 数据，计算这一步的k0 和结果，并以数组的形式返回
        for prop_name in dir(self):
            prop = getattr(self, prop_name)
            if (isinstance(prop, State)):
                assert type(prop) == State
                res.append(prop.curr_value)
                prop.calc()
        return res
    
    def get_states(self):
        res = []
        for prop_name in dir(self):
            prop = getattr(self, prop_name)
            if (isinstance(prop, State)):
                res.append(prop_name)
        return res

    def set_step(self, h=0.01):  # 重新设置步长，越小越精确
        self.h = h
        for prop_name in dir(self):
            prop = getattr(self, prop_name)
            if (isinstance(prop, State)):
                assert type(prop) == State
                prop.h = self.h

    def simulate(self, stop_at = 1):
        print("----- simulation started -----")
        self.reset()       
        self.res.append(self.get_states())

        i = 0
        while i <= stop_at+self.h:  # 保证计算覆盖范围
            self.res.append(m.calc())
            i += self.h


##### Test #####
import math
m = Module()
m.s3 = m.create_state(lambda m: math.sin(m.time.val()), init_value=-1.0)
m.s4 = m.create_state(lambda m: -math.sin(m.time.val()), init_value=1.0)

m.set_step(0.001)
m.simulate(stop_at=1)
print(m.res)