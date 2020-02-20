<template>
    <div class="imageset-details-root">
        <navbar :initial-active-tab="1">
            <navbar-profile/>
            <template v-slot:tabs>
                <navbar-tab routeName="imagesetDetails">Overview</navbar-tab>
                <navbar-tab routeName="imagesetImages">Images</navbar-tab>
            </template>
        </navbar>

        <router-view/>
    </div>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import Navbar from "@/components/Navbar.vue"
import NavbarProfile from "@/components/NavbarProfile.vue"
import NavbarTab from "@/components/NavbarTab.vue"

@Component({
    components: {NavbarTab, NavbarProfile, Navbar}
})
export default class Imageset extends Vue {

}
</script>

<style scoped lang="scss">

</style>
