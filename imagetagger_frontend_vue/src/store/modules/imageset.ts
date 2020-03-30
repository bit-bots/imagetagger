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
            return VueInstance.$resource("image_sets").get()
                .then(response => response.json())
                .then((response: Imageset[]) => {
                    context.commit("setImagesets", response)
                })
        },

        retrieveImageset: function (context, payload: {
            id: number,
            sideloadTeam: boolean,
            sideloadCreator: boolean
        }) {
            return VueInstance.$http.get(`image_sets/${payload.id}/`)
                .then(response => response.json())
                .then((response: Imageset) => {
                    context.commit("setImageset", response)

                    const children: Promise<any>[] = []
                    if (payload.sideloadTeam)
                        children.push(context.dispatch("retrieveTeam", {id: response.team}))
                    if (payload.sideloadCreator)
                        children.push(context.dispatch("retrieveUser", {id: response.creator}))

                    return Promise.all(children)
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
                .then((response: Imageset) => {
                    context.commit("setImageset", response)
                    return response.id
                })
        }
    },
    getters: {
        imagesetById: (state) => (id: number) => state.imagesets.filter(i => i.id === id)[0]
    }
} as Module<ImagesetState, any>
