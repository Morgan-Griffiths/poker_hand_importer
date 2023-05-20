<script lang="ts">
import { defineComponent } from 'vue'
// const images = import.meta.glob('@/assets/images/4_color_cards/*.png');
export default defineComponent({
  name: 'PokerBoard',
  props: {
    boardCards: {
      type: Array,
      required: true
    },
    pot: {
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
  }
})
</script>

<template>
  <div
    class="board-cards"
    :class="{ 'model-review-position': modelReview, 'hand-review-position': !modelReview }"
  >
    <img
      v-for="(card, index) in boardCards"
      :key="index"
      class="card"
      :src="'/src/assets/images/4_color_cards/' + card + '.png'"
    />
  </div>
  <div
    class="pot"
    :class="{ 'pot-model-review-position': modelReview, 'pot-hand-review-position': !modelReview }"
  >
    Pot: ${{ pot.toFixed(2) }}
  </div>
</template>

<style scoped>
@import '../assets/cards.css';

.pot {
  bottom: 45%;
  left: 54%;
  position: absolute;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 2rem;
  font-weight: 600;
  color: #fff;
}

.pot-model-review-position {
  bottom: 35%;
}
.pot-hand-review-position {
  bottom: 45%;
}
.model-review-position {
  top: 48%;
}
.hand-review-position {
  top: 35%;
}
.board-cards {
  left: 41%;
  position: absolute;
  width: 38%;
  height: 17%;
  display: flex;
}
</style>
