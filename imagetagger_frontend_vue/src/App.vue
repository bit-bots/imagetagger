<template>
    <v-app>
        <it-navbar/>
        <v-main>
            <router-view/>
        </v-main>
    </v-app>
</template>


<script>
import Vue from "vue"
import Component from "vue-class-component"
import ItNavbar from "@/components/ItNavbar"

@Component({
    components: {ItNavbar}
})
export default class App extends Vue {}
</script>


<style lang="scss">
    @use "src/styles/colors";
    @use "src/styles/color_classes";
    @import "~vuetify/src/styles/main";
    @import "~@mdi/font/css/materialdesignicons.css";
    @import "styles/global_style";

    // Global style fixes
    body {
        margin: 0;
    }
</style>
