from collections import namedtuple
import numpy as np

Action = namedtuple(
    "Action",
    [
        "position",
        "is_hero",
        "action_type",
        "amount",
        "street_total",
        "bet_ratio",
        "is_blind",
        "pot",
        "rake",
        "last_aggressor_index",
        "num_active_players",
        "action_order",
    ],
)
Street = namedtuple("Street", ["street_type", "board_cards"])
Player = namedtuple(
    "Player", ["stack", "hole_cards", "position", "is_hero", "winnings"]
)

RAISE = "Raises"
BET = "Bets"
FOLD = "Folds"
CALL = "Calls"
CHECK = "Checks"
BLIND = "blind"
PREFLOP = "preflop"
FLOP = "flop"
TURN = "turn"
RIVER = "river"


def return_max_potlimit_betsize(
    previous_aggro_action: Action,
    current_player_stack: float,
    current_player_street_total: float,
    last_aggro_street_total: float,
    pot: float,
    bb: float,
    penultimate_betsize: float,
):
    """
    bet_fraction in POTLIMIT is a float [0,1] representing fraction of pot.
    this function returns raise sizes starting at min raise. Typical ratios are calculated starting at previous raise.
    """
    assert isinstance(current_player_stack, float), type(current_player_stack)
    assert isinstance(current_player_street_total, float), type(
        current_player_street_total
    )
    assert isinstance(last_aggro_street_total, float), type(last_aggro_street_total)
    assert isinstance(pot, float), type(pot)
    if previous_aggro_action is None:
        max_betsize = min(current_player_stack, pot)
        min_betsize = 0
    elif previous_aggro_action.action_type == BET:  # Bet
        max_betsize = min(pot + 2 * previous_aggro_action.amount, current_player_stack)
        min_betsize = min(2 * previous_aggro_action.amount, current_player_stack)
    elif previous_aggro_action.action_type == RAISE:  # Raise
        max_betsize = min(
            (2 * previous_aggro_action.street_total)
            + (pot - current_player_street_total),
            current_player_stack + current_player_street_total,
        )
        min_betsize = min(
            max(
                2 * (previous_aggro_action.street_total - penultimate_betsize)
                + penultimate_betsize,
                2 * bb,
            ),
            current_player_stack + current_player_street_total,
        )
    else:
        max_betsize = 0
        min_betsize = 0
    return (min_betsize, max_betsize)


def return_standard_max_potlimit_betsize(
    previous_aggro_action: Action,
    current_player_stack: float,
    current_player_street_total: float,
    last_aggro_street_total: float,
    pot: float,
    bb: float,
    penultimate_betsize: float,
):
    """bet_fraction in POTLIMIT is a float [0,1] representing fraction of pot"""
    assert isinstance(current_player_stack, float), type(current_player_stack)
    assert isinstance(current_player_street_total, float), type(
        current_player_street_total
    )
    assert isinstance(last_aggro_street_total, float), type(last_aggro_street_total)
    assert isinstance(pot, float), type(pot)
    if previous_aggro_action is None:
        max_betsize = pot
        min_betsize = 0
    elif previous_aggro_action.action_type == BET:  # Bet
        max_betsize = pot + 2 * previous_aggro_action.amount
        min_betsize = min(previous_aggro_action.amount, current_player_stack)
    elif previous_aggro_action.action_type == RAISE:  # Raise
        max_betsize = (2 * previous_aggro_action.street_total) + (
            pot - current_player_street_total
        )
        min_betsize = previous_aggro_action.street_total
    else:
        max_betsize = 0
        min_betsize = 0
    return (min_betsize, max_betsize)


rake_cap = {
    "low": {
        2: 0.5,
        3: 1,
        4: 1,
        5: 2,
        6: 2,
        7: 2,
        8: 2,
        9: 2,
    },
    "high": {
        2: 1,
        3: 2,
        4: 3,
        5: 3,
        6: 4,
        7: 4,
        8: 4,
        9: 4,
    },
}


def calc_rake(num_players, bb, pot):
    # print(f"calc_rake {num_players},{bb},{pot}")
    # rake only taken post flop or after the second raise.
    stake = "high" if bb > 0.25 else "low"
    cap = rake_cap[stake][num_players]
    rake = min(cap, (pot / 0.2) * 0.01)
    # print(f"rake {rake}")
    return rake


ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
suits = ["c", "d", "h", "s"]
card_to_int = {}
rank_to_int = {rank: i for i, rank in enumerate(ranks, start=1)}
suit_to_int = {suit: i for i, suit in enumerate(suits, start=1)}
idx = 1  # zero padded
for rank in range(0, 13):
    for suit in range(0, 4):
        card_to_int[ranks[rank] + suits[suit]] = idx
        idx += 1
int_to_card = {v: k for k, v in card_to_int.items()}
int_to_rank = {v: k for k, v in rank_to_int.items()}
int_to_suit = {v: k for k, v in suit_to_int.items()}
int_to_suit[0] = "-"
int_to_rank[0] = "-"
preflop_positions = ["UTG", "UTG+1", "UTG+2", "Dealer", "Small Blind", "Big Blind"]
preflop_order = {p: i for i, p in enumerate(preflop_positions)}
postflop_positions = [
    "Small Blind",
    "Big Blind",
    "UTG",
    "UTG+1",
    "UTG+2",
    "Dealer",
]
postflop_order = {p: i for i, p in enumerate(postflop_positions)}
PLAYERS_POSITIONS_DICT = {
    2: ["Dealer", "Big Blind"],
    3: ["Small Blind", "Big Blind", "Dealer"],
    4: ["Small Blind", "Big Blind", "UTG", "Dealer"],
    5: ["Small Blind", "Big Blind", "UTG", "UTG+1", "Dealer"],
    6: ["Small Blind", "Big Blind", "UTG", "UTG+1", "UTG+2", "Dealer"],
}
# print(postflop_order, preflop_order)
betsizes = (1, 0.9, 0.75, 0.67, 0.5, 0.33, 0.25, 0.1)
action_strs = [FOLD, CHECK, CALL]
action_type_to_int = {a: i for i, a in enumerate(action_strs, start=1)}
action_betsize_to_int = {b: i for i, b in enumerate(betsizes, start=4)}
action_to_int = action_type_to_int | action_betsize_to_int
action_to_str = {v: k for k, v in action_to_int.items()}
action_to_str[0] = "None"
num_actions = 11
street_to_int = {"-": 0.0, PREFLOP: 1.0, FLOP: 2.0, TURN: 3.0, RIVER: 4.0}
int_to_street = {v: k for k, v in street_to_int.items()}
state_shape = 49

state_mapping = {
    "hand_range": [0, 8],
    "board_range": [8, 18],
    "street": 18,
    "num_players": 19,
    "hero_pos": 20,
    "hero_active": 21,
    "vil1_active": 22,
    "vil2_active": 23,
    "vil3_active": 24,
    "vil4_active": 25,
    "vil5_active": 26,
    "next_player": 27,
    "next_player2": 28,
    "next_player3": 29,
    "next_player4": 30,
    "next_player5": 31,
    "last_agro_amount": 32,
    "last_agro_action": 33,
    "last_agro_position": 34,
    "last_agro_is_blind": 35,
    "hero_stack": 36,
    "vil1_stack": 37,
    "vil2_stack": 38,
    "vil3_stack": 39,
    "vil4_stack": 40,
    "vil5_stack": 41,
    "pot": 42,
    "amount_to_call": 43,
    "pot_odds": 44,
    "previous_amount": 45,
    "previous_position": 46,
    "previous_action": 47,
    "previous_bet_is_blind": 48,
}

# class State:
#     def __init__(self,state):
#         self.state = state

#     def __repr__(self):
#         return f"self.state"


def convert_cards(cards):
    hole_cards = []
    for card in cards:
        hole_cards.append(rank_to_int[card[0]])
        hole_cards.append(suit_to_int[card[1]])
    return hole_cards


# def sort_positions(a):
#     return preflop_order[a[2]]


def process_players(players, bb):
    # 0 = stack, 1 = hole_cards, 2 = position, 3 = is_hero, 4 = winnings
    hero = None
    all_players = []
    for player in players:
        # player[0] = player[0] / bb
        if player[3]:
            player[1] = convert_cards(player[1])
            hero = player
        all_players.append(player)
    all_players.sort(key=lambda x: preflop_order[x[2]])
    # print("hero", hero)
    return hero, all_players


def classify_betsize(betsize):
    l, r = 0, 1
    # print("classify_betsize", betsize, betsizes)
    while r < len(betsizes):
        if betsize == betsizes[l]:
            return action_betsize_to_int[betsize]
        elif betsize < betsizes[l] and betsize > betsizes[r]:
            # probabilistically sample the supports
            l_dist = betsizes[l] - betsize
            r_dist = abs(betsizes[r] - betsize)
            total = l_dist + r_dist
            r_prob = r_dist / total
            roll = np.random.uniform()
            if roll > r_prob:
                # l
                return action_betsize_to_int[betsizes[r]]
            else:
                # r
                return action_betsize_to_int[betsizes[l]]
        r += 1
        l += 1
    return action_betsize_to_int[betsizes[-1]]


def calculate_last_agro_action(action, last_agro_action, position_to_int):
    # print("calculate_last_agro_action", last_agro_action)
    # last agro action
    if last_agro_action.action_type in action_type_to_int:
        agro_action = action_type_to_int[last_agro_action.action_type]
    else:
        # bet/raise
        if last_agro_action.is_blind:
            action_category = 0
        else:
            action_category = classify_betsize(last_agro_action.bet_ratio)
        agro_action = action_category

    last_agro_position = (
        position_to_int[last_agro_action.position] if action.last_aggressor_index else 0
    )
    last_agro_is_blind = last_agro_action.is_blind if action.last_aggressor_index else 0
    # print(
    #     "last_agro_action.amount, agro_action, last_agro_position, last_agro_is_blind",
    #     last_agro_action.amount,
    #     agro_action,
    #     last_agro_position,
    #     last_agro_is_blind,
    # )
    return last_agro_action.amount, agro_action, last_agro_position, last_agro_is_blind


def normalize_dataset(states: np.array):
    r = range(state_mapping["hero_stack"], state_mapping["vil5_stack"] + 1)
    max_stack = np.max(states[:, :, r])
    # states[:, :, r] = states[:, :, r] / max_stack
    print("max_stack", max_stack)
    # print("new max", np.max(states[:, :, r]))
    max_pot = np.max(states[:, :, state_mapping["pot"]])
    print("max_pot", max_pot)
    return states


def scale_state(state, bb):
    """Scale all non-categorical features by the bb."""
    state[state_mapping["previous_amount"]] = np.log(
        (state[state_mapping["previous_amount"]] / bb) + 1
    )
    state[state_mapping["amount_to_call"]] = np.log(
        (state[state_mapping["amount_to_call"]] / bb) + 1
    )
    state[state_mapping["pot"]] = np.log((state[state_mapping["pot"]] / bb) + 1)
    state[state_mapping["hero_stack"]] = np.log(
        (state[state_mapping["hero_stack"]] / bb) + 1
    )
    state[state_mapping["vil1_stack"]] = np.log(
        (state[state_mapping["vil1_stack"]] / bb) + 1
    )
    state[state_mapping["vil2_stack"]] = np.log(
        (state[state_mapping["vil2_stack"]] / bb) + 1
    )
    state[state_mapping["vil3_stack"]] = np.log(
        (state[state_mapping["vil3_stack"]] / bb) + 1
    )
    state[state_mapping["vil4_stack"]] = np.log(
        (state[state_mapping["vil4_stack"]] / bb) + 1
    )
    state[state_mapping["vil5_stack"]] = np.log(
        (state[state_mapping["vil5_stack"]] / bb) + 1
    )
    state[state_mapping["last_agro_amount"]] = np.log(
        ((state[state_mapping["last_agro_amount"]] / bb) + 1)
    )
    return state


