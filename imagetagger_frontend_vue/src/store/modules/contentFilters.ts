import {Module} from "vuex"


export class ContentFilterState {
    searchTerm: string = ""
}


export const contentFilterModule = {
    state: () => new ContentFilterState(),
    mutations: {
        search: function (state, payload: string) {
            state.searchTerm = payload
        },

        clearSearch: function (state, payload: string) {
            state.searchTerm = ""
        }
    }
} as Module<ContentFilterState, any>
