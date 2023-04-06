const previousButton = document.querySelector(".btn-previous-action");
const nextButton = document.querySelector(".btn-next-action");
const resetButton = document.querySelector(".btn-reset");
const nextStateButton = document.querySelector(".btn-next-state");
const previousStateButton = document.querySelector(".btn-previous-state");
const APIServer = "http://localhost:4000/api";

SUITS_STOI = {
  C: 1,
  D: 2,
  H: 3,
  S: 4,
};
SUITS_ITOS = Object.fromEntries(
  Object.entries(SUITS_STOI).map((a) => a.reverse())
);
RANKS_ITOS = {
  1: "2",
  2: "3",
  3: "4",
  4: "5",
  5: "6",
  6: "7",
  7: "8",
  8: "9",
  9: "10",
  10: "J",
  11: "Q",
  12: "K",
  13: "A",
};
RANKS_STOI = Object.fromEntries(
  Object.entries(RANKS_ITOS).map((a) => a.reverse())
);

// POSITION_TO_SEAT = {
//   'Small Blind': 1,
//   'Big Blind': 2,
//   'UTG+2':3,
//   'UTG+1':4,
//   'UTG':5,
//   'Dealer':6
// }
const POSITIONS = ["SB", "BB", "UTG", "MP", "CO", "BTN"];
const POSITION_STOI = Object.fromEntries(POSITIONS.map((p, i) => [p, i + 1]));
const POSITION_ITOS = Object.fromEntries(
  Object.entries(POSITION_STOI).map((a) => a.reverse())
);
const STREET_ITOS = {
  1: "Preflop",
  2: "Flop",
  3: "Turn",
  4: "River",
};
const RAISE = "Raises";
const BET = "Bets";
const FOLD = "Folds";
const CALL = "Calls";
const CHECK = "Checks";
const BLIND = "blind";
const PREFLOP = "preflop";
const FLOP = "flop";
const TURN = "turn";
const RIVER = "river";
const betsizes = [1, 0.9, 0.75, 0.67, 0.5, 0.33, 0.25, 0.1];
const action_strs = ["None", FOLD, CHECK, CALL];
const action_type_to_int = Object.fromEntries(
  action_strs.map((a, i) => [a, i])
);
const action_betsize_to_int = Object.fromEntries(
  betsizes.map((b, i) => [b, i + 4])
);
const action_to_int = Object.assign(action_type_to_int, action_betsize_to_int);
const action_to_str = Object.fromEntries(
  Object.entries(action_to_int).map((a) => a.reverse())
);
let GAME_STATE = [];
let GAME_IDX = 0;

function isStatePadded(state) {
  return (
    state.vil1_active === 0 &&
    state.vil2_active === 0 &&
    state.vil3_active === 0 &&
    state.vil4_active === 0 &&
    state.vil5_active === 0
  );
}

async function callPreviousStep() {
  return await (await fetch(`${APIServer}/previous`)).json();
}

async function callStep() {
  return await (await fetch(`${APIServer}/step`)).json();
}

function updateGameIndex() {
  // updates the GAME_IDX to the number of child elements in the action-list
  const actionContainer = document.querySelector(".action-list");
  GAME_IDX = actionContainer.childElementCount;
}

previousButton.addEventListener("click", async (event) => {
  event.preventDefault();
  const data = await callPreviousStep();
  GAME_STATE = data;
  clearActions();
  next_decision_point(data);
  updateGameIndex();
  updateTargetAction(GAME_STATE.target_actions);
  updateTargetReward(GAME_STATE.target_rewards);
});

nextButton.addEventListener("click", async (event) => {
  event.preventDefault();
  const data = await callStep();
  GAME_STATE = data;
  instantiatePlayers();
  clearActions();
  next_decision_point(data);
  updateGameIndex();
  updateTargetAction(GAME_STATE.target_actions);
  updateTargetReward(GAME_STATE.target_rewards);
});

resetButton.addEventListener("click", async (event) => {
  event.preventDefault();
  const data = await (await fetch(`${APIServer}/reset`)).json();
  GAME_STATE = data;
  clearActions();
  next_decision_point(data);
  updateGameIndex();
  updateTargetAction(GAME_STATE.target_actions);
  updateTargetReward(GAME_STATE.target_rewards);
});