def convert_to_ml(hand):
    """
    Reason for round stats:
    Pot is including current bet
    num_active_players is including current player (so -1 if current action is folds)
    """
    # print(list(hand.keys()))
    stack_data = hand["stack_data"]
    # print("stack_data", stack_data)
    game_states, target_actions = [], []
    # game_states = stack of gamestates up to hero decision
    # Y = discounted reward and action choice
    print(hand["hand_data"]["file_name"])
    current_street = 1
    stat_data = hand["stat_data"]
    padded_board = [0] * 10
    actions = hand["actions"][1:]  # skip preflop street

    number_of_players = hand["hand_data"]["num_players"]
    num_active_players = number_of_players
    bb = hand["hand_data"]["big_blind"]
    hero, players = process_players(hand["player_data"].values(), bb)
    # print("hero", hero, players)
    if not hero:
        return [], [], []
    hero_position = hero[2]
    result = hero[4]
    active_positions = set([p[2] for p in players])

    position_conversion = sorted(
        [p[2] for p in players if p[2] != hero_position],
        key=lambda x: preflop_positions,
    )
    position_conversion = [hero_position] + position_conversion
    # position_conversion = PLAYERS_POSITIONS_DICT[number_of_players]
    position_to_int = {p: i for i, p in enumerate(position_conversion, start=1)}
    position_to_str = {v: k for k, v in position_to_int.items()}
    position_to_str[0] = "None"
    stacks = [hero[0]] + [p[0] for p in players if p[2] != hero_position]
    stacks += [0 for _ in range(6 - number_of_players)]
    active_players = [1 if i < number_of_players else 0 for i in range(6)]
    position_to_active = {p: i for i, p in enumerate(position_conversion, start=0)}
    # position_to_active[hero[2]] = 0
    position_to_stack = {p: i for i, p in enumerate(position_conversion, start=0)}
    # position_to_stack[hero[2]] = 0
    next_players = [p for p in postflop_positions if p in active_positions]
    next_player_padding = [0 for _ in range(5 - len(active_positions))]
    # print("position_conversion", position_conversion)
    # print("position_to_int", position_to_int)
    # print("position_to_str", position_to_str)
    # print("position_to_stack", position_to_stack)
    # print("stacks", stacks)
    hand_board = hero[1] + padded_board
    # convert int position into index for
    num_hero_decisions = 0
    model_inputs = []
    for i, (action, round_stats, round_seats) in enumerate(
        zip(actions, stat_data, stack_data)
    ):
        # print("action", action)
        next_state = np.zeros(state_shape)
        if isinstance(action, Street):
            current_street += 1
            board = convert_cards(action.board_cards)
            hand_board = hero[1] + board + [0 for _ in range(10 - len(board))]
            next_state[state_mapping["pot"]] = round_stats["pot"]
            # postflop ordering minus active players
            next_players = [p for p in postflop_positions if p in active_positions]
            next_players_used = next_players[:-1]
            next_player_padding = [0 for _ in range(5 - len(next_players_used))]
            next_player_complete = [
                position_to_int[p] for p in next_players_used
            ] + next_player_padding
        elif isinstance(action, Action):
            if action.action_type == FOLD:
                action_category = action_type_to_int[action.action_type]
                # change active. convert position into index for active positions
                if action.position == hero_position:  # hero folded
                    num_hero_decisions += 1
                    game_states.append(np.stack(model_inputs))
                    target_actions.append(action_category)
                    break
                num_active_players -= 1
                active_positions.remove(action.position)
                active_players[position_to_active[action.position]] = 0
                # calculated for the next player
                if action.last_aggressor_index is None:
                    # Player folded when check was possible
                    bet_amount = 0
                elif i + 1 == len(actions):  # end of game
                    bet_amount = hand["actions"][
                        action.last_aggressor_index
                    ].street_total
                else:
                    next_action = actions[i + 1]
                    if isinstance(next_action, Street):
                        bet_amount = 0
                    else:
                        bet_amount = (
                            hand["actions"][action.last_aggressor_index].street_total
                            - round_seats[next_action.position]["street_total"]
                        )
                # calculated for the next player (if any)
                next_state[state_mapping["amount_to_call"]] = bet_amount
                next_state[state_mapping["pot_odds"]] = bet_amount / (
                    bet_amount + action.pot
                )
            elif action.action_type == CHECK:
                action_category = action_type_to_int[action.action_type]
                next_state[state_mapping["amount_to_call"]] = 0
                next_state[state_mapping["pot_odds"]] = 0
            elif action.action_type == CALL:
                action_category = action_type_to_int[action.action_type]
                # calculated for the next player (if any)
                if i + 1 == len(actions):  # end of game
                    bet_amount = (
                        hand["actions"][action.last_aggressor_index].street_total
                        - action.amount
                    )
                else:
                    next_action = actions[i + 1]
                    if isinstance(next_action, Street):
                        bet_amount = 0
                    else:
                        bet_amount = (
                            hand["actions"][action.last_aggressor_index].street_total
                            - round_seats[next_action.position]["street_total"]
                        )
                next_state[state_mapping["amount_to_call"]] = bet_amount
                next_state[state_mapping["pot_odds"]] = bet_amount / (
                    bet_amount + round_stats["pot"]
                )
            elif action.action_type == BET:
                if action.is_blind:
                    action_category = 0
                    next_state[state_mapping["amount_to_call"]] = 0
                    next_state[state_mapping["pot_odds"]] = 0
                    next_state[state_mapping["previous_bet_is_blind"]] = 1
                else:
                    action_category = classify_betsize(action.bet_ratio)
                    next_state[state_mapping["previous_bet_is_blind"]] = 0
                    next_state[state_mapping["amount_to_call"]] = action.amount
                    next_state[state_mapping["pot_odds"]] = action.amount / (
                        2 * action.amount + action.pot
                    )
                # print("action_category", action_to_str[action_category])
                # print("action.bet_ratio", action.bet_ratio)
                # calculated for the next player
                # next active player street total - this player street total
            elif action.action_type == RAISE:
                # classify betsize
                if action.is_blind:
                    next_state[state_mapping["previous_bet_is_blind"]] = 1
                    action_category = 0
                else:
                    next_state[state_mapping["previous_bet_is_blind"]] = 0
                    action_category = classify_betsize(action.bet_ratio)
                # calculated for the next player
                next_action = actions[i + 1]
                bet_amount = (
                    action.street_total
                    - round_seats[next_action.position]["street_total"]
                )
                next_state[state_mapping["amount_to_call"]] = bet_amount
                next_state[state_mapping["pot_odds"]] = bet_amount / (
                    bet_amount + action.street_total + action.pot
                )

            if action.position == hero_position and not action.is_blind:
                # if not action.is_blind: # gather all datapoints
                num_hero_decisions += 1
                game_states.append(np.stack(model_inputs))
                target_actions.append(action_category)
            if action.last_aggressor_index:
                (
                    last_agro_amount,
                    last_agro_action,
                    last_agro_position,
                    last_agro_is_blind,
                ) = calculate_last_agro_action(
                    action,
                    hand["actions"][action.last_aggressor_index],
                    position_to_int,
                )
            else:
                last_agro_amount = 0
                last_agro_action = 0
                last_agro_position = 0
                last_agro_is_blind = 0
            action_amount = action.amount if action.amount else 0
            # update pot, update stacks
            # print("action", action)
            stacks[position_to_stack[action.position]] -= action_amount
            next_state[state_mapping["last_agro_amount"]] = last_agro_amount
            next_state[state_mapping["last_agro_action"]] = last_agro_action
            next_state[state_mapping["last_agro_position"]] = last_agro_position
            next_state[state_mapping["last_agro_is_blind"]] = last_agro_is_blind
            next_state[state_mapping["pot"]] = round_stats["pot"]
            next_state[state_mapping["previous_amount"]] = action_amount
            next_state[state_mapping["previous_position"]] = position_to_int[
                action.position
            ]
            next_state[state_mapping["previous_action"]] = action_category
            # player ordering minus active players
            # rotate next players
            try:
                next_players.append(action.position)
                next_players = [p for p in next_players[1:] if p in active_positions]
                next_players_used = next_players[:-1]
                next_player_padding = [0 for _ in range(5 - len(next_players_used))]
                next_player_complete = [
                    position_to_int[p] for p in next_players_used
                ] + next_player_padding

            except:

                print("action", action)
                print("active_positions", active_positions)
                print("next_players", next_players)
                print("position_to_int", position_to_int)
                raise ValueError()
        # print("previous_amount", next_state[state_mapping["previous_amount"]])
        # print(
        #     "previous_position",
        #     position_to_str[next_state[state_mapping["previous_position"]]],
        # )
        # print("previous_action", next_state[state_mapping["previous_action"]])
        next_state[state_mapping["vil1_stack"]] = stacks[1]
        next_state[0:18] = hand_board
        next_state[state_mapping["num_players"]] = num_active_players
        next_state[state_mapping["street"]] = current_street
        next_state[state_mapping["hero_pos"]] = position_to_int[hero_position]
        next_state[state_mapping["hero_stack"]] = stacks[0]
        next_state[state_mapping["vil1_stack"]] = stacks[1]
        next_state[state_mapping["vil2_stack"]] = stacks[2]
        next_state[state_mapping["vil3_stack"]] = stacks[3]
        next_state[state_mapping["vil4_stack"]] = stacks[4]
        next_state[state_mapping["vil5_stack"]] = stacks[5]
        next_state[state_mapping["next_player"]] = next_player_complete[0]
        next_state[state_mapping["next_player2"]] = next_player_complete[1]
        next_state[state_mapping["next_player3"]] = next_player_complete[2]
        next_state[state_mapping["next_player4"]] = next_player_complete[3]
        next_state[state_mapping["next_player5"]] = next_player_complete[4]
        next_state[state_mapping["hero_active"]] = active_players[0]
        next_state[state_mapping["vil1_active"]] = active_players[1]
        next_state[state_mapping["vil2_active"]] = active_players[2]
        next_state[state_mapping["vil3_active"]] = active_players[3]
        next_state[state_mapping["vil4_active"]] = active_players[4]
        next_state[state_mapping["vil5_active"]] = active_players[5]
        scale_state(next_state, bb)
        model_inputs.append(next_state)

    target_rewards = [result * 0.95 ** i for i in range(num_hero_decisions - 1, -1, -1)]
    # visualize_state(
    #     game_states,
    #     target_actions,
    #     target_rewards,
    #     hand,
    #     position_to_int,
    #     position_to_str,
    # )
    return (game_states, target_actions, target_rewards)


