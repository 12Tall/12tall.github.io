<template>
    <div class="flex">
        <el-badge class="m-1">
            <el-button size="small" :type="'all' == selected_cate ? 'primary' : 'default'" @click="onCategorySelected('all')">全部</el-button>
        </el-badge>
        <el-badge class="m-1" v-for="(v, k) in categories" :value="v">
            <el-button size="small" :type="k == selected_cate ? 'primary' : 'default'" @click="onCategorySelected(k)">{{ k
            }}</el-button>
        </el-badge>
    </div>
    <h3 class="mb-6 ms-3 text-2xl font-bold text-neutral-700 dark:text-neutral-300">
        当前分类共有 {{ category_contents.length }} 篇日志。
    </h3>
    <div>
        <el-timeline>
            <el-timeline-item v-for="(_, index) in category_contents" :key="index">
                <el-tag size="small">{{ moment(_.frontmatter.date).format("YYYY-MM-DD") }}</el-tag>
                <el-link class=" ml-2" :href="_.url"> <el-text class="mx-1" size="large" truncated> {{
                    _.frontmatter.title
                        }}</el-text></el-link>
            </el-timeline-item>
        </el-timeline>
    </div>
    <el-divider></el-divider>
    <el-pagination layout=" prev, pager, next" :total="data.length" v-model:current-page="currentPage"
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

const selected_cate = ref('all')



const categories = computed(() => {
    let categories = {}

    for (let i = 0; i < data.length; i++) {
        const url = data[i].url
        const cate = url.split("/")[2]
        if (categories[cate]) {
            categories[cate] += 1
        } else {
            categories[cate] = 1
        }
    }
    const sortedCategories = Object.fromEntries(
        Object.entries(categories).sort(([k1], [k2]) => k1.localeCompare(k2))
    );

    return sortedCategories
})


const category_contents = computed(() => {
    if (selected_cate.value != 'all') {
        return data.filter(item => item.url?.split("/")?.[2] === selected_cate.value)
    }
    return data
})


function onCategorySelected(val) {
    selected_cate.value = val
    currentPage.value = 1
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