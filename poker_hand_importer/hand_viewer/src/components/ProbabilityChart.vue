<template>
  <div class="chart-container">
    <BarChartVue :probabilities="probabilities" />
  </div>
</template>

<script lang="ts">
import { defineComponent, type PropType } from 'vue'
import BarChartVue from './BarChart.vue'

export default defineComponent({
  name: 'ProbabilityBarChart',
  components: {
    BarChartVue
  },
  props: {
    probabilities: {
      type: Array as PropType<number[]>,
      required: true
    }
  }
})
</script>

<style>
.chart-container {
  width: calc(100% - 200px);
  height: 200px;
  position: absolute;
  left: 200px;
  top: 65px;
  overflow: hidden;
  background-color: beige;
}
</style>
