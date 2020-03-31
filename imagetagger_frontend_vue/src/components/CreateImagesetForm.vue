<template>
    <div class="create-imageset-root">
        <form @submit.prevent="onFormSubmit()">
            <div>
                <imagetagger-text-field label="Name" outlined v-model="name"/>
            </div>
            <div>
                <imagetagger-dropdown :choices="teamNames" label="Team" @input="onTeamSelect"/>
            </div>
            <div>
                <imagetagger-text-field label="Description (optional)" outlined v-model="description"/>
            </div>
            <div>
                <imagetagger-text-field label="Location (optional)" outlined v-model="location"/>
            </div>
            <div class="space-before">
                <imagetagger-switch label="Public" v-model="public"/>
            </div>
            <div>
                <imagetagger-switch label="Public Collaboration" v-model="publicCollaboration"/>
            </div>

            <div class="space-before">
                <imagetagger-button type="submit" :disabled="!isFormValid">Create</imagetagger-button>
            </div>
        </form>
    </div>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import "vue-class-component/hooks"
import {Prop, Watch} from "vue-property-decorator"
import VueTypes from "vue-types"
import {Team} from "@/plugins/store/modules/team"
import ImagetaggerTextField from "@/components/base/ImagetaggerTextField.vue"
import ImagetaggerButton from "@/components/base/ImagetaggerButton.vue"
import ImagetaggerSwitch from "@/components/base/ImagetaggerSwitch.vue"
import ImagetaggerDropdown from "@/components/base/ImagetaggerDropdown.vue"

@Component({
    components: {ImagetaggerSwitch, ImagetaggerButton, ImagetaggerTextField, ImagetaggerDropdown}
})
export default class CreateImagesetForm extends Vue {
    name: string = ""
    description: string = ""
    location: string = ""
    public: boolean = false
    publicCollaboration: boolean = false
    teamId: number = -1

    get isFormValid(): boolean {
        return this.name != "" && this.teamId != -1
    }

    get teamNames(): string[] {
        return this.$store.getters.myTeams.map((t: Team) => t.name)
    }

    onTeamSelect(teamName: string): void {
        if (teamName)
            this.teamId = this.$store.getters.myTeams.find((t: Team) => t.name === teamName).id
        else
            this.teamId = -1
    }

    onFormSubmit() {
        this.$store.dispatch("createImageset", {
            name: this.name,
            description: this.description,
            location: this.location,
            public: this.public,
            publicCollaboration: this.publicCollaboration,
            team: this.teamId
        }).then(id => this.$emit("imagesetCreated", id))
    }
}
</script>

<style scoped lang="scss">
    .space-before {
        margin-top: 0.5rem;
    }
</style>
