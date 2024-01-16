import numpy as np
from torch.optim import AdamW
import torch.nn.functional as F
import torch
import matplotlib.pyplot as plt
from torch.utils.data import Dataset, DataLoader

from src.train.models import Simple, Transformer
from src.utils.config import Config


class PokerDataset(Dataset):
    def __init__(self, states, actions, rewards):
        self.states = states
        self.actions = actions
        self.rewards = rewards

    def __len__(self):
        return len(self.states)

    def __getitem__(self, idx):
        return self.states[idx], self.actions[idx], self.rewards[idx]


class PokerDataLoader(DataLoader):
    def __init__(self, states, actions, rewards, batch_size=32, shuffle=True):
        self.dataset = PokerDataset(states, actions, rewards)
        super().__init__(self.dataset, batch_size=batch_size, shuffle=shuffle)

    def __iter__(self):
        for batch in super().__iter__():
            yield batch

    def __len__(self):
        return len(self.dataset)


def train_network(training_params, game_states, target_actions, target_rewards, config):
    # torch.cude.empty_cache()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    weight_dir = "weights"
    model = Transformer(
        config.n_embd,
        config.n_heads,
        config.dropout,
        config.block_size,
        config.action_size,
        config.n_layers,
        device,
    )
    model.to(device)
    optimizer = AdamW(model.parameters(), lr=0.0003)
    losses = []
    try:
        for e in range(training_params["epochs"]):
            epoch_losses = []

            torch.save(model.state_dict(), f"{weight_dir}/model_{e}.pth")
            for game_state, target_action, target_reward in PokerDataLoader(
                game_states, target_actions, target_rewards
            ):
                game_state = game_state.to(device)
                target_action = target_action.to(device)
                target_reward = target_reward.to(device)
                out = model(game_state)
                loss = F.cross_entropy(out, target_action)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                epoch_losses.append(loss.item())
            print(f"Epoch: {e}, loss {np.mean(epoch_losses)}")
            losses.append(np.mean(epoch_losses))
    except Exception as e:
        print(e)
        # print(torch.cuda.memory_summary(device=None, abbreviated=False))
        # save weights
        torch.save(model.state_dict(), f"{weight_dir}/model_{e}.pth")
        np.save(f"{weight_dir}/losses_{e}.npy", losses)

    # save loss graph
    plt.plot(losses)
    plt.savefig(f"{weight_dir}/losses.png")


if __name__ == "__main__":
    config = Config()
    training_params = {
        "epochs": 10,
    }
    game_states = torch.from_numpy(np.load("data/states.npy"))
    target_actions = torch.from_numpy(np.load("data/actions.npy"))
    target_rewards = torch.from_numpy(np.load("data/rewards.npy"))
    train_network(training_params, game_states, target_actions, target_rewards, config)
