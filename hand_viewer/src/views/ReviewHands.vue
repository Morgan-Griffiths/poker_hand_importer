<script lang="ts">
import { defineComponent } from 'vue'
import History from '../components/History.vue'
import Actions from '../components/Actions.vue'
import PokerTable from '../components/Table.vue'
import { APIServer } from '../variables.js'
import type { ServerResponse, State, PlayerType, LastAction, Present } from '@/mixins/Utils'
import Utils from '@/mixins/Utils'
import UpdateMethods from '@/updateMethods'

export default defineComponent({
  name: 'ReviewHands',
  components: {
    History,
    Actions,
    PokerTable
  },
  data(): {
    boardCards: string[]
    pot: number
    players: PlayerType[]
    present: Present
    history: string[]
    modelInference: boolean
    lastActionsPerPlayer: LastAction
  } {
    return {
      // Define your component's data properties here
      boardCards: ['card_back', 'card_back', 'card_back', 'card_back', 'card_back'],
      pot: 0,
      players: [],
      present: {},
      history: [],
      modelInference: false,
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
    // Define your component's methods here
    updateState(data: ServerResponse) {
      console.log('data', data)
      this.history = []
      let first = false
      try {
        for (let i = 0; i < data.game_states.length; i++) {
          if (!Utils.isStatePadded(data.game_states[i])) {
            if (!first) {
              UpdateMethods.recordPresent(this.present, data.game_states[i])
              first = true
            }
            this.processState(data.game_states[i])
          }
        }
        this.updatePlayers(data.game_states[data.game_states.length - 1], this.lastActionsPerPlayer)
        this.history.push(
          `Target action: ${Utils.convertAction(
            data.target_actions,
            data.game_states[23].last_agro_action
          )}, Target reward: ${data.target_rewards.toFixed(2)}`
        )
      } catch (error) {
        console.error(`Error occurred while getting next action: ${error}`)
      }
    },
    processState(game_state: State) {
      // check for padded games. If all players are inactive, break
      this.updateHistory(game_state)
      this.pot = game_state.pot
      this.updateBoard(game_state.board_cards)
      Utils.updateLastAction(game_state, this.lastActionsPerPlayer)
    },
    updateHistory(game_state: State) {
      this.history.push(UpdateMethods.updateHistory(game_state))
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
    this.updateState(data)
  }
})
</script>

<template>
  <History :history="history" />
  <PokerTable
    :players="players"
    :board-cards="boardCards"
    :pot="pot"
    :model-review="modelInference"
  />
  <Actions @update="updateState" :query-model="modelInference" />
</template>

<style>
/* If you have styles in a separate file, you can copy them here */
/* If you want to keep the styles in a separate file, you can use the following syntax: */
@import '../assets/styles.css';
</style>
