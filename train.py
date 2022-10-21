from models import Simple
from torch.optim import AdamW
import torch.nn.functional as F


def train_network(training_params, game_states, target_actions, target_rewards):
    model = Simple()
    optimizer = AdamW(model.parameters(), lr=0.003)
    for e in range(training_params["epochs"]):
        out = model(game_states)
        print("out", out.shape)
        loss = F.cross_entropy(out, target_actions)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        print(loss.item())
