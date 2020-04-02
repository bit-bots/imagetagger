<template>
    <v-combobox type="solo"
                hide-selected
                multiple
                small-chips
                deletable-chips
                flat
                placeholder="Enter a new Tag name or select one"
                v-model="selectedTags"
                :items="availableTags"></v-combobox>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import "vue-class-component/hooks"
import {Prop} from "vue-property-decorator"
import VueTypes from "vue-types"
import {Imageset} from "@/plugins/store/modules/imageset"

@Component({})
export default class ItImagesetTags extends Vue {
    @Prop(VueTypes.integer.isRequired) public readonly id: number

    // noinspection JSUnusedGlobalSymbols because v-model uses it
    set selectedTags(value: string[]) {
        this.$store.dispatch("updateImagesetTags", {
            id: this.imageset.id,
            tags: value
        }).then(() => {
            this.$store.dispatch("retrieveAvailableTags")
        })
    }
    get selectedTags(): string[] {
        return this.imageset.tags
    }

    get imageset(): Imageset {
        return this.$store.getters.imagesetById(this.id)
    }

    get availableTags(): string[] {
        return this.$store.state.imagesets.availableTags
    }
}
</script>

<style scoped lang="scss">

</style>
