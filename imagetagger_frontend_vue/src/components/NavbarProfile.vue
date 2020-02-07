<template>
    <div class="mdc-top-app-bar__action mdc-menu-surface--anchor">
        <!-- Profile icon -->
        <div v-if="isLoggedIn">
            <button class="mdc-icon-button" v-on:click="toggleMenu">
                <i class="mdi mdi-account"/>
            </button>
        </div>

        <!-- Opened menu -->
        <div class="mdc-menu mdc-menu-surface" ref="elMenu">
            <ul class="mdc-list" role="menu" aria-hidden="true" aria-orientation="vertical">
                <li class="mdc-list-item" role="menuitem">
                    <router-link :to="{name: 'profile'}">
                        <i class="mdc-list-item__icon mdi mdi-account-cog"/>
                        <span class="mdc-list-item__text">Profile</span>
                    </router-link>
                </li>
                <li class="mdc-list-item" role="menuitem" v-on:click="logout()">
                    <i class="mdc-list-item__icon mdi mdi-exit-to-app"/>
                    <span class="mdc-list-item__text">Logout</span>
                </li>
            </ul>
        </div>
    </div>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import {MDCMenu} from "@material/menu/component"
import {Corner} from "@material/menu-surface/constants"

@Component({})
export default class Navbar extends Vue {
    private _mdcMenu: MDCMenu;

    isProfileMenuExtended = false;

    mounted() {
        this._mdcMenu = new MDCMenu(this.$refs.elMenu as Element)
        this._mdcMenu.setAnchorCorner(Corner.BOTTOM_LEFT)
    }

    toggleMenu() {
        this._mdcMenu.open = !this._mdcMenu.open
    }

    beforeDestroy() {
        this._mdcMenu.destroy()
    }

    logout() {
        this.$store.commit("logout")
    }

    get isLoggedIn(): boolean {
        return this.$store.state.auth.loggedIn
    }

}
</script>

<style scoped lang="scss">
</style>
