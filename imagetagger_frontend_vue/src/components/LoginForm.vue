<template>
    <div class="login--root">

            <div v-if="loginError">
                <p class="login-error mdc-theme--error">{{ loginError }}</p>
            </div>

            <!-- Main login mask -->
            <form v-on:submit.prevent="onSubmit">
                <!-- Username -->
                <div class="text-field-wrap">
                    <imagetagger-text-field type="text" label="Username" outlined v-model="username"/>
                </div>

                <!-- Password -->
                <div class="text-field-wrap">
                    <imagetagger-text-field type="password" label="Password" outlined v-model="password"/>
                </div>

                <button class="mdc-button mdc-button--outlined mdc-card__action mdc-card__action--button"
                        :disabled="!isFormValid"
                        type="submit">
                    <div class="mdc-button__ripple"/>
                    <span class="mdc-button__label">Login</span>
                </button>
            </form>
        </div>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import Navbar from "@components/Navbar.vue"
import ImagetaggerTextField from "@/components/base/ImagetaggerTextField.vue"

@Component({
    components: {ImagetaggerTextField, Navbar}
})
export default class LoginForm extends Vue {
    username = ""
    password = ""
    rememberMe = true
    loginError = ""

    onSubmit(): void {
        this.$store.dispatch("login", {
            username: this.username,
            password: this.password
        }).then(() => {
            this.loginError = ""
            this.$emit("loggedIn")
        }).catch(reason => {
            this.loginError = reason
        })
    }

    get isFormValid(): boolean {
        return this.username != "" && this.password != ""
    }
}
</script>

<style scoped lang="scss">
    @import "../styles/global_style";

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
