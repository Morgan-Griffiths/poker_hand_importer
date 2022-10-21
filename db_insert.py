from math import isnan
import psycopg2
import time
import datetime
from utils import Action, Street

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


def store_hand(data):
    with psycopg2.connect("dbname=poker user=postgres") as conn:
        with conn.cursor() as cursor:
            # 2022-08-16 23:58:34
            data["hand_data"]["ts"] = datetime.datetime.strptime(
                data["hand_data"]["ts"], "%Y-%m-%d %H:%M:%S"
            )
            values = tuple([data["hand_data"][k] for k in hand_keys])
            cursor.execute(
                """
            insert into hands (file_name,hand_number,ts, game_type, bet_limit, num_players, big_blind, hero)
values(%s, %s, %s,%s,%s,%s,%s,%s) RETURNING id
        """,
                values,
            )
            conn.commit()
            hand_id = cursor.fetchone()[0]
            player_values = []
            for position in player_positions:
                if position in data["player_data"]:
                    player_values.append(
                        tuple(
                            [hand_id]
                            + [
                                data["player_data"][position][i]
                                for i in range(len(player_keys))
                            ]
                        )
                    )
            player_ids = {}
            for player in player_values:
                cursor.execute(
                    """
                    insert into players (hand_id, stack, hole_cards, position, is_hero,winnings)
                    values(%s,%s,%s,%s,%s,%s) RETURNING id
                    """,
                    player,
                )
                conn.commit()
                player_id = cursor.fetchone()[0]
                player_ids[player[-3]] = player_id

            current_street = -1
            street_id = None
            row_ids = []
            for action in data["actions"]:
                # print("row_ids", row_ids, len(row_ids))
                if isinstance(action, Street):
                    cursor.execute(
                        """
                    insert into streets (hand_id, type, board_cards)
        values(%s, %s, %s) RETURNING id
                """,
                        (hand_id, action.street_type, action.board_cards),
                    )
                    conn.commit()
                    street_id = cursor.fetchone()[0]
                    current_street += 1
                    row_ids.append(None)
                elif isinstance(action, Action):
                    if action.last_aggressor_index:
                        last_aggressor_action_id = row_ids[action.last_aggressor_index]
                    else:
                        last_aggressor_action_id = None
                    # print("action.last_aggressor_index", action.last_aggressor_index)
                    action_type = "posts" if action.is_blind else action.action_type
                    cursor.execute(
                        """
                    insert into actions (hand_id, action_order, player_id, action_type,amount,bet_ratio, street_id, pot, rake, last_aggressor_action_id, num_active_players,is_blind)
        values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id
                """,
                        (
                            hand_id,
                            action.action_order,
                            player_ids[action.position],
                            action_type.lower(),
                            action.amount,
                            action.bet_ratio,
                            street_id,
                            action.pot,
                            action.rake,
                            last_aggressor_action_id,
                            action.num_active_players,
                            action.is_blind,
                        ),
                    )
                    conn.commit()
                    action_id = cursor.fetchone()[0]
                    row_ids.append(action_id)


# turn position into player_id, add hand_id, street_id
