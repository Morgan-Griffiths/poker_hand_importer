<script lang="ts">
import { defineComponent } from 'vue'
import History from '../components/History.vue'
import Actions from '../components/Actions.vue'
import PokerTable from '../components/Table.vue'
import ProbabilityChart from '../components/ProbabilityChart.vue'
import { APIServer } from '../variables.js'
import type { ServerResponse, State, PlayerType, LastAction, Present } from '@/mixins/Utils'
import Utils from '@/mixins/Utils'
import UpdateMethods from '@/updateMethods'
import { watchEffect } from 'vue'

export default defineComponent({
  name: 'ReviewHands',
  components: {
    History,
    Actions,
    PokerTable,
    ProbabilityChart
  },
  data(): {
    boardCards: string[]
    pot: number
    players: PlayerType[]
    history: string[]
    present: Present
    modelReview: boolean
    probabilities: number[]
    lastActionsPerPlayer: LastAction
  } {
    return {
      // Define your component's data properties here
      boardCards: ['card_back', 'card_back', 'card_back', 'card_back', 'card_back'],
      pot: 0,
      players: [],
      present: {},
      history: [],
      modelReview: true,
      probabilities: Array(11).fill(0),
      lastActionsPerPlayer: {
        1: { action: 0, amount: 0, is_blind: 0 },
        2: { action: 0, amount: 0, is_blind: 0 },
        3: { action: 0, amount: 0, is_blind: 0 },
        4: { action: 0, amount: 0, is_blind: 0 },
        5: { action: 0, amount: 0, is_blind: 0 },
        6: { action: 0, amount: 0, is_blind: 0 }
      }
    }
  },
  mixins: [Utils],
  methods: {
    async updateState(data: ServerResponse) {
      // states are bottom padded
      const modelOutputs = await (await fetch(`${APIServer}/inference`)).json()
      this.probabilities = modelOutputs.model_outputs
      console.log('data', data)
      console.log('first state', data.game_states[0])
      console.log('modelOutputs', modelOutputs.model_outputs)
      this.history = []
      try {
        for (let i = 0; i < data.game_states.length; i++) {
          if (!Utils.isStatePadded(data.game_states[i])) {
            UpdateMethods.recordPresent(this.present, data.game_states[i])
            this.processState(data.game_states[i])
          } else {
            this.updatePlayers(data.game_states[i - 1], this.lastActionsPerPlayer)
            this.history.push(
              `Target action: ${Utils.convertAction(
                data.target_actions,
                data.game_states[i-1].last_agro_action
              )}, Target reward: ${data.target_rewards.toFixed(2)}`
            )
            break
          }
        }
      } catch (error) {
        console.error(`Error occurred while getting next action: ${error}`)
      }
    },
    processState(game_state: State) {
      // check for padded games. If all players are inactive, break
      this.history.push(UpdateMethods.updateHistory(game_state))
      this.pot = game_state.pot
      this.updateBoard(game_state.board_cards)
      Utils.updateLastAction(game_state, this.lastActionsPerPlayer)
    },
    updateBoard(board_cards: number[]) {
      this.boardCards = UpdateMethods.updateBoard(board_cards)
    },
    updatePlayers(game_state: State, lastActionsPerPlayer: LastAction) {
      this.players = []
      this.players = UpdateMethods.updatePlayers(game_state, lastActionsPerPlayer, this.present)
    }
  },
  async mounted() {
    const data: ServerResponse = await (await fetch(`${APIServer}/reset`)).json()
    const modelOutputs = await (await fetch(`${APIServer}/inference`)).json()
    watchEffect(() => {
      this.probabilities = modelOutputs.model_outputs[0]
      console.log('probabilities', modelOutputs.model_outputs[0])
      this.updateState(data)
    })
  }
})
</script>

<template>
  <History :history="history" />
  <ProbabilityChart :probabilities="probabilities" />
  <PokerTable :players="players" :board-cards="boardCards" :pot="pot" :model-review="modelReview" />
  <Actions @update="updateState" :query-model="true" />
</template>

<style>
@import '../assets/styles.css';
</style>
