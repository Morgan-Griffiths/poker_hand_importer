<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'PokerHistory',
  props: {
    history: {
      type: Array,
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
  <div class="action-history">
    <ul class="action-list">
      <li v-for="(action, index) in history" :key="index">
        {{ action }}
      </li>
    </ul>
  </div>
</template>

<style scoped>
.action-history {
  height: calc(100% - 60px);
  position: absolute;
  top: 60px;
  /* bottom: 60px; */
  width: 200px;
  flex: 0 0 auto;
  background: rgba(0, 0, 0, 0.6);
  box-shadow: 0px 0px 4px 3px rgba(0, 0, 0, 0.3);
  overflow-y: scroll;
}

.action-history ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

.action-history ul li {
  margin-bottom: 5px;
  font-size: 1.2rem;
  line-height: 1.5;
  color: #fff;
}
</style>
