import Vue from "vue"
import Vuex, {Store} from "vuex"
import {authModule} from "@/store/modules/auth"
import {userModule} from "@/store/modules/user"
import {contentFilterModule} from "@/store/modules/contentFilter"
import {imagesetModule} from "@/store/modules/imageset"
import {teamModule} from "@/store/modules/team"

Vue.use(Vuex)

export const store = new Vuex.Store({
    state: {},
    mutations: {},
    actions: {},
    modules: {
        auth: authModule,
        user: userModule,
        contentFilter: contentFilterModule,
        imagesets: imagesetModule,
        teams: teamModule
    }
})
