<template>
    <div>
        <navbar>
            <navbar-search/>
        </navbar>

        <div class="mdc-layout-grid">
            <div class="mdc-layout-grid__inner">
                <div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-6">
                    test
                </div>
            </div>
        </div>
    </div>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import Navbar from "@/components/Navbar.vue"
import NavbarSearch from "@/components/NavbarSearch.vue"

@Component({
    components: {NavbarSearch, Navbar}
})
export default class Dashboard extends Vue {
}
</script>

<style lang="scss">
</style>
