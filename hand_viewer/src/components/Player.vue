<script lang="ts">
import { defineComponent } from 'vue'
import { POSITION_ITOS } from '../variables.js'
import Utils from '@/mixins/Utils'

export default defineComponent({
  name: 'PokerPlayer',
  props: {
    player: {
      type: Object,
      required: true
    },
    playerNumber: {
      type: Number,
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
  },
  computed: {
    positionITOS() {
      return POSITION_ITOS
    },
    utilConvertAction() {
      return Utils.convertAction
    }
  }
})
</script>

<template>
  <div
    v-if="player.position !== 0"
    class="player"
    :class="modelReview ? 'player-model-' + playerNumber : 'player-' + playerNumber"
  >
    <div class="highlighted" v-if="player.is_turn">{{ player.is_turn }}</div>
    <div class="cards">
      <img
        v-for="(card, index) in player.hand"
        class="card"
        :class="'card-' + (index + 1)"
        :key="index"
        :src="'/src/assets/images/4_color_cards/' + card + '.png'"
      />
    </div>
    <div class="player-info">
      <div class="stack">{{ player.stack?.toFixed(2) }}</div>
      <div class="action-container">
        <div class="last-action">
          <!-- {{ utilConvertAction(player.action, player.last_agro_action) }} -->
        </div>
        <div class="amount">{{ player.amount.toFixed(2) }}</div>
        <div class="position">{{ positionITOS[player.position] }}</div>
      </div>
    </div>
    <div class="dealer-chip" :style="modelReview && player.position == 6 ? 'display: flex' : ''">
      D
    </div>
  </div>
</template>

<style scoped>
@import '../assets/cards.css';

.player {
  position: absolute;
  width: 150px;
  height: 200px;
}
.player .cards {
  position: relative;
}

.player .cards img {
  position: absolute;
  top: 0;
  left: 0;
  z-index: 1;
}

.player .cards img:nth-child(1) {
  z-index: 2;
  transform: translateX(-91px);
}

.player .cards img:nth-child(2) {
  z-index: 2;
  transform: translateX(-51px);
}

.player .cards img:nth-child(3) {
  z-index: 3;
  transform: translateX(-11px);
}

.player .cards img:nth-child(4) {
  z-index: 4;
  transform: translateX(28px);
}

.player-info {
  height: 10%;
  width: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  border-radius: 5px;
  padding: 5px;
  margin-top: 5px;
  transform: translateY(-95px);
}

.dealer-chip {
  transform: translateY(-38px);
  height: 20px;
  width: 20px;
  line-height: 20px;
  border-radius: 10px;
  background-color: white;
  color: black;
  margin-left: 10px;
  justify-content: center;
  display: none;
}

.stack {
  /* left: 50%; */
  /* transform: translate(-50%, -40px); */
  background-color: white;
  padding: 5px 10px;
  border-radius: 5px;
  font-size: 16px;
}

.last-action {
  top: 50%;
  /* transform: translate(-50%, -40px); */
  background-color: white;
  padding: 5px 10px;
  border-radius: 5px;
  font-size: 16px;
}

.amount {
  background-color: white;
  padding: 5px 10px;
  border-radius: 5px;
  font-size: 16px;
}

.position {
  background-color: white;
  padding: 5px 10px;
  border-radius: 5px;
  font-size: 16px;
}

.action-container {
  display: flex;
}

.player-1 {
  top: 10%;
  left: 36%;
}

.player-2 {
  top: 10%;
  left: 61%;
}

.player-3 {
  top: 37%;
  left: 81%;
}

.player-4 {
  top: 66%;
  left: 61%;
}

.player-5 {
  top: 66%;
  left: 36%;
}

.player-6 {
  top: 37%;
  left: 20%;
}

.player-model-1 {
  top: 29%;
  left: 36%;
}

.player-model-2 {
  top: 29%;
  left: 61%;
}

.player-model-3 {
  top: 50%;
  left: 81%;
}

.player-model-4 {
  top: 71%;
  left: 61%;
}

.player-model-5 {
  top: 71%;
  left: 36%;
}

.player-model-6 {
  top: 50%;
  left: 20%;
}
</style>
