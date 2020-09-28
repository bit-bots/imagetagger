import {authModule, AuthState} from "@/plugins/store/modules/auth";
import {userModule, UserState} from "@/plugins/store/modules/user";
import {imagesetModule, ImagesetState} from "@/plugins/store/modules/imageset";
import {teamModule, TeamState} from "@/plugins/store/modules/team";
import {imageModule, ImageState} from "@/plugins/store/modules/image";
import {ActionTree, GetterTree, ModuleTree, MutationTree} from "vuex";

export class RootState {
    currentlyLoading = false
    auth: AuthState
    user: UserState
    imagesets: ImagesetState
    teams: TeamState
    images: ImageState
}

export const rootMutations: MutationTree<RootState> = {
    toggleCurrentlyLoading: function (state: RootState, payload?: boolean): void {
        if (payload != null)
            state.currentlyLoading = payload
        else
            state.currentlyLoading = !state.currentlyLoading
    }
}

export const rootActions: ActionTree<RootState, RootState> = {}

export const rootGetters: GetterTree<RootState, RootState> = {}

export const modules: ModuleTree<RootState> = {
    auth: authModule,
    user: userModule,
    imagesets: imagesetModule,
    teams: teamModule,
    images: imageModule
}
