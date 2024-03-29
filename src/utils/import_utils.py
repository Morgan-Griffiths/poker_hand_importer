import re
from typing import Union
from more_itertools import peekable
import numpy as np
from src.utils.utils import (
    MLConversion,
    calc_rake,
    return_standard_max_potlimit_betsize,
)
from src.utils.data_types import (
    ActionType,
    HandData,
    HandStats,
    PlayerData,
    PokerHand,
    PositionStats,
    StatsItem,
    StreetType,
    state_shape,
    Action,
    ActionType,
    Street,
)


def parse_seats(
    lines: peekable, hand_data: HandData
) -> tuple[
    dict[str, PositionStats],
    HandStats,
    list[Union[Action, Street]],
    list[dict[str, dict[str, str]]],
    list[StatsItem],
]:
    actions = [Street(street_type=StreetType.PREFLOP, board_cards=None)]
    stat_data: list[StatsItem] = []
    stacks = []
    stats = HandStats(
        pot=0.0,
        rake=0.0,
        bet_ratios=[],
        num_active_players=0,
        action_order=0,
        last_aggressor=None,
        last_aggressor_index=None,
        penultimate_raise=None,
    )
    seats: dict[str, PositionStats] = {}  # position: hand, stack, hero, seat
    while lines.peek().startswith("Seat"):
        seat_num, position, is_hero, stack = re.search(
            r"Seat (\d+): ([\w\s\+\d]+)(\s\[ME\])? (?:.*)\(\$([0-9\,\.]+)", lines.peek()
        ).groups()
        stack = float(stack.replace(",", ""))
        # stack = 100 * hand_data["bb"] if stack == 0 else stack

        position = position.rstrip()
        next(lines)
        seats[position] = PositionStats(
            seat_num=seat_num,
            is_hero=bool(is_hero),
            stack=stack,
            hole_cards=None,
            winnings=0.0,
            street_total=0.0,
        )
    stats.num_active_players = int(len(seats))
    while not lines.peek().startswith("***"):
        line = next(lines)
        if re.search(r"Dealer|Small Blind|Big Blind|Posts|sit out", line):
            out = re.search(
                r"([\w\s\d\+]+)(\s\[ME\])? : ([\w\-\s]+\b)(?:\s\$)?([\d\,\.]+)?", line
            )
            position, hero, blind, amount = out.groups()
            position = position.rstrip()
            if blind.lower() in [
                "small blind",
                "big blind",
                "posts chip",
                "posts dead chip",
            ]:
                amount = float(amount.replace(",", ""))
                actions.append(
                    Action(
                        position=position,
                        is_hero=bool(hero),
                        action_type=ActionType.RAISE,
                        amount=amount,
                        street_total=amount,
                        bet_ratio=None,
                        is_blind=True,
                        pot=stats.pot,
                        rake=stats.rake,
                        last_aggressor_index=stats.last_aggressor_index,
                        num_active_players=stats.num_active_players,
                        action_order=stats.action_order,
                    )
                )
                try:
                    if amount > hand_data.big_blind:
                        seats[position].street_total += hand_data.big_blind
                    else:
                        seats[position].street_total += amount
                    seats[position].winnings -= amount
                    stats.pot += amount
                    if blind.lower()[:5] != "posts":
                        stats.last_aggressor = position
                        stats.last_aggressor_index = len(actions) - 1
                        stats.penultimate_raise = amount
                except Exception as e:
                    print(line)
                    print(seats)
                    print(position)
                    print(stats)
                    raise ValueError("Blind error", e)
                stat_data.append(
                    StatsItem(
                        pot=stats.pot,
                        num_active_players=stats.num_active_players,
                    )
                )
                stacks.append(
                    {k: {"street_total": seats[k].street_total} for k in seats.keys()}
                )
            elif blind == "Seat sit out":
                stats.num_active_players -= 1
            if blind.lower() in ["small blind", "big blind"]:
                stats.action_order += 1
    hand_data.num_players = stats.num_active_players
    assert stats.last_aggressor is not None, "stats missing last_aggressor"
    return seats, stats, actions, stacks, stat_data


def parse_cards(
    lines: list[str], seats: dict[str, PositionStats], deck: list[str]
) -> None:
    out = re.search(r"([\w\s\d\+]+)(\s\[ME\])? (?:.*)\[([\w\s\d]+)\]", next(lines))
    position, hero, hand = out.groups()
    position = position.rstrip()
    cards = hand.split(" ")
    seats[position].hole_cards = cards
    deck.extend(cards)


def parse_hole_cards(
    lines: peekable, seats: dict[str, PositionStats], deck: list
) -> None:
    while re.search(r"Card dealt", lines.peek()):
        parse_cards(lines, seats, deck)


