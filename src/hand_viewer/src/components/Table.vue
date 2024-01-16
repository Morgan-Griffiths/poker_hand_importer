<script lang="ts">
import { defineComponent } from 'vue'
import Player from './Player.vue'
import Board from './Board.vue'
import type { PlayerType } from '@/mixins/Utils'

export default defineComponent({
  name: 'PokerTable',
  components: {
    Player,
    Board
  },
  props: {
    // Define your component's props here
    players: {
      type: Object as () => Array<PlayerType>,
      required: true
    },
    pot: {
      type: Number,
      required: true
    },
    boardCards: {
      type: Array,
      required: true
    },
    modelReview: {
      type: Boolean,
      required: true
    }
  },
  data() {
    return {
      // Define your component's data properties here
      dataProperty: 'example property value'
    }
  },
  methods: {
    // Define your component's methods here
    exampleMethod() {}
  }
})
</script>

<template>
  <div class="play-area">
    <Board :board-cards="boardCards" :pot="pot" :modelReview="modelReview" />
    <Player
      v-for="(player, index) in players"
      :key="index"
      :player="player"
      :player-number="index + 1"
      :model-review="modelReview"
    />
  </div>
</template>

<style>
/* If you have styles in a separate file, you can copy them here */
/* If you want to keep the styles in a separate file, you can use the following syntax: */
@import '../assets/styles.css';
</style>
