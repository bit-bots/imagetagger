import Vue from "vue"
import Vuex, {StoreOptions} from "vuex"
import {modules, rootActions, rootGetters, rootMutations, RootState} from "@/plugins/store/root";

Vue.use(Vuex)

export const store = new Vuex.Store({
    state: () => new RootState(),
    mutations: rootMutations,
    actions: rootActions,
    getters: rootGetters,
    modules: modules,
    strict: true
} as StoreOptions<RootState>)
