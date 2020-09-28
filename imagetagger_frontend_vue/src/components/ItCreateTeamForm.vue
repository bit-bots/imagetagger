<template>
    <v-form @submit.prevent="onSubmit" ref="form">
        <p>
            When creating a new Team you wil automatically be added to that team and given all permissions.<br>
            You can add members to your new Team later.
        </p>
        <v-text-field label="Team Name" :rules="[required]" v-model="name"/>
        <div class="d-flex flex-row justify-end">
            <div>
                <slot>
                    <v-btn color="primary" type="submit">Create Team</v-btn>
                </slot>
            </div>
        </div>
    </v-form>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import "vue-class-component/hooks"
import {required} from "@/plugins/vuetify/formValidators"

@Component({})
export default class ItCreateTeamForm extends Vue {
    name = ""

    onSubmit(): void {
        if ((this.$refs.form as unknown).validate()) {
            this.$store.dispatch("createTeam", {name: this.name})
                .then(id => this.$emit("teamCreated", id))
        }
    }

    required = required
}
</script>

<style scoped lang="scss">
</style>
