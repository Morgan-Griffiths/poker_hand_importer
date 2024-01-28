<template>
  <div class="bar-container">
    <div
      v-for="(probability, index) in probabilities[0]"
      :key="index"
      class="bar"
      :style="{
        height: probability * 100 + '%',
        backgroundColor: 'rgba(75, 192, 192, 0.8)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: '1px'
      }"
    >
      <div class="bar-label">{{ labels[index] }}</div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, type PropType } from 'vue'

export default defineComponent({
  name: 'BarChart',
  props: {
    probabilities: {
      type: Array as PropType<number[]>,
      required: true
    }
  },
  data() {
    return {
      // Define your component's data properties here
      labels: [
        'Fold',
        'Check',
        'Call',
        'B/R 1',
        'B/R 0.9',
        'B/R 0.75',
        'B/R 0.67',
        'B/R 0.5',
        'B/R 0.33',
        'B/R 0.25',
        'B/R 0.1'
      ]
    }
  }
})
</script>

<style>
.bar-container {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: flex-end;
  height: 100%;
}

.bar {
  flex: 1;
  margin: 0 5px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  align-items: center;
  position: relative;
  bottom: 10%;
}

.bar-label {
  position: absolute;
  bottom: -20px;
}
</style>
