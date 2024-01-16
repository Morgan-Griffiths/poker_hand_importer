<template>
    <div class="model-outputs">
        <div class="model-headers">
            <div class="header">Hand Strength</div>
            <div class="header">Win Probability</div>
            <div class="header">Pot Equity</div>
        </div>
        <div class="model-values">
            <div class="value">0.5</div>
            <div class="value">0.5</div>
            <div class="value">0.5</div>
        </div>
    </div>
  </template>
  
  <script lang="ts">
  export default {
    name: 'ModelOutputs',
    data() {
      return {
        // Define your component's data properties here
        betsizes : [1, 0.9, 0.75, 0.67, 0.5, 0.33, 0.25, 0.1],
        action_itos : {0: 'FOLD', 1: 'CHECK', 2: 'CALL',3:1,4:0.9,5:0.75,6:0.67,7:0.5,8:0.33,9:0.25,10:0.1},
      };
    },
  };
  </script>
  
  <style scoped>
  .model-outputs {
    position: absolute;
    top: 60px;
    left: 200px;
    width: calc(100% - 130px);
    height: 130px;
    background-color: blanchedalmond;
  }
  .model-headers {
    display: flex;
    justify-content: space-around;
    align-items: center;
    list-style: none;
  }
  .model-values {
    display: flex;
    justify-content: space-around;
    align-items: center;
    list-style: none;
  }
  </style>
  