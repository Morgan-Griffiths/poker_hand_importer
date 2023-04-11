
from collections import namedtuple


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

class Player:
    def __init__(self,stack,hole_cards,position,is_hero,winnings,is_active) -> None:
        self.stack = stack
        self.hole_cards = hole_cards
        self.position = position
        self.is_hero = is_hero
        self.winnings = winnings
        self.is_active = is_active

    def update_stack(self,amount):
        if self.stack - amount < 0 and self.stack - amount > -0.1:
            self.stack = 0
        else:
            self.stack -= amount

    def update_is_active(self,is_active):
        self.is_active = is_active

    def __repr__(self):
        return f"Player({self.stack},{self.position},{'Hero' if self.is_hero else 'Villain'},{'Active' if self.is_active else 'Folded'})"

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

POSITION_TO_SEAT = {
    None: 0,
    'Small Blind': 1,
    'Big Blind': 2,
    'UTG+2':3,
    'UTG+1':4,
    'UTG':5,
    'Dealer':6
}

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
    "vil1_position": 27,
    "vil2_position": 28,
    "vil3_position": 29,
    "vil4_position": 30,
    "vil5_position": 31,
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
    "next_player": 49,
}
state_shape = 50

