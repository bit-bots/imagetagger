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
        <div ref="elTabBar" v-show="isTabRowVisible"
                class="mdc-tab-bar mdc-theme--primary-bg grow-from-top" role="tablist">
            <div class="mdc-tab-scroller" ref="elTabScroller">
                <div class="mdc-tab-scroller__scroll-area">
                    <div class="mdc-tab-scroller__scroll-content">
                        <slot name="tabs"/>
                    </div>
                </div>
            </div>
        </div>

        <!-- Loading bar -->
        <div ref="elLoadingBar" :class="isLoadingBarVisible ? '' : 'mdc-linear-progress--closed'"
             role="progressbar" class="mdc-linear-progress mdc-linear-progress--indeterminate">
            <div class="mdc-linear-progress__buffering-dots"/>
            <div class="mdc-linear-progress__buffer"/>
            <div class="mdc-linear-progress__bar mdc-linear-progress__primary-bar">
                <span class="mdc-linear-progress__bar-inner"/>
            </div>
            <div class="mdc-linear-progress__bar mdc-linear-progress__secondary-bar">
                <span class="mdc-linear-progress__bar-inner"/>
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
import {MDCLinearProgress} from "@material/linear-progress/component"

@Component({})
export default class Navbar extends Vue {
    private _mdcAppBar: MDCTopAppBar
    private _mdcTabBar: MDCTabBar
    private _mdcTabScroller: MDCTabScroller
    private _mdcLoadingBar: MDCLinearProgress

    mounted() {
        this.warnTabAmount()

        this._mdcAppBar = new MDCTopAppBar(this.$refs.elHeader as Element)
        this._mdcTabScroller = new MDCTabScroller(this.$refs.elTabScroller as Element)
        this._mdcTabBar = new MDCTabBar(this.$refs.elTabBar as Element)
        this._mdcLoadingBar = new MDCLinearProgress(this.$refs.elLoadingBar as Element)
    }

    destroyed(): void {
        this._mdcAppBar.destroy()
        this._mdcTabScroller.destroy()
        this._mdcTabBar.destroy()
        this._mdcLoadingBar.destroy()
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

    get isLoadingBarVisible() {
        return this.$store.state.currentlyLoading
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
    @import "../styles/global_style";

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

    .mdc-linear-progress__bar-inner {
        border-color: $accent-color;
    }
</style>
