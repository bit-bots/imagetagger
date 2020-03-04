import Vue from "vue"
import {Module} from "vuex"
import {VueInstance} from "@/main"


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
        retrieveAllTeams: function(context) {
            return VueInstance.$resource("teams").get().then(async response => {
                const teams: Team[] = (await response.json()).teams
                context.commit("setTeams", teams)
            })
        },
        retrieveTeam: function (context, payload: {id: number}) {
            return VueInstance.$resource(`team/${payload.id}`).get().then(async response => {
                const team: Team = (await response.json()).team
                context.commit("setTeam", team)
            })
        }
    },
    getters: {
        teamById: (state) => (id: number) =>
            state.teams.find(iteam => iteam.id === id),
    }
} as Module<TeamState, any>
