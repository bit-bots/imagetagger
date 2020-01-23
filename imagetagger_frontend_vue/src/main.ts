import Vue from "vue"
import App from "./App.vue"
import {router} from "@/router"
import {store} from "@/store"
import VueResource from "vue-resource"

Vue.use(VueResource)

Vue.config.productionTip = false

export const VueInstance = new Vue({
    router,
    store,
    http: {
        root: "http://localhost:8000/api"
    },
    render: h => h(App),
    beforeCreate: function () {
        this.$store.dispatch("restorePersistentLogin")
    }
}).$mount("#app")
