import VueRouter from 'vue-router'
import Vue from 'vue'
import {store} from "src/store";

Vue.use(VueRouter)

const routes = [
	{
		path: '/imagesets/list/:filter',
		name: 'dashboard',
		component: loadView('Dashboard')
	},

	{path: '/', redirect: '/imagesets/list/public'},

	{
		path: '*',
		name: '404',
		component: loadView('404')
	}
]

const router = new VueRouter({
	mode: 'history',
	routes,
})

router.beforeEach((to, from, next) => {
	store.commit('toggleCurrentlyLoading')
	next()
})

router.afterEach((to, from) => {
	store.commit('toggleCurrentlyLoading')
})

function loadView(name) {
	return resolve => require(['views/' + name + '.vue'], resolve)
}

export {
	router
}
