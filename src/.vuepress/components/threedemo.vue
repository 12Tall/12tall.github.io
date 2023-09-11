<template>
    <div ref="root" height="400" width="600"></div>
</template>

<script setup>
import { onMounted, ref } from "vue"
import * as THREE from 'three';
const root = ref(null)

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, 600 / 400, 0.1, 1000);

const renderer = new THREE.WebGLRenderer();
renderer.setSize(600, 400);

onMounted(() => {
    if (typeof window !== 'undefined') {
        // 这里是浏览器端代码
        root.value.appendChild(renderer.domElement);
    }
    camera.position.set(0, 0, 30)
    camera.lookAt(0, 0, 0);

    const geoWing = new THREE.BoxGeometry(10, 1, 1);
    geoWing.translate(5, 0, 0)
    const matWing = new THREE.MeshBasicMaterial({ color: 0x00ffff });
    const wing = new THREE.Mesh(geoWing, matWing);

    const geoArm = new THREE.BoxGeometry(1, 6, 1);
    geoArm.translate(0, 3, 0)
    const matArm = new THREE.MeshBasicMaterial({ color: 0xffff00 });
    const arm = new THREE.Mesh(geoArm, matArm);
    arm.position.set(10, 0, 0)

    wing.add(arm)


    scene.add(wing);
    // scene.add(arm);

    // 立方体旋转动画效果
    function render() {
        renderer.render(scene, camera);
        //每次绕y轴旋转0.01弧度
        // 不平移几何体，绕立方体的几何中心旋转
        // 平移距离是变长的一半，绕立方体侧边线旋转
        wing.rotateZ(0.01);
        arm.rotateZ(0.02)
        requestAnimationFrame(render);
    }

    render();
})
</script>

<style></style>