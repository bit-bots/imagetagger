import Vue from "vue"
import Vuetify from "vuetify/lib"
import "@mdi/font/css/materialdesignicons.css"

Vue.use(Vuetify)

export default new Vuetify({
    icons: {
        iconfont: "mdi"
    },
    theme: {
        options: {
            customProperties: true      // expose theme colors as css variables
        },
        themes: {
            light: {
                primary: "#083358",
                secondary: "#F67280",
                accent: "#F67280",
                white: "#FFFFFF",
            },
        }
    }
})
