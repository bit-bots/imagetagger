import {VueInstance} from "@/main"
import {Module} from "vuex"
import {RawLocation} from "vue-router"

export const authModule = {
    state: {
        loggedIn: "",
        authToken: "",
        nextRoute: {name: "dashboard", params: {filter: "all"}} as RawLocation
    },
    mutations: {
        setAuthToken: function (state, payload: string) {
            state.authToken = payload
            state.loggedIn = true

            localStorage.setItem("authToken", payload)
        }
    },
    actions: {
        /**
         * Restore authToken which is persistently saved in localStore and commit it to the store
         */
        restorePersistentLogin: function(context) {
            const authToken = localStorage.getItem("authToken")
            if (authToken) {
                context.commit("setAuthToken", authToken)
            }
        },

        /**
         * Login with the credentials contained in payload by retrieving an authToken from the backend server.
         * Commit that authToken into the store
         */
        login: async function (context,
                               payload: { username: string, password: string }): Promise<void> {
            return VueInstance.$http.post("auth/", payload)
                .then(async response => {
                    const token = (await response.json()).token
                    context.commit("setAuthToken", token)
                    return Promise.resolve()
                }, response => {
                    if (response.status == 400) {
                        return Promise.reject("Invalid login credentials")
                    } else {
                        return Promise.reject("Unknown error during login")
                    }
                })
        },
        // TODO logout action
    }
} as Module<any, any>
