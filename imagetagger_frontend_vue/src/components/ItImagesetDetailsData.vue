<template> <!-- TODO Make editable by double clicking in table field -->
    <v-simple-table class="small-first-td">
        <tbody>
        <tr>
            <td>Name</td>
            <td>{{ imageset.name }}</td>
        </tr>
        <tr>
            <td>Description</td>
            <td v-if="imageset.description">{{ imageset.description }}</td>
            <td v-else class="font-italic font-weight-light">not set</td>
        </tr>
        <tr>
            <td>Tags</td>
            <td><it-imageset-tags :id="id"/></td>
        </tr>
        <tr>
            <td>Location</td>
            <td v-if="imageset.location">{{ imageset.location }}</td>
            <td v-else class="font-italic font-weight-light">not set</td>
        </tr>
        </tbody>
    </v-simple-table>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import "vue-class-component/hooks"
import {Prop} from "vue-property-decorator"
import VueTypes from "vue-types"
import {Imageset} from "@/plugins/store/modules/imageset"
import ItImagesetTags from "@/components/ItImagesetTags.vue"

@Component({
    components: {ItImagesetTags}
})
export default class ItImagesetDetailsData extends Vue {
    @Prop(VueTypes.integer.isRequired) public readonly id: number

    get imageset(): Imageset {
        return this.$store.getters.imagesetById(this.id)
    }
}
</script>

<style scoped lang="scss">
    .small-first-td td:nth-of-type(1) {
        width: 48px;
    }
</style>