def parse_board(
    seats: dict,
    stats: HandStats,
    stage: str,
    actions: list[Action],
    stacks: list,
    stat_data: list,
    hand_data: HandData,
    deck: list,
):
    for k in seats.keys():
        seats[k].street_total = 0.0
    stats.action_order = 0
    # parse board cards
    street_name = re.search(r"\*\s([A-Z]+)\s\*", stage).groups()[0]
    board = re.findall(r"([AKQJTcdsh\d]{2})", stage)
    actions.append(Street(street_type=street_name.lower(), board_cards=board))
    stacks.append({k: {"street_total": seats[k].street_total} for k in seats.keys()})
    stat_data.append({"pot": stats.pot, "num_active_players": stats.num_active_players})
    stats.last_aggressor = None
    stats.last_aggressor_index = None
    stats.rake = calc_rake(hand_data.num_players, hand_data.big_blind, stats.pot)
    if len(board) == 3:
        deck.extend(board)
    else:
        deck.append(board[-1])


def parse_actions(
    line: list[str],
    actions: list[Union[Action, Street]],
    stats: HandStats,
    seats: dict[str, PositionStats],
    hand_data: HandData,
    stacks: list,
    stat_data: list,
):
    if re.search(r"All-in|Check|Call|Bets|Raises|Folds", line):
        if re.search(r"All-in", line):
            position, hero, amount, street_total = re.search(
                r"([\w\s\d\+]*[\w\d])\s*(\[ME\])?\s*:(?:\D*)\$([\d\,\.]+)(?:[\D]+)?([\d\,\.]+)?",
                line,
            ).groups()
            if re.search(r"All-in\(raise\)", line):
                street_total = re.search(r"to \$([\d\,\.]+)", line).groups()
                action_type = ActionType.RAISE
            elif (
                isinstance(actions[-1], Street)
                or actions[-1].action_type == ActionType.CHECK
            ):
                # allin bet
                action_type = ActionType.BET
            else:
                action_type = ActionType.CALL
        else:
            position, hero, action_type, amount, street_total = re.search(
                r"([\w\s\d\+]*[\w\d])\s*(\[ME\])?\s*:\s*([\w\-]+)(?:\s\$)?([\d\,\.]+)?(?:[\D]+)?([\d\,\.]+)?",
                line,
            ).groups()
        bet_ratio = 0
        if amount:
            amount = float(amount.replace(",", ""))
            if street_total:
                if isinstance(street_total, tuple):
                    street_total = street_total[0]
                street_total = float(street_total.replace(",", ""))
            else:
                street_total = amount
            if action_type in [ActionType.RAISE, ActionType.BET]:
                if stats.last_aggressor is not None:
                    last_aggro_street_total = seats[stats.last_aggressor].street_total
                else:
                    last_aggro_street_total = 0.0
                min_bet, max_bet = return_standard_max_potlimit_betsize(
                    actions[stats.last_aggressor_index]
                    if stats.last_aggressor_index is not None
                    else None,
                    seats[position].stack + seats[position].winnings,
                    seats[position].street_total,
                    last_aggro_street_total,
                    stats.pot - stats.rake,
                    hand_data.big_blind,
                    stats.penultimate_raise,
                )
                if max_bet > 0 and max_bet > min_bet:
                    bet_ratio = min(
                        round((street_total - min_bet) / (max_bet - min_bet), 2),
                        1.0,
                    )
            stats.pot += amount
            seats[position].street_total += amount
            seats[position].winnings -= amount
            stats.bet_ratios.append(bet_ratio)
        actions.append(
            Action(
                position=position,
                is_hero=bool(hero),
                action_type=action_type,
                amount=amount,
                street_total=street_total if street_total else amount,
                bet_ratio=bet_ratio
                if action_type in [ActionType.RAISE, ActionType.BET]
                else None,
                is_blind=False,
                pot=stats.pot - amount if amount else stats.pot,
                rake=stats.rake,
                last_aggressor_index=stats.last_aggressor_index,
                num_active_players=stats.num_active_players,
                action_order=stats.action_order,
            )
        )
        if action_type in [ActionType.BET, ActionType.RAISE]:
            if stats.last_aggressor is not None:
                stats.penultimate_raise = seats[stats.last_aggressor].street_total
            else:
                stats.penultimate_raise = 0
            stats.last_aggressor = position
            stats.last_aggressor_index = len(actions) - 1
        elif action_type == ActionType.FOLD:
            stats.num_active_players -= 1
        stats.action_order += 1
        stacks.append(
            {k: {"street_total": seats[k].street_total} for k in seats.keys()}
        )
        stat_data.append(
            {"pot": stats.pot, "num_active_players": stats.num_active_players}
        )


def parse_return(line: peekable, seats: dict[str, PositionStats], stats: HandStats):
    if re.search(r"Return", line):
        position, hero, amount = re.search(
            r"([\w\s\d\+]*[\w\d])\s*(\[ME\])?\s*:(?:.*)\$([\d\,\.]+)", line
        ).groups()
        amount = amount.replace(",", "")
        seats[position].winnings += float(amount)
        seats[position].street_total -= float(amount)
        stats.pot -= float(amount)


