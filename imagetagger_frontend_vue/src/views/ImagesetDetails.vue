<template>
    <div class="imageset-details-root">
        <h4>
            <span class="mdc-theme--text-disabled-on-light">Details of </span>
            <span class="mdc-theme--secondary">{{ team.name }}</span>
            <span class="mdc-theme--text-disabled-on-light">'s </span>
            <span class="mdc-theme--primary">{{ imageset.name }}</span>
        </h4>

        <imageset-tags :imageset-id="imageset.id"/>

        <div>
            <table>
                <tr>
                    <td>Tags</td>
                    <td>
                        <span v-for="tag of imageset.tags" :key="tag">
                            {{ tag }}
                        </span>
                    </td>
                </tr>

                <tr>
                    <td>Location</td>
                </tr>
            </table>
        </div>
    </div>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import "vue-class-component/hooks"
import {Prop} from "vue-property-decorator"
import VueTypes from "vue-types"
import {Route} from "vue-router"
import {VueInstance} from "@/main"
import {Imageset} from "@/store/modules/imageset"
import {Team} from "@/store/modules/team"
import ImagesetTags from "@/components/ImagesetTags.vue"
import HorizontalDivider from "@/components/HorizontalDivider.vue";


const resolve = function (toRoute: Route, fromRoute: Route, next: () => void) {
    Promise.all([
        VueInstance.$store.dispatch("retrieveImageset", {
            id: toRoute.params.id,
            sideloadTeam: true
        })
    ]).finally(next)
}


@Component({
    components: {HorizontalDivider, ImagesetTags},
    beforeRouteEnter: resolve
})
export default class ImagesetDetails extends Vue {
    get imageset(): Imageset {
        return this.$store.getters.imagesetById(+this.$route.params.id)
    }
    get team(): Team {
        return this.$store.getters.teamById(this.imageset.team)
    }
}
</script>

<style scoped lang="scss">
    .imageset-details-root {
        margin: 2% 3%;
    }

    .imageset-details-root h4 {
        margin-bottom: 1.8%;
    }

    .imageset-tags-root {
        margin-bottom: 2%;
        margin-left: -6px;
    }
</style>
