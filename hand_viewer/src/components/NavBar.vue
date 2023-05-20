<template>
  <nav class="nav-bar">
    <ul class="nav-items">
      <RouterLink class="nav-item" to="/review-hands">
        <li>Review Hands</li>
      </RouterLink>
      <RouterLink class="nav-item" to="/review-model">
        <li>Review Model</li>
      </RouterLink>
      <RouterLink class="nav-item" to="/play-model">
        <li>Play Model</li>
      </RouterLink>
      <li class="nav-item settings">Settings
        <!-- <img src="path/to/your/settings-gear-icon.svg" alt="Settings" /> -->
      </li>
    </ul>
  </nav>
</template>


  <script lang="ts">
  // import { RouterLink } from 'vue-router'
  export default {
    name: 'TopNavBar',
  };
  </script>
  
  <style scoped>
  /* @import '../assets/styles.css'; */
  .nav-bar {
    margin: 0;
    display: flex;
    justify-content: center;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 60px;
    background-color: #ffffff;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    z-index: 1000;
  }
  
  .nav-items {
    display: flex;
    justify-content: space-around;
    align-items: center;
    list-style: none;
    padding: 0;
    margin: 0;
    width: 100%;
    max-width: 1200px;
  }
  
  .nav-item {
    font-family: sans-serif;
    text-decoration: none;
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

  .nav-item:hover {
    background-color: #f5f5f5;
  }
  
  .settings img {
    width: 24px;
    height: 24px;
  }
  </style>
  