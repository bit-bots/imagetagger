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

        <!-- Tab bar -->
        <div v-show="isTabRowVisible" ref="elTabBar"
             class="mdc-top-app-bar__row tab-row mdc-theme--primary-bg">
            <div class="mdc-tab-bar" role="tablist">
                <div class="mdc-tab-scroller" ref="elTabScroller">
                    <div class="mdc-tab-scroller__scroll-area">
                        <div class="mdc-tab-scroller__scroll-content">
                            <slot name="tabs"/>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </header>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import "vue-class-component/hooks"
import VueTypes from "vue-types"
import {Prop} from "vue-property-decorator"
import {MDCTopAppBar} from "@material/top-app-bar/component"
import {MDCTabBar} from "@material/tab-bar/component"
import {MDCTabScroller} from "@material/tab-scroller/component"

@Component({})
export default class Navbar extends Vue {
    private _mdcAppBar: MDCTopAppBar
    private _mdcTabBar: MDCTabBar
    private _mdcTabScroller: MDCTabScroller

    mounted() {
        this.warnTabAmount()

        this._mdcAppBar = new MDCTopAppBar(this.$refs.elHeader as Element)
        this._mdcTabScroller = new MDCTabScroller(this.$refs.elTabScroller as Element)
        this._mdcTabBar = new MDCTabBar(this.$refs.elTabBar as Element)
    }

    updated(): void {
        this.warnTabAmount()
    }

    get isLoginVisible() {
        return !this.$store.state.auth.loggedIn
    }

    get isTabRowVisible() {
        return this.$slots.tabs && this.$slots.tabs[0]
    }

    private warnTabAmount() {
        if (this.$slots.tabs && this.$slots.tabs.length == 1) {
            console.warn("Having only one tab on the Navbar is bad UI design")
        }
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
