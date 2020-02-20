<template>
    <div class="imageset-tags-root mdc-chip-set" role="grid">
        <div v-for="tag of imageset.tags" :key="tag"
                class="mdc-chip" role="row">
            <div class="mdc-chip__ripple"/>
            <span role="gridcell">
                <span role="button" class="mdc-chip__text mdc-typography--caption">{{ tag }}</span>
            </span>
            <span role="gridcell" @click="removeTag(tag)">
                <i class="mdc-chip__icon mdc-chip__icon--trailing mdi mdi-close"/>
            </span>
        </div>
    </div>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import "vue-class-component/hooks"
import {Prop} from "vue-property-decorator"
import VueTypes from "vue-types"
import {Imageset} from "@/store/modules/imageset"

@Component({})
export default class ImagesetTags extends Vue {
    @Prop(VueTypes.integer.isRequired) readonly imagesetId: number

    get imageset(): Imageset {
        return this.$store.getters.imagesetById(this.imagesetId)
    }

    removeTag(tag: string): void {
        this.$store.dispatch("removeImagesetTag", {imageset: this.imageset, tag: tag})
            .catch(console.error)
    }
}
</script>

<style scoped lang="scss">

</style>
