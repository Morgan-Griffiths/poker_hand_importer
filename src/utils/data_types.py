from collections import namedtuple
from typing import Optional, Union
from pydantic import BaseModel


class Hero:
    TJ = "tj"
    CHRIS = "chris"


class StreetTotal(BaseModel):
    street_total: float


class PositionStats(BaseModel):
    seat_num: int
    is_hero: bool
    stack: float
    hole_cards: Optional[list[str]]
    winnings: float
    street_total: float


class StatsItem(BaseModel):
    pot: float
    num_active_players: int


class HandStats(BaseModel):
    pot: float
    rake: float
    bet_ratios: list[float]
    num_active_players: int
    action_order: int
    last_aggressor: Optional[str]
    last_aggressor_index: Optional[int]
    penultimate_raise: Optional[float]


class HandData(BaseModel):
    file_name: str
    hand_number: int
    hero: str
    ts: Optional[str]
    game_type: Optional[str]
    bet_limit: Optional[str]
    big_blind: Optional[float]
    num_players: Optional[int]


class Action(BaseModel):
    position: str
    is_hero: bool
    action_type: str
    amount: Optional[float]
    street_total: Optional[float]
    bet_ratio: Optional[float]
    is_blind: bool
    pot: float
    rake: float
    last_aggressor_index: Optional[int]
    num_active_players: int
    action_order: int

    def __repr__(self):
        return f"Action({self.position},{self.action_type},{self.amount},{self.street_total},{self.bet_ratio},{self.is_blind},{self.pot},{self.rake},{self.last_aggressor_index},{self.num_active_players},{self.action_order})"


class Street(BaseModel):
    street_type: str
    board_cards: Optional[list[str]]


class PlayerData(BaseModel):
    position: str
    is_hero: bool
    stack: float
    hole_cards: Optional[list[str]]
    winnings: float


class PokerHand(BaseModel):
    seats: dict
    stats: HandStats
    actions: list[Union[Action, Street]]
    result: dict
    hand_data: HandData
    player_data: dict[str, PlayerData]
    stat_data: list[StatsItem]
    stack_data: list


class Positions:
    SMALL_BLIND = "Small Blind"
    BIG_BLIND = "Big Blind"
    UTG = "UTG"
    UTG_1 = "UTG+1"
    UTG_2 = "UTG+2"
    DEALER = "Dealer"


class Player(BaseModel):
    stack: float
    hole_cards: list[int]
    position: Optional[str]
    is_hero: bool
    winnings: float
    is_active: int

    def update_stack(self, amount):
        if self.stack - amount < 0 and self.stack - amount > -0.1:
            self.stack = 0
        else:
            self.stack -= amount

    def update_is_active(self, is_active):
        self.is_active = is_active

    def __repr__(self):
        return f"Player({self.stack},{self.position},{'Hero' if self.is_hero else 'Villain'},{'Active' if self.is_active else 'Folded'})"


class ActionType:
    RAISE = "Raises"
    BET = "Bets"
    FOLD = "Folds"
    CALL = "Calls"
    CHECK = "Checks"
    BLIND = "blind"


class StreetType:
    PREFLOP = "preflop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"


POSITION_TO_SEAT = {
    None: 0,
    "Small Blind": 1,
    "Big Blind": 2,
    "UTG+2": 3,
    "UTG+1": 4,
    "UTG": 5,
    "Dealer": 6,
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
PLAYERS_POSITIONS_POSTFLOP_DICT = {
    2: [
        "Big Blind",
        "Dealer",
    ],
    3: ["Small Blind", "Big Blind", "Dealer"],
    4: ["Small Blind", "Big Blind", "UTG", "Dealer"],
    5: ["Small Blind", "Big Blind", "UTG", "UTG+1", "Dealer"],
    6: ["Small Blind", "Big Blind", "UTG", "UTG+1", "UTG+2", "Dealer"],
}
PLAYERS_POSITIONS_PREFLOP_DICT = {
    2: ["Dealer", "Big Blind"],
    3: ["Dealer", "Small Blind", "Big Blind"],
    4: ["UTG", "Dealer", "Small Blind", "Big Blind"],
    5: ["UTG", "UTG+1", "Dealer", "Small Blind", "Big Blind"],
    6: ["UTG", "UTG+1", "UTG+2", "Dealer", "Small Blind", "Big Blind"],
}
betsizes = (1, 0.9, 0.75, 0.67, 0.5, 0.33, 0.25, 0.1)
action_strs = [ActionType.FOLD, ActionType.CHECK, ActionType.CALL]
action_type_to_int = {a: i for i, a in enumerate(action_strs, start=1)}
action_betsize_to_int = {b: i for i, b in enumerate(betsizes, start=4)}
action_to_int = action_type_to_int | action_betsize_to_int
action_to_str = {v: k for k, v in action_to_int.items()}
action_to_str[0] = "None"
num_actions = 11
street_to_int = {
    "-": 0.0,
    StreetType.PREFLOP: 1.0,
    StreetType.FLOP: 2.0,
    StreetType.TURN: 3.0,
    StreetType.RIVER: 4.0,
}
int_to_street = {v: k for k, v in street_to_int.items()}

state_mapping = {
    "hand_range": [0, 8],
    "board_range": [8, 18],
    "street": 18,
    "num_players": 19,
    "hero_position": 20,
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
    "current_player": 50,
}
state_shape = 51
