import json
import logging
import numpy as np
from flask import Flask
from flask_cors import CORS
from utils.utils import state_mapping


class API:
    def __init__(self):
        self.game_states = np.load("data/states.npy").tolist()
        self.target_actions = (np.load("data/actions.npy")).tolist()
        self.target_rewards = np.load("data/rewards.npy").tolist()
        self.index = -1
        print(len(self.game_states), len(self.target_actions), len(self.target_rewards))

    def parse_env_outputs(self,state):
        """Wraps state and passes to frontend. Can be the dummy last state. In which case hero mappings are reversed."""
        state_object = {
            'hero_cards'                :state[state_mapping['hand_range'][0]:state_mapping['hand_range'][1]],
            'board_cards'               :state[state_mapping['board_range'][0]:state_mapping['board_range'][1]],
            'street'                    :state[state_mapping['street']],
            'num_players'               :state[state_mapping['num_players']],
            'hero_pos'                  :state[state_mapping['hero_pos']],
            'hero_active'               :state[state_mapping['hero_active']],
            'vil1_active'               :state[state_mapping['vil1_active']],
            'vil2_active'               :state[state_mapping['vil2_active']],
            'vil3_active'               :state[state_mapping['vil3_active']],
            'vil4_active'               :state[state_mapping['vil4_active']],
            'vil5_active'               :state[state_mapping['vil5_active']],
            'vil1_position'               :state[state_mapping['vil1_position']],
            'vil2_position'              :state[state_mapping['vil2_position']],
            'vil3_position'              :state[state_mapping['vil3_position']],
            'vil4_position'              :state[state_mapping['vil4_position']],
            'vil5_position'              :state[state_mapping['vil5_position']],
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
        }
        return state_object

    def step(self):
        self.index = min(self.index + 1,len(self.game_states) - 1)
        return json.dumps({'game_states':[self.parse_env_outputs(game) for game in self.game_states[self.index]],'target_actions': self.target_actions[self.index],'target_rewards': self.target_rewards[self.index]})

    def reset(self):
        self.index = -1
        return self.step()
    
    def previous(self):
        self.index = max(self.index - 1,0)
        return json.dumps({'game_states':[self.parse_env_outputs(game) for game in self.game_states[self.index]],'target_actions': self.target_actions[self.index],'target_rewards': self.target_rewards[self.index]})


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

if __name__ == '__main__':
    app.run(debug=True, port=4000)