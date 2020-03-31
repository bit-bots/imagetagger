<template>
    <button
            class="navbar-tab-root mdc-tab" ref="elTab" role="tab">
        <span class="mdc-tab__content">
            <i v-if="icon" class="mdi" :class="`mdi-${icon}`"/>
            <span class="mdc-tab__text-label mdc-theme--on-primary"><slot>Text is not set</slot></span>
        </span>
        <span class="mdc-tab-indicator" ref="elTabIndicator">
            <span class="mdc-tab-indicator__content mdc-tab-indicator__content--underline mdc-theme--on-primary"/>
        </span>
        <span class="mdc-tab__ripple"/>
    </button>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import "vue-class-component/hooks"
import {Prop} from "vue-property-decorator"
import VueTypes from "vue-types"
import {RawLocation} from "vue-router"
import {MDCTab} from "@material/tab/component"
import {MDCTabIndicator} from "@material/tab-indicator/component"

@Component({})
export default class NavbarTab extends Vue {
    @Prop(VueTypes.string.def("")) readonly icon: string
    @Prop(VueTypes.string.isRequired) readonly routeName: string
    private tab: MDCTab
    private tabIndicator: MDCTabIndicator

    mounted(): void {
        this.tab = new MDCTab(this.$refs.elTab as Element)
        this.tabIndicator = new MDCTabIndicator(this.$refs.elTabIndicator as Element)

        this.tab.listen("click", () => this.navigateToSelf())

        if (this.isActiveRoute) {
            this.navigateToSelf()
            this.tab.activate()
        }
    }

    destroyed(): void {
        this.tab.destroy()
        this.tabIndicator.destroy()
    }

    get isActiveRoute(): boolean {
        return this.$route.matched.some(({name}) => name === this.routeName)
    }

    private navigateToSelf(): void {
        this.$router.push({name: this.routeName}).catch(err => {
            if (err._name != "NavigationDuplicated")
                console.error(err)
        })
    }
}
</script>

<style scoped lang="scss">
    @import "../styles/global_style";

    .mdc-tab-indicator .mdc-tab-indicator__content--underline.mdc-theme--on-primary {
        border-color: $background-color;
    }
</style>