nextStateButton.addEventListener("click", async (event) => {
  event.preventDefault();
  if (GAME_STATE.length === 0) {
    GAME_IDX = -1;
  }
  if (
    GAME_STATE.length === 0 ||
    GAME_IDX === GAME_STATE.game_states.length ||
    isStatePadded(GAME_STATE.game_states[GAME_IDX])
  ) {
    let data = await callStep();
    GAME_STATE = data;
    instantiatePlayers();
    updateGameIndex();
  }
  console.log(
    "nextState",
    GAME_IDX,
    GAME_STATE.game_states.length,
    GAME_IDX === GAME_STATE.game_states.length
  );
  GAME_IDX = Math.min(GAME_IDX + 1, 23);
  displayState(GAME_STATE.game_states[GAME_IDX]);
  updateTargetAction(GAME_STATE.target_actions);
  updateTargetReward(GAME_STATE.target_rewards);
});
previousStateButton.addEventListener("click", async (event) => {
  event.preventDefault();
  if (GAME_STATE.length === 0 || GAME_IDX === 0) {
    let data = await callPreviousStep();
    GAME_STATE = data;
    GAME_IDX = data.game_states.length;
  }
  GAME_IDX = Math.max(GAME_IDX - 1, 0);
  clearActions();
  displayState(GAME_STATE.game_states[GAME_IDX]);
});

function instantiatePlayers() {
  for (let i = 1; i <= 6; i++) {
    const playerContainer = document.querySelector(`.player-${i}`);
    const cardsContainer = playerContainer.querySelector(".cards");

    for (let i = 0; i < 4; i++) {
      const cardElement = cardsContainer.querySelector(`.card-${i + 1}`);
      const cardCode = "card_back";
      toggleCardDisplay(cardElement, cardCode, false);
    }
  }
}

function updatePlayer(
  cards,
  stack,
  pos,
  active,
  isTurn,
  action,
  amount,
  is_blind
) {
  if (pos > 0) {
    if (cards) {
      card_images = convertCards(cards);
    } else {
      card_images = ["card_back", "card_back", "card_back", "card_back"];
    }
    // console.log("amount", amount);
    // console.log("is_blind", is_blind);
    const playerContainer = document.querySelector(`.player-${pos}`);
    const cardsContainer = playerContainer.querySelector(".cards");
    const stackContainer = playerContainer.querySelector(".stack");
    const actionContainer = playerContainer.querySelector(".last-action");
    const amountContainer = playerContainer.querySelector(".amount");
    const positionContainer = playerContainer.querySelector(".position");

    // update player's cards
    for (let i = 0; i < 4; i++) {
      const cardElement = cardsContainer.querySelector(`.card-${i + 1}`);
      const cardCode = card_images[i];
      toggleCardDisplay(cardElement, cardCode, true);
    }

    // update player's stack size
    // round to 2 decimal places
    stackContainer.textContent = `$${stack.toFixed(2)}`;
    positionContainer.textContent = `${POSITION_ITOS[pos]}`;

    // update dealer button display
    const dealerButton = playerContainer.querySelector(".dealer-chip");
    if (pos === 6) {
      dealerButton.style.display = "flex";
    } else {
      dealerButton.style.display = "none";
    }

    // update turn indicator
    if (isTurn) {
      if (is_blind) {
        actionContainer.textContent = "Posts";
      } else {
        actionContainer.textContent = action_to_str[action];
      }
      amountContainer.textContent = amount;
      playerContainer.classList.add("is-turn");
    } else {
      playerContainer.classList.remove("is-turn");
    }
  }
}

function toggleCardDisplay(cardElement, cardCode, isFaceUp) {
  if (isFaceUp) {
    cardElement.src = `images/4_color_cards/${cardCode}.png`;
  } else {
    cardElement.src = "images/4_color_cards/card_back.png";
  }
}

