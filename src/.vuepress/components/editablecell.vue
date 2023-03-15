<template>
    <div @dblclick="editable = true">
        <el-tooltip v-if="!editable" effect="dark" placement="top">

            <template #content>double click to edit<br/>press ESC/Enter to exit</template>
            <slot name="content"></slot>
        </el-tooltip>
        <component :is="component_type" v-bind="$attrs" v-if="editable" @keyup.enter="editable = false"
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

<style></style>