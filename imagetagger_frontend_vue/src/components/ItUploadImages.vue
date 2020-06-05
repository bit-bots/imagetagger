<template>
    <v-form @submit.prevent="onSubmit">
        <p>
            By uploading images to this tool you accept that the images get published under
            creative commons license and confirm that you have the permission to do so.
        </p>
        <p>
            Upload images as single files or as zip file with the images in its root directory (recommended).
        </p>
        <v-file-input label="Images or zip" multiple counter show-size accept=".zip,image/*" v-model="files"/>
        <div class="d-flex flex-row justify-end mt-4">
            <v-btn color="primary" type="submit" disabled>Upload</v-btn>
        </div>
    </v-form>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import "vue-class-component/hooks"
import {Prop} from "vue-property-decorator"
import VueTypes from "vue-types"

@Component({})
export default class ItUploadImages extends Vue {
    @Prop(VueTypes.integer.isRequired) public readonly imagesetId: number

    files: File[] = []

    onSubmit(): void {
        this.$store.dispatch("uploadImages", {imageset: this.imagesetId, files: this.files})
            .finally(console.log)
    }
}
</script>

<style scoped lang="scss">

</style>
