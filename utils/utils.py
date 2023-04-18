from collections import deque
import pprint
from typing import List
import numpy as np
from utils.data_types import Action,PLAYERS_POSITIONS_PREFLOP_DICT, Player, Positions, rake_cap,Action,RAISE,BET,FOLD,CALL,CHECK,BLIND,PREFLOP,FLOP,TURN,RIVER,POSITION_TO_SEAT,rank_to_int,suit_to_int,preflop_order,betsizes,action_type_to_int,state_mapping,action_betsize_to_int,preflop_positions,postflop_positions,Street,state_shape,int_to_rank,int_to_suit

def calc_rake(num_players, bb, pot):
    # print(f"calc_rake {num_players},{bb},{pot}")
    # rake only taken post flop or after the second raise.
    stake = "high" if bb > 0.25 else "low"
    cap = rake_cap[stake][num_players]
    rake = min(cap, (pot / 0.2) * 0.01)
    return rake

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


def convert_cards(cards):
    hole_cards = []
    for card in cards:
        hole_cards.append(rank_to_int[card[0]])
        hole_cards.append(suit_to_int[card[1]])
    return hole_cards


def process_players(players, bb):
    # 0 = stack, 1 = hole_cards, 2 = position, 3 = is_hero, 4 = winnings, 5 = active
    hero = None
    all_players = []
    for player in players:
        if player[1]:
            player[1] = convert_cards(player[1])
        else:
            player[1] = [0, 0, 0, 0] * 2
        player_obj = Player(*player,is_active=1)
        all_players.append(player_obj)
        if player_obj.is_hero:
            hero = player_obj
        
    all_players.sort(key=lambda x: preflop_order[x.position])
    return hero, all_players


def classify_betsize(betsize):
    l, r = 0, 1
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

def update_player_stack(players:List[Player],position,amount):
    for p in players:
        if p.position == position:
            p.update_stack(amount)
            break

def update_player_is_active(players:List[Player],position,is_active):
    for p in players:
        if p.position == position:
            p.update_is_active(is_active)
            break


