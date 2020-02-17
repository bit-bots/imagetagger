<template>
    <div class="imageset-details-root">
        <navbar>
            <navbar-profile/>
        </navbar>

        <p>Hello there.</p>
        <p>This view is not yet implemented</p>
    </div>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import Navbar from "@/components/Navbar.vue";
import NavbarProfile from "@/components/NavbarProfile.vue";

@Component({
    components: {NavbarProfile, Navbar}
})
export default class ImagesetDetails extends Vue {

}
</script>

<style scoped lang="scss">

</style>
