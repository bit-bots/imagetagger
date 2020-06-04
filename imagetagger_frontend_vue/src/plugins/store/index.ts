import Vue from "vue"
import Vuex, {Store, StoreOptions} from "vuex"
import {authModule} from "@/plugins/store/modules/auth"
import {userModule} from "@/plugins/store/modules/user"
import {imagesetModule} from "@/plugins/store/modules/imageset"
import {teamModule} from "@/plugins/store/modules/team"
import {imageModule} from "@/plugins/store/modules/image"

Vue.use(Vuex)

export class GlobalState {
    currentlyLoading: boolean = false
}

export const store = new Vuex.Store({
    state: () => new GlobalState(),
    mutations: {
        toggleCurrentlyLoading: function (state, payload?: boolean) {
            if (payload != null)
                state.currentlyLoading = payload
            else
                state.currentlyLoading = !state.currentlyLoading
        }
    },
    actions: {},
    modules: {
        auth: authModule,
        user: userModule,
        imagesets: imagesetModule,
        teams: teamModule,
        images: imageModule
    },
    strict: true
} as StoreOptions<GlobalState>)
