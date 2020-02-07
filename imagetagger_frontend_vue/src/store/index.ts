import Vue from "vue"
import Vuex, {Store} from "vuex"
import {authModule} from "@/store/modules/auth"
import {userModule} from "@/store/modules/user"
import {contentFilterModule} from "@/store/modules/contentFilters"

Vue.use(Vuex)

export const store = new Vuex.Store({
    state: {},
    mutations: {},
    actions: {},
    modules: {
        auth: authModule,
        user: userModule,
        contentFilter: contentFilterModule
    }
})
