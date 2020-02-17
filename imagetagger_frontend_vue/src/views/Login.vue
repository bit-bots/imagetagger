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
                <form v-on:submit.prevent="onSubmit">
                    <!-- Username -->
                    <div class="text-field-wrap">
                        <div class="mdc-text-field mdc-text-field--outlined" ref="elUsername">
                            <input type="text" id="username" class="mdc-text-field__input"
                                    v-model="username">
                            <div class="mdc-notched-outline">
                                <div class="mdc-notched-outline__leading"/>
                                <div class="mdc-notched-outline__notch">
                                    <label class="mdc-floating-label" for="username">Username</label>
                                </div>
                                <div class="mdc-notched-outline__trailing"/>
                            </div>
                        </div>
                    </div>

                    <!-- Password -->
                    <div class="text-field-wrap">
                        <div class="mdc-text-field mdc-text-field--outlined" ref="elPassword">
                            <input type="password" id="password" class="mdc-text-field__input"
                                    v-model="password">
                            <div class="mdc-notched-outline">
                                <div class="mdc-notched-outline__leading"/>
                                <div class="mdc-notched-outline__notch">
                                    <label class="mdc-floating-label" for="password">Password</label>
                                </div>
                                <div class="mdc-notched-outline__trailing"/>
                            </div>
                        </div>
                    </div>

                    <button class="mdc-button mdc-button--outlined mdc-card__action mdc-card__action--button"
                            :disabled="!isFormValid"
                            type="submit">
                        <div class="mdc-button__ripple"/>
                        <span class="mdc-button__label">Login</span>
                    </button>
                </form>
            </div>
        </div>
    </div>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import Navbar from "@components/Navbar.vue"
import {MDCTextField} from "@material/textfield/component"

@Component({
    components: {Navbar}
})
export default class Login extends Vue {
    username = ""
    password = ""
    rememberMe = true
    loginError = ""

    private _mdcTextUsername: MDCTextField
    private _mdcTextPassword: MDCTextField

    mounted() {
        this._mdcTextUsername = new MDCTextField(this.$refs.elUsername as Element)
        this._mdcTextPassword = new MDCTextField(this.$refs.elPassword as Element)
    }

    beforeDestroy() {
        this._mdcTextUsername.destroy()
        this._mdcTextPassword.destroy()
    }

    onSubmit(): void {
        this.$store.dispatch("login", {
            username: this.username,
            password: this.password
        }).then(() => {
            this.loginError = ""
            this.navigateNext()
        }).catch(reason => {
            this.loginError = reason
        })
    }

    navigateNext(): void {
        this.$router.push(this.$store.state.auth.nextRoute)
    }

    get isFormValid(): boolean {
        return this.username != "" && this.password != ""
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
