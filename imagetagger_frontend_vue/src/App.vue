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
</style>
