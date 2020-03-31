<template>
    <div class="fab-button-subaction-root">
        <button class="mdc-fab mdc-fab--mini mdc-theme--surface">
            <div class="mdc-fab__ripple"/>
            <span class="mdc-fab__icon mdc-theme--primary mdi" :class="`mdi-${icon}`"/>
        </button>
    </div>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import "vue-class-component/hooks"
import {Prop} from "vue-property-decorator"
import VueTypes from "vue-types"

@Component({})
export default class FabButtonSubAction extends Vue {
    @Prop(VueTypes.string.isRequired) public readonly icon: string
}
</script>

<style scoped lang="scss">

</style>
