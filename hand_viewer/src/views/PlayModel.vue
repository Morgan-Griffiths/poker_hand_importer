<script lang="ts">
import { defineComponent } from 'vue'
import History from '../components/History.vue'
import PlayActions from '../components/PlayActions.vue'
import PokerTable from '../components/Table.vue'
import ProbabilityChart from '../components/ProbabilityChart.vue'
import { APIServer, POSITION_ITOS } from '../variables.js'
import type { State, PlayerType, ServerGameResponse, LastAction, Present } from '@/mixins/Utils'
import Utils from '@/mixins/Utils'
import UpdateMethods from '@/updateMethods'
import { watchEffect } from 'vue'
import Actions from '@/components/Actions.vue'

export default defineComponent({
  name: 'ReviewHands',
  components: {
    History,
    PlayActions,
    PokerTable,
    ProbabilityChart
  },
  data(): {
    boardCards: string[]
    pot: number
    players: PlayerType[]
    present: Present
    history: string[]
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
      // lastActionsPerPlayer is a dictionary that stores the last action taken by each player
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
    async updateState(data: ServerGameResponse) {
      console.log('data', data.winnings, data.done, data.game_states, data.action_mask)
      this.probabilities = data.model_outputs
      this.history = []
      let first = false
      for (let i = 0; i < data.game_states.length; i++) {
        if (!Utils.isStatePadded(data.game_states[i])) {
          if (!first) {
            UpdateMethods.recordPresent(this.present, data.game_states[i])
            first = true
          }
          console.log('present', this.present)
          this.processState(data.game_states[i])
        }
      }
      this.updatePlayers(data.game_states[data.game_states.length - 1], this.lastActionsPerPlayer)

      Utils.gray_out_buttons(data.done, data.action_mask)
      if (data.done) {
        Utils.end_of_game_action_history(this.history, data.winnings, this.players)
        const showdown = this.players.filter((player) => player.is_active).length > 1
        if (showdown) {
          // display all board cards
        }
      }

      // const modelOutputs = await (await fetch(`${APIServer}/inference`)).json()
      // this.probabilities = modelOutputs.model_outputs
      // console.log('last state', data.game_states[23])
      // console.log('modelOutputs', modelOutputs.model_outputs)

      // this.history.push(
      //   `Target action: ${Utils.convertAction(
      //     data.target_actions,
      //     data.game_states[23].last_agro_action
      //   )}, Target reward: ${data.target_rewards.toFixed(2)}`
      // )
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
    const data: ServerGameResponse = await (await fetch(`${APIServer}/reset_game`)).json()
    // const modelOutputs = await (await fetch(`${APIServer}/inference`)).json()
    // watchEffect(() => {
    //   this.probabilities = modelOutputs.model_outputs
    //   console.log('modelOutputs', modelOutputs.model_outputs)
    this.updateState(data)
    // })
  }
})
</script>

<template>
  <History :history="history" />
  <ProbabilityChart :probabilities="probabilities" />
  <PokerTable :players="players" :board-cards="boardCards" :pot="pot" :model-review="modelReview" />
  <PlayActions @update="updateState" :query-model="true" />
</template>

<style>
@import '../assets/styles.css';
</style>
