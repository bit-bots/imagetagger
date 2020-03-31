<template>
     <div class="mdc-top-app-bar__action">
         <button class="mdc-icon-button"
                 v-if="!isCurrentlySearching"
                 v-on:click="toggleManualSearch">
             <i class="mdi mdi-magnify"/>
         </button>
         <div class="mdc-text-field mdc-text-field--with-leading-icon"
              v-show="isCurrentlySearching"
              ref="elTextField">
             <i class="mdi mdi-magnify mdc-text-field__icon"/>
             <input class="mdc-text-field__input" id="navbarSearch" v-model="searchTerm">
             <label for="navbarSearch" class="mdc-floating-label">{{ searchLabel }}</label>
             <div class="mdc-line-ripple"/>
         </div>
     </div>
</template>

<script lang="ts">
import Vue from "vue"
import VueTypes from "vue-types"
import Component from "vue-class-component"
import {MDCTextField} from "@material/textfield/component"
import {debounce} from "lodash"

@Component({
    props: {
        searchLabel: VueTypes.string.def("Search")
    }
})
export default class NavbarSearch extends Vue {
    private _mdcTextField: MDCTextField

    searchbarManuallyExtended = false

    mounted() {
        this._mdcTextField = new MDCTextField(this.$refs.elTextField as Element)
    }

    beforeDestroy() {
        this._mdcTextField.destroy()
    }

    toggleManualSearch() {
        this.searchbarManuallyExtended = !this.searchbarManuallyExtended
    }

    get searchTerm(): string {
        return this.$store.state.contentFilter.searchTerm
    }
    set searchTerm(value: string) {
        this.setSearchTermDebounced(value)
    }
    private setSearchTermDebounced = debounce(value => this.$store.commit("search", value), 150)

    get isCurrentlySearching(): boolean {
        return this.searchTerm != "" || this.searchbarManuallyExtended
    }
}
</script>

<style scoped lang="scss">
    .mdc-text-field {
        border-radius: 16px;
        height: 80%;
    }
</style>
