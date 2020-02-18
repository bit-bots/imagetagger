<template>
    <header class="mdc-top-app-bar" ref="elHeader">
        <div class="mdc-top-app-bar__row">

            <!-- Left section -->
            <section class="mdc-top-app-bar__section mdc-top-app-bar__section--align-start">
                <!--button class="mdc-icon-button material-icons mdc-top-app-bar__navigation-icon--unbounded">menu</button-->
                <router-link class="brand" to="/">
                    <img class="brand-logo" src="../assets/bit-bot.svg" alt="Bit-Bots Logo">
                    <span class="brand-text">ImageTagger</span>
                </router-link>
            </section>

            <!-- Right section -->
            <section class="mdc-top-app-bar__section mdc-top-app-bar__section--align-end">
                
                <router-link v-if="isLoginVisible"
                             :to="{name: 'login'}">
                    <button class="mdc-button mdc-theme--on-primary">
                        <span class="mdc-button__ripple"/> Login
                    </button>
                </router-link>

                <slot/>
            </section>
        </div>
    </header>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import {MDCTopAppBar} from "@material/top-app-bar/component"

@Component({
})
export default class Navbar extends Vue {
    private _mdcAppBar: MDCTopAppBar;

    mounted() {
        this._mdcAppBar = new MDCTopAppBar(this.$refs.elHeader as Element)
    }

    get isLoginVisible() {
        return !this.$store.state.auth.loggedIn
    }
}
</script>

<style scoped lang="scss">
    @import "~@material/top-app-bar/mdc-top-app-bar";

    header.mdc-top-app-bar {
        top: 0;
        position: initial;
        display: block;
    }

    .brand {
        display: flex;
        align-items: center;
        padding-left: 10px;
    }

    .brand-logo {
        height: 45px;
        padding: 0 5px;
    }

    .brand-text {
        @extend .mdc-top-app-bar__title;
        padding-left: 8px;
    }

    .mdc-button {
        text-transform: capitalize;
    }
</style>
