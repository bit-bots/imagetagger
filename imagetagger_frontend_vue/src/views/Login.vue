<template>
    <div>
        <Navbar/>

        <div class="mdc-card mdc-elevation--z6">
            <div class="mdc-card__primary">
                <h2 class="mdc-typography--headline6">Login</h2>
                <h3 class="mdc-typography--subtitle2">You need to login to access this part of ImageTagger</h3>
            </div>

            <div class="mdc-card__primary" v-if="loginError">
                <p class="login-error mdc-theme--error">{{ loginError }}</p>
            </div>

            <!-- Main login mask -->
            <div class="mdc-card__primary">
                <login-form @loggedIn="navigateNext()"/>
            </div>
        </div>
    </div>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import Navbar from "@components/Navbar.vue"
import {MDCTextField} from "@material/textfield/component"
import LoginForm from "@/components/LoginForm.vue"

@Component({
    components: {Navbar, LoginForm}
})
export default class Login extends Vue {
    username = ""
    password = ""
    rememberMe = true

    navigateNext(): void {
        this.$router.push(this.$store.state.auth.nextRoute)
    }
}
</script>

<style scoped lang="scss">
    @import "src/global_style.sccs";

    .mdc-card {
        margin: 3% auto auto;
        width: 30%;
        padding: 10px 20px;
    }

    .mdc-card .mdc-typography--subtitle2 {
        margin-top: 0;
        opacity: 0.54;
    }

    .align-horizontal-center > div {
        margin: 4px 0;

    }

    .text-field-wrap {
        margin: 4px 0;
    }

    form {
        .mdc-text-field {
        }

        .mdc-text-field__input {
            padding: 6px 14px 8px;
        }

        .mdc-card__primary {
            padding: 1rem;
        }
    }
</style>
