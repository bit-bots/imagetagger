import Vue from "vue"
import {VueInstance} from "@/main"
import {Module} from "vuex"

export class MeUser {
    id = -1
    username = ""
    points = 0
    pinnedSets: number[] = []
    teams: number[] = []
}

export interface User {
    id: number
    username: string
    points: number
    teams: number[]
}

export class UserState {
    me = new MeUser()
    users: User[] = []
}

export const userModule = {
    state: () => new UserState(),

    mutations: {
        setMeUser: function (state, payload: MeUser) {
            state.me = payload
        },
        setUser: function(state, payload: User) {
            const index = state.users.findIndex(i => i.id === payload.id)
            if (index === -1)
                state.users.push(payload)
            else
                Vue.set(state.users, index, payload)
        },
        logout: function (state) {
            state.me = new MeUser()
        }
    },

    actions: {
        retrieveMeUser: function (context) {
            return VueInstance.$resource("users/me").get()
                .then(response => response.json())
                .then((response: MeUser) => {
                    context.commit("setMeUser", response)
                })
        },
        retrieveUser: function (context, payload: {id: number}) {
            return VueInstance.$resource(`users/${payload.id}`).get()
                .then(response => response.json())
                .then((response: User) => {
                    context.commit("setUser", response)
                })
        }
    },

    getters: {
        userById: (state) => (id: number) =>
            state.users.find(iuser => iuser.id === id)
    }
} as Module<UserState, any>
