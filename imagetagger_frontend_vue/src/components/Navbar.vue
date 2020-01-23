<template>
    <nav class="navbar navbar-expand-lg navbar-light bg-light" role="navigation" aria-label="main navigation">
        <!-- Logo with application name -->
        <router-link v-bind:to="{name: 'dashboard', params: {filter: 'all'}}" class="navbar-brand">
            <img src="../assets/bit-bot.png" alt="bit-bots logo">
            <span>ImageTagger</span>
        </router-link>

        <!-- Hamburger button for when the navbar is responsively collapsed -->
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarCollapse">
            <span class="navbar-toggler-icon"/>
        </button>

        <!-- Navbar buttons on right side -->
        <div class="collapse navbar-collapse">
            <ul class="navbar-nav ml-auto">
                <li class="nav-item">
                    <router-link v-bind:to="{name: 'dashboard', params: {filter: 'all'}}"
                                 class="nav-link">Dashboard
                    </router-link>
                </li>
                <li>
                    <router-link to="/" class="nav-link">Explore</router-link>
                </li>
                <li>
                    <router-link to="/" class="nav-link">Messages</router-link>
                </li>
                <li>
                    <router-link to="/" class="nav-link">Tools</router-link>
                </li>
                <li>
                    <router-link
                            v-if="isLoginVisible"
                            v-bind:to="{name: 'login'}" class="nav-link">Login
                    </router-link>
                </li>
            </ul>
        </div>
    </nav>
</template>

<script lang="ts">
import Vue from "vue"

export default Vue.extend({
    computed: {
        isLoginVisible() {
            return !this.$store.state.auth.loggedIn
        }
    }
})
</script>

<style scoped lang="scss">
    .navbar-brand img {
        height: 40px;
        padding-right: 6px;
    }
</style>
