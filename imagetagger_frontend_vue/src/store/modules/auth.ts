import {VueInstance} from "@/main"
import {Module} from "vuex"
import {RawLocation} from "vue-router"

export const authModule = {
    state: {
        loggedIn: false,
        authToken: "",
        nextRoute: {name: "dashboard", params: {filter: "all"}} as RawLocation
    },
    mutations: {
        setAuthToken: function (state, payload: string) {
            state.authToken = payload
            state.loggedIn = true
        }
    },
    actions: {
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
        }
    }
} as Module<any, any>
