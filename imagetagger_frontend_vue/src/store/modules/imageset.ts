import {Module} from "vuex"
import {VueInstance} from "@/main"


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
        }
    },
    actions: {
        retrieveAllImagesets: function(context) {
            return VueInstance.$resource("image_sets").get().then(async response => {
                const imagesets: Imageset[] = (await response.json()).imageSets
                context.commit("setImagesets", imagesets)
            })
        }
    },
    getters: {
        imagesetById: (state) => (
            id: number) => state.imagesets.find(iimageset => iimageset.id === id)
    }
} as Module<ImagesetState, any>
