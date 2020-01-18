import Vue from 'vue'
import {router} from './router'
import {store} from './store'
import './main.scss'

const app = new Vue({
    router,
    store,
}).$mount('#app');
