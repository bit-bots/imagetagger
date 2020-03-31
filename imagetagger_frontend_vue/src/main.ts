import Vue from "vue"
import App from "./App.vue"
import {router} from "@/plugins/router"
import {store} from "@/plugins/store"
import {http} from "@/plugins/resource"

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
