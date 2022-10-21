import torch.nn as nn
import torch.nn.functional as F
import torch
from utils import state_mapping


# state_mapping = {
#     "hand_range": [0, 8],
#     "board_range": [8, 18],
#     "street": 18,
#     "num_players": 19,
#     "hero_pos": 20,
#     "hero_active": 21,
#     "vil1_active": 22,
#     "vil2_active": 23,
#     "vil3_active": 24,
#     "vil4_active": 25,
#     "vil5_active": 26,
#     "next_player": 27,
#     "next_player2": 28,
#     "next_player3": 29,
#     "next_player4": 30,
#     "next_player5": 31,
#     "last_agro_amount": 32,
#     "last_agro_action": 33,
#     "last_agro_position": 34,
#     "last_agro_is_blind": 35,
#     "hero_stack": 36,
#     "vil1_stack": 37,
#     "vil2_stack": 38,
#     "vil3_stack": 39,
#     "vil4_stack": 40,
#     "vil5_stack": 41,
#     "pot": 42,
#     "amount_to_call": 43,
#     "pot_odds": 44,
#     "previous_amount": 45,
#     "previous_position": 46,
#     "previous_action": 47,
#     "previous_bet_is_blind": 48,
# }


# @torch.no_grad()
# def init_weights(m):
#     # print(m)
#     if type(m) == nn.Linear:
#         torch.nn.init.kaiming_normal_(m, nonlinearity="leaky_relu")
#         # print(m.weight)


class Simple(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(456, 128),
            nn.LeakyReLU(),
            nn.Linear(128, 128),
            nn.LeakyReLU(),
            nn.Linear(128, 64),
            nn.LeakyReLU(),
            nn.Linear(64, 11),
        )
        # self.layers.apply(init_weights)
        self.emb_position = nn.Embedding(7, 8, padding_idx=0)
        self.emb_action = nn.Embedding(12, 8, padding_idx=0)

    def forward(self, state):
        B, M, C = state.shape
        print(state.shape)
        stats = state.float()
        pot = state[:, :, state_mapping["pot"]]
        amnt_to_call = state[:, :, state_mapping["amount_to_call"]]
        previous_amount = state[:, :, state_mapping["previous_amount"]]
        action = self.emb_action(state[:, :, state_mapping["previous_action"]].long())
        position = self.emb_position(
            state[:, :, state_mapping["previous_position"]].long()
        )
        print(action.shape, position.shape, pot.shape)
        x = (
            torch.cat(
                (
                    pot.unsqueeze(-1),
                    amnt_to_call.unsqueeze(-1),
                    previous_amount.unsqueeze(-1),
                    action,
                    position,
                ),
                dim=-1,
            )
            .view(B, -1)
            .float()
        )
        out = self.layers(x)
        print(out.shape)
        return out
