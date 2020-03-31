<template>
    <div class="create-team--root">
        <p>
            When creating a new Team you wil automatically be added to that team and given all permissions.<br>
            You can add members to your new Team later.
        </p>
        <div class="vertical-spacer"/>
        <form @submit.prevent="onFormSubmit()">
            <div>
                <imagetagger-text-field label="Team Name" outlined v-model="teamName"/>
            </div>
            <div class="vertical-spacer"/>
            <div>
                <imagetagger-button :disabled="!isFormValid" type="submit">Create</imagetagger-button>
            </div>
        </form>
    </div>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import "vue-class-component/hooks"
import {Prop} from "vue-property-decorator"
import VueTypes from "vue-types"
import ImagetaggerTextField from "@/components_old/base/ImagetaggerTextField.vue"
import ImagetaggerButton from "@/components_old/base/ImagetaggerButton.vue"

@Component({
    components: {ImagetaggerButton, ImagetaggerTextField}
})
export default class CreateTeamForm extends Vue {
    teamName: string = ""

    get isFormValid(): boolean {
        return Boolean(this.teamName)
    }

    onFormSubmit(): void {
        this.$store.dispatch("createTeam", {name: this.teamName})
            .then(id => this.$emit("teamCreated", id))
    }
}
</script>

<style scoped lang="scss">
    .vertical-spacer {
        height: 0.5rem;
    }
</style>
