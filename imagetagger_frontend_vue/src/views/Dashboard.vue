<template>
    <div>
        <Navbar/>

        <h1 class="title">Dashboard</h1>
    </div>
</template>

<script>
    import Navbar from "components/Navbar";

    export default {
        components: {Navbar},
        computed: {
            test() {
                return this.$route.params
            }
        }
    }
</script>

<style lang="scss">
</style>