def parse_stage(
    lines: peekable,
    seats: dict[str, PositionStats],
    stats: HandStats,
    hand_data: HandData,
    deck: list[str],
    actions: list[Union[Action, Street]],
    stacks: list[dict],
    stat_data: list,
):
    stage = next(lines)
    if stage.startswith("*** HOLE"):  # Parsing Preflop
        parse_hole_cards(lines, seats, deck)
    else:  # Parsing Postflop
        parse_board(seats, stats, stage, actions, stacks, stat_data, hand_data, deck)
    # check that none of the cards overlap.
    assert len(set(deck)) == len(deck), f"Cards overlap, {hand_data['file_name']}"
    # print(deck, hand_data["file_name"])
    while not lines.peek().startswith("***"):
        # Parsing actions. Can also be [All-in,All-in(raise)]. First option is either call or bet.
        line = next(lines)
        parse_actions(line, actions, stats, seats, hand_data, stacks, stat_data)
        parse_return(line, seats, stats)
        stats.rake = calc_rake(hand_data.num_players, hand_data.big_blind, stats.pot)


def parse_summary(lines: peekable, seats: dict[str, PositionStats]):
    next(lines)
    while lines.peek() != "" and lines:
        line = next(lines)
        if line.startswith("Seat"):
            out = re.search(
                r": ([\w\s\d\+]*[\w\d])\s*(\[ME\])?(?:\s\$)([\d\,\.]+)?", line
            )
            if out:
                position, hero, amount = out.groups()
                amount = amount.replace(",", "")
                seats[position].winnings += float(amount)
    return {k: seats[k].winnings for k in seats.keys()}


def parse_hand(
    lines: peekable, file_name: str, hand_number: int, hero: str
) -> PokerHand:
    # hand_data = {"file_name": file_name, "hand_number": hand_number, "hero": hero}
    hand_data = HandData(
        file_name=file_name,
        hand_number=hand_number,
        hero=hero,
        ts=None,
        game_type=None,
        bet_limit=None,
        big_blind=None,
        num_players=None,
    )
    if lines.peek().startswith("Ignition"):
        line = next(lines)
        # TODO account for other game types and bet limits
        ts = re.search(r"\-\s(.+)(?<![\sUTC])", line).groups()[0]
        hand_data.ts = ts
        hand_data.game_type = "omaha"
        hand_data.bet_limit = "pot limit"

    if lines.peek().startswith("Table Info"):
        line = next(lines)
        out = re.search(r"Stakes: \$(?:[\d\,\.]+)-\$([\d\.\,]+)(?<!,)", line)
        try:
            bb = float(out.groups()[0])
        except Exception as e:
            print(e, line)
            raise Exception()
    hand_data.big_blind = bb
    seats, stats, actions, stacks, stat_data = parse_seats(lines, hand_data)
    deck = []
    while lines.peek() != "*** SUMMARY ***":
        parse_stage(lines, seats, stats, hand_data, deck, actions, stacks, stat_data)
    # record winnings and losses for all players?
    result = parse_summary(lines, seats)
    # digest data for db insertion
    player_data = {
        k: PlayerData(
            position=k,
            is_hero=seats[k].is_hero,
            stack=seats[k].stack,
            hole_cards=seats[k].hole_cards,
            winnings=seats[k].winnings,
        )
        for k in seats.keys()
    }
    return PokerHand(
        seats=seats,
        stats=stats,
        actions=actions,
        result=result,
        hand_data=hand_data,
        player_data=player_data,
        stat_data=stat_data,
        stack_data=stacks,
    )


def parse_file(lines: list[str], file_name: str, hero: str) -> list[PokerHand]:
    hands = []
    line_iter = peekable(lines)
    num_hands = 0
    while line_iter.peek() == "":
        next(line_iter)
    while line_iter:
        hand = parse_hand(line_iter, file_name, num_hands, hero)
        hands.append(hand)
        num_hands += 1
        if num_hands == 10:
            break
        while line_iter and line_iter.peek() == "":
            next(line_iter)
    return hands


def return_bet_ratios(hands: list[PokerHand]):
    bet_ratios = []
    for hand in hands:
        bet_ratios.append(hand.stats.bet_ratios)
    return bet_ratios


def create_dataset(hands: list[PokerHand]):
    game_states, target_actions, target_rewards = [], [], []
    max_len = 24
    max_original_length = 0
    converter = MLConversion()
    game_states, target_actions, target_rewards = converter.convert_hands(hands)
    padded_states = []
    for s in game_states:
        max_original_length = max(s.shape[0], max_original_length)
        pad_amount = max_len - s.shape[0]
        if pad_amount < 0:
            padded_state = s[abs(pad_amount) :]
            padded_states.append(padded_state)
        else:
            padded = np.zeros((pad_amount, state_shape))
            # padding on end
            padded_state = np.concatenate(
                [s, padded], axis=0
            )  # reverse padding to pad on the end vs in the front.
            padded_states.append(padded_state)
    return np.stack(padded_states), np.stack(target_actions), np.stack(target_rewards)
