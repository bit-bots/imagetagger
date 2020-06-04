import Vue from "vue"
import {Module} from "vuex"
import {VueInstance} from "@/main"


export interface Image {
    id: number
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
        retrieveImage: function (context, payload: {id: number}) {
            return VueInstance.$resource(`images/${payload.id}`).get()
                .then(response => response.json())
                .then((response: Image) => {
                    context.commit("setImage", response)
                })
        },

        uploadImages: function (context, payload: {imageset: number, files: File[]}) {
            return new Promise((resolve, reject) => {
                const reader = new FileReader()
                reader.onload = (event) => {
                    VueInstance.$http.post("images/", {
                        name: payload.files[0].name,
                        imagesetId: payload.imageset,
                        data: reader.result
                    }).then(resolve)
                }
                reader.readAsBinaryString(payload.files[0])
            })
        }
    },
    getters: {
        imageById: (state) => (id: number) =>
            state.images.find(t => t.id === id),
    }
} as Module<ImageState, any>
