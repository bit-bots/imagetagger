import Vue from "vue"
import {Module} from "vuex"
import {VueInstance} from "@/main"
import {Imageset} from "@/plugins/store/modules/imageset"
import {RootState} from "@/plugins/store/root";


export interface Image {
    id: number
    name: string
    width: number
    height: number
    url: string
    annotations: number[]
}


export class ImageState {
    images: Image[] = []
}


export const imageModule = {
    state: () => new ImageState(),
    mutations: {
        setImages: (state, payload: Image[]) => {
            state.images = payload
        },
        setImage: (state, payload: Image) => {
            const index = state.images.findIndex(i => i.id === payload.id)
            if (index === -1)
                state.images.push(payload)
            else
                Vue.set(state.images, index, payload)
        }
    },
    actions: {
        retrieveImage: function (context, payload: { id: number }) {
            return VueInstance.$resource(`images/${payload.id}`).get()
                .then(response => response.json())
                .then((response: Image) => {
                    context.commit("setImage", response)
                })
        },

        // TODO implement image uploading
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        uploadImages: function (context, payload: { imageset: number, files: File[] }) {
            throw new Error("Image uploading is not yet implemented")
        }
    },
    getters: {
        imageById: (state) => (id: number) => state.images.find(t => t.id === id),

        imagesFromImageset: (state, getters, rootState, rootGetters) => (imagesetId: number) => {
            return (rootGetters.imagesetById(imagesetId) as Imageset)
                .images.map(i => getters.imageById(i))
        },
    }
} as Module<ImageState, RootState>
