<template>
    <div>
        <Navbar/>

        <section class="hero is-fullheight-with-navbar">
            <div class="hero-body">
                <div class="container">
                    <h1 class="title">Error 404</h1>
                    <h2 class="subtitle">
                        The page you were looking for could not be found
                    </h2>
                </div>
            </div>
        </section>
    </div>
</template>

<script lang="ts">
import Vue from "vue"
import Navbar from "@components/Navbar.vue"

export default Vue.extend({
    name: "NotFound",
    components: {Navbar},
    data() {
        return {}
    },

    computed: {},

    methods: {}
})
</script>

<style scoped lang="scss"></style>
