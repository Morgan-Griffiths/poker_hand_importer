import { createRouter, createWebHistory } from 'vue-router'
import ReviewHands from '../views/ReviewHands.vue'
import PlayModel from '../views/PlayModel.vue'
import ReviewModel from '../views/ReviewModel.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: ReviewHands
    },
    {
      path: '/',
      name: 'home',
      component: ReviewModel
    },
    {
      path: '/',
      name: 'home',
      component: PlayModel
    }
  ]
})

export default router
