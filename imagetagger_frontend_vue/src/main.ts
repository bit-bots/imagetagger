import Vue from "vue"
import App from "./App.vue"
import {router} from "@/plugins/router"
import {store} from "@/plugins/store"
import {http} from "@/plugins/resource"
import vuetify from "./plugins/vuetify"
import "roboto-fontface/css/roboto/roboto-fontface.css"
import "@mdi/font/css/materialdesignicons.css"

Vue.config.productionTip = false

export const VueInstance = new Vue({
    router,
    store,
    http,
    vuetify,
    render: h => h(App),

    created: function () {
        this.$store.dispatch("restorePersistentLogin")
    }
}).$mount("#app")
