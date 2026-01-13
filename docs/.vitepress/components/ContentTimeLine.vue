<template>
    <h3 class="mb-2 text-2xl font-bold text-neutral-700 dark:text-neutral-300">
        非常好! 目前共计 {{ data.length }} 篇日志。 继续努力。
    </h3>
    <el-divider></el-divider>
    <div>
        <el-timeline>
            <el-timeline-item v-for="(_, index) in posts" :key="index">
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
import { ref, computed } from 'vue';
import { data } from '../theme/contents.data.ts'
import moment from 'moment';

const currentPage = ref(1)
const pageSize = ref(10)

const posts = computed(() => {
    const start = (currentPage.value - 1) * pageSize.value
    return data.slice(start, start + pageSize.value)
})

</script>

<style lang="css" scoped>
.el-timeline-item::marker {
    content: '';
}

:deep(.number) {
    margin-top: 0 !important;
}
</style>