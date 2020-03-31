import Vue from "vue"
import Vuetify from "vuetify"

Vue.use(Vuetify)

export default new Vuetify({
    theme: {
        options: {
            customProperties: true      // expose theme colors as css variables
        },
        themes: {
            light: {
                primary: "#083358",
                secondary: "#F67280",
                accent: "#F67280",
                white: "#FFFFFF"
            }
        }
    }
})
