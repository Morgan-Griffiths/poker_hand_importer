import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import ReviewHands from './views/ReviewHands.vue'
import ReviewModel from './views/ReviewModel.vue'
import PlayModel from './views/PlayModel.vue'

import App from './App.vue'

import './assets/styles.css'

const app = createApp(App)

const routes = [
  { path: '/review-hands', component: ReviewHands },
  { path: '/review-model', component: ReviewModel },
  { path: '/play-model', component: PlayModel }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

app.use(createPinia())
app.use(router)

app.mount('#app')
