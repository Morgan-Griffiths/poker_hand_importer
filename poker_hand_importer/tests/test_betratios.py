from more_itertools import peekable
from utils.import_utils import parse_file, return_bet_ratios
from utils.utils import Action
import os

hand1 = [1.0, 0, 0.5, 0.5, 0, 0.5]
hand2 = [1.0, 1.0, 0, 0.28, 0, 1.0]
hand3 = [0]
hand4 = [1.0, 0, 1.0]
hand5 = [1.0]
hand6 = [0, 0.75]
hand7 = [0, 1.0, 0, 0.75]
hand8 = [1.0, 0, 0.5, 1.0, 0, 1.0]
hand9 = [1.0, 0, 0, 1.0]
hand10 = [1.0, 1.0, 0, 0.75]
hand11 = [0, 1.0, 0, 0]
hand12 = [0, 1.0, 0, 1.0, 0, 0.68, 0]
hand13 = [1.0, 0, 1.0, 0.69, 0.07, 0]
ratio_answers = [
    hand1,
    hand2,
    hand3,
    hand4,
    hand5,
    hand6,
    hand7,
    hand8,
    hand9,
    hand10,
    hand11,
    hand12,
    hand13,
]
ohand1 = [0, 1.0]
ohand2 = [1.0, 0.34, 0, 1.0, 0, 0.62]

ratio_answers2 = [ohand1, ohand2]


def test_betratio():
    hand_path = "/Users/morgan/Code/hand_import/hand_example.txt"
    lines = peekable(open(hand_path, "r", encoding="utf-8-sig").read().splitlines())
    hands = parse_file(lines, hand_path, "tj", False)
    bet_ratios = return_bet_ratios(hands)
    assert bet_ratios[0] == [1.0, 0, 1.0, 0.86, 0], bet_ratios


def test_betratio2():
    hand_path = "/Users/morgan/Code/hand_import/hand_example2.txt"
    lines = peekable(open(hand_path, "r", encoding="utf-8-sig").read().splitlines())
    hands = parse_file(lines, hand_path, "tj", False)
    bet_ratios = return_bet_ratios(hands)
    assert bet_ratios[0] == [1.0, 0, 1.0, 0.69, 0.07, 0], bet_ratios


def test_betratio_hh():
    folder = "/Users/morgan/Downloads/Ignition chris"
    hand_path = "27655534 - $10 PL Hi (6 max) - 202209232301.txt"
    lines = peekable(
        open(os.path.join(folder, hand_path), "r", encoding="utf-8-sig")
        .read()
        .splitlines()
    )
    hands = parse_file(lines, hand_path, "tj", False)
    bet_ratios = return_bet_ratios(hands)
    for i, (ratio, answer) in enumerate(zip(bet_ratios, ratio_answers)):
        assert ratio == answer, (ratio, answer, i)
    # assert bet_ratios == [1.0, 0, 0.5, 0.5, 0], bet_ratios


def test_betratio_hh2():
    folder = "/Users/morgan/Downloads/Ignition chris"
    hand_path = "27503356 - $5 PL Hi (6 max) - 202209041958.txt"
    lines = peekable(
        open(os.path.join(folder, hand_path), "r", encoding="utf-8-sig")
        .read()
        .splitlines()
    )
    hands = parse_file(lines, hand_path, "chris", False)
    bet_ratios = return_bet_ratios(hands)
    for i, (ratio, answer) in enumerate(zip(bet_ratios, ratio_answers2)):
        assert ratio == answer, (ratio, answer, i)
    # assert bet_ratios == [1.0, 0, 0.5, 0.5, 0], bet_ratios
