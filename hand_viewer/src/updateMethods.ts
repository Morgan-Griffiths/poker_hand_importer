import type { State, PlayerType, LastAction, Present } from '@/mixins/Utils'
import { action_to_str, POSITION_ITOS, STREET_ITOS } from './variables.js'
import Utils from '@/mixins/Utils'

export default {
  updateHistory(game_state: State) {
    let actionText
    if (game_state.previous_position === 0) {
      // street update
      actionText = `${STREET_ITOS[game_state.street]}`
    } else {
      const action = game_state.previous_bet_is_blind
        ? 'Posts'
        : action_to_str[game_state.previous_action]
      actionText = `Player ${
        POSITION_ITOS[game_state.previous_position]
      } ${action} $${game_state.previous_amount.toFixed(2)}`
    }
    return actionText
  },
  updateBoard(board_cards: number[]) {
    return Utils.convertCards(board_cards)
  },
  recordPresent(present: Present, game_state: State) {
    // set is_present to true for active players
    for (let j = 1; j < 6; j++) {
      const vil_position = getValueFromState(
        game_state,
        `vil${j}_position` as keyof State
      ) as number
      const vil_active = getValueFromState(game_state, `vil${j}_active` as keyof State) as number
      present[vil_position] = vil_active
    }
    const hero_position = getValueFromState(game_state, 'hero_position' as keyof State) as number
    const hero_active = getValueFromState(game_state, 'hero_active' as keyof State) as number
    present[hero_position] = hero_active
  },
  updatePlayers(game_state: State, lastActionsPerPlayer: LastAction, is_present: Present) {
    const players: PlayerType[] = []
    console.log('game_state', game_state)
    for (let j = 1; j < 6; j++) {
      players.push({
        hand: ['card_back', 'card_back', 'card_back', 'card_back'],
        stack: game_state[`vil${j}_stack` as keyof typeof game_state] as number,
        position: game_state[`vil${j}_position` as keyof typeof game_state] as number,
        is_active: game_state[`vil${j}_active` as keyof typeof game_state] as number,
        is_turn:
          game_state.current_player === game_state[`vil${j}_position` as keyof typeof game_state],
        action: lastActionsPerPlayer[j].action,
        amount: lastActionsPerPlayer[j].amount,
        is_blind: lastActionsPerPlayer[j].is_blind,
        is_present: is_present[game_state[`vil${j}_position` as keyof typeof game_state] as number]
      })
    }
    players.push({
      hand: Utils.convertCards(game_state.hero_cards),
      stack: game_state[`hero_stack` as keyof typeof game_state] as number,
      position: game_state[`hero_position` as keyof typeof game_state] as number,
      is_active: game_state[`hero_active` as keyof typeof game_state] as number,
      is_turn: game_state.current_player === game_state[`hero_position` as keyof typeof game_state],
      action: game_state.previous_action,
      amount: game_state.previous_amount,
      is_blind: game_state.previous_bet_is_blind,
      is_present: is_present[game_state[`hero_position` as keyof typeof game_state] as number]
    })
    const present_players = players.filter((player) => player.is_present === 1)
    present_players.sort((a, b) => a.position - b.position)
    // rotate players until hero is in index 0
    while (
      present_players[0].position !==
      (game_state[`hero_position` as keyof typeof game_state] as number)
    ) {
      const lastPlayer = present_players.pop()
      if (lastPlayer) {
        present_players.unshift(lastPlayer)
      }
    }
    // pad players with empty objects
    while (present_players.length < 6) {
      present_players.push({
        hand: [],
        stack: 0,
        position: 0,
        is_active: 0,
        is_turn: false,
        action: 0,
        amount: 0,
        is_blind: 0,
        is_present: 0
      })
    }
    return present_players
  }
}
function getValueFromState<T extends keyof State>(game_state: State, key: T): State[T] {
  return game_state[key]
}
