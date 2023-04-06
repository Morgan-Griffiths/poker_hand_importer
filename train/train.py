import numpy as np
from train.models import Simple,Transformer
from torch.optim import AdamW
import torch.nn.functional as F
from utils.config import Config
import torch


def train_network(training_params, game_states, target_actions, target_rewards,config):
    model = Transformer(config.flattened_token_size,config.n_embd,config.n_heads,config.dropout,config.block_size,config.action_size,config.n_layers)
    optimizer = AdamW(model.parameters(), lr=0.003)
    for e in range(training_params["epochs"]):
        out = model(game_states)
        print("out", out.shape)
        print('target_actions', target_actions.shape)
        loss = F.cross_entropy(out, target_actions)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        print('loss',loss.item())

if __name__ == "__main__":
    config = Config()
    training_params = {
        "epochs": 10,
    }
    game_states = torch.from_numpy(np.load("data/states.npy"))
    target_actions = torch.from_numpy(np.load("data/actions.npy"))
    target_rewards = torch.from_numpy(np.load("data/rewards.npy"))
    train_network(training_params, game_states, target_actions, target_rewards,config)