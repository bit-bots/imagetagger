<template>
    <div class="fab-root">
        <!-- Expanding button actions -->
        <div v-if="hasSubActions" class="sub-action-container">
            <slot/>
        </div>

        <!-- Actual button -->
        <button @click="onClick()"
                class="mdc-fab" aria-label="Downloads and Exports">
            <div class="mdc-fab__ripple"/>
            <span class="mdc-fab__icon mdi" :class="`mdi-${icon}`"/>
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
export default class FabButton extends Vue {
    @Prop(VueTypes.string.isRequired) public readonly icon: string

    public onClick(): void {

    }

    get hasSubActions(): boolean {
        return Boolean(this.$slots.default && this.$slots.default[0])
    }
}
</script>

<style scoped lang="scss">
    .fab-root {
        .sub-action-container {
            margin-bottom: 25px;

            .fab-button-subaction-root {
                margin-bottom: 13px;
            }
        }
    }
</style>
