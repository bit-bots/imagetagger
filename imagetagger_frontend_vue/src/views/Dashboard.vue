<template>
    <div>
        <navbar class="space-after">
            <navbar-search/>
            <navbar-profile/>
        </navbar>

        <div v-for="(iimageset, i) in imagesets" :key="iimageset.id"
             class="centered">
            <router-link :to="{name: 'imagesetDetails', params: {'id': iimageset.id}}">
                <imageset-overview class="raise-on-hover"
                                   :imageset-id="iimageset.id"/>
            </router-link>
            <horizontal-divider v-if="i < imagesets.length - 1"/>
        </div>
    </div>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import {Route} from "vue-router"
import {VueInstance} from "@/main"
import Navbar from "@/components/Navbar.vue"
import NavbarSearch from "@/components/NavbarSearch.vue"
import NavbarProfile from "@/components/NavbarProfile.vue"
import {Imageset} from "@/store/modules/imageset"
import ImagesetOverview from "@/components/ImagesetOverview.vue"
import HorizontalDivider from "@/components/HorizontalDivider.vue"


/**
 * Resolve API dependencies of all included components.
 *
 * Done here because components don't get the beforeRouteEnter event call.
 */
const resolve = function (toRoute: Route, fromRoute: Route, next: any) {
    Promise.all([
        VueInstance.$store.dispatch("retrieveAllImagesets"),
        VueInstance.$store.dispatch("retrieveAllTeams")
    ]).catch(console.error).finally(next)
}


@Component({
    components: {HorizontalDivider, ImagesetOverview, NavbarProfile, NavbarSearch, Navbar},
    beforeRouteEnter: resolve
})
export default class Dashboard extends Vue {
    get imagesets(): Imageset[] {
        return this.$store.state.imagesets.imagesets
    }
}
</script>

<style scoped lang="scss">
    @import "~@material/elevation/mdc-elevation.scss";

    .space-after {
        margin-bottom: 40px;
    }

    .raise-on-hover {
        transition-duration: 0.25s;
    }
    .raise-on-hover:hover {
        @extend .mdc-elevation--z8
    }

    .imageset-overview-root {
        padding: 0 15px;
        border-radius: 3px;
    }

    .centered {
        width: 80%;
        margin-left: auto;
        margin-right: auto;
    }
</style>
