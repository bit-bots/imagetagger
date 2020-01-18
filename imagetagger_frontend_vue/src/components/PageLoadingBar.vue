<template>
    <progress v-if="currentlyLoadingPage" class="progress"/>
</template>

<script>
    import { mapState } from "vuex"

    export default {
        name: "PageLoadingBar",
        computed: mapState(['currentlyLoadingPage'])
    }
</script>

<style scoped lang="scss">
    progress {
        width: 100%;
        height: 10px;
    }
</style>
