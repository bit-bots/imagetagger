<template>
    <div class="create-team--root">
        <imagetagger-text-field label="Test Label" :outlined="true"/>
    </div>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import "vue-class-component/hooks"
import {Prop} from "vue-property-decorator"
import VueTypes from "vue-types"
import ImagetaggerTextField from "@/components/base/ImagetaggerTextField.vue"

@Component({
    components: {ImagetaggerTextField}
})
export default class CreateTeamForm extends Vue {
}
</script>

<style scoped lang="scss">

</style>
