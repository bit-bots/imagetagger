<template>
    <div class="welcome-new-imagetagger--root">
        <navbar class="space-after">
            <navbar-profile/>
        </navbar>

        <!-- Modals (multiple because that's simpler) -->
        <imagetagger-dialog :open="isLoginDialogOpen" @close="isLoginDialogOpen = false">
            <template v-slot:title>Login</template>
            <template v-slot:default>
                <login-form @loggedIn="onLogin()"/>
            </template>
        </imagetagger-dialog>
        <imagetagger-dialog :open="isCreateTeamDialogOpen" @close="isCreateTeamDialogOpen = false">
            <template v-slot:title>Create a Team</template>
            <template v-slot:default>
                <create-team/>
            </template>
        </imagetagger-dialog>

        <div class="centered">
            <h2>Welcome to your new ImageTagger</h2>
            <p>bla bla bla</p>
            <p>this is an introduction to ImageTagger</p> <!-- TODO Write imagetagger introduction -->

            <div class="steps-container">
                <!-- Create user -->
                <imagetagger-card :title-over-media="true">
                    <template v-slot:title>
                        <span class="mdc-theme--text-disabled-on-light">1. </span>
                        <span :class="isCreateUserActive ? 'mdc-theme--primary' : 'mdc-theme--text-disabled-on-light'">
                            Create a User
                        </span>
                    </template>
                    <template v-slot:media>
                        <i class="mdi mdi-account-plus action-icon"
                           :class="isCreateUserActive ? 'mdc-theme--secondary' : 'mdc-theme--text-disabled-on-light'"/>
                    </template>
                    <template v-slot:body v-if="isCreateUserActive">
                        <p>
                            First you need to create a new user with admin access.<br>
                            This user will be able to manage annotation types and change global settings of the
                            Imagetagger instance.
                        </p>
                        <p>
                            Do so by running the following command and answering its prompts:
                        </p>
                        <p class="text-box mdc-theme--primary-bg mdc-theme--on-primary">
                            &lt;imagetagger-folder&gt;$ ./manage.py createsuperuser
                        </p>
                    </template>
                    <template v-slot:action-buttons v-if="isCreateUserActive">
                        <router-link :to="{name: 'welcomeNewImagetagger', params: {step: 2}}">
                            <imagetagger-button :disabled="!isCreateUserActive">Done</imagetagger-button>
                        </router-link>
                        <a href="https://docs.djangoproject.com/en/3.0/ref/django-admin/#createsuperuser"
                           target="_blank">
                            <imagetagger-button :disabled="!isCreateUserActive">Explain</imagetagger-button>
                        </a>
                    </template>
                </imagetagger-card>

                <!-- Login -->
                <imagetagger-card :title-over-media="true">
                    <template v-slot:title>
                        <span class="mdc-theme--text-disabled-on-light">2. </span>
                        <span :class="isLoginActive ? 'mdc-theme--primary' : 'mdc-theme--text-disabled-on-light'">
                            Login with that user
                        </span>
                    </template>
                    <template v-slot:media>
                        <i class="mdi mdi-account action-icon"
                           :class="isLoginActive ? 'mdc-theme--secondary' : 'mdc-theme--text-disabled-on-light'"/>
                    </template>
                    <template v-slot:body v-if="isLoginActive">
                        <p>
                            Now that a you have created a user, it is time to log in.
                        </p>
                    </template>
                    <template v-slot:action-buttons v-if="isLoginActive">
                        <imagetagger-button @click="isLoginDialogOpen = true">Login</imagetagger-button>
                    </template>
                </imagetagger-card>

                <!-- Create Team -->
                <imagetagger-card :title-over-media="true">
                    <template v-slot:title>
                        <span class="mdc-theme--text-disabled-on-light">3. </span>
                        <span :class="isCreateTeamActive ? 'mdc-theme--primary' : 'mdc-theme--text-disabled-on-light'">
                            Create a Team
                        </span>
                    </template>
                    <template v-slot:media>
                        <i class="mdi mdi-account-group action-icon"
                           :class="isCreateTeamActive ? 'mdc-theme--secondary' : 'mdc-theme--text-disabled-on-light'"/>
                    </template>
                    <template v-slot:body v-if="isCreateTeamActive">
                        <p>
                            In ImageTagger every user is part of a Team which owns a number of Imagesets.
                            By default no Teams exist so you better create one now.
                        </p>
                    </template>
                    <template v-slot:action-buttons v-if="isCreateTeamActive">
                        <imagetagger-button @click="isCreateTeamDialogOpen = true">Create Team</imagetagger-button>
                    </template>
                </imagetagger-card>

                <!-- Create Imageset -->
                <imagetagger-card :title-over-media="true">
                    <template v-slot:title>
                        <span class="mdc-theme--text-disabled-on-light">4. </span>
                        <span :class="isCreateImagesetActive ? 'mdc-theme--primary' : 'mdc-theme--text-disabled-on-light'">
                            Create an Imageset
                        </span>
                    </template>
                    <template v-slot:media>
                        <i class="mdi mdi-folder-multiple-image action-icon"
                           :class="isCreateImagesetActive ? 'mdc-theme--secondary' : 'mdc-theme--text-disabled-on-light'"/>
                    </template>
                </imagetagger-card>
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
import {Route} from "vue-router"
import Navbar from "@/components/Navbar.vue"
import NavbarProfile from "@/components/NavbarProfile.vue"
import ImagetaggerCard from "@/components/base/ImagetaggerCard.vue"
import ImagetaggerButton from "@/components/base/ImagetaggerButton.vue"
import ImagetaggerDialog from "@/components/base/ImagetaggerDialog.vue"
import LoginForm from "@/components/LoginForm.vue"
import CreateTeam from "@/components/CreateTeam.vue"


const STEP_CREATE_USER = 1
const STEP_LOGIN = 2
const STEP_CREATE_TEAM = 3
const STEP_CREATE_IMAGESET = 4

/**
 * Prevents the user from navigating to a step that is not yet available
 */
const beforeRouteEnter = function(to: Route, fromRoute: Route, next: Function): void {
    next((vm: WelcomeNewImagetagger) => {
        if (vm.currentStep > STEP_LOGIN && !vm.$store.state.auth.loggedIn)
            vm.$router.push({name: "welcomeNewImagetagger", params: {step: STEP_LOGIN.toString()}})
        else if (vm.currentStep <= STEP_LOGIN && vm.$store.state.auth.loggedIn)
            vm.$router.push({name: "welcomeNewImagetagger", params: {step: STEP_CREATE_TEAM.toString()}})
    })
}


@Component({
    components: {CreateTeam, Login: LoginForm, ImagetaggerDialog, ImagetaggerButton, NavbarProfile, Navbar, ImagetaggerCard},
    beforeRouteEnter: beforeRouteEnter
})
export default class WelcomeNewImagetagger extends Vue {
    public isLoginDialogOpen = false
    public isCreateTeamDialogOpen = false
    public isCreateImagesetDialogOpen = false

    get currentStep(): number {
        return +this.$route.params.step
    }

    get isCreateUserActive(): boolean {
        return this.currentStep === STEP_CREATE_USER
    }

    get isLoginActive(): boolean {
        return this.currentStep === STEP_LOGIN
    }

    get isCreateTeamActive(): boolean {
        return this.currentStep === STEP_CREATE_TEAM
    }

    get isCreateImagesetActive(): boolean {
        return this.currentStep === STEP_CREATE_IMAGESET
    }

    onLogin(): void {
        this.$router.push({name: "welcomeNewImagetagger", params: {step: "3"}})
        this.isLoginDialogOpen = false
    }

    onTeamCreated(): void {
        this.$router.push({name: "welcomeNewImagetagger", params: {step: "4"}})
        this.isCreateTeamDialogOpen = false
    }

    onImagesetCreated(e: {id: number}): void {
        this.$router.push({name: "imagesetDetails", params: {id: e.id.toString()}})
        this.isCreateImagesetDialogOpen = false
    }
}
</script>

<style scoped lang="scss">
    .centered {
        width: 80%;
        margin-left: auto;
        margin-right: auto;
    }

    .steps-container {
        display: flex;
        flex-flow: row;
        justify-content: space-between;
        max-width: 100%;

        & > * {
            padding: 8px 10px;
            margin: 0 8px;
            min-width: 20%;

            &:last-child {
                margin-right: 0;
            }
            &:first-child {
                margin-left: 0;
            }
        }

        .imagetagger-card--root .action-icon {
            font-size: 112px;
        }

        .text-box {
            padding: 1rem;
            border-radius: 0.25rem;
        }
    }
</style>
