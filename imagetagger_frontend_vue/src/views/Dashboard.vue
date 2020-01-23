<template>
    <div>
        <Navbar/>

        <div class="container-fluid">
            <div class="row">
                <div class="col col-12"><h1>Dashboard</h1></div>
            </div>

            <div class="row">
                <div class="col col-8">
                    <Card class="my-2" title="Imagesets" :tabs="tabs" :active-tab-name="activeImagesetTab">
                        <div>Public content</div>
                    </Card>
                </div>

                <div class="col col-4">
                    <div class="row">
                        <div class="container-fluid">
                            <Card class="my-2" title="Create Team">
                                <div class="alert alert-warning">Create Team is not yet implemented</div>
                            </Card>
                        </div>
                    </div>

                    <div class="row">
                        <div class="container-fluid">
                            <Card class="my-2" title="Create Imageset">
                                <div class="alert alert-warning">Create Imageset is not yet implemented</div>
                            </Card>
                        </div>
                    </div>

                    <div class="row">
                        <div class="container-fluid">
                            <Card class="my-2" title="Imagetagger Stats">
                                <div class="alert alert-warning">Create Team is not yet implemented</div>
                            </Card>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script lang="ts">
import Vue from "vue"
import Navbar from "@/components/Navbar.vue"
import Card from "@/components/Card.vue"
import {CardTabDefinition} from "@/types"

export default Vue.extend({
    components: {Card, Navbar},
    computed: {
        activeImagesetTab: function (): string {
            return this.$route.params.filter
        },
        tabs: function (): CardTabDefinition[] {
            return [
                new CardTabDefinition("All", {name: "dashboard", params: {filter: "all"}}),
                new CardTabDefinition("Public", {name: "dashboard", params: {filter: "public"}}),
            ]
        }
    }
})
</script>

<style lang="scss">
</style>
