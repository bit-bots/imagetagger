import VueRouter from 'vue-router'
import Vue from 'vue'

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
	routes
})

function loadView(name) {
	return resolve => require(['views/' + name + '.vue'], resolve)
}

export {
	router
}
