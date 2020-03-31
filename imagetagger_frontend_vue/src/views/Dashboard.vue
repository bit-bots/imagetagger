<template>
    <div class="dashboard-root">
        <navbar class="space-after">
            <navbar-search/>
            <navbar-profile/>
        </navbar>

        <div class="centered actions-container">
            <imagetagger-button>Create Imageset</imagetagger-button>
        </div>

        <div v-if="imagesets.length === 0" class="centered">
            <h4 class="no-imagesets-error">No Imagesets created yet</h4>
        </div>

        <!-- List of imagesets -->
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
import {Imageset} from "@/plugins/store/modules/imageset"
import ImagesetOverview from "@/components/ImagesetOverview.vue"
import HorizontalDivider from "@/components/HorizontalDivider.vue"
import ImagetaggerButton from "@/components/base/ImagetaggerButton.vue"


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
    components: {ImagetaggerButton, HorizontalDivider, ImagesetOverview, NavbarProfile, NavbarSearch, Navbar},
    beforeRouteEnter: resolve
})
export default class Dashboard extends Vue {
    get imagesets(): Imageset[] {
        const filter = this.$store.state.contentFilter.searchTerm as string
        const imagesets = this.$store.state.imagesets.imagesets as Imageset[]

        return imagesets.filter(iimageset => iimageset.id.toString() == filter ||
            iimageset.name.toLowerCase().includes(filter.toLowerCase()) ||
            this.$store.getters.teamById(iimageset.team).name.toLowerCase().includes(filter.toLowerCase()))
    }
}
</script>

<style scoped lang="scss">
    @import "~@material/elevation/mdc-elevation.scss";
    @import "../styles/global_style";

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

    .actions-container {
        display: flex;
        padding: 6px 8px;
        flex-flow: row nowrap;
        justify-items: center;
        justify-content: flex-start;

        & > * {
            margin-right: 8px;
        }
    }
</style>
