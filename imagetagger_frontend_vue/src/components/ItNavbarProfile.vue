<template>
    <div>
        <v-menu>
            <template v-slot:activator="{ on }">
                <v-btn icon color="white" v-on="on"><i class="mdi mdi-account"/></v-btn>
            </template>

            <template v-slot:default>
                <v-list>
                    <v-list-item>
                        <router-link :to="{name: 'profile'}">
                            <v-list-item-action>Profile</v-list-item-action>
                        </router-link>
                    </v-list-item>

                    <v-list-item>
                        <router-link :to="{name: 'logout', query: {next: currentUrl}}">
                            <v-list-item-action>Logout</v-list-item-action>
                        </router-link>
                    </v-list-item>
                </v-list>
            </template>
        </v-menu>
    </div>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import "vue-class-component/hooks"
import {Prop} from "vue-property-decorator"
import VueTypes from "vue-types"

@Component({})
export default class ItNavbarProfile extends Vue {
    get currentUrl(): string {
        return this.$route.fullPath
    }
}
</script>

<style scoped lang="scss">

</style>
