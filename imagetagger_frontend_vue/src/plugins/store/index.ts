import Vue from "vue"
import Vuex, {Store, StoreOptions} from "vuex"
import {authModule} from "@/plugins/store/modules/auth"
import {userModule} from "@/plugins/store/modules/user"
import {contentFilterModule} from "@/plugins/store/modules/contentFilter"
import {imagesetModule} from "@/plugins/store/modules/imageset"
import {teamModule} from "@/plugins/store/modules/team"

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
