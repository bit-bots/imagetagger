import VueRouter from "vue-router"
import Vue from "vue"

Vue.use(VueRouter)

const routes = [
    {
        path: "/imagesets/list/:filter",
        name: "dashboard",
        component: loadView("Dashboard")
    },

    {
        path: "/login",
        name: "login",
        component: loadView("Login")
    },

    {path: "/", name: "dashboard-public", redirect: "/imagesets/list/public"},

    {
        path: "*",
        name: "404",
        component: loadView("NotFound")
    }
]

const router = new VueRouter({
    mode: "history",
    routes
})

function loadView(name: string) {
    // @ts-ignore
    return resolve => require(["@views/" + name + ".vue"], resolve)
}

export {router}