class MLConversion:
    def __init__(self):
        self.game_states, self.target_actions, self.target_rewards = [], [], []

    def convert_hands(self,hands):
        for i,hand in enumerate(hands):
            states, actions, rewards = self.convert_hand(hand)
            if states:
                self.game_states.extend(states)
                self.target_actions.extend(actions)
                self.target_rewards.extend(rewards)
            # if i == 2:
            #     break
        return self.game_states, self.target_actions, self.target_rewards

    def record_hand(self,next_state,num_active_players,hero,hand_board,current_street,padded_villains,next_players):
        next_state[0:18] = hand_board
        for i in range(1,6):
            next_state[state_mapping[f"vil{i}_active"]] = padded_villains[i-1].is_active
            next_state[state_mapping[f"vil{i}_stack"]] = padded_villains[i-1].stack
            next_state[state_mapping[f"vil{i}_position"]] = POSITION_TO_SEAT[padded_villains[i-1].position]
        next_state[state_mapping["num_players"]] = num_active_players
        next_state[state_mapping["street"]] = current_street
        next_state[state_mapping["hero_position"]] = POSITION_TO_SEAT[hero.position]
        next_state[state_mapping["hero_stack"]] = hero.stack
        next_state[state_mapping["hero_active"]] = hero.is_active
        next_state[state_mapping["current_player"]] = POSITION_TO_SEAT[next_players[0]]
        next_state[state_mapping["next_player"]] = POSITION_TO_SEAT[next_players[1]] if len(next_players) > 1 else 0

    def convert_hand(self,hand):
        """
        Reason for round stats:
        Pot is including current bet
        num_active_players is including current player (so -1 if current action is folds)
        """
        stack_data = hand["stack_data"]
        game_states, target_actions = [], []
        # game_states = stack of gamestates up to hero decision
        # Y = discounted reward and action choice
        # print(hand["hand_data"]["file_name"])
        current_street = 1
        stat_data = hand["stat_data"]
        padded_board = [0] * 10
        actions = hand["actions"][1:]  # skip preflop street

        # number_of_players = hand["hand_data"]["num_players"]
        bb = hand["hand_data"]["big_blind"]
        hero, players = process_players(hand["player_data"].values(), bb)
        number_of_players = num_active_players = len(players)
        
        if not hero or any([True if p.is_active and p.stack == 0 else False for p in players ]):
            return [], [], []
        result = hero.winnings
        active_positions = set([p.position for p in players])
        position_conversion = sorted(
            [p.position for p in players if p.position != hero.position],
            key=lambda x: preflop_positions,
        )
        position_conversion = [hero.position] + position_conversion
        position_to_int = {p: i for i, p in enumerate(position_conversion, start=1)}
        position_to_str = {v: k for k, v in position_to_int.items()}
        position_to_str[0] = "None"
        # position_to_stack[hero[2]] = 0
        next_players = deque([p for p in postflop_positions if p in active_positions])
        if number_of_players == 2 and Positions.DEALER in active_positions:
            next_players.rotate(-1)
        hand_board = hero.hole_cards + padded_board
        # convert int position into index for
        num_hero_decisions = 0
        model_inputs = []
        if number_of_players == 2:
            print('beginning',next_players)
        # for a in actions:
        #     print(a)
        # print(POSITION_TO_SEAT)
        for i, (action, round_stats, round_seats) in enumerate(
            zip(actions, stat_data, stack_data)
        ):
            if i > 1 and number_of_players == 2:
                print("action i",i, action)
            next_state = np.zeros(state_shape)
            if isinstance(action, Street):
                current_street += 1
                board = convert_cards(action.board_cards)

                hand_board = hero.hole_cards + board + [0 for _ in range(10 - len(board))]
                next_state[state_mapping["pot"]] = round_stats["pot"]
                # postflop ordering minus active players
                next_players = deque([p for p in postflop_positions if p in active_positions])
            elif isinstance(action, Action):
                if action.action_type == FOLD:
                    action_category = action_type_to_int[action.action_type]
                    # change active. convert position into index for active positions
                    if action.position == hero.position:  # hero folded
                        num_hero_decisions += 1
                        game_states.append(np.stack(model_inputs))
                        target_actions.append(action_category)
                        break
                    num_active_players -= 1
                    active_positions.remove(action.position)
                    update_player_is_active(players,action.position,0)
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
                    next_players.remove(action.position)
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
                        action_category = 4
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
                    # calculated for the next player
                    # next active player street total - this player street total
                elif action.action_type == RAISE:
                    # classify betsize
                    if action.is_blind:
                        next_state[state_mapping["previous_bet_is_blind"]] = 1
                        action_category = 4
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

                if action.position == hero.position and not action.is_blind:
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
                if action.action_type != FOLD:
                    # rotate next players
                    next_players.rotate(-1)
                action_amount = action.amount if action.amount else 0
                # update pot, update stacks
                cur_player = [p for p in players if p.position == action.position][0]
                if cur_player.stack - action_amount < -1:
                    print(hand["hand_data"]["file_name"])
                    pprint.pprint(actions)
                    print(stat_data)
                    print(stack_data)
                    print(action_amount)
                    print(cur_player.stack - action_amount)
                    print([p.stack for p in players])
                    return [],[],[]
                update_player_stack(players,action.position,action_amount)
                next_state[state_mapping["last_agro_amount"]] = last_agro_amount
                next_state[state_mapping["last_agro_action"]] = last_agro_action
                next_state[state_mapping["last_agro_position"]] = last_agro_position
                next_state[state_mapping["last_agro_is_blind"]] = last_agro_is_blind
                next_state[state_mapping["pot"]] = round_stats["pot"]
                next_state[state_mapping["previous_amount"]] = action_amount
                next_state[state_mapping["previous_position"]] = POSITION_TO_SEAT[
                    action.position
                ]
                next_state[state_mapping["previous_action"]] = action_category

                if i > 1 and number_of_players == 2:
                    # print file name
                    print('ith stage',i,next_players)
            padded_villains = [p for p in players if p.position != hero.position] + [Player(0,0,None,0,0,0)] * (
                6 - len(players)
            )
            # print('padded_villains',padded_villains)
            # need to correct active players so it matches padded_villains.
            # check if hero.position overlaps with villain positions
            assert POSITION_TO_SEAT[hero.position] not in [POSITION_TO_SEAT[p.position] for p in padded_villains], "hero position overlaps with villain positions"
            padded_villains.sort(key=lambda x: POSITION_TO_SEAT[x.position])
            hero = [p for p in players if p.position == hero.position][0]
            
            self.record_hand(next_state,num_active_players,hero,hand_board,current_street,padded_villains,next_players)
            scale_state(next_state, bb)
            model_inputs.append(next_state)
        target_rewards = [(result/bb) * 0.95 ** i for i in range(num_hero_decisions - 1, -1, -1)]
        return (game_states, target_actions, target_rewards)
