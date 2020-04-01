<template>
    <v-container>
        <v-row align="center" justify="center">
            <v-col cols="12" md="4" sm="8">
                <v-card elevation="12">
                    <v-toolbar color="primary" flat>
                        <v-toolbar-title class="theme-white-fg">Login</v-toolbar-title>
                    </v-toolbar>
                    <v-card-text>
                        <it-login-form @loggedIn="onLoggedIn"/>
                    </v-card-text>
                </v-card>
            </v-col>
        </v-row>
    </v-container>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import "vue-class-component/hooks"
import {Prop} from "vue-property-decorator"
import VueTypes from "vue-types"
import ItLoginForm from "@/components/ItLoginForm.vue"

@Component({
    components: {ItLoginForm}
})
export default class Login extends Vue {
    onLoggedIn(): void {
        this.$router.push(this.nextUrl)
    }

    get nextUrl(): string {
        const queryParam = this.$route.query.next
        if (queryParam && typeof queryParam === "string")
            return queryParam as string
        else if (queryParam && typeof queryParam === "object" && queryParam.length > 0)
            return queryParam[0]
        else
            return "/"
    }
}
</script>

<style scoped lang="scss">

</style>