def visualize_state(
    game_states, target_actions, target_rewards, hand, position_to_int, position_to_str
):
    # print(game_states)
    if game_states:
        print(len(game_states))
        print(game_states[0].shape)
        print(hand["hand_data"])
        print("target_actions", target_actions)
        print("target_rewards", target_rewards)
        num_players = hand["hand_data"]["num_players"]
        # for game_state in game_states:
        game_state = game_states[-1]
        for i in range(game_state.shape[0]):
            ...
            print_state(game_state[i], position_to_int, position_to_str)
        # for action in target_actions:
        #     print(action_to_str[action])
        # print("target_rewards", target_rewards)


def print_state(state, position_to_int, position_to_str):
    # position_conversion = PLAYERS_POSITIONS_DICT[num_players]
    # position_to_int = {p: i for i, p in enumerate(position_conversion, start=1)}
    # position_to_str = {v: k for k, v in position_to_int.items()}
    # position_to_str[0] = "None"
    # print(f'hero hand: {state[0:8]}')
    print_cards(state[0:8])
    print_cards(state[8:18])
    # print(int_to_street[state[state_mapping["street"]]])
    # print('Number of active players',state[state_mapping["num_players"]])
    # print(position_to_str[state[state_mapping["hero_pos"]]])
    last_agro_action = state[state_mapping["last_agro_action"]]
    last_agro_position = state[state_mapping["last_agro_position"]]
    last_agro_is_blind = state[state_mapping["last_agro_is_blind"]]

    pot = state[state_mapping["pot"]]
    amount_to_call = state[state_mapping["amount_to_call"]]
    pot_odds = state[state_mapping["pot_odds"]]
    previous_amount = state[state_mapping["previous_amount"]]
    previous_position = state[state_mapping["previous_position"]]
    previous_action = state[state_mapping["previous_action"]]
    previous_bet_is_blind = state[state_mapping["previous_bet_is_blind"]]

    next_player = state[state_mapping["next_player"]]
    next_player2 = state[state_mapping["next_player2"]]
    next_player3 = state[state_mapping["next_player3"]]
    next_player4 = state[state_mapping["next_player4"]]
    next_player5 = state[state_mapping["next_player5"]]

    hero_stack = state[state_mapping["hero_stack"]]
    vil1_stack = state[state_mapping["vil1_stack"]]
    vil2_stack = state[state_mapping["vil2_stack"]]
    vil3_stack = state[state_mapping["vil3_stack"]]
    vil4_stack = state[state_mapping["vil4_stack"]]
    vil5_stack = state[state_mapping["vil5_stack"]]

    hero_active = state[state_mapping["hero_active"]]
    vil1_active = state[state_mapping["vil1_active"]]
    vil2_active = state[state_mapping["vil2_active"]]
    vil3_active = state[state_mapping["vil3_active"]]
    vil4_active = state[state_mapping["vil4_active"]]
    vil5_active = state[state_mapping["vil5_active"]]
    # print(f"Previously active players: hero {hero_active}, ")
    print(f"pot {pot}, amount_to_call {amount_to_call}, pot_odds {pot_odds}")
    print(
        f"Previous_position {position_to_str[previous_position]}, previous_amount {previous_amount}, previous_action {action_to_str[int(previous_action)]}, previous_bet_is_blind {previous_bet_is_blind}"
    )
    print(
        f"last_agro_position {position_to_str[last_agro_position]}, last_agro_action {action_to_str[int(last_agro_action)]}, last_agro_is_blind {last_agro_is_blind}"
    )
    print(f"Next player to act {position_to_str[next_player]}")
    print(f"Next player2 to act {position_to_str[next_player2]}")
    print(f"Next player3 to act {position_to_str[next_player3]}")
    print(f"Next player4 to act {position_to_str[next_player4]}")
    print(f"Next player5 to act {position_to_str[next_player5]}")

    print(f"hero_active {hero_active}")
    print(f"vil1_active {vil1_active}")
    print(f"vil2_active {vil2_active}")
    print(f"vil3_active {vil3_active}")
    print(f"vil4_active {vil4_active}")
    print(f"vil5_active {vil5_active}")
    print(f"hero_stack {hero_stack}")
    print(f"vil1_stack {vil1_stack}")
    print(f"vil2_stack {vil2_stack}")
    print(f"vil3_stack {vil3_stack}")
    print(f"vil4_stack {vil4_stack}")
    print(f"vil5_stack {vil5_stack}")


def print_cards(row):
    ranks = row[0::2]
    suits = row[1::2]
    cards = [
        "".join((int_to_rank[rank].upper(), int_to_suit[suit]))
        for rank, suit in zip(ranks, suits)
    ]
    print(cards)
