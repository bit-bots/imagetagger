<template>
<v-row>
    <!-- Upload new Images -->
    <v-col cols="5">
        <v-card>
            <v-card-title>Upload Images</v-card-title>
            <v-card-text>
                <it-upload-images :imageset-id="+$route.params.id"/>
            </v-card-text>
        </v-card>
    </v-col>

    <v-col cols="7">
        <v-card>
            <v-card-title>List of Images</v-card-title>
            <v-card-text>
                <it-imageset-image-list :imageset-id="+$route.params.id"/>
            </v-card-text>
        </v-card>
    </v-col>
</v-row>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import "vue-class-component/hooks"
import ItUploadImages from "@/components/ItUploadImages.vue"
import ItImagesetImageList from "@/components/ItImagesetImageList.vue"

@Component({
    components: {ItImagesetImageList, ItUploadImages}
})
export default class ImagesetImages extends Vue {
}
</script>

<style scoped lang="scss">

</style>
