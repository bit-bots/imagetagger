<template>
    <v-container class="fill-height">
        <!-- List of imagesets -->
        <v-row dense>
            <v-col v-if="imagesets.length === 0" cols="8" offset="2">
                <v-banner class="elevation-4">No imagesets created yet</v-banner>
            </v-col>

            <v-col v-for="iimageset in imagesets" :key="iimageset.id"
                   cols="8" offset="2">
                <v-hover v-slot:default="{ hover }">
                    <router-link :to="{name: 'imagesetDetails', params: {id: iimageset.id}}" class="a-unstyle">
                        <it-imageset-overview :imageset-id="iimageset.id"
                                              class="px-2"
                                              :class="hover ? ['active-imageset', 'elevation-6'] : ''"/>
                    </router-link>
                </v-hover>
            </v-col>
        </v-row>
    </v-container>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import "vue-class-component/hooks"
import {Route} from "vue-router/types/router"
import {Imageset} from "@/plugins/store/modules/imageset"
import {VueInstance} from "@/main"
import ItImagesetOverview from "@/components/ItImagesetOverview.vue";


/**
 * Resolve network dependencies of all included components
 */
const resolve = function(to: Route, fromRoute: Route, next: Function): void {
    Promise.all([
        VueInstance.$store.dispatch("retrieveAllImagesets"),
        VueInstance.$store.dispatch("retrieveAllTeams")
    ]).catch(console.error).finally(next())
}

@Component({
    components: {ItImagesetOverview},
    beforeRouteEnter: resolve
})
export default class Dashboard extends Vue {
    get imagesets(): Imageset[] {
        return this.$store.state.imagesets.imagesets
    }
}
</script>

<style scoped lang="scss">
    .active-imageset {
        transition-duration: 0.25s;
    }
</style>
