<template>
    <v-container>
            <v-stepper v-model="currentStep">
                <v-stepper-header>
                    <v-stepper-step :complete="currentStep > STEP_CREATE_USER" :step="STEP_CREATE_USER">
                        Create User
                    </v-stepper-step>
                    <v-divider/>
                    <v-stepper-step :complete="currentStep > STEP_LOGIN" :step="STEP_LOGIN">
                        Login
                    </v-stepper-step>
                    <v-divider/>
                    <v-stepper-step :complete="currentStep > STEP_CREATE_TEAM" :step="STEP_CREATE_TEAM">
                        Create Team
                    </v-stepper-step>
                    <v-divider/>
                    <v-stepper-step :complete="currentStep > STEP_CREATE_IMAGESET" :step="STEP_CREATE_IMAGESET">
                        Create Imageset
                    </v-stepper-step>
                </v-stepper-header>

                <v-stepper-items>
                    <!-- Create User -->
                    <v-stepper-content :step="STEP_CREATE_USER">
                        <h1 class="title">Create an admin User</h1>
                        <p>
                            First you need to create a new user with admin access.<br>
                            This user will be able to manage annotation types and change global settings of the
                            Imagetagger instance.
                        </p>
                        <p>
                            Do so by running the following command and answering its prompts:
                        </p>
                        <kbd>
                            &lt;imagetagger-folder&gt;$ ./manage.py createsuperuser
                        </kbd>
                        <v-spacer class="my-8"/>
                        <v-btn color="primary" @click="currentStep++">Done</v-btn>
                        <v-btn color="secondary" outlined class="ml-3" target="_blank"
                               href="https://docs.djangoproject.com/en/3.0/ref/django-admin/#createsuperuser">
                            Explain
                        </v-btn>
                    </v-stepper-content>

                    <!-- Login -->
                    <v-stepper-content :step="STEP_LOGIN">
                        <h1 class="title">Login with the created User</h1>
                        <p>
                            Now that a you have created a user, it is time to log in.
                        </p>
                        <p v-if="isLoggedIn">
                            Although you are already logged in, you can log in with a different user or simply
                            continue.
                        </p>
                        <it-login-form @loggedIn="currentStep++">
                            <v-btn color="primary" type="submit">Login</v-btn>
                            <v-btn v-if="isLoggedIn" color="secondary" outlined class="ml-3" @click="currentStep++">
                                Continue
                            </v-btn>
                        </it-login-form>
                    </v-stepper-content>

                    <!-- Create Team -->
                    <v-stepper-content :step="STEP_CREATE_TEAM">
                        <h1 class="title">Create a Team</h1>
                        <p>
                            In ImageTagger every user is part of a Team which owns a number of Imagesets.
                            By default no Teams exist so you better create one now.
                        </p>
                        <p v-if="myTeams.length > 0">
                            You are already in a Team. You can create another one or simply continue.
                        </p>
                        <it-create-team-form @teamCreated="currentStep++">
                            <v-btn color="primary" type="submit">Create Team</v-btn>
                            <v-btn color="secondary" outlined class="ml-3" @click="currentStep++">Continue</v-btn>
                        </it-create-team-form>
                    </v-stepper-content>

                    <!-- Create Imageset -->
                    <v-stepper-content :step="STEP_CREATE_IMAGESET">
                        <h1 class="title">Create an Imageset</h1>
                        <p>
                            Imagesets help you organize your tagging tasks by grouping multiple Images.
                        </p>
                        <p>
                            It is possible to mark Imagesets as important and assign labels to them so that you can
                            easily communicate with your teams which tasks are to be prioritized.
                        </p>
                        <it-create-imageset-form @imagesetCreated="$router.push({name: 'imagesetDetails', params: {id: $event}})"/>
                    </v-stepper-content>
                </v-stepper-items>
            </v-stepper>
    </v-container>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import "vue-class-component/hooks"
import {Prop} from "vue-property-decorator"
import VueTypes from "vue-types"
import ItLoginForm from "@/components/ItLoginForm.vue"
import {Team} from "@/plugins/store/modules/team"
import {RawLocation, Route} from "vue-router"
import {VueInstance} from "@/main"
import ItCreateTeamForm from "@/components/ItCreateTeamForm.vue"
import ItCreateImagesetForm from "@/components/ItCreateImagesetForm.vue"

const STEP_CREATE_USER = 1
const STEP_LOGIN = 2
const STEP_CREATE_TEAM = 3
const STEP_CREATE_IMAGESET = 4

const guardRoute = function (to: Route, fromRoute: Route, next: Function) {
    const nextStep: number = +to.params.step
    if (nextStep > STEP_LOGIN && !VueInstance.$store.state.auth.loggedIn)
        next({name: "welcomeNewImagetagger", params: {step: STEP_LOGIN.toString()}} as RawLocation)
    else if (nextStep >= STEP_CREATE_TEAM && VueInstance.$store.getters.myTeams.length === 0)
        VueInstance.$store.dispatch("retrieveAllTeams").then(() => next())
    else
        next()
}

@Component({
    components: {ItCreateImagesetForm, ItCreateTeamForm, ItLoginForm},
    beforeRouteEnter: guardRoute,
    beforeRouteUpdate: guardRoute
})
export default class WelcomeNewImagetagger extends Vue {
    // make step constants available inside component
    public readonly STEP_CREATE_USER = STEP_CREATE_USER
    public readonly STEP_LOGIN = STEP_LOGIN
    public readonly STEP_CREATE_TEAM = STEP_CREATE_TEAM
    public readonly STEP_CREATE_IMAGESET = STEP_CREATE_IMAGESET

    get currentStep(): number {
        return +this.$route.params.step
    }
    set currentStep(value: number) {
        this.$router.push({name: "welcomeNewImagetagger", params: {step: value.toString()}})
    }

    get myTeams(): Team[] {
        return this.$store.getters.myTeams
    }

    get isLoggedIn(): boolean {
        return this.$store.state.auth.loggedIn
    }
}
</script>

<style scoped lang="scss">

</style>
