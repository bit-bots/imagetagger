<template>
    <v-form @submit.prevent="onSubmit" ref="form">
        <v-text-field label="Name" :rules="[required]" v-model="name"/>
        <v-select label="Team" :items="teamNames" :rules="[required]" v-model="teamName"/>
        <v-text-field label="Description (optional)" v-model="description"/>
        <v-text-field label="Location (optional)" v-model="location"/>

        <div class="d-flex flex-row justify-space-between align-baseline">
            <div class="d-flex flex-row">
                <v-switch label="Public" class="mr-8" v-model="isPublic"/>
                <v-switch label="Public Collaboration" v-model="isPublicCollaboration"/>
            </div>
            <div>
                <slot>
                    <v-btn color="primary" type="submit">Create Imageset</v-btn>
                </slot>
            </div>
        </div>
    </v-form>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import "vue-class-component/hooks"
import {Prop} from "vue-property-decorator"
import VueTypes from "vue-types"
import {required} from "@/plugins/vuetify/formValidators"
import {Team} from "@/plugins/store/modules/team"

@Component({})
export default class ItCreateImagesetForm extends Vue {
    name: string = ""
    teamId: number = -1
    description: string = ""
    location: string = ""
    isPublic: boolean = false
    isPublicCollaboration: boolean = false

    get teamNames(): string[] {
        return this.$store.getters.myTeams.map((t: Team) => t.name)
    }

    // noinspection JSUnusedGlobalSymbols because v-model uses it
    set teamName(value: string) {
        this.teamId = (this.$store.getters.myTeams as Team[]).find(t => t.name === value).id
    }
    get teamName(): string | null {
        if (this.teamId === -1)
            return null
        else
            return (this.$store.getters.teamById(this.teamId) as Team).name
    }

    onSubmit(): void {
        if ((this.$refs.form as any).validate()) {
            this.$store.dispatch("createImageset", {
                name: this.name,
                description: this.description,
                location: this.location,
                team: this.teamId,
                public: this.isPublic,
                publicCollaboration: this.isPublicCollaboration
            }).then(id => this.$emit("imagesetCreated", id))
        }
    }

    required = required
}
</script>

<style scoped lang="scss">

</style>