function main() {}
function updateBoard(boardCards) {
  boardCardImages = convertCards(boardCards);
  const boardContainer = document.querySelector(".board-cards");
  for (let i = 0; i < boardCardImages.length; i++) {
    const cardElement = boardContainer.querySelector(`.card-${i + 1}`);
    if (boardCardImages[i].startsWith("card_back")) {
      // set display none for the card
      toggleCardDisplay(cardElement, boardCardImages[i], false);
      continue;
    }
    const cardCode = boardCardImages[i];
    toggleCardDisplay(cardElement, cardCode, true);
  }
}

function convertCards(cards) {
  // cards is an array of numbers from 0 to 13. 0 is padding.1 is 2, 2 is 3, ..., 13 is A
  // the first number is the rank, the second number is the suit.
  // the card images are in images/4_color_cards/2C.png.
  card_images = [];
  for (let i = 0; i < cards.length; i += 2) {
    const rank = cards[i];
    const suit = cards[i + 1];
    if (rank === 0) {
      // padding
      card_images.push("card_back");
      continue;
    } else {
      const rankCode = RANKS_ITOS[rank];
      const suitCode = SUITS_ITOS[suit];
      card_images.push(`${rankCode}${suitCode}`);
    }
  }
  return card_images;
}

function updatePot(pot) {
  const potContainer = document.querySelector(".pot");
  potContainer.textContent = `Pot: $${pot.toFixed(2)}`;
}

function next_decision_point(data) {
  console.log("data", data);
  try {
    for (let i = 0; i < data.game_states.length; i++) {
      displayState(data.game_states[i]);
    }
  } catch (error) {
    console.error(`Error occurred while getting next action: ${error}`);
  }
}

function hidePlayer(position) {
  const playerContainer = document.querySelector(`.player-${position}`);
  playerContainer.style.display = "none";
}

function showPlayer(position) {
  const playerContainer = document.querySelector(`.player-${position}`);
  playerContainer.style.display = "block";
}

function clearActions() {
  const actionContainer = document.querySelector(".action-list");
  // remove all children
  while (actionContainer.firstChild) {
    actionContainer.removeChild(actionContainer.firstChild);
  }
}

function updateTargetAction(targetAction) {
  const actionContainer = document.querySelector(".action-list");
  // get last li element
  const lastAction = actionContainer.lastChild;
  // update text to incorporate target action
  lastAction.textContent += ` (Target Action:${action_to_str[targetAction]}`;
}

function updateTargetReward(targetReward) {
  const actionContainer = document.querySelector(".action-list");
  // get last li element
  const lastAction = actionContainer.lastChild;
  // update text to incorporate target action
  lastAction.textContent += ` (Target reward:${targetReward}`;
}

function updateHistory(game_state) {
  const actionContainer = document.querySelector(".action-list");
  // append a new li to the child ul
  // console.log("game_state", game_state);
  const newAction = document.createElement("li");
  if (game_state.previous_position === 0) {
    // street update
    newAction.textContent = `${STREET_ITOS[game_state.street]}`;
  } else {
    let action = game_state.previous_bet_is_blind
      ? "Posts"
      : action_to_str[game_state.previous_action];
    newAction.textContent = `Player ${
      POSITION_ITOS[game_state.previous_position]
    } ${action} $${game_state.previous_amount.toFixed(2)}`;
  }
  actionContainer.appendChild(newAction);
}

function displayState(game_state) {
  // check for padded games. If all players are inactive, break
  if (!isStatePadded(game_state)) {
    updateHistory(game_state);
    updatePot(game_state.pot);
    updateBoard(game_state.board_cards);
    for (let j = 1; j < 6; j++) {
      updatePlayer(
        null,
        game_state[`vil${j}_stack`],
        game_state[`vil${j}_position`],
        game_state[`vil${j}_active`],
        game_state.previous_position == game_state[`vil${j}_position`],
        game_state.previous_action,
        game_state.previous_amount,
        game_state.previous_bet_is_blind
      );
    }
    updatePlayer(
      game_state.hero_cards,
      game_state.hero_stack,
      game_state.hero_pos,
      game_state.hero_active,
      game_state.previous_position == game_state.hero_pos,
      game_state.previous_action,
      game_state.previous_amount,
      game_state.previous_bet_is_blind
    );
  }
}
