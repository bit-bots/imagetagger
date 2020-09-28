<!--
Display all Images which are contained in a given Imageset in a list.
It can optionally show context actions like "view" or "delete" on one image item.
 -->

<template>
<v-simple-table>
    <template v-slot:default>
        <tbody>
        <router-link tag="tr" v-for="image in images" :key="image.id"
                     :to="{ name: 'imageView', params: {imagesetId, imageId: image.id} }"
                     class="image-link">
            <td>{{ image.name }}</td>
            <td>{{ image.annotations.length }} Annotations</td>
        </router-link>
        </tbody>
    </template>
</v-simple-table>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import "vue-class-component/hooks"
import {Prop} from "vue-property-decorator"
import VueTypes from "vue-types"
import {Image} from "@/plugins/store/modules/image"

// :to="{ name: 'imageView', params: {imagesetId, imageId: image.id} }"

@Component({})
export default class ItImagesetImageList extends Vue {
    @Prop(VueTypes.integer.isRequired) public readonly imagesetId: number

    get images(): Image[] {
        return this.$store.getters.imagesFromImageset(this.imagesetId)
    }
}
</script>

<style scoped lang="scss">
.image-link {
  cursor: pointer;
}
</style>
