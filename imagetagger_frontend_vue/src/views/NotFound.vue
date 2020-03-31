<template>
    <div class="not-found__root">
        <h1>Page not found.</h1>
    </div>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import "vue-class-component/hooks"
import {Prop} from "vue-property-decorator"
import VueTypes from "vue-types"
import ItNavbar from "@/components/ItNavbar.vue"

@Component({
    components: {ItNavbar}
})
export default class NotFound extends Vue {
}
</script>

<style scoped lang="scss">

</style>
