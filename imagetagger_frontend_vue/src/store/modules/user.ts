import {VueInstance} from "@/main"
import {Module} from "vuex"

class MeUser {
    id = -1
    username = ""
    points = 0
    pinnedSets: number[] = []
    teams: number[] = []
}

export class UserState {
    me = new MeUser()
}

export const userModule = {
    state: () => new UserState(),
    mutations: {
        setMeUser: function (state, payload: MeUser) {
            state.me = payload
        },
        clearMeUser: function (state) {
            state.me = new MeUser()
        }
    },
    actions: {
        retrieveMeUser: function (context) {
            return VueInstance.$resource("users/me").get().then(async response => {
                const user: MeUser = await response.json()
                context.commit("setMeUser", user)
            })
        }
    }
} as Module<UserState, any>
