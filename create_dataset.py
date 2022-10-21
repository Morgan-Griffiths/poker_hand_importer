from math import isnan
import psycopg2
import time
import datetime
from utils import DataAction, Street

street_mapping = {
    "preflop": 0,
    "flop": 1,
    "turn": 2,
    "river": 3,
}
hand_keys = [
    "file_name",
    "hand_number",
    "ts",
    "game_type",
    "bet_limit",
    "num_players",
    "big_blind",
    "hero",
]
player_keys = ["stack", "hole_cards", "position", "is_hero", "winnings"]
player_positions = ["UTG", "UTG+1", "UTG+2", "Dealer", "Small Blind", "Big Blind"]
position_to_int = {p: i for i, p in enumerate(player_positions)}
int_to_posiiton = {v: k for k, v in position_to_int.items()}


def fetch_hand():
    with psycopg2.connect("dbname=poker user=postgres") as conn:
        with conn.cursor() as cursor:
            # cursor.execute(
            #     """
            #         select t.* from actions as t inner join players as p on t.player_id = p.id and p.is_hero = true and t.action_type = 'raises';
            #     """
            # )
            # print(cursor.fetchall())
            cursor.execute(
                """
                    select * from hands;
                """
            )
            (
                hand_id,
                file_name,
                hand_number,
                ts,
                game_type,
                bet_limit,
                num_players,
                big_blind,
                hero,
            ) = cursor.fetchone()
            print(
                hand_id,
                file_name,
                hand_number,
                ts,
                game_type,
                bet_limit,
                num_players,
                big_blind,
                hero,
            )

            cursor.execute(
                """
                    select * from players where hand_id = %s;
                """,
                (hand_id,),
            )

            players = cursor.fetchall()
            print("players", players)
            hero = [player for player in players if player[-2] is True]
            print("hero", hero)

            cursor.execute(
                """
                    select * from streets where hand_id = %s;
                """,
                (hand_id,),
            )
            # print(cursor.fetchone())
            streets = cursor.fetchall()
            print(streets)
            for street in streets:
                print(street)
                street_id = street[0]
                cursor.execute(
                    """
                    select * from actions where hand_id = %s and street_id = %s;
                """,
                    (
                        hand_id,
                        street_id,
                    ),
                )
                actions = cursor.fetchall()
                print(actions)
            # street_id, _, street_type, board_cards =
            # print(street_id, street_type, board_cards)


fetch_hand()

""" 

Stack sizes are in ratios to pot? maybe need the log of the ratio? 
This would mean it changes little as the stack increases. but changes rapidly as the stack size approaches 0.

hand = 4 cards * 2 = 8
board = 5 cards * 2 = 10
cards = 18
street = 19 # categorical
number of players = 20 # categorical

Hero position = 20 # categorical
villain1 position active = 21 # boolean
villain2 position active = 22 # boolean
villain3 position active = 23 # boolean
villain4 position active = 24 # boolean
villain5 position active = 25 # boolean

next position to act = 26 # categorical
next position to act = 27 # categorical
next position to act = 28 # categorical
next position to act = 29 # categorical
next position to act = 30 # categorical
next position to act = 31 # categorical



last_aggressive_ action = 32 # categorical
last_aggressive_ betsize = 33 # categorical
last_aggressive_ position = 34 # categorical

hero stack = 35 # continuous
villain1 stack = 36 # continuous
villain2 stack = 37 # continuous
villain3 stack = 38 # continuous
villain4 stack = 39 # continuous
villain5 stack = 40 # continuous

pot = 41            # continuous
amount to call = 42 # continuous
pot odds = 43       # continuous

stack of 22 of these or so. can play with different depths

how many actions?

fold,check,call,bet+raise
sizes = 1,.75,.5,.25 = 7
sizes = 1,.75,.67,.5,.34,.25,.1 = 10

"""


# 'state':{
#     'suit':T([1,3,5,7]).long(),
#     'rank':T([0,2,4,6]).long(),
#     'hand':T([0,1,2,3,4,5,6,7]).long(),
#     'board':T([8,9,10,11,12,13,14,15,16,17]).long(),
#     'board_ranks':T([8,10,12,14,16]).long(),
#     'board_suits':T([9,11,13,15,17]).long(),
#     'street':T([18]).long(),
#     'hero_position':T([19]).long(),
#     'vil_position':T([20]).long(),
#     'previous_action':T([21]).long(),
#     'previous_betsize':T([22]).long(),
#     'hero_stack':T([23]).long(),
#     'villain_stack':T([24]).long(),
#     'amnt_to_call':T([25]).long(),
#     'pot_odds':T([26]).long(),
#     'hand_board':T([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]).long(),
#     'ordinal':T([18,19,20,21]).long(),
#     'continuous':T([22,23,24,25,26]).long()
#     },
# 'pot':3,
# 'amnt_to_call':4,
# 'pot_odds':5
