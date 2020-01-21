<template>
    <nav class="navbar" role="navigation" aria-label="main navigation">
        <div class="navbar-brand">
            <router-link
                    class="navbar-item"
                    :to="{ name: 'dashboard', params: { filter: 'all' } }"
            >
                <img src="../../src/assets/bit-bot.png" alt="bit-bots logo"/>
                <span>ImageTagger</span>
            </router-link>

            <a
                    role="button"
                    class="navbar-burger"
                    aria-label="menu"
                    aria-expanded="false"
            >
                <span aria-hidden="true"/>
                <span aria-hidden="true"/>
                <span aria-hidden="true"/>
            </a>
        </div>

        <div class="navbar-menu">
            <div class="navbar-start"></div>
            <div class="navbar-end">
                <router-link to="/" class="navbar-item">Home</router-link>
                <router-link to="/" class="navbar-item">Explore</router-link>
                <router-link to="/" class="navbar-item">Messages</router-link>
                <router-link to="/" class="navbar-item">Tools</router-link>
                <router-link to="/not-found" class="navbar-item">404</router-link>
            </div>
        </div>
    </nav>
</template>

<script>
//import PageLoadingBar from "components/PageLoadingBar"
export default {
    name: "Navbar",
    //components: { PageLoadingBar }
}
</script>

<style scoped lang="scss">
    .navbar-brand img {
        padding-right: 6px;
    }
</style>
