import os
import pathlib
import json
from tqdm import tqdm
from utils.config import Config
from utils.import_utils import create_dataset, parse_file
from utils.utils import normalize_dataset
import numpy as np
from train.train import train_network
import torch
import os
from env.poker import Poker
from env.data_types import GameTypes, Globals


def main(args):
    chris_folder = pathlib.Path(__file__).parent / "Ignition chris"
    tj_folder = pathlib.Path(__file__).parent / "Ignition tj"
    if args.dataset == "tj":
        target_folder = tj_folder
        dataset_name = "tj_dataset"
    else:
        target_folder = chris_folder
        dataset_name = "chris_dataset"
    dataset_destination = os.path.join(training_params["data_folder"],dataset_name)
    if args.play:
        game_object = Globals.GameTypeDict[GameTypes.OMAHAHI]
        env_params = {
            'game':GameTypes.OMAHAHI,
            'betsizes': game_object.rule_params['betsizes'],
            'bet_type': game_object.rule_params['bettype'],
            'n_players': 2,
            'pot':0,
            'stacksize': game_object.state_params['stacksize'],
            'cards_per_player': game_object.state_params['cards_per_player'],
            'starting_street': game_object.starting_street,
            'global_mapping':config.global_mapping,
            'state_mapping':config.state_mapping,
            'obs_mapping':config.obs_mapping,
            'shuffle':True
        }
        print(f'Environment Parameters: Starting street: {env_params["starting_street"]},\
            Stacksize: {env_params["stacksize"]},\
            Pot: {env_params["pot"]},\
            Bettype: {env_params["bet_type"]},\
            Betsizes: {env_params["betsizes"]}')
        env = Poker(env_params)
        state,obs,done,action_mask,betsize_mask = env.reset()
        while not done:
            action = np.random.choice(np.arange(len(action_mask)),p=action_mask)
            state,obs,done,action_mask,betsize_mask = env.step(action)
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
        training_params = {"epochs": 25, "data_folder": os.path.join(os.getcwd(), "data")}

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
            "epochs": 10,
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
    args = parser.parse_args()
    main(args)
