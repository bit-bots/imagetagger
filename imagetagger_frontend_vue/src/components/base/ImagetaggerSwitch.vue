<template>
    <div class="imagetagger-switch-root">
        <div class="mdc-switch" ref="elSwitch"
             :class="disabled ? 'mdc-switch--disabled' : ''">
            <div class="mdc-switch__track"/>
            <div class="mdc-switch__thumb-underlay">
                <div class="mdc-switch__thumb"/>
                <!--suppress HtmlFormInputWithoutLabel because label is dynamically bound by Vue -->
                <input type="checkbox" :id="inputId" class="mdc-switch__native-control"
                       role="switch" aria-checked="false" :disabled="disabled"
                       :checked="value"
                       @input="$emit('input', $event.target.checked)">
            </div>
        </div>
        <label :for="inputId">{{ label }}</label>
    </div>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import "vue-class-component/hooks"
import {Prop} from "vue-property-decorator"
import VueTypes from "vue-types"
import {MDCSwitch} from "@material/switch/component"

@Component({})
export default class ImagetaggerSwitch extends Vue {
    @Prop(VueTypes.string.isRequired) readonly label: string
    @Prop(VueTypes.bool.def(false)) readonly disabled: boolean
    @Prop(VueTypes.bool.def(false)) readonly value: boolean

    inputId: string
    mdcSwitch: MDCSwitch

    created() {
        this.inputId = Math.random().toString()
    }

    mounted(): void {
        this.mdcSwitch = new MDCSwitch(this.$refs.elSwitch as Element)
    }

    beforeDestroy(): void {
        this.mdcSwitch.destroy()
    }
}
</script>

<style scoped lang="scss">
    .imagetagger-switch-root {
        padding: 14px 6px;

        & label {
            margin-left: 12px;
        }
    }
</style>
