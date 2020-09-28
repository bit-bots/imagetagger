<template>
    <v-container>
        <v-row>
            <v-col cols="10" offset="1">
                <v-toolbar dense >
                    <template v-slot:default>
                        <v-toolbar-title>
                            <span class="theme-primary-fg font-weight-medium">{{ imageset.name }}</span>
                            <span class="font-weight-thin"> by {{ team.name }}</span>
                        </v-toolbar-title>
                    </template>
                    <template v-slot:extension>
                        <v-tabs grow>
                            <v-tab :to="{name: 'imagesetDetails'}">Imageset Details</v-tab>
                            <v-tab :to="{name: 'imagesetImages'}">Images</v-tab>
                        </v-tabs>
                    </template>
                </v-toolbar>
            </v-col>
        </v-row>

        <v-row>
            <v-col cols="10" offset="1">
                <router-view/>
            </v-col>
        </v-row>
    </v-container>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import "vue-class-component/hooks"
import {Imageset as ImagesetData} from "@/plugins/store/modules/imageset"
import {Route} from "vue-router"
import {VueInstance} from "@/main"
import {Team} from "@/plugins/store/modules/team"

const resolve = function (to: Route, fromRoute: Route, next: () => void) {
    if (VueInstance.$store.getters.imagesetById(+to.params.id) === undefined) {
        VueInstance.$store.dispatch("retrieveImageset", {
            id: to.params.id,
            sideloadTeam: true,
            sideloadImages: true
        }).finally(next)
    } else
        next()
}

    @Component({
        beforeRouteEnter: resolve,
        beforeRouteUpdate: resolve
    })
export default class Imageset extends Vue {
    get imageset(): ImagesetData {
        return this.$store.getters.imagesetById(+this.$route.params.id)
    }

    get team(): Team {
        return this.$store.getters.teamById(this.imageset.team)
    }
}
</script>

<style scoped lang="scss">

</style>
