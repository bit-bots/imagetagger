import {Module} from "vuex"
import {VueInstance} from "@/main"


export interface Team {
    id: number
    name: string
    webstie: string
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
    },
    actions: {
        retrieveAllTeams: function(context) {
            return VueInstance.$resource("teams").get().then(async response => {
                const teams: Team[] = (await response.json()).teams
                context.commit("setTeams", teams)
            })
        },
    },
    getters: {
        teamById: (state) => (id: number) =>
            state.teams.find(iteam => iteam.id === id),
    }
} as Module<TeamState, any>
