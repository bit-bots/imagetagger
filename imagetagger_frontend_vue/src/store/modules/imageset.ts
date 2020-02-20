import {Module} from "vuex"
import {VueInstance} from "@/main"
import {Vue} from "vue-property-decorator"


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
        retrieveAllImagesets: function(context) {
            return VueInstance.$resource("image_sets").get().then(async response => {
                const imagesets: Imageset[] = (await response.json()).imageSets
                context.commit("setImagesets", imagesets)
            })
        },

        retrieveImageset: function (context, payload: {
            id: number,
            sideloadTeam: boolean
        }) {
            let getArgs: any = {}
            if (payload.sideloadTeam)
                getArgs["include[]"] = "team.*"

            return VueInstance.$resource(`image_sets/${payload.id}`).get(getArgs)
                .then(response => response.json())
                .then(response => {
                    context.commit("setImageset", response.imageSet)

                    if (payload.sideloadTeam)
                        if (response.teams[0])
                            context.commit("setTeam", response.teams[0])
                        else
                            console.warn("Requested to sideload the imagesets team but no team was received")
                })
        },

        updateImagesetTags: function(context,
                                     payload: {imageset: Imageset, tags: string[]}) {
            return VueInstance.$http.patch(`image_sets/${payload.imageset.id}/`, {tags: payload.tags})
                .then(response => response.json())
                .then(response => context.commit("setImageset", response.imageSet))
        }
    },
    getters: {
        imagesetById: (state) => (id: number) => state.imagesets.filter(i => i.id === id)[0]
    }
} as Module<ImagesetState, any>
