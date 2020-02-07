<template>
    <router-view/>
</template>

<style lang="scss">
    @import url("https://fonts.googleapis.com/css?family=Roboto:300,400,500");
    @import url("https://fonts.googleapis.com/icon?family=Material+Icons");

    $primary-color-dark: #455A64;
    $primary-color: #607D8B;
    $primary-color-light: #CFD8DC;
    $primary-color-text: #FFFFFF;
    $accent-color: #009688;
    $primary-text-color: #212121;
    $secondary-text-color: #757575;
    $divider-color: #BDBDBD;
    $background-color: #FFFFFF;

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
</style>
