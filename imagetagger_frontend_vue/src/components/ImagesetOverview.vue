<template>
    <div class="imageset-overview-root">
        <div class="marker">
            <i class="mdi mdi-alert-circle-outline mdc-theme--error"/>
            <!-- TODO v-if="imageset.priority but only after the api returns that information on listing imagesets" -->
        </div>
        <div class="details-container">
            <h6 class="mdc-typography--subtitle1">
                <span class="mdc-theme--secondary">{{ team.name }}</span>
                <span class="mdc-theme--secondary"> / </span>
                <span class="mdc-theme--primary">{{ imageset.name }}</span>
            </h6>
        </div>
        <div class="actions-container">
            <p>no actions yet</p>
        </div>
    </div>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import VueTypes from "vue-types"
import {Imageset} from "@/store/modules/imageset"
import {Team} from "@/store/modules/team"


@Component({
    props: {
        imagesetId: VueTypes.integer.isRequired
    }
})
export default class ImagesetOverview extends Vue {
    private imagesetId: number // prop

    get imageset(): Imageset {
        return this.$store.getters.imagesetById(this.imagesetId)
    }
    get team(): Team {
        return this.$store.getters.teamById(this.imageset.team)
    }
}
</script>

<style scoped lang="scss">
    .imageset-overview-root {
        display: flex;
        flex-flow: row nowrap;
        align-items: center;
    }

    .marker {
        margin-right: 20px;
        width: 25px;
        text-align: center;
        i {
            font-size: x-large;
        }
    }

    .actions-container {
        margin-left: auto;
    }

    h6 {
        margin-top: 1.2em;
        margin-bottom: 1.2em;
    }
</style>
