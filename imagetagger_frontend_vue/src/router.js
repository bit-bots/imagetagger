import VueRouter from 'vue-router'
import Vue from 'vue'

Vue.use(VueRouter)

const routes = [
	{
		path: '/',
		name: 'home',
		component: loadView('Home')
	},

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
