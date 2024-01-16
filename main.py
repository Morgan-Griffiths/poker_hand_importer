import os
import pathlib
import json
from tqdm import tqdm
from poker_hand_importer.utils.config import Config
from poker_hand_importer.utils.import_utils import create_dataset, parse_file
from poker_hand_importer.utils.utils import normalize_dataset
import numpy as np
from poker_hand_importer.train.train import train_network
import torch
import os


def main(args):
    chris_folder = pathlib.Path(__file__).parent / "Ignition chris"
    tj_folder = pathlib.Path(__file__).parent / "Ignition tj"
    if args.dataset == "tj":
        target_folder = tj_folder
        dataset_name = "tj_dataset"
    else:
        target_folder = chris_folder
        dataset_name = "chris_dataset"
    dataset_destination = os.path.join(os.path.join(os.getcwd(),'data'),dataset_name)
    if args.convert:
        all_hands = []
        for i, hand_path in enumerate(tqdm(os.listdir(target_folder))):
            # hand_path = '{os.path.expanduser('~')}/Code/PokerAI/poker/hand_example.txt'
            # hand_path = "24851028 - $20 PL Hi (6 max) - 202108232357.txt"
            lines = (
                open(os.path.join(target_folder, hand_path), "r", encoding="utf-8-sig")
                .read()
                .splitlines()
            )
            hero = "tj" if target_folder == tj_folder else "chris"
            hands = parse_file(lines, hand_path, hero)
            all_hands.extend(hands)
        training_params = {"epochs": 25, "data_folder": dataset_destination}

        # json.dump(all_hands, open("all_hands.json", "w"))
        # all_hands = json.loads(open("all_hands.json", "r").read())
        (game_states, target_actions, target_rewards) = create_dataset(all_hands)

        if not os.path.exists(training_params["data_folder"]):
            os.makedirs(training_params["data_folder"])
        
        if not os.path.exists(dataset_destination):
            os.makedirs(dataset_destination)
        np.save(f"{dataset_destination}/states", game_states)
        np.save(f"{dataset_destination}/actions", target_actions)
        np.save(f"{dataset_destination}/rewards", target_rewards)
        # find max stacks, pot
        # game_states = normalize_dataset(game_states)
    elif args.train:
        config = Config()
        training_params = {
            "epochs": int(args.epochs),
        }
        game_states = torch.from_numpy(np.load(f"{dataset_destination}/states.npy"))
        target_actions = torch.from_numpy(np.load(f"{dataset_destination}/actions.npy") - 1)
        target_rewards = torch.from_numpy(np.load(f"{dataset_destination}/rewards.npy"))
        # print(game_states.shape, target_actions.shape, target_rewards.shape)
        train_network(training_params, game_states, target_actions, target_rewards,config)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="building a dataset from poker txt files from Ignition, Or training the network on the subsequent dataset"
    )
    parser.add_argument("-c", "--convert", action="store_true")
    parser.add_argument("-d", "--dataset", help="which dataset to convert", default="tj")
    parser.add_argument("-t", "--train", action="store_true")
    parser.add_argument("-p", "--play", action="store_true")
    parser.add_argument("-e", "--epochs", help="number of epochs to train for", default=10)

    args = parser.parse_args()
    main(args)
