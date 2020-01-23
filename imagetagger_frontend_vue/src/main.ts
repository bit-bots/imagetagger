import Vue from "vue"
import App from "./App.vue"
import {router} from "@/router"
import {store} from "@/store"
import {http} from "@/resource"

Vue.config.productionTip = false

export const VueInstance = new Vue({
    router,
    store,
    http,
    render: h => h(App),
    created: function () {
        this.$store.dispatch("restorePersistentLogin")
    }
}).$mount("#app")
