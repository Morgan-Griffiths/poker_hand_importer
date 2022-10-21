import os
from tqdm import tqdm
from import_utils import create_dataset, parse_file
import numpy as np


def main():
    chris_folder = "/Users/morgan/Downloads/Ignition chris"
    tj_folder = "/Users/morgan/Downloads/Ignition tj"
    target_folder = chris_folder
    for i, hand_path in enumerate(tqdm(os.listdir(target_folder))):
        # hand_path = '/Users/morgan/Code/PokerAI/poker/hand_example.txt'
        # hand_path = "24851028 - $20 PL Hi (6 max) - 202108232357.txt"
        # logger.debug(f'hand_path: {hand_path}')
        # try:
        # lines = open(hand_path,'r',encoding='utf-8-sig').read().splitlines()
        lines = (
            open(os.path.join(target_folder, hand_path), "r", encoding="utf-8-sig")
            .read()
            .splitlines()
        )
        hero = "tj" if target_folder == tj_folder else "chris"
        hands = parse_file(lines, hand_path, hero, db_insertion=False)
        create_dataset(hands)
        # if db_insertion:
        #     store_hand(hand)
        if i == 0:
            break
        # break


main()
