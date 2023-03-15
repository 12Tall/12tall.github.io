---
title: Element-Plus 可编辑单元格的实现   
date: 2023-03-15    
timeLine: true
sidebar: false  
icon: nodeJS  
category:  
    - 开发  
    - Javascript  
tag:  
    - Vue      
    - Element-Plus  
---   

在前端开发时，会经常用到`table` 元素来展示内容。虽然为每条记录都设置一个编辑的页面，会使项目结构更清晰，但是在一些要求不那么严格的场合，如果能直接编辑表格内容，则无论是对用户、还是对开发来讲，都是更友好的选择。  

在寻找方案时，遇到了[EditableCell.vue](https://codesandbox.io/s/mrqqz43yx?file=/src/components/EditableCell.vue) 这个组件，觉得实现挺好的。因为这个组件是`vue2` 实现的，这里用`vue3` 语法复现一下，也可以用来学习`Vue` 中的一些特性。  

> 需要在`.vuepree/client.ts` 中启用第三方组件的支持。这样可以直接在Markdown 文件中预览组件的效果。    

## ElTable 的用法  

`<el-table></el-table>` 组件属于`Element-Plus` 的自带组件，主要用于展示列表内容。其核心属性`:data=[{},{}]` 即为要展示的内容。表格包含若干个`<el-table-column></el-table-column>` 子元素，对应数组中内元素的不同属性。 **我们也可以通过插槽想表格中添加按钮等其他任何合法的元素。** 以下面代码为例：  

```vue  
<template>
    <el-table style="margin:0" :data="data" height="250" border stripe >
        <el-table-column prop="name" label="Name"></el-table-column>  
        <el-table-column prop="date" label="Date"></el-table-column>  
        <el-table-column prop="gender" label="Gender"></el-table-column>  
        <el-table-column label="Operation">        
            <template #default="scope">
                <el-button type="primary">Edit {{scope.row.name}}</el-button>
            </template>
        </el-table-column>  
    </el-table>
</template>


<script setup lang="ts">

const data=[
    {name:'Tom', date:'2023-03-15', gender:'male'},
    {name:'Jerry', date:'2023-03-15', gender:'male'},
    {name:'Tara', date:'2023-03-15', gender:'female'},
    {name:'Tuffy', date:'2023-03-15', gender:'female'},
]

</script>  

<style>
    table{
        margin:0 !important; /* 可能是Element 的样式与主题默认样式冲突，所以需要手动修复 */
    }
</style>

```

<el-table style="margin:0" :data="data" height="250" border stripe >
    <el-table-column prop="name" label="Name"></el-table-column>  
    <el-table-column prop="date" label="Date"></el-table-column>  
    <el-table-column prop="gender" label="Gender"></el-table-column>  
    <el-table-column label="Operation">
        <template #default="scope">
            <el-button type="primary">Edit {{scope.row.name}}</el-button>
        </template>
    </el-table-column>  
</el-table>


<style>
    table{
        margin:0 !important; /* 可能是Element 的样式与主题默认样式冲突，所以需要手动修复 */
    }
</style>  

### 默认插槽  
上面的代码中，通过`<template #default="scope"></template>` 将模板中的内容添加到表格中，所利用的就是插槽。  

插槽是在新建元素时，提供一个占位符，以便后期向元素中添加更多元素，模板与插槽的功能也是HTML 默认所支持的[模板与插槽](https://developer.mozilla.org/zh-CN/docs/Web/Web_Components/Using_templates_and_slots)，但是使用上并没有`vue` 的插槽简单、强大：  

```vue  
<!-- 定义MyDiv 组件 -->
<template>
    <div>
        <slot>缺省内容</slot>
    </div>
</template>  

<!-- 使用MyDiv 组件 -->
<MyDiv></MyDiv>
<MyDiv>替换缺省内容</MyDiv>
```

### 具名插槽  
顾名思义，这类插槽在定义时需要指定`name` 属性，在使用时也会按`name` 属性替换响应的内容，`el-table-clomun` 中的插槽就是这一类，只不过它的名字属于缺省名字`default`（`#slot-name` 相当于`v-slot:slot-name` 的缩写）。具名插槽可以实现一个组件中存在多个插槽：  

```vue  
<!-- 定义MyDiv 组件 -->
<template>
    <div>
        <slot name="header">缺省头部</slot><br/>
        <slot name="body">缺省内容</slot>
    </div>
</template>  


<!-- 使用MyDiv 组件 -->
<MyDiv>
    <span #header>header</span>
    <div v-slot:body>body</div>
</MyDiv>
```


### 作用域插槽  
因为插槽中的内容无法访问到子组件的状态，但是有时我们需要用到父、子组件域内的数据，就像我们需要在`<el-table></el-table>` 中使用数据一样，这时我们就需要在插槽的出口上传递一些`attributes`:  
```vue  
<!-- <MyComponent> 的模板 -->
<script setup>
import {ref} from 'vue'

const count = ref(1)
const count2 = ref(1)

function add(){
  count.value++;
  count2.value++;
}
</script>

<template>
  <div  @click="add">
  	<slot :text="'slot1'" :count="count">original slot 1</slot>
    <div></div>
  	<slot name="slot-2" :text="'slot2'" :count="count2">original slot 2</slot>
	</div>
</template>



<!-- 使用MyComponent 组件 -->
<MyComponent #slot-2="slotProps">
  	{{ slotProps.text }} {{ slotProps.count }}
</MyComponent>

<!-- 渲染效果就是：
original slot 1
slot2 1
-->
```  

也就是说， **子组件通过作用域插槽向父组件暴露了一个访问其内部数据的接口。** 这样回头看`<el-table-column></el-table-column>` 也就容易理解，这个组件默认会暴露内部的`row` 也就是行数据或者叫做某个元素到父组件。下面两种写法是等效的：   
```vue  
<el-table-column label="Operation" #default="scope">
    <el-button type="primary">Edit {{scope.row.name}}</el-button>
</el-table-column>    

<!-- 或者我们应该更习惯下面这种写法 -->
<el-table-column label="Operation">
    <template #default="scope">
        <el-button type="primary">Edit {{scope.row.name}}</el-button>
    </template>
</el-table-column>  
```  

事实上也可以访问到`scope.column`，但是比较少用。  


## 可编辑单元格组件  

我们需要的效果是要有这么一个组件，平时是文本，在被单击时，其内部的元素变成`input, select, date-picker` 等类型。首先我们可以通过`is` 属性来实现动态组件的切换。  

### 动态组件  

通过`<component :is="conponent_type"></component>` 可以动态修改一个元素的类型。该动态元素内部还可以增加插槽，用于添加更多自定义的内容。`v-bind="$attrs"` 可以透传组件上的所有`props` 包括`v-model` 双向绑定的指令。

```vue{3,8-10} 
<!-- editablecell.vue  -->
<template>
    <component :is="props.component_type" v-bind="$attrs">
        <slot name="edit-component-slot">"slot content"</slot>
    </component>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';
const props = defineProps(['component_type'])
</script>
```

### 编辑状态切换  

设计双击单元格可以切换编辑状态，按`Enter` 或`ESC` 退出编辑状态。于是我们需要另一个插槽，通过`v-if` 指令渲染具体的组件。  
```vue{2-3,7-9,19}  
<template>
    <div @dblclick="editable = true">
        <div v-if="!editable">
            <slot name="content"></slot>
        </div>
        <component :is="component_type" v-bind="$attrs" 
            v-if="editable" 
            @keyup.enter="editable = false"
            @keyup.esc="editable = false">
            <slot name="edit-component-slot">"slot content"</slot>
        </component>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps(['component_type'])
const editable = ref(false)
</script>
```



#### 使用示例   

下面的例子可以演示用法，双击文本就可以打开一个`<el-select></el-select>` 并编辑选项，按`enter` 或`esc` 键就能退出编辑状态。唯一需要注意的是：如果`res_1` 的类型与`<el-select></el-select>` 中的`<el-option></el-option>` 中`value` 的类型不一致，则`label` 标签渲染可能会有异常。  

```vue
<editablecell component_type="el-select"  v-model="value">  
    <template #edit-component-slot>
        <el-option v-for="n in 3" :key="n" :label="`option: ${n}`" :value="n"/>
    </template>
</editablecell>
```

<editablecell component_type="el-select" v-model="res_1" @change="test"> 
    <template #content>
        <span>双击这里：-- {{res_1}} --</span>
    </template>
    <template #edit-component-slot>
        <el-option v-for="n in 3" :key="n" :label="`option: ${n}`" :value="n"/>
    </template>
</editablecell>



<script setup lang="ts">
import {ref} from 'vue'

/** 表格1 所需的数据 */
const data=[
    {name:'Tom', date:'2023-03-15', gender:'male'},
    {name:'Jerry', date:'2023-03-15', gender:'male'},
    {name:'Tara', date:'2023-03-15', gender:'female'},
    {name:'Tuffy', date:'2023-03-15', gender:'female'},
]

const component_type= ref('el-link');
function switch_component(c){
    component_type.value = c
}

const res_1 = ref(1)  

function test(){
    console.log(res_1.value)
}

</script>  