<template>
    <div>
        <Navbar/>

        <div class="container-fluid">
            <div class="row">
                <div class="col-4 offset-4">
                    <div class="card my-4">

                        <!-- Content of login card -->
                        <div class="card-body">
                            <h5 class="card-title">Login</h5>
                            <h6 class="card-subtitle text-muted mb-4">
                                You need to login to access this part of Imagetagger
                            </h6>

                            <!-- Error display -->
                            <div v-if="loginError" class="alert alert-danger" role="alert">{{ loginError }}</div>

                            <form v-on:submit.prevent="onSubmit">
                                <!-- Username -->
                                <div class="form-group">
                                    <label for="inp-username">Username</label>
                                    <input id="inp-username" class="form-control"
                                           type="text" placeholder="Enter your username"
                                           v-model="username">
                                </div>

                                <!-- Password -->
                                <div class="form-group">
                                    <label for="inp-password">Password</label>
                                    <input id="inp-password" class="form-control"
                                           type="password" placeholder="Password"
                                           v-model="password">
                                </div>

                                <!-- Remember me -->
                                <div class="form-group form-check float-right">
                                    <input class="form-check-input" id="inp-remember" type="checkbox"
                                           v-model="rememberMe">
                                    <label class="form-check-label" for="inp-remember">Remember me</label>
                                </div>

                                <!-- Submit -->
                                <button class="btn btn-primary" :disabled="!isFormValid">
                                    Login
                                </button>
                            </form>
                        </div>

                    </div>
                </div>
            </div>
        </div>

    </div>
</template>

<script lang="ts">
import Vue from "vue"
import Navbar from "@components/Navbar.vue"

export default Vue.extend({
    name: "Login",
    components: {Navbar},
    data: function () {
        return {
            username: "",
            password: "",
            rememberMe: true,
            loginError: ""
        }
    },
    methods: {
        onSubmit() {
            this.$store.dispatch("login", {
                username: this.username,
                password: this.password
            }).then(() => {
                this.loginError = ""
                this.navigateNext()
            }).catch(reason => {
                this.loginError = reason
            })
        },
        navigateNext() {
            console.log("success")
            this.$router.push(this.$store.state.auth.nextRoute)
        }
    },
    computed: {
        isFormValid: function(): boolean {
            return this.username != "" && this.password != ""
        }
    }
})
</script>

<style scoped lang="scss">
    #progress-wrapper {
        margin-top: 3%;
        width: 100%;
    }
</style>
