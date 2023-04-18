import json
import logging
import numpy as np
from requests import request
import torch
from flask import Flask
from flask_cors import CORS
from train.models import Transformer
from utils.config import Config
from utils.utils import state_mapping

from pokerrl.config import Config as EnvConfig
from pokerrl import Game, json_view, return_current_player, player_view

class API:
    def __init__(self,dataset='chris'):
        self.app = Flask(__name__)

        ## LOAD DATASET
        if dataset == 'tj':
            dataset_path = 'data/tj_dataset'
        else:
            dataset_path = 'data/chris_dataset'
        self.game_states = np.load(f"{dataset_path}/states.npy").tolist()
        self.target_actions = (np.load(f"{dataset_path}/actions.npy")).tolist()
        self.target_rewards = np.load(f"{dataset_path}/rewards.npy").tolist()
        self.index = -1
        print(len(self.game_states), len(self.target_actions), len(self.target_rewards))

        ## LOAD MODEL
        config = Config()
        self.device = 'cpu'#torch.device("cuda" if torch.cuda.is_available() else "cpu")
        weights = torch.load('weights/model_99.pth',map_location=torch.device('cpu'))
        self.model = Transformer(config.n_embd,config.n_heads,config.dropout,config.block_size,config.action_size,config.n_layers,self.device)
        self.model.load_state_dict(weights)

        ## LOAD ENVIRONMENT
        self.env_config = EnvConfig()
        self.player_position = self.env_config.player_positions[0]
        self.env = Game(self.env_config)


    def parse_dataset_sample(self,state):
        """Wraps state and passes to frontend. Can be the dummy last state. In which case hero mappings are reversed."""
        state_object = {
            'hero_cards'                :state[state_mapping['hand_range'][0]:state_mapping['hand_range'][1]],
            'board_cards'               :state[state_mapping['board_range'][0]:state_mapping['board_range'][1]],
            'street'                    :state[state_mapping['street']],
            'num_players'               :state[state_mapping['num_players']],
            'hero_position'             :state[state_mapping['hero_position']],
            'hero_active'               :state[state_mapping['hero_active']],
            'vil1_active'               :state[state_mapping['vil1_active']],
            'vil2_active'               :state[state_mapping['vil2_active']],
            'vil3_active'               :state[state_mapping['vil3_active']],
            'vil4_active'               :state[state_mapping['vil4_active']],
            'vil5_active'               :state[state_mapping['vil5_active']],
            'vil1_position'             :state[state_mapping['vil1_position']],
            'vil2_position'             :state[state_mapping['vil2_position']],
            'vil3_position'             :state[state_mapping['vil3_position']],
            'vil4_position'             :state[state_mapping['vil4_position']],
            'vil5_position'             :state[state_mapping['vil5_position']],
            'last_agro_amount'          :state[state_mapping['last_agro_amount']],
            'last_agro_action'          :state[state_mapping['last_agro_action']],
            'last_agro_position'        :state[state_mapping['last_agro_position']],
            'last_agro_is_blind'        :state[state_mapping['last_agro_is_blind']],
            'hero_stack'                :state[state_mapping['hero_stack']],
            'vil1_stack'                :state[state_mapping['vil1_stack']],
            'vil2_stack'                :state[state_mapping['vil2_stack']],
            'vil3_stack'                :state[state_mapping['vil3_stack']],
            'vil4_stack'                :state[state_mapping['vil4_stack']],
            'vil5_stack'                :state[state_mapping['vil5_stack']],
            'pot'                       :state[state_mapping['pot']],
            'amount_to_call'            :state[state_mapping['amount_to_call']],
            'pot_odds'                  :state[state_mapping['pot_odds']],
            'previous_amount'           :state[state_mapping['previous_amount']],
            'previous_position'         :state[state_mapping['previous_position']],
            'previous_action'           :state[state_mapping['previous_action']],
            'previous_bet_is_blind'     :state[state_mapping['previous_bet_is_blind']],
            'next_player'               :state[state_mapping['next_player']],
            'current_player'            :state[state_mapping['current_player']],
        }
        return state_object
    
    def increment_player_position(self):
        self.player_position = self.env_config.player_positions[(self.env_config.player_positions.index(self.player_position) + 1) % len(self.env_config.player_positions)]

    def step(self):
        self.index = min(self.index + 1,len(self.game_states) - 1)
        return json.dumps({'game_states':[self.parse_dataset_sample(game) for game in self.game_states[self.index]],'target_actions': self.target_actions[self.index],'target_rewards': self.target_rewards[self.index]})

    def previous(self):
        self.index = max(self.index - 1,0)
        return json.dumps({'game_states':[self.parse_dataset_sample(game) for game in self.game_states[self.index]],'target_actions': self.target_actions[self.index],'target_rewards': self.target_rewards[self.index]})

    def reset(self):
        self.index = -1
        return self.step()
    
    def inference(self):
        state = torch.tensor(self.game_states[self.index]).to(self.device)
        outputs = self.model(state.unsqueeze(0)).squeeze(0).detach().cpu()
        probs = outputs.softmax(dim=-1)
        return json.dumps({"model_outputs":probs.numpy().tolist()})
    
    def iterate_game_until_player_turn(self,global_states,done,winnings,action_mask):
        current_player = return_current_player(global_states,self.env_config)
        while current_player != self.player_position:
            player_state = player_view(global_states,current_player,self.env_config)
            outputs = self.model(torch.tensor(player_state).to(self.device).unsqueeze(0)).squeeze(0).detach().cpu()
            probs = (outputs * torch.tensor(action_mask).to(self.device)).softmax(dim=-1)
            action = torch.multinomial(probs,1).item()
            global_states,done,winnings,action_mask = self.env.step(action)
            current_player = return_current_player(global_states,self.env_config)
        return global_states,done,winnings,action_mask,current_player
    
    def reset_game(self):
        self.increment_player_position()
        global_states,done,winnings,action_mask = self.env.reset()
        current_player = return_current_player(global_states,self.env_config)
        # global_states,done,winnings,action_mask,current_player = self.iterate_game_until_player_turn(global_states,done,winnings,action_mask)
        return json.dumps({"game_states":json_view(global_states,current_player,self.env_config), "done":done, "winnings":winnings, "action_mask":action_mask.tolist()})
    
    def step_game(self,action):
        print('action',action)
        global_states,done,winnings,action_mask = self.env.step(action)
        current_player = return_current_player(global_states,self.env_config)
        # global_states,done,winnings,action_mask,current_player = self.iterate_game_until_player_turn(global_states,done,winnings,action_mask)
        return json.dumps({"game_states":json_view(global_states,current_player,self.env_config), "done":done, "winnings":winnings, "action_mask":action_mask.tolist()})

    def reset_game_model_observer(self):
        self.increment_player_position()
        global_states,done,winnings,action_mask = self.env.reset()
        global_states,done,winnings,action_mask,current_player = self.iterate_game_until_player_turn(global_states,done,winnings,action_mask)
        return json.dumps({"game_states":json_view(global_states,current_player,self.env_config), "done":done, "winnings":winnings, "action_mask":action_mask.tolist()})
    
    def step_game_model_observer(self,action):
        global_states,done,winnings,action_mask = self.env.step(action)
        global_states,done,winnings,action_mask,current_player = self.iterate_game_until_player_turn(global_states,done,winnings,action_mask)
        return json.dumps({"game_states":json_view(global_states,current_player,self.env_config), "done":done, "winnings":winnings, "action_mask":action_mask.tolist()})
    

# instantiate env
api = API()

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'

cors = CORS(app, resources={r"/api/*": {"origins": "http://localhost:*"}})
cors = CORS(app, resources={r"/api/*": {"origins": "http://127.0.0.1:5501*"}}) # This should be replaced with server public ip

logging.basicConfig(level=logging.DEBUG)

@app.route('/health')
def home():
    return 'Server is up and running'

@app.route('/api/reset')
def reset():
    return api.reset()

@app.route('/api/step', methods=['GET'])
def step():
    return api.step()

@app.route('/api/previous', methods=['GET'])
def previous():
    return api.previous()

@app.route('/api/reset_game', methods=['GET'])
def reset_game():
    return api.reset_game()

@app.route('/api/step_game', methods=['POST'])
def step_game():
    action = request.get_json()
    return api.step_game(action)

@app.route('/api/inference', methods=['GET'])
def inference():
    return api.inference()

if __name__ == '__main__':
    app.run(debug=True, port=4000)