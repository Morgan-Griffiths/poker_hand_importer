export const APIServer = 'http://localhost:4000/api'

export const SUITS_STOI = {
  C: 1,
  D: 2,
  H: 3,
  S: 4
}
export const SUITS_ITOS = Object.fromEntries(Object.entries(SUITS_STOI).map((a) => a.reverse()))
export const RANKS_ITOS = {
  1: '2',
  2: '3',
  3: '4',
  4: '5',
  5: '6',
  6: '7',
  7: '8',
  8: '9',
  9: '10',
  10: 'J',
  11: 'Q',
  12: 'K',
  13: 'A'
}
export const RANKS_STOI = Object.fromEntries(Object.entries(RANKS_ITOS).map((a) => a.reverse()))
export const POSITIONS = ['SB', 'BB', 'UTG', 'MP', 'CO', 'BTN']
export const POSITION_STOI = Object.fromEntries(POSITIONS.map((p, i) => [p, i + 1]))
export const POSITION_ITOS = Object.fromEntries(
  Object.entries(POSITION_STOI).map((a) => a.reverse())
)
export const STREET_ITOS = {
  1: 'Preflop',
  2: 'Flop',
  3: 'Turn',
  4: 'River'
}
export const RAISE = 'Raises'
export const BET = 'Bets'
export const FOLD = 'Folds'
export const CALL = 'Calls'
export const CHECK = 'Checks'
export const BLIND = 'blind'
export const PREFLOP = 'preflop'
export const FLOP = 'flop'
export const TURN = 'turn'
export const RIVER = 'river'
export const betsizes = [1, 0.9, 0.75, 0.67, 0.5, 0.33, 0.25, 0.1]
export const action_strs = ['None', FOLD, CHECK, CALL]
export const action_type_to_int = Object.fromEntries(action_strs.map((a, i) => [a, i]))
export const action_betsize_to_int = Object.fromEntries(betsizes.map((b, i) => [b, i + 4]))
export const action_to_int = Object.assign(action_type_to_int, action_betsize_to_int)
export const action_to_str = Object.fromEntries(
  Object.entries(action_to_int).map((a) => a.reverse())
)
export const GAME_STATE = []
export const GAME_IDX = 0
