
from matplotlib import pyplot as plt
import numpy as np


# 定义函数  
def func(row):
    x,y = row
    # return x**2 + y -7*np.cos(np.pi*x) - 8*np.cos(2*np.pi*y)
    return (x-2)**2 + y**2

def fitness(arr):  
    return np.apply_along_axis(func, axis=1, arr=arr)

# 位置矩阵  
x = np.random.uniform(-5,5, (100,2))
# 速度矩阵  
v = np.random.uniform(-5,5, (100,2))
# 适应度矩阵  
f = fitness(x)  
# 最合适的坐标索引
index = np.argmin(f)
fmin = f[index]
# 粒子最优解
pb = x.copy()
# 全局最优解  
gb = [x[index][0],x[index][1]]



c1 = 0.4  
c2 = 1  
theta = 1  
omega = 0.1  

for j in range(50):
    # 限制速度和粒子的活动范围
    vNew = np.clip(omega*v + c1*np.random.uniform(-1,1)*(pb-x)+c2*np.random.uniform(-1,1)*(gb-x),-1,1  )
    xNew = np.clip(x+theta*vNew, -5,5)
    fNew = fitness(xNew)  
    indexNew = np.argmin(fNew)
    fminNew = fNew[indexNew]  

    if fminNew < fmin:  # 更新全局最优解  
        fmin = fminNew
        gb = [xNew[indexNew][0],xNew[indexNew][1]]
    

    for i in range(100):  # 更新粒子的历史最优解
        if f[i] > fNew[i]:
            f[i] = fNew[i]  
            pb[i] = xNew[i]
            
    x = xNew  
    v = vNew

    print(f"=== 已迭代{j}次 ===")

    if j % 1 == 0 :
        plt.clf()
        plt.scatter(x[:,0], x[:,1], s=10)

        # 设置坐标轴范围
        plt.xlim(-5, 5)
        plt.ylim(-5, 5)

        # 显示图像
        plt.savefig(f"res{j:02d}.png")


import imageio  
# 读取所有PNG图片并添加到列表中
images = []
for i in range(50):
    filename = 'res{:02d}.png'.format(i)
    images.append(imageio.imread(filename))

# 将所有PNG图片转换为GIF动画
imageio.mimsave('animation.gif', images, duration=1, loop=0)