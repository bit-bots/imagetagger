<template>
    <div class="imagetagger-dropdown-root">
        <label :for="inputId">{{ label }}</label>
        <!--suppress HtmlFormInputWithoutLabel because label is dynamically bound by Vue -->
        <select :id="inputId" ref="elSelect">
            <option v-for="choice of choices" :key="choice" :value="choice" @click="onSelect(choice)">
                {{ choice }}
            </option>
        </select>
    </div>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import "vue-class-component/hooks"
import {Prop} from "vue-property-decorator"
import VueTypes from "vue-types"

@Component({})
export default class ImagetaggerDropdown extends Vue {
    @Prop(VueTypes.arrayOf(VueTypes.string).isRequired) readonly choices: string[]
    @Prop(VueTypes.string.isRequired) readonly label: string

    inputId: string = ""

    created(): void {
        this.inputId = Math.random().toString()
    }

    mounted(): void {
        this.$emit("input", (this.$refs.elSelect as HTMLSelectElement).value)
    }

    updated(): void {
        this.$emit("input", (this.$refs.elSelect as HTMLSelectElement).value)
    }

    onSelect(choice: string): void {
        this.$emit("input", choice)
    }
}
</script>

<style scoped lang="scss">
    @import "src/global_style.sccs";

    .imagetagger-dropdown-root {
        margin-top: 8px;

        select {
            margin-left: 8px;
            background-color: $background-color;
            border-radius: 4px;
            border: rgba(0, 0, 0, 0.38) solid 1px;
        }
    }
</style>
