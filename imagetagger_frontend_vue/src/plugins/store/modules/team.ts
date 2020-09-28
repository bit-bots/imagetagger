import Vue from "vue"
import {Module} from "vuex"
import {VueInstance} from "@/main"
import {RootState} from "@/plugins/store/root";


export interface Team {
    id: number
    name: string
    website: string
    members: number[]
    admins: number[]
}


export class TeamState {
    teams: Team[] = []
}


export const teamModule = {
    state: () => new TeamState(),
    mutations: {
        setTeams: (state, payload: Team[]) => {
            state.teams = payload
        },
        setTeam: (state, payload: Team) => {
            const index = state.teams.findIndex(i => i.id === payload.id)
            if (index === -1)
                state.teams.push(payload)
            else
                Vue.set(state.teams, index, payload)
        }
    },
    actions: {
        retrieveAllTeams: function (context) {
            return VueInstance.$resource("teams").get()
                .then(response => response.json())
                .then((response: Team[]) => {
                    context.commit("setTeams", response)
                })
        },
        retrieveTeam: function (context, payload: { id: number }) {
            return VueInstance.$resource(`teams/${payload.id}`).get()
                .then(response => response.json())
                .then((response: Team) => {
                    context.commit("setTeam", response)
                })
        },
        createTeam: function (context, payload: { name: string, website?: string }) {
            return VueInstance.$http.post("teams/", payload)
                .then(response => response.json())
                .then((response: Team) => {
                    context.commit("setTeam", response)
                    return response.id
                })
        }
    },
    getters: {
        teamById: (state) => (id: number) =>
            state.teams.find(t => t.id === id),
        myTeams: (state, getters, rootState) =>
            state.teams.filter(t => rootState.user.me.teams.includes(t.id))
    }
} as Module<TeamState, RootState>
