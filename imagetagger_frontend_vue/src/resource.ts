import Vue from "vue"
import VueResource from "vue-resource"
import {VueInstance} from "@/main"

Vue.use(VueResource)

// @ts-ignore because the type export of vue-resource is not complete
Vue.http.interceptors.push(function (request: VueResource.HttpOptions): void {
    const authToken = VueInstance.$store.state.auth.authToken

    if (authToken) {
        request.headers.set("Authorization", `Token ${authToken}`)
    }
})


export const http = {
    root: "http://localhost:8000/api"
}
