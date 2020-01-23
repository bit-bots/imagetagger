<template>
    <div class="card">
        <div class="card-header">
            <h5>{{ title }}</h5>

            <!-- Draw tabs dynamically if any are defined -->
            <ul v-if="tabs.length > 0" class="nav nav-tabs card-header-tabs">
                <li v-for="tab of tabs" class="nav-item" :key="tab.name">
                    <router-link
                            :to="tab.link"
                            class="nav-link"
                            :class="tab.name.toLowerCase() === activeTabName.toLowerCase() ? 'active' : ''">
                        {{ tab.name }}
                    </router-link>
                </li>
            </ul>
        </div>

        <div class="card-body">
            <slot/>
        </div>
    </div>
</template>

<script lang="ts">
import Vue from "vue"
import VueTypes from "vue-types"
import {CardTabDefinition} from "@/types"

export default Vue.extend({
    props: {
        title: VueTypes.string,
        tabs: VueTypes.arrayOf(CardTabDefinition).def([]),
        activeTabName: VueTypes.string.def("")
    }
})
</script>

<style scoped lang="scss">

</style>
