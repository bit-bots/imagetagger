<template>
    <div class="divider"/>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import VueTypes from "vue-types"

@Component({})
export default class HorizontalDivider extends Vue {
}
</script>

<style scoped lang="scss">
    @import "../global_style.sccs";

    .divider {
        height: 1px;
        background-color: $divider-color;
    }
</style>
