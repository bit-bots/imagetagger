<template>
    <div class="imagetagger-text-field-root">
        <div class="mdc-text-field" ref="elTextField"
             :class="outlined ? 'mdc-text-field--outlined': ''">
            <!--suppress HtmlFormInputWithoutLabel because label is dynamically bound by Vue -->
            <input :id="inputId"
                   class="mdc-text-field__input"
                   :type="type"
                   :value="value"
                   @input="$emit('input', $event.target.value)">
            <div class="mdc-line-ripple" v-if="!outlined"/>
            <div :class="outlined ? 'mdc-notched-outline' : ''">
                <div class="mdc-notched-outline__leading" v-if="outlined"/>
                <div :class="outlined ? 'mdc-notched-outline__notch' : ''">
                    <label class="mdc-floating-label" :for="inputId">{{ label }}</label>
                </div>
                <div class="mdc-notched-outline__trailing" v-if="outlined"/>
            </div>
        </div>
    </div>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import "vue-class-component/hooks"
import {Prop} from "vue-property-decorator"
import VueTypes from "vue-types"
import {MDCTextField} from "@material/textfield/component"

@Component({})
export default class ImagetaggerTextField extends Vue {
    @Prop(VueTypes.string.def("text").validate(s => ["text", "password"].includes(s))) readonly type: string
    @Prop(VueTypes.string.isRequired) readonly label: string
    @Prop(VueTypes.bool.def(false)) readonly outlined: boolean
    @Prop(VueTypes.string) readonly value: string

    inputId: string
    mdcTextField: MDCTextField

    created(): void {
        this.inputId = Math.random().toString()
    }

    mounted(): void {
        this.mdcTextField = new MDCTextField(this.$refs.elTextField as Element)
    }

    beforeDestroy(): void {
        this.mdcTextField.destroy()
    }
}
</script>

<style scoped lang="scss">
    .imagetagger-text-field-root {
        padding-top: 8px;
        display: inline-block;
    }
</style>
