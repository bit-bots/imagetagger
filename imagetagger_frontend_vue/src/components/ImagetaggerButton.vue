<template>
    <button class="button-root mdc-button" :class="rootClasses" :disabled="disabled" @click="$emit('click')">
        <span class="mdc-button__ripple"/>
        <slot>Undefined</slot>
    </button>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import "vue-class-component/hooks"
import {Prop} from "vue-property-decorator"
import VueTypes from "vue-types"

@Component({})
export default class ImagetaggerButton extends Vue {
    @Prop(VueTypes.string.def("raised")
        .validate(value => ["raised", "text", "outlined", "unelevated"].includes(value)))
    readonly variant: string
    @Prop(VueTypes.bool.def(false)) readonly disabled: boolean

    get rootClasses(): string {
        switch (this.variant) {
        case "raised": return "mdc-button--raised"
        case "text": return ""
        case "outlined": return "mdc-button--outlined"
        case "unelevated": return "mdc-button--unelevated"
        }
    }
}
</script>

<style scoped lang="scss">

</style>
