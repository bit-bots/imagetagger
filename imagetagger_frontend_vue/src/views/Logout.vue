<template>
    <v-container>
        <v-row align="center" justify="center">
            <v-progress-circular indeterminate color="primary"/>
        </v-row>
    </v-container>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import "vue-class-component/hooks"
import {Prop} from "vue-property-decorator"
import VueTypes from "vue-types"

@Component({})
export default class Logout extends Vue {
    mounted(): void {
        this.$store.commit("logout")
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
