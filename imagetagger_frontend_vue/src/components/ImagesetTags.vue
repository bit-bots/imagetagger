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

        <form @submit.prevent="addTag()">
            <div class="mdc-text-field mdc-text-field--outlined mdc-text-field--no-label chip-text-field">
                <input v-model="newTagName" aria-label="New Tag" placeholder="New Tag"
                       type="text" id="new-tag--name" class="mdc-text-field__input">
                <div class="mdc-notched-outline">
                    <div class="mdc-notched-outline__leading"/>
                    <div class="mdc-notched-outline__trailing"/>
                </div>
            </div>
            <transition name="fade">
                <button v-if="newTagName !== ''" class="mdc-button mdc-button--raised">
                    <span class="mdc-button__label">Add</span>
                </button>
            </transition>
        </form>
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
    newTagName: string = ""

    get imageset(): Imageset {
        return this.$store.getters.imagesetById(this.imagesetId)
    }

    removeTag(tag: string): void {
        this.$store.dispatch("updateImagesetTags", {
            imageset: this.imageset,
            tags: this.imageset.tags.filter(i => i !== tag)
        }).catch(console.error)
    }

    addTag(): void {
        this.$store.dispatch("updateImagesetTags", {
            imageset: this.imageset,
            tags: this.imageset.tags.concat([this.newTagName])
        })
            .then(() => this.newTagName = "")
            .catch(console.error)
    }
}
</script>

<style scoped lang="scss">
    @import "src/global_style.sccs";

    .mdc-text-field.chip-text-field {
        // values taken from mdc-chip classes
        $border-radius: 16px;
        margin: 4px 4px 4px 40px;
        height: 32px;
        padding: 0 12px;

        .mdc-notched-outline__leading {
            border-radius: $border-radius 0 0 $border-radius;
        }
        .mdc-notched-outline__trailing {
            border-radius: 0 $border-radius $border-radius 0;
        }

        input {
            padding: 0;
            width: unset;
        }
    }

    @include anim-fade()

</style>
