import Vue from "vue"
import Vuex from "vuex"
import {authModule} from "@/store/modules/auth"
import {userModule} from "@/store/modules/user"

Vue.use(Vuex)

const store = new Vuex.Store({
    state: {},
    mutations: {},
    actions: {},
    modules: {
        auth: authModule,
        user: userModule
    }
})

export {store}
