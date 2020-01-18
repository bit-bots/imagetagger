import Vue from "vue"
import Vuex from "vuex"

Vue.use(Vuex)

const store = new Vuex.Store({
    state: {
        currentlyLoadingPage: false,
    },
    mutations: {
        toggleCurrentlyLoading(state) {
            state.currentlyLoadingPage = !state.currentlyLoadingPage
        }
    }
})

export {
    store
}
