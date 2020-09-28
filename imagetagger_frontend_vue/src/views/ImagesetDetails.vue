<template>
    <v-row>
        <!-- Information -->
        <v-col>
            <v-card>
                <v-card-title>Imageset Details</v-card-title>
                <v-card-text><it-imageset-details-data :id="this.imageset.id"/></v-card-text>
                <v-card-actions>
                    <v-btn outlined disabled>Export</v-btn> <!-- TODO Implement tag exporting -->
                    <v-btn outlined disabled>Import</v-btn> <!-- TODO Implement tag importing -->
                </v-card-actions>
            </v-card>
        </v-col>

        <!-- Statistics -->
        <v-col cols="3">
            <v-card>
                <v-card-title>Statistics</v-card-title>
                <v-card-text>
                    <v-alert color="warning">Not yet implemented</v-alert> <!-- TODO Implement Imageset statistics -->
                </v-card-text>
            </v-card>
        </v-col>
    </v-row>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import "vue-class-component/hooks"
import {Imageset} from "@/plugins/store/modules/imageset"
import ItImagesetDetailsData from "@/components/ItImagesetDetailsData.vue"
import {VueInstance} from "@/main"
import {Route} from "vue-router"

const resolve = function (to: Route, fromRoute: Route, next: () => void) {
    VueInstance.$store.dispatch("retrieveAvailableTags")
        .finally(next)
}

@Component({
    components: {ItImagesetDetailsData},
    beforeRouteEnter: resolve
})
export default class ImagesetDetails extends Vue {
    get imageset(): Imageset {
        return this.$store.getters.imagesetById(+this.$route.params.id)
    }
}
</script>

<style scoped lang="scss">

</style>
