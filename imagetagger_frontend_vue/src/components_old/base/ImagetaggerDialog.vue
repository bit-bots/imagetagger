<template>
    <div class="imagetagger-dialog--root mdc-dialog" ref="elDialog">
        <div class="mdc-dialog__container">
            <div class="mdc-dialog__surface"
                role="dialog"
                aria-modal="true">
                <h2 class="mdc-dialog__title">
                    <slot name="title">No Title</slot>
                </h2>
                <div class="mdc-dialog__content">
                    <slot>No content</slot>
                </div>
                <!-- There are special dialog footer styles for actions but I don't need them yet -->
            </div>
        </div>
        <div class="mdc-dialog__scrim"/>
    </div>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import "vue-class-component/hooks"
import {Prop, Watch} from "vue-property-decorator"
import VueTypes from "vue-types"
import {MDCDialog} from "@material/dialog/component"

@Component({})
export default class ImagetaggerDialog extends Vue {
    @Prop(VueTypes.bool.def(false)) readonly open: boolean
    private mdcDialog: MDCDialog

    mounted(): void {
        this.mdcDialog = new MDCDialog(this.$refs.elDialog as Element)
        this.mdcDialog.listen("MDCDialog:closed", () => this.$emit("close"))
    }

    beforeDestroy(): void {
        this.mdcDialog.destroy()
    }

    @Watch("open")
    onOpenChange(newVal: boolean, oldVal: boolean): void {
        if (newVal)
            this.mdcDialog.open()
        else
            this.mdcDialog.close()
    }
}
</script>

<style scoped lang="scss">

</style>
