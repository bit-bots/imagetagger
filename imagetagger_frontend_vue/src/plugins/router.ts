import VueRouter from "vue-router"
import Vue from "vue"
import {VueInstance} from "@/main"

Vue.use(VueRouter)

const routes = [
    {
        path: "/imagesets/list/:filter",
        name: "dashboard",
        component: loadView("Dashboard"),
    },

    {path: "/welcome/new_imagetagger",redirect: "/welcome/new_imagetagger/1"},
    {
        path: "/welcome/new_imagetagger/:step",
        name: "welcomeNewImagetagger",
        component: loadView("WelcomeNewImagetagger")
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
                component: loadView("ImagesetImages")
            },

            {path: "", redirect: "details"}
        ]
    },

    {
        path: "/imagesets/view/:imagesetId/image/:imageId",
        name: "imageView",
        component: loadView("Image")
    },

    {
        path: "/login",
        name: "login",
        component: loadView("Login")
    },

    {
        path: "/logout",
        name: "logout",
        component: loadView("Logout")
    },

    {
        path: "/profile",
        name: "profile",
        component: loadView("Profile")
    },

    {path: "/", redirect: "/imagesets/list/public"},

    {
        path: "*",
        name: "404",
        component: loadView("NotFound")
    }
]


/**
 * Dynamically import a component from its name
 */
function loadView(name: string) {
    return (resolve: (...modules: unknown[]) => void) => require(["@/views/" + name + ".vue"], resolve)
}


export const router = new VueRouter({
    mode: "history",
    routes
})


// guard to resolve user when a user is logged in
router.beforeResolve((to, from, next) => {
    if (VueInstance.$store.state.user.me.id == -1 && VueInstance.$store.state.auth.loggedIn) {
        VueInstance.$store.dispatch("retrieveMeUser")
            .catch(reason => console.error(reason))
            .finally(() => next())
    } else {
        next()
    }
})

router.onError(err => {
    alert(`That navigation did not work because ${err}`)
    throw err
})

router.beforeEach((toRoute, fromRoute, next) => {
    if (VueInstance)
        VueInstance.$store.commit("toggleCurrentlyLoading", true)
    next()
})


router.afterEach(() => {
    VueInstance.$store.commit("toggleCurrentlyLoading", false)
})
