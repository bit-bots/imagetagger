<template>
<v-form @submit.prevent="onSubmit" ref="form">
    <v-alert v-if="login_error !== ''" color="error">
        {{ login_error }}
    </v-alert>

    <v-text-field label="Username" name="username" prepend-icon="mdi-account" type="text"
                  :rules="[validateUsername]" v-model="username"/>
    <v-text-field label="Password" name="password" prepend-icon="mdi-lock" type="password"
                  :rules="[validatePassword]" v-model="password"/>
    <div class="d-flex flex-row align-baseline justify-space-between">
        <v-switch label="Remember me" name="remember" v-model="remember_me"/>
        <div>
            <slot>
                <v-btn color="primary" type="submit">Login</v-btn>
            </slot>
        </div>
    </div>
</v-form>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import "vue-class-component/hooks"
import {VFormType} from "@/plugins/vuetify/extraTypes";

@Component({})
export default class ItLoginForm extends Vue {
    username = ""
    password = ""
    remember_me = true     // TODO implement remember_me for login
    login_error = ""

    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    onSubmit(e: never): void {
        if ((this.$refs.form as VFormType).validate()) {
            this.$store.dispatch("login", {
                username: this.username,
                password: this.password
            }).then(() => {
                this.login_error = ""
                this.$emit("loggedIn")
            }).catch(reason => {
                this.login_error = reason
            })
        }
    }

    validateUsername(value: string): boolean | string {
        if (value !== "")
            return true
        else
            return "Username cannot be empty"
    }

    validatePassword(value: string): boolean | string {
        if (value !== "")
            return true
        else
            return "Password cannot be empty"
    }
}
</script>

<style scoped lang="scss">
</style>
