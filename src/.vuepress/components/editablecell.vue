<template>
    <div class="editable-cell">
        <div v-if="editable && !isBeingEdited" placement="bottom" @click="edit">
            <el-link type="primary" :icon="Edit" plain />
            <slot></slot>
        </div>
        <div v-else-if="editable && isBeingEdited">
            <el-link type="success" :icon="Check" plain @click="finishSelectEditing" />
            <component ref="input" autofocus="true" :is="component" v-bind="$attrs" @blur="finishEditing">
                <slot name="sub-component"></slot>
            </component>
        </div>
        <div v-else class="uneditable-cell">
            <slot></slot>
        </div>
    </div>
</template>

<script setup lang="ts">
import { Check, Edit } from '@element-plus/icons-vue';
import { computed, nextTick, ref } from 'vue';

const props = defineProps([
    'editable',   // the editable switch
    'component',  // editable componenet instance
]);
const isSelect = computed(() => {
    return props.component == 'el-select'
})
const isBeingEdited = ref(false);  // internal editing state
const input = ref()


function finishEditing() {
    if (isSelect.value) {
    } else {
        isBeingEdited.value = false
    }
}


function edit(e) {
    isBeingEdited.value = true
    // can not get ref input before the element is created
    nextTick(() => {
        input.value.focus()
    })
}

function finishSelectEditing() {
    isBeingEdited.value = false
}
</script>



<style scoped>
.editable-cell {
    min-height: zpx;
    /* set minimum height to extend the div container */
    cursor: pointer;
}

.uneditable-cell {
    cursor: default;
}
</style>