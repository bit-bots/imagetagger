<template>
    <div>
        <Navbar/>

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
