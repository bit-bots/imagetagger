<template>
    <section class="section">
        <div class="container">
            <img src="../assets/bit-bot.png">
            <h1 class="title">
                Hello World
            </h1>
            <p class="subtitle">
                My first website with <strong>{{test}}</strong>!
            </p>
        </div>
    </section>
</template>

<script>
    export default {
        computed: {
            test() {
                return this.$route.params
            }
        }
    }
</script>

<style lang="scss">
</style>
