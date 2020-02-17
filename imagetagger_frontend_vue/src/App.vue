<template>
    <router-view/>
</template>

<style lang="scss">
    @import "global_style.sccs";
    @import url("https://fonts.googleapis.com/css?family=Roboto:300,400,500");
    @import url("~@mdi/font/css/materialdesignicons.css");

    // Set custom theme to be used by material design components framework
    $mdc-theme-primary: $primary-color;
    $mdc-theme-secondary: $accent-color;
    $mdc-theme-background: $background-color;
    $mdc-theme-surface: $background-color;
    $mdc-theme-error: #FF5722;
    $mdc-theme-text-primary-on-background: $primary-text-color;
    $mdc-theme-text-secondary-on-background: $secondary-text-color;
    $mdc-theme-text-icon-on-background: $primary-color-text;
    $mdc-theme-text-primary-on-light: $primary-text-color;
    $mdc-theme-text-secondary-on-light: $secondary-text-color;

    @import "~material-components-web/material-components-web";

    // Global style fixes
    body {
        margin: 0;
    }
    button.mdc-icon-button {
        padding: 8px;
    }
    .mdc-list-item__icon {
        @extend .mdc-list-item__text;
        margin-right: 10px;
    }
    a:link, a:visited, a:hover, a:active {
        color: inherit;
        text-decoration: inherit;
    }

    h1 {
        @extend .mdc-typography--headline1
    }
    h2 {
        @extend .mdc-typography--headline2
    }
    h3 {
        @extend .mdc-typography--headline3
    }
    h4 {
        @extend .mdc-typography--headline4
    }
    h5 {
        @extend .mdc-typography--headline5
    }
    h6 {
        @extend .mdc-typography--headline6
    }

    // Cursors
    .cursor-alias {cursor: alias;}
    .cursor-all-scroll {cursor: all-scroll;}
    .cursor-auto {cursor: auto;}
    .cursor-cell {cursor: cell;}
    .cursor-context-menu {cursor: context-menu;}
    .cursor-col-resize {cursor: col-resize;}
    .cursor-copy {cursor: copy;}
    .cursor-crosshair {cursor: crosshair;}
    .cursor-default {cursor: default;}
    .cursor-e-resize {cursor: e-resize;}
    .cursor-ew-resize {cursor: ew-resize;}
    .cursor-grab {cursor: grab;}
    .cursor-grabbing {cursor: grabbing;}
    .cursor-help {cursor: help;}
    .cursor-move {cursor: move;}
    .cursor-n-resize {cursor: n-resize;}
    .cursor-ne-resize {cursor: ne-resize;}
    .cursor-nesw-resize {cursor: nesw-resize;}
    .cursor-ns-resize {cursor: ns-resize;}
    .cursor-nw-resize {cursor: nw-resize;}
    .cursor-nwse-resize {cursor: nwse-resize;}
    .cursor-no-drop {cursor: no-drop;}
    .cursor-none {cursor: none;}
    .cursor-not-allowed {cursor: not-allowed;}
    .cursor-pointer {cursor: pointer;}
    .cursor-progress {cursor: progress;}
    .cursor-row-resize {cursor: row-resize;}
    .cursor-s-resize {cursor: s-resize;}
    .cursor-se-resize {cursor: se-resize;}
    .cursor-sw-resize {cursor: sw-resize;}
    .cursor-text {cursor: text;}
    .cursor-w-resize {cursor: w-resize;}
    .cursor-wait {cursor: wait;}
    .cursor-zoom-in {cursor: zoom-in;}
    .cursor-zoom-out {cursor: zoom-out;}
</style>
