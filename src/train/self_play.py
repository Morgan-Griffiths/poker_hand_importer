import numpy as np
from torch.optim import AdamW
import torch.nn.functional as F
from src.utils.config import Config
import torch
import matplotlib.pyplot as plt
import pokerrl

from src.train.models import Simple, Transformer
from torch.utils.data import Dataset, DataLoader


def gather_trajectories():
    ...


def self_play(training_params, config):
    # torch.cude.empty_cache()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    weight_dir = "src/weights"
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
    config = pokerrl.Config()
    env = pokerrl.Game(config)
    try:
        for e in range(training_params["epochs"]):
            epoch_losses = []
            torch.save(model.state_dict(), f"{weight_dir}/model_{e}.pth")
            global_states, done, winnings, action_mask = env.reset()
            while not done:
                current_player = pokerrl.return_current_player(global_states, config)
                player_state = pokerrl.player_view(
                    global_states, current_player, config
                )
                outputs = (
                    model(torch.tensor(player_state).to(device).unsqueeze(0))
                    .squeeze(0)
                    .detach()
                    .cpu()
                )
                probs = (outputs * torch.tensor(action_mask).to(device)).softmax(dim=-1)
                action = torch.multinomial(probs, 1).item()
                global_states, done, winnings, action_mask = env.step(action)

            # actor critic loss
            # loss = F.cross_entropy(out, target_action)
            # optimizer.zero_grad()
            # loss.backward()
            # optimizer.step()
            # epoch_losses.append(loss.item())
            print(f"Epoch: {e}, loss {np.mean(epoch_losses)}")
            losses.append(np.mean(epoch_losses))
    except Exception as e:
        print(e)
        # print(torch.cuda.memory_summary(device=None, abbreviated=False))
        # save weights
        torch.save(model.state_dict(), f"{weight_dir}/model_{e}.pth")

    # save loss graph
    plt.plot(losses)
    plt.savefig(f"{weight_dir}/losses.png")


if __name__ == "__main__":
    config = Config()
    training_params = {
        "epochs": 10,
    }
    self_play(training_params, config)
