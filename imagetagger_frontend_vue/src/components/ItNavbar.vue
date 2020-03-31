<template>
    <v-app-bar color="primary" :app="true">
        <!-- Main row -->
        <template v-slot:default>
            <router-link class="brand a-unstyle theme-white-fg" to="/">
                <img class="brand__logo" src="../assets/bit-bot.svg" alt="Bit-Bots Logo">
                <span class="brand__text">ImageTagger</span>
            </router-link>
            <v-spacer/>

            <!-- Right side controls -->
            <it-navbar-profile v-if="isLoggedIn"/>
            <router-link v-else :to="{name: 'login'}">
                <v-btn text color="white">Login</v-btn>
            </router-link>
        </template>

        <template v-slot:extension v-if="isLoadingBarVisible">
            <!-- TODO Implement loading bar -->
        </template>
    </v-app-bar>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import "vue-class-component/hooks"
import {Prop} from "vue-property-decorator"
import VueTypes from "vue-types"
import ItNavbarProfile from "@/components/ItNavbarProfile.vue"

@Component({
    components: {ItNavbarProfile}
})
export default class ItNavbar extends Vue {
    get isLoggedIn(): boolean {
        return this.$store.state.auth.loggedIn
    }

    get isLoadingBarVisible(): boolean {
        return this.$store.state.currentlyLoading && false
    }
}
</script>

<style scoped lang="scss">
    .brand {
        display: flex;
        align-items: center;

        & .brand__logo {
            height: 45px;
            padding: 0 5px;
        }

        & .brand__text {
            padding-left: 8px;
        }
    }
</style>
