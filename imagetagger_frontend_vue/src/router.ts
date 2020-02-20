import VueRouter from "vue-router"
import Vue from "vue"
import {VueInstance} from "@/main"

Vue.use(VueRouter)

const routes = [
    {
        path: "/imagesets/list/:filter",
        name: "dashboard",
        component: loadView("Dashboard")
    },
    {
        path: "/imagesets/view/:id",
        component: loadView("Imageset"),
        children: [
            {
                path: "details",
                name: "imagesetDetails",
                component: loadView("ImagesetDetails")
            },

            {
                path: "images",
                name: "imagesetImages",
                component: loadView("ImagesetDetails")
            },

            {path: "", redirect: "details"}
        ]
    },

    {
        path: "/login",
        name: "login",
        component: loadView("Login")
    },

    {
        path: "/profile",
        name: "profile",
        component: loadView("Profile")
    },

    {path: "/", name: "dashboard-public", redirect: "/imagesets/list/public"},

    {
        path: "*",
        name: "404",
        component: loadView("NotFound")
    }
]

function loadView(name: string) {
    // @ts-ignore
    return resolve => require(["@views/" + name + ".vue"], resolve)
}


export const router = new VueRouter({
    mode: "history",
    routes
})

router.beforeResolve((to, from, next) => {
    if (VueInstance.$store.state.user.me.id == -1 && VueInstance.$store.state.auth.loggedIn) {
        VueInstance.$store.dispatch("retrieveMeUser")
            .catch(reason => console.error(reason))
            .finally(() => next())
    } else {
        next()
    }
})

router.beforeEach((toRoute, fromRoute, next) => {
    if (VueInstance)
        VueInstance.$store.commit("toggleCurrentlyLoading", true)
    next()
})


router.afterEach(() => {
    VueInstance.$store.commit("toggleCurrentlyLoading", false)
})
