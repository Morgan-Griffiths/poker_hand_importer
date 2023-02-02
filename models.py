import einops
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


class SelfAttention(nn.Module):
    def __init__(self,head_size,n_embd,block_size,dropout):
        super().__init__()
        self.head_size = head_size
        self.keys = nn.Linear(n_embd,head_size,bias=False)
        self.queries = nn.Linear(n_embd,head_size,bias=False)
        self.values = nn.Linear(n_embd,head_size,bias=False)
        self.dropout = nn.Dropout(dropout)
        self.register_buffer('tril',torch.tril(torch.ones((block_size,block_size))))


    def forward(self,x):
        # x.shape = B,T,C
        B,T,C = x.shape
        k = self.keys(x)
        q = self.queries(x)
        v = self.values(x)
        qk = (q @ einops.rearrange(k,'b t c -> b c t')) * self.head_size**0.5 # (b t t)
        qk = qk.masked_fill(self.tril[:T,:T] == 0,float('-inf'))
        qk = F.softmax(qk,dim=-1)
        qk = self.dropout(qk)
        out = qk @ v # (b t c)
        return out

class MultiHeadedAttention(nn.Module):
    def __init__(self,n_heads,head_size,n_embd,dropout,block_size):
        super().__init__()
        self.heads = nn.ModuleList([SelfAttention(head_size,n_embd,dropout,block_size) for _ in range(n_heads)])
        self.projection = nn.Linear(n_embd,n_embd)
        self.dropout = nn.Dropout(dropout)

    def forward(self,x):
        out = torch.cat([h(x) for h in self.heads],dim=-1)
        out = self.dropout(self.projection(out))
        return out

class FeedForward(nn.Module):
    def __init__(self,n_embd,dropout):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_embd,4 * n_embd),
            nn.ReLU(),
            nn.Linear(4 * n_embd,n_embd),
            nn.Dropout(dropout)
        )

    def forward(self,x):
        return self.net(x)

class TransformerBlock(nn.Module):
    def __init__(self,n_embd,n_heads,dropout,block_size):
        super().__init__()
        self.head = MultiHeadedAttention(n_heads,n_embd//n_heads,n_embd,dropout,block_size)
        self.ff = FeedForward(n_embd,dropout)
        self.layernorm1 = nn.LayerNorm(n_embd)
        self.layernorm2 = nn.LayerNorm(n_embd)

    def forward(self,x):
        x = x + self.head(self.layernorm1(x))
        x = x + self.ff(self.layernorm2(x))
        return x

class Transformer(nn.Module):
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
