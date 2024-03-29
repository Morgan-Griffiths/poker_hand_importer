import json
import logging
import numpy as np
from requests import request
import torch
from flask import Flask, request
from flask_cors import CORS
from pathlib import Path
import os

from src.utils.utils import select_relevant_actions
from src.train.models import Transformer
from src.utils.config import Config
from src.utils.utils import state_mapping

import pokerrl_env as pokerrl


class API:
    def __init__(self, dataset="tj"):
        self.app = Flask(__name__)

        ## LOAD DATASET
        if dataset == "tj":
            dataset_path = "data/tj_dataset"
        else:
            dataset_path = "data/chris_dataset"
        self.game_states = np.load(f"{dataset_path}/states.npy").tolist()
        self.target_actions = (np.load(f"{dataset_path}/actions.npy")).tolist()
        self.target_rewards = np.load(f"{dataset_path}/rewards.npy").tolist()
        self.index = -1
        print(len(self.game_states), len(self.target_actions), len(self.target_rewards))

        ## LOAD MODEL
        config = Config()
        self.device = (
            "cpu"  # torch.device("cuda" if torch.cuda.is_available() else "cpu")
        )
        weight_dir = Path(os.getcwd()) / "src" / "weights"
        print("weight_dir", weight_dir)
        weights = torch.load(
            f"{weight_dir}/model_6.pth", map_location=torch.device("cpu")
        )
        self.model = Transformer(
            config.n_embd,
            config.n_heads,
            config.dropout,
            config.block_size,
            config.action_size,
            config.n_layers,
            self.device,
        )
        self.model.load_state_dict(weights)

        ## LOAD ENVIRONMENT
        self.env_config = pokerrl.Config(num_players=2)
        self.player_position = self.env_config.player_positions[0]
        self.env = pokerrl.Game(self.env_config)

    def parse_dataset_sample(self, state):
        """Wraps state and passes to frontend. Can be the dummy last state. In which case hero mappings are reversed."""
        state_object = {
            "hero_cards": state[
                state_mapping["hand_range"][0] : state_mapping["hand_range"][1]
            ],
            "board_cards": state[
                state_mapping["board_range"][0] : state_mapping["board_range"][1]
            ],
            "street": state[state_mapping["street"]],
            "num_players": state[state_mapping["num_players"]],
            "hero_position": state[state_mapping["hero_position"]],
            "hero_active": state[state_mapping["hero_active"]],
            "vil1_active": state[state_mapping["vil1_active"]],
            "vil2_active": state[state_mapping["vil2_active"]],
            "vil3_active": state[state_mapping["vil3_active"]],
            "vil4_active": state[state_mapping["vil4_active"]],
            "vil5_active": state[state_mapping["vil5_active"]],
            "vil1_position": state[state_mapping["vil1_position"]],
            "vil2_position": state[state_mapping["vil2_position"]],
            "vil3_position": state[state_mapping["vil3_position"]],
            "vil4_position": state[state_mapping["vil4_position"]],
            "vil5_position": state[state_mapping["vil5_position"]],
            "last_agro_amount": state[state_mapping["last_agro_amount"]],
            "last_agro_action": state[state_mapping["last_agro_action"]],
            "last_agro_position": state[state_mapping["last_agro_position"]],
            "last_agro_is_blind": state[state_mapping["last_agro_is_blind"]],
            "hero_stack": state[state_mapping["hero_stack"]],
            "vil1_stack": state[state_mapping["vil1_stack"]],
            "vil2_stack": state[state_mapping["vil2_stack"]],
            "vil3_stack": state[state_mapping["vil3_stack"]],
            "vil4_stack": state[state_mapping["vil4_stack"]],
            "vil5_stack": state[state_mapping["vil5_stack"]],
            "pot": state[state_mapping["pot"]],
            "amount_to_call": state[state_mapping["amount_to_call"]],
            "pot_odds": state[state_mapping["pot_odds"]],
            "previous_amount": state[state_mapping["previous_amount"]],
            "previous_position": state[state_mapping["previous_position"]],
            "previous_action": state[state_mapping["previous_action"]],
            "previous_bet_is_blind": state[state_mapping["previous_bet_is_blind"]],
            "next_player": state[state_mapping["next_player"]],
            "current_player": state[state_mapping["current_player"]],
        }
        return state_object

    def increment_player_position(self):
        self.player_position = self.env_config.player_positions[
            (self.env_config.player_positions.index(self.player_position) + 1)
            % len(self.env_config.player_positions)
        ]

    def step(self):
        self.index = min(self.index + 1, len(self.game_states) - 1)
        return json.dumps(
            {
                "game_states": [
                    self.parse_dataset_sample(game)
                    for game in self.game_states[self.index]
                ],
                "target_actions": self.target_actions[self.index],
                "target_rewards": self.target_rewards[self.index],
            }
        )

    def previous(self):
        self.index = max(self.index - 1, 0)
        return json.dumps(
            {
                "game_states": [
                    self.parse_dataset_sample(game)
                    for game in self.game_states[self.index]
                ],
                "target_actions": self.target_actions[self.index],
                "target_rewards": self.target_rewards[self.index],
            }
        )

    def reset(self):
        self.index = -1
        return self.step()

    def inference(self):
        state = torch.tensor(self.game_states[self.index]).to(self.device)
        outputs = self.model(state.unsqueeze(0)).detach().cpu()
        relevant_actions = select_relevant_actions(state.unsqueeze(0), outputs)
        probs = relevant_actions.softmax(dim=-1)
        return json.dumps({"model_outputs": probs.numpy().tolist()})

    def pad_states(self, states):
        B = states.shape[0]
        padding = torch.zeros((24 - B, self.env_config.player_state_shape)).to(
            self.device
        )
        padded_states = torch.cat(
            (padding, torch.tensor(states).to(self.device)), dim=0
        ).unsqueeze(0)
        return padded_states

    def iterate_game_until_player_turn(
        self, global_states, done, winnings, action_mask
    ):
        current_player = pokerrl.return_current_player(global_states, self.env_config)
        probs = torch.zeros(self.env_config.num_actions)
        while current_player != self.player_position and not done:
            print(
                "current_player,player_position", current_player, self.player_position
            )
            player_state = pokerrl.player_view(
                global_states, current_player, self.env_config
            )
            padded_state = self.pad_states(player_state)
            outputs = self.model(padded_state).squeeze(0).detach().cpu()
            relevant_actions = select_relevant_actions(padded_state, outputs)
            probs = relevant_actions.softmax(dim=-1) * torch.tensor(action_mask)
            probs = probs / probs.sum()
            print("probs", probs.shape, probs.sum())
            print("action_mask", action_mask.shape, action_mask)
            action = torch.multinomial(probs, 1).item()
            print("model action", action)
            global_states, done, winnings, action_mask = self.env.step(action)
            current_player = pokerrl.return_current_player(
                global_states, self.env_config
            )
        return global_states, done, winnings, action_mask, current_player, probs

    def reset_game(self):
        self.increment_player_position()
        global_states, done, winnings, action_mask = self.env.reset()
        # current_player = pokerrl.return_current_player(global_states,self.env_config)
        (
            global_states,
            done,
            winnings,
            action_mask,
            current_player,
            probs,
        ) = self.iterate_game_until_player_turn(
            global_states, done, winnings, action_mask
        )
        return json.dumps(
            {
                "game_states": pokerrl.json_view(
                    global_states, current_player, self.env_config
                ),
                "done": done,
                "winnings": winnings,
                "action_mask": action_mask.tolist(),
                "model_outputs": probs.numpy().tolist(),
            }
        )

    def step_game(self, action):
        print("player action", action)
        global_states, done, winnings, action_mask = self.env.step(action)
        # current_player = pokerrl.return_current_player(global_states,self.env_config)
        (
            global_states,
            done,
            winnings,
            action_mask,
            current_player,
            probs,
        ) = self.iterate_game_until_player_turn(
            global_states, done, winnings, action_mask
        )
        return json.dumps(
            {
                "game_states": pokerrl.json_view(
                    global_states, current_player, self.env_config
                ),
                "done": done,
                "winnings": winnings,
                "action_mask": action_mask.tolist(),
                "model_outputs": probs.numpy().tolist(),
            }
        )

    # def reset_game_model_observer(self):
    #     self.increment_player_position()
    #     global_states,done,winnings,action_mask = self.env.reset()
    #     global_states,done,winnings,action_mask,current_player = self.iterate_game_until_player_turn(global_states,done,winnings,action_mask)
    #     return json.dumps({"game_states":pokerrl.json_view(global_states,current_player,self.env_config), "done":done, "winnings":winnings, "action_mask":action_mask.tolist()})

    # def step_game_model_observer(self,action):
    #     global_states,done,winnings,action_mask = self.env.step(action)
    #     global_states,done,winnings,action_mask,current_player = self.iterate_game_until_player_turn(global_states,done,winnings,action_mask)
    #     return json.dumps({"game_states":pokerrl.json_view(global_states,current_player,self.env_config), "done":done, "winnings":winnings, "action_mask":action_mask.tolist()})


# instantiate env
api = API()

app = Flask(__name__)
app.config["CORS_HEADERS"] = "Content-Type"

cors = CORS(app, resources={r"/api/*": {"origins": "http://localhost:*"}})
cors = CORS(
    app, resources={r"/api/*": {"origins": "http://127.0.0.1:5501*"}}
)  # This should be replaced with server public ip

logging.basicConfig(level=logging.DEBUG)


@app.route("/health")
def home():
    return "Server is up and running"


@app.route("/api/reset")
def reset():
    return api.reset()


@app.route("/api/step", methods=["GET"])
def step():
    return api.step()


@app.route("/api/previous", methods=["GET"])
def previous():
    return api.previous()


@app.route("/api/reset_game", methods=["GET"])
def reset_game():
    return api.reset_game()


@app.route("/api/step_game", methods=["POST"])
def step_game():
    data = request.get_json()
    action = data["action"]
    return api.step_game(action)


@app.route("/api/inference", methods=["GET"])
def inference():
    return api.inference()


if __name__ == "__main__":
    app.run(debug=True, port=4000)
