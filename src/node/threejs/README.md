---
title: ThreeJS     
date: 2023-09-11    
timeLine: true
sidebar: false  
icon: nodeJS  
category:  
    - 开发  
    - Javascript   
tag:  
    - ThreeJS    
    - 3D  
    - Simulation      
---   

> 上周看到一个`Unity` 的项目，可以在Web 页面中开挖掘机。感觉挺好玩的，于是想着是否可以通过`ThreeJS` 实现一个乞丐版的demo。还有一个比较难的点在物理引擎上面吧，具体问题还描述不清楚。  


## 改变对象的旋转轴   
**ThreeJS 中物体的旋转轴默认都是以几何中心**。但是可以[通过平移几何体或嵌套父对象来改变旋转轴的位置](http://www.yanhuangxueyuan.com/doc/Three.js/translateAxis.html)。  
```js
// *** 平移集合体 *** //
var box=new THREE.BoxGeometry(56,56,56);
box.translate ( 28, 0, 0 );  // 平移几何体，改变旋转轴

var mesh=new THREE.Mesh(box,material);
mesh.position.set(65,23,0)  // 平移网格模型，不影响mesh自身的旋转轴


// *** 嵌套父对象 *** //
var mesh=new THREE.Mesh(box,material);  // 加载外部网格

var group = new THREE.Group()  // group作为mesh的父对象
group.add(mesh)
mesh.position.x= -25  // mesh相对父对象沿着x方向平移-25
scene.add(group);
// 这样旋转group 就好了  
```  

## 嵌套Group  
在`ThreeJS` 中，**模型可以作为另一个模型的子部分，这样在平移和旋转时便可以同时运动**，叫做[层级模型](http://www.webgl3d.cn/pages/c86096/)。这个在机械仿真时应该还是蛮重要的，因为很多部件都是联动的。而通过`Group` 这一概念来实现则是最直接的思路。  
```js
//创建两个网格模型mesh1、mesh2
const geometry = new THREE.BoxGeometry(20, 20, 20);
const material = new THREE.MeshLambertMaterial({color: 0x00ffff});
const group = new THREE.Group();
const mesh1 = new THREE.Mesh(geometry, material);
const mesh2 = new THREE.Mesh(geometry, material);

mesh2.translateX(25);  //把mesh1型插入到组group中，mesh1作为group的子对象
group.add(mesh1);  //把mesh2型插入到组group中，mesh2作为group的子对象
group.add(mesh2);  //把group插入到场景中作为场景子对象
scene.add(group);
```  

## DEMO   

下面是一个丐中丐版的demo，仅实现两个杆的联动，并且动画也是循环的。  

```js
// 预先创建了一个canvas 400x600 <template>
// <div ref="root" height="400" width="600"></div>

import { onMounted, ref } from "vue"
import * as THREE from 'three';
const root = ref(null)

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, 600 / 400, 0.1, 1000);

const renderer = new THREE.WebGLRenderer();
renderer.setSize(600, 400);


onMounted(() => {
// 模型渲染到canvas 里面 
    root.value.appendChild(renderer.domElement);
    camera.position.set(0, 0, 50)
    camera.lookAt(0, 0, 0);

    // 创建wing
    const geoWing = new THREE.BoxGeometry(10, 1, 1);
    geoWing.translate(5, 0, 0)
    const matWing = new THREE.MeshBasicMaterial({ color: 0x00ffff });
    const wing = new THREE.Mesh(geoWing, matWing);

    // 创建arm  
    const geoArm = new THREE.BoxGeometry(1, 6, 1);
    geoArm.translate(0, 3, 0)   // 平移形状，此操作会修改物体的旋转轴
    const matArm = new THREE.MeshBasicMaterial({ color: 0xffff00 });
    const arm = new THREE.Mesh(geoArm, matArm);
    arm.position.set(10, 0, 0)  // 平移网格，不会改变物体的旋转轴

    wing.add(arm)  // 将arm 添加为wing 的子部件，就会同步旋转了
    scene.add(wing);
    // scene.add(arm);

    // 立方体旋转动画效果
    function render() {
        renderer.render(scene, camera);
        //每次绕z 轴旋转0.01弧度
        // 不平移几何体，绕立方体的几何中心旋转
        // 平移距离是变长的一半，绕立方体侧边线旋转
        wing.rotateZ(0.01);
        arm.rotateZ(0.02)
        requestAnimationFrame(render);
    }

    render();
})
```

<ClientOnly>
    <threedemo></threedemo>  
</ClientOnly>


## 参考资料  
1. [WebGL教程_Three.js教程_郭隆邦技术博客](http://www.yanhuangxueyuan.com/)。这是一个不错的技术博客，其中工具资源部分也挺好。 
2. [Web3D系统课程视频_Three.js中文网](http://www.webgl3d.cn/pages/aac9ab/)   
3. [国外破碎锤demo](https://www.trigonal.fr/brise-roche/ )  
4. [国内挖掘机demo](https://www.hightopo.com/demo/ht-excavator/)