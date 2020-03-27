import Vue from "vue"
import Vuex, {Store, StoreOptions} from "vuex"
import {authModule} from "@/store/modules/auth"
import {userModule} from "@/store/modules/user"
import {contentFilterModule} from "@/store/modules/contentFilter"
import {imagesetModule} from "@/store/modules/imageset"
import {teamModule} from "@/store/modules/team"

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
        contentFilter: contentFilterModule,
        imagesets: imagesetModule,
        teams: teamModule
    },
    strict: true
} as StoreOptions<GlobalState>)
