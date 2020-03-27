import Vue from "vue"
import {Module} from "vuex"
import {VueInstance} from "@/main"
import {User} from "@/store/modules/user"
import {Team} from "@/store/modules/team"
import {Url} from "@/httpResourceExtensions"


export interface ImagesetPermissions {
    verify: boolean
    annotate: boolean
    createExport: boolean
    deleteAnnotation: boolean
    deleteExport: boolean
    deleteSet: boolean
    deleteImages: boolean
    editAnnotation: boolean
    editSet: boolean
    read: boolean
}


export interface Imageset {
    id: number
    name: string
    description: string
    location: string
    time: string
    public: boolean
    publicCollaboration: boolean
    imageLock: boolean
    priority: number
    zipState: number
    images: number[]
    mainAnnotationType: number
    tags: string[]
    team: number
    creator: number
    zipUrl: string
    numberOfImages: number
    permissions: ImagesetPermissions
    isPinned: boolean
}


export class ImagesetState {
    imagesets: Imageset[] = []
}


export const imagesetModule = {
    state: () => new ImagesetState(),
    mutations: {
        setImagesets: (state, payload: Imageset[]) => {
            state.imagesets = payload
        },
        setImageset: (state, payload: Imageset) => {
            const index = state.imagesets.findIndex(i => i.id === payload.id)
            if (index === -1)
                state.imagesets.push(payload)
            else
                Vue.set(state.imagesets, index, payload)
        }
    },
    actions: {
        retrieveAllImagesets: function (context) {
            return VueInstance.$resource("image_sets").get().then(async response => {
                const imagesets: Imageset[] = (await response.json()).imageSets
                context.commit("setImagesets", imagesets)
            })
        },

        retrieveImageset: function (context, payload: {
            id: number,
            sideloadTeam: boolean,
            sideloadCreator: boolean
        }) {
            const url = new Url("image_sets")
            url.addPart(payload.id)
            if (payload.sideloadTeam)
                url.addGetArg("include[]", "team.*")
            if (payload.sideloadCreator)
                url.addGetArg("include[]", "creator.*")

            return VueInstance.$http.get(url.toString())
                .then(response => response.json())
                .then(response => {
                    context.commit("setImageset", response.imageSet)

                    if (payload.sideloadTeam)
                        context.commit("setTeam", response.teams.find((t: Team) => t.id === response.imageSet.team))
                    if (payload.sideloadCreator)
                        context.commit("setUser", response.users.find((u: User) => u.id === response.imageSet.creator))
                })
        },

        updateImagesetTags: function (context,
                                      payload: { imageset: Imageset, tags: string[] }) {
            return VueInstance.$http.patch(`image_sets/${payload.imageset.id}/`, {tags: payload.tags})
                .then(response => response.json())
                .then(response => context.commit("setImageset", response.imageSet))
        },

        createImageset: (context,
                         payload: {
                             name: string,
                             description: string,
                             location: string,
                             public: boolean,
                             publicCollaboration: boolean,
                             team: number
                         }) => {
            return VueInstance.$http.post("image_sets/", payload)
                .then(response => response.json())
                .then(response => {
                    const imageset: Imageset = response.imageSet
                    context.commit("setImageset", imageset)
                    return imageset.id
                })
        }
    },
    getters: {
        imagesetById: (state) => (id: number) => state.imagesets.filter(i => i.id === id)[0]
    }
} as Module<ImagesetState, any>
