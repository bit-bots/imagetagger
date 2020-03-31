<template>
    <div class="imageset-details-root">
        <h4 class="imageset-title">
            <span class="mdc-theme--text-disabled-on-light">Details of </span>
            <span class="mdc-theme--secondary">{{ team.name }}</span>
            <span class="mdc-theme--text-disabled-on-light">'s </span>
            <span class="mdc-theme--primary">{{ imageset.name }}</span>
        </h4>
        <p v-if="imageset.description" class="mdc-typography--subtitle1">{{ imageset.description }}</p>
        <horizontal-divider/>

        <imageset-tags :imageset-id="imageset.id"/>

        <div>
            <table class="mdc-typography--subtitle1">
                <tr v-if="imageset.location">
                    <td>
                        <i class="mdi mdi-map-marker"/>
                        <span>Location</span>
                    </td>
                    <td>{{ imageset.location }}</td>
                </tr>

                <tr>
                    <td>
                        <i class="mdi mdi-professional-hexagon"/>
                        <span>Creator</span>
                    </td>
                    <td>{{ creator.username }}</td>
                </tr>

                <tr>
                    <td>
                        <i class="mdi mdi-nuke"/>
                        <span>Image count</span>
                    </td>
                    <td>{{ imageset.numberOfImages }}</td>
                </tr>

                <tr>
                    <td>
                        <i class="mdi mdi-null"/>
                        <span>Annotation count</span>
                    </td>
                    <td>Not yet in data-type <!-- TODO Retrieve annotation count --></td>
                </tr>
            </table>
        </div>

        <fab-button class="fixed-bottom-right" icon="download">
            <fab-button-sub-action icon="download">Download Zip</fab-button-sub-action>
            <fab-button-sub-action icon="export">Export</fab-button-sub-action>
            <fab-button-sub-action icon="plus">Create new Format</fab-button-sub-action>
        </fab-button>
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
import {Imageset} from "@/plugins/store/modules/imageset"
import {Team} from "@/plugins/store/modules/team"
import ImagesetTags from "@/components_old/ImagesetTags.vue"
import HorizontalDivider from "@/components_old/HorizontalDivider.vue"
import {User} from "@/plugins/store/modules/user"
import FabButton from "@/components_old/base/FabButton.vue"
import FabButtonSubAction from "@/components_old/base/FabButtonSubAction.vue"


const resolve = function (toRoute: Route, fromRoute: Route, next: () => void) {
    Promise.all([
        VueInstance.$store.dispatch("retrieveImageset", {
            id: toRoute.params.id,
            sideloadTeam: true,
            sideloadCreator: true
        })
    ]).finally(next)
}


@Component({
    components: {FabButtonSubAction, FabButton, HorizontalDivider, ImagesetTags},
    beforeRouteEnter: resolve
})
export default class ImagesetDetails extends Vue {
    get imageset(): Imageset {
        return this.$store.getters.imagesetById(+this.$route.params.id)
    }
    get team(): Team {
        return this.$store.getters.teamById(this.imageset.team)
    }
    get creator(): User {
        return this.$store.getters.userById(this.imageset.creator)
    }
}
</script>

<style scoped lang="scss">
    .imageset-details-root {
        margin: 2% 3%;

        h4 {
            margin-bottom: 12px;
        }

        .divider {
            margin: 8px 0 16px;
        }

        .imageset-tags-root {
            margin-bottom: 24px;
            margin-left: -6px;
        }

        .fixed-bottom-right {
            position: fixed;
            bottom: 25px;
            right: 25px;
        }
    }
</style>
