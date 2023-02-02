import os
from tqdm import tqdm
from import_utils import create_dataset, parse_file
from utils import normalize_dataset
import numpy as np
from train import train_network
import torch


def main():
    chris_folder = "/Users/morgan/Downloads/Ignition chris"
    tj_folder = "/Users/morgan/Downloads/Ignition tj"
    target_folder = chris_folder
    all_hands = []
    for i, hand_path in enumerate(tqdm(os.listdir(target_folder))):
        # hand_path = '/Users/morgan/Code/PokerAI/poker/hand_example.txt'
        # hand_path = "24851028 - $20 PL Hi (6 max) - 202108232357.txt"
        # logger.debug(f'hand_path: {hand_path}')
        # try:
        # lines = open(hand_path,'r',encoding='utf-8-sig').read().splitlines()
        # print(hand_path)
        lines = (
            open(os.path.join(target_folder, hand_path), "r", encoding="utf-8-sig")
            .read()
            .splitlines()
        )
        hero = "tj" if target_folder == tj_folder else "chris"
        hands = parse_file(lines, hand_path, hero)
        all_hands.extend(hands)
        # if db_insertion:
        #     store_hand(hand)
        # if i == 5:
        #     break
        # break
    training_params = {"epochs": 25, "data_folder": os.path.join(os.getcwd(), "data")}

    (game_states, target_actions, target_rewards) = create_dataset(all_hands)

    # np.save("data/states", game_states)
    # np.save("data/actions", target_actions)
    # np.save("data/rewards", target_rewards)
    # find max stacks, pot
    # game_states = normalize_dataset(game_states)
    game_states = torch.from_numpy(game_states)
    target_actions = torch.from_numpy(target_actions)
    target_rewards = torch.from_numpy(target_rewards)
    print(game_states.shape, target_actions.shape, target_rewards.shape)
    # train_network(training_params, game_states, target_actions, target_rewards)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="building a dataset from poker txt files from Ignition, Or training the network on the subsequent dataset"
    )
    parser.add_argument("-d", "--dataset", action="store_true")
    args = parser.parse_args()
    main(args.dataset)
