<template>
    <div class="imagetagger-card--root mdc-card" :class="outlined ? 'mdc-card--outlined' : ''">
        <!-- Card Title (only conditionally rendered here) -->
        <div v-if="titleOverMedia" class="card-header">
            <h2 class="mdc-typography mdc-typography--headline6">
                <slot name="title"/>
            </h2>
            <h3 class="mdc-typography mdc-typography--subtitle2">
                <slot name="subtitle"/>
            </h3>
        </div>

        <!-- Card primary -->
        <div class="card-primary">
            <div class="mdc-card__media">
                <slot name="media"/>
            </div>
            <div v-if="!titleOverMedia">
                <h2 class="mdc-typography mdc-typography--headline6">
                    <slot name="title"/>
                </h2>
                <h3 class="mdc-typography mdc-typography--subtitle2">
                    <slot name="subtitle"/>
                </h3>
            </div>
            <div class="mdc-typography mdc-typography--body2">
                <slot name="body"/>
            </div>
        </div>

        <!-- Card secondary actions -->
        <div class="mdc-card__actions">
            <div class="mdc-card__action-buttons">
                <slot name="action-buttons"/>
            </div>
            <div class="mdc-card__action-icons">
                <slot name="action-icons"/>
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

@Component({})
export default class ImagetaggerCard extends Vue {
    @Prop(VueTypes.bool.def(false)) readonly outlined: boolean
    @Prop(VueTypes.bool.def(false)) readonly titleOverMedia: boolean
}
</script>

<style scoped lang="scss">
    @import "../../../node_modules/@material/card/mdc-card";

    .mdc-card__media {
        text-align: center;
    }

    .mdc-card__action-buttons > * {
        margin-right: 10px;
    }

    .mdc-card__action-icons > * {
        margin-right: 8px;
    }

    .card-primary,.card-header {
        padding: 0 8px;
    }
</style>
