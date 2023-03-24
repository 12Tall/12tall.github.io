<template>
    <div @click="edit" class="editable-cell">
        <ElTooltip v-if="editable && !isBeingEdited" placement="bottom">
            <template v-if="editable" #content>Click to edit<br />Press Enter/Esc/Tab to exit</template>

            <slot></slot>
        </ElTooltip>
        <component ref="input" autofocus="true" v-else-if="editable && isBeingEdited" :is="component" v-bind="$attrs"
            @keyup.enter="finishEditing" @keyup.esc="finishEditing" @keyup.tab="finishEditing">
            <slot name="sub-component"></slot>
        </component>
        <div v-else class="uneditable-cell">
            <slot></slot>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ElTooltip } from 'element-plus';
import { nextTick, ref } from 'vue';

const props = defineProps([
    'editable',   // the editable switch
    'component',  // editable componenet instance
]);
const isBeingEdited = ref(false);  // internal editing state
const input = ref()


function finishEditing() {
    isBeingEdited.value = false
}

function edit(e) {
    if (props.editable) {
        isBeingEdited.value = true
        // can not get ref input before the element is created
        nextTick(() => {
            input.value.focus()
        })
    }
}

</script>



<style scoped>
.editable-cell {
    min-height: 32px;
    /* set minimum height to extend the div container */
    cursor: pointer;
}

.uneditable-cell {
    cursor: default;
}
</style>