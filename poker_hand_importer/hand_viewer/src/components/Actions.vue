<script lang="ts">
import { defineComponent } from 'vue'
import type { ServerResponse } from '@/mixins/Utils'
import { APIServer } from '../variables.js'

export default defineComponent({
  name: 'PokerHistory',
  props: {
    queryModel: {
      type: Boolean,
      required: true
    }
  },
  data() {
    return {}
  },
  methods: {
    async fetchData(endpoint: string) {
      // const modifiedEndpoint = this.queryModel ? `${endpoint}_inference` : endpoint
      const data: ServerResponse = await (await fetch(`${APIServer}/${endpoint}`)).json()
      this.$emit('update', data)
    }
  }
})
</script>

<template>
  <div class="action-bar">
    <ul class="action-items">
      <li @click="fetchData('previous')" class="action-item">Previous Action</li>
      <li @click="fetchData('step')" class="action-item">Next Action</li>
      <li @click="fetchData('reset')" class="action-item">Reset</li>
    </ul>
  </div>
</template>

<style scoped>
@import '../assets/styles.css';
.action-buttons {
  bottom: 3%;
  left: 25%;
  position: absolute;
  display: flex;
  font-size: 1.2rem;
  font-weight: 600;
}

.action-bar {
  margin: 0;
  display: flex;
  justify-content: center;
  position: fixed;
  bottom: 0;
  left: 200px;
  width: calc(100% - 200px);
  height: 60px;
  background-color: #ffffff;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.action-items {
  display: flex;
  justify-content: space-around;
  align-items: center;
  list-style: none;
  padding: 0;
  margin: 0;
  width: 100%;
  max-width: 1200px;
}

.action-item {
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  height: 100%;
  padding: 0 20px;
  font-size: 16px;
  font-weight: 500;
  color: #333;
  text-transform: uppercase;
}

.action-item:hover {
  background-color: #f5f5f5;
}
</style>
