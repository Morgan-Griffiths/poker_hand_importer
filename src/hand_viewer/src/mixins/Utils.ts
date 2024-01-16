// type an array of 50 numbers

import { POSITION_ITOS, RANKS_ITOS, SUITS_ITOS } from '@/variables'

export type State = {
  hero_cards: Array<number>
  board_cards: Array<number>
  street: number
  num_players: number
  hero_pos: number
  hero_active: number
  vil1_active: number
  vil2_active: number
  vil3_active: number
  vil4_active: number
  vil5_active: number
  vil1_position: number
  vil2_position: number
  vil3_position: number
  vil4_position: number
  vil5_position: number
  last_agro_amount: number
  last_agro_action: number
  last_agro_position: number
  last_agro_is_blind: number
  hero_stack: number
  vil1_stack: number
  vil2_stack: number
  vil3_stack: number
  vil4_stack: number
  vil5_stack: number
  pot: number
  amount_to_call: number
  pot_odds: number
  previous_amount: number
  previous_action: number
  previous_position: number
  previous_bet_is_blind: number
  current_player: number
  next_player: number
}

export type PositionsITOS = {
  [key: number]: string
}

export type Present = {
  [key: number]: number
}

export type PlayerType = {
  position: number
  stack: number
  hand: Array<string>
  is_active: number
  is_turn: boolean
  action: number
  amount: number
  is_blind: number
  is_present: number
}

export type LastAction = { [key: number]: { action: number; amount: number; is_blind: number } }

export type ServerGameResponse = {
  game_states: State[]
  done: boolean
  winnings: {
    [key: number]: {
      hand_value: number
      hand: Array<number>
      result: number
    }
  }
  action_mask: Array<number>
  current_player: number
  model_outputs: Array<number>
}
// state,obs,self.game_over(),action_mask,betsize_mask

export type ServerResponse = {
  game_states: State[]
  target_actions: number
  target_rewards: number
}

export type ActionHistory = {
  history: Array<string>
}

export function isStatePadded(state: State) {
  return (
    state.vil1_active === 0 &&
    state.vil2_active === 0 &&
    state.vil3_active === 0 &&
    state.vil4_active === 0 &&
    state.vil5_active === 0
  )
}
export function convertCards(cards: Array<number>) {
  // cards is an array of numbers from 0 to 13. 0 is padding.1 is 2, 2 is 3, ..., 13 is A
  // the first number is the rank, the second number is the suit.
  // the card images are in images/4_color_cards/2C.png.
  const card_images = []
  for (let i = 0; i < cards.length; i += 2) {
    const rank = cards[i]
    const suit = cards[i + 1]
    if (rank === 0) {
      // padding
      card_images.push('card_back')
      continue
    } else {
      const rankCode = RANKS_ITOS[rank]
      const suitCode = SUITS_ITOS[suit]
      card_images.push(`${rankCode}${suitCode}`)
    }
  }
  return card_images
}

export function convertCardsToReadable(cards: Array<number>) {
  // cards is an array of numbers from 0 to 13. 0 is padding.1 is 2, 2 is 3, ..., 13 is A
  // the first number is the rank, the second number is the suit.
  // the card images are in images/4_color_cards/2C.png.
  const readable_cards = []
  for (let i = 0; i < cards.length; i += 2) {
    const rank = cards[i]
    const suit = cards[i + 1]
    const rankCode = RANKS_ITOS[rank]
    const suitCode = SUITS_ITOS[suit]

    // lower case the suit code
    readable_cards.push(`${rankCode}${suitCode.toLowerCase()}`)
  }
  return readable_cards
}

export function updateLastAction(game_state: State, lastActionsPerPlayer: LastAction) {
  lastActionsPerPlayer[game_state.previous_position] = {
    action: game_state.previous_action,
    amount: game_state.previous_amount,
    is_blind: game_state.previous_bet_is_blind
  }
}

export function convertAction(action: number, previousAction: number) {
  if (action === 0) {
    return 'None'
  } else if (action === 1) {
    return 'Folds'
  } else if (action === 2) {
    return 'Checks'
  } else if (action === 3) {
    return 'Calls'
  } else if (previousAction > 2) {
    return 'Raises'
  } else {
    return 'Bets'
  }
}

export function gray_out_buttons(done: Boolean, action_mask: Array<number>) {
  if (done) {
    // gray out all action buttons. They go from 'action-0' to 'action-10'
    const actionButtons = document.getElementsByClassName('action-item')
    for (let i = 0; i < actionButtons.length - 1; i++) {
      actionButtons[i].classList.add('disabled')
    }
  } else {
    action_mask.forEach((action, index) => {
      if (action === 0) {
        const actionButton = document.getElementById(`action-${index}`)
        if (actionButton) {
          actionButton.classList.add('disabled')
        }
      } else {
        // remove disabled class if action is enabled
        const actionButton = document.getElementById(`action-${index}`)
        if (actionButton) {
          actionButton.classList.remove('disabled')
        }
      }
    })
  }
}

export function end_of_game_action_history(
  history: String[],
  winnings: { [key: number]: { result: number; hand: Array<number>; hand_value: number } },
  players: PlayerType[]
) {
  history.push(`Game over.`)
  history.push(`Result.`)
  history.push(
    `${Object.keys(winnings)
      .map((key) => {
        const numKey = parseInt(key, 10)
        return `${POSITION_ITOS[numKey]}: ${winnings[numKey].result}\n`
      })
      .join(' ')}`
  )
  // show the hands for the relevant players
  // If more than 1 player is active then showdown
  const showdown = players.filter((player) => player.is_active).length > 1
  if (showdown) {
    history.push(`Showdown.`)
    history.push(
      `${Object.keys(winnings)
        .map((key) => {
          const numKey = parseInt(key, 10)
          return `${POSITION_ITOS[numKey]}: ${convertCardsToReadable(winnings[numKey].hand)}\n`
        })
        .join(' ')}`
    )
    history.push(`Hand ranks.`)
    history.push(
      `${Object.keys(winnings)
        .map((key) => {
          const numKey = parseInt(key, 10)
          return `${POSITION_ITOS[numKey]}: ${winnings[numKey].hand_value}\n`
        })
        .join(' ')}`
    )
    for (const player of players) {
      if (player.position in winnings) {
        player.hand = convertCards(winnings[player.position].hand)
      }
    }
  }
}

export default {
  isStatePadded,
  convertCards,
  convertAction,
  updateLastAction,
  gray_out_buttons,
  convertCardsToReadable,
  end_of_game_action_history
}
