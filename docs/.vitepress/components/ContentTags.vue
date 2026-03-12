<template>

    <div class="flex">
        <el-badge class="m-1">
            <el-button size="small" :type="'all' == selected_tag ? 'primary' : 'default'"
                @click="onTagSelected('all')">全部</el-button>
        </el-badge>
        <el-badge class="m-1" v-for="(v, k) in tags" :value="v">
            <el-button size="small" :type="k == selected_tag ? 'primary' : 'default'" @click="onTagSelected(k)">{{ k
            }}</el-button>
        </el-badge>

    </div>



    <h3 class="mb-6 ms-3 text-2xl font-bold text-neutral-700 dark:text-neutral-300">
        当前标签共有 {{ tag_contents.length }} 篇日志。
    </h3>
    <div>
        <el-timeline>
            <el-timeline-item v-for="(_, index) in tag_contents.slice((currentPage-1)*pageSize,currentPage*pageSize)" :key="index">
                <el-tag size="small">{{ moment(_.frontmatter.date).format("YYYY-MM-DD") }}</el-tag>
                <el-link class=" ml-2" :href="_.url"> <el-text class="mx-1" size="large" truncated> {{
                    _.frontmatter.title
                        }}</el-text></el-link>
            </el-timeline-item>
        </el-timeline>
    </div>
    <el-divider></el-divider>
    <el-pagination layout=" prev, pager, next" :total="tag_contents.length" v-model:current-page="currentPage"
        :page-size="pageSize" />
</template>


<script setup>
import { computed, ref } from 'vue';
import { data } from '../theme/contents.data.ts'
import moment from 'moment';

import { useData } from 'vitepress';
const { isDark } = useData();

const currentPage = ref(1)
const pageSize = ref(10)
const collapseTitle = ref("展开")

const selected_tag = ref('all')



const tags = computed(() => {
    let tags = {}

    for (let i = 0; i < data.length; i++) {
        const _tags = data[i].frontmatter.tags ?? []
        for (let j = 0; j < _tags.length; j++) {
            const _t = _tags[j]
            if (tags[_t]) {
                tags[_t] += 1
            } else {
                tags[_t] = 1
            }

        }
    }
    const sortedTags = Object.fromEntries(
        Object.entries(tags).sort(([k1], [k2]) => k1.localeCompare(k2))
    );

    return sortedTags
})


const tag_contents = computed(() => {
    if (selected_tag.value != 'all') {
        return data.filter(item => item.frontmatter.tags?.indexOf(selected_tag.value) > -1)
    }
    return data
})


function onTagSelected(val) {
    selected_tag.value = val
    currentPage.value = 1
}

const handleChange = (activeNames) => {
    console.log(activeNames)
    collapseTitle.value = activeNames.length < 1 ? "展开" : "折叠"
}


</script>

<style lang="css" scoped>
.el-timeline-item::marker {
    content: '';
}

:deep(.number) {
    margin-top: 0 !important;
}
</style>