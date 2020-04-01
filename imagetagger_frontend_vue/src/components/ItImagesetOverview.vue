<template>
    <div class="d-flex flex-row flex-nowrap align-center">
        <div class="marker-container">
            <v-icon class="theme-error-fg">mdi-alert-circle-outline</v-icon>
        </div>

        <div>
            <h6 class="title">
                <span class="theme-secondary-fg">{{ team.name }}</span>
                <span class="theme-secondary-fg"> / </span>
                <span class="theme-primary-fg">{{ imageset.name }}</span>
            </h6>
        </div>
    </div>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import "vue-class-component/hooks"
import {Prop} from "vue-property-decorator"
import VueTypes from "vue-types"
import {Imageset} from "@/plugins/store/modules/imageset"
import {Team} from "@/plugins/store/modules/team"

@Component({})
export default class ItImagesetOverview extends Vue {
    @Prop(VueTypes.integer.isRequired) public readonly imagesetId: number

    get imageset(): Imageset {
        return this.$store.getters.imagesetById(this.imagesetId)
    }

    get team(): Team {
        return this.$store.getters.teamById(this.imageset.team)
    }
}
</script>

<style scoped lang="scss">
    .marker-container {
        margin-right: 16px;
        width: 24px;
        text-align: center;
    }

    h6 {
        margin-top: 1em;
        margin-bottom: 1em;
    }
</style>
