import Vue from 'vue'
import {router} from 'src/router'
import {store} from 'src/store'
import './main.scss'

const app = new Vue({
    router,
    store,
}).$mount('#app');
