import einops
import torch.nn as nn
import torch.nn.functional as F
import torch
from src.utils.utils import state_mapping


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
    def __init__(self, head_size, n_embd, block_size, dropout):
        super().__init__()
        self.head_size = head_size
        self.keys = nn.Linear(n_embd, head_size, bias=False)
        self.queries = nn.Linear(n_embd, head_size, bias=False)
        self.values = nn.Linear(n_embd, head_size, bias=False)
        self.dropout = nn.Dropout(dropout)
        self.register_buffer("tril", torch.tril(torch.ones((block_size, block_size))))

    def forward(self, x):
        # x.shape = B,T,C
        B, T, C = x.shape
        k = self.keys(x)
        q = self.queries(x)
        v = self.values(x)
        qk = (
            q @ einops.rearrange(k, "b t c -> b c t")
        ) * self.head_size**0.5  # (b t t)
        # qk = qk.masked_fill(self.tril[:T,:T] == 0,float('-inf'))
        qk = F.softmax(qk, dim=-1)
        qk = self.dropout(qk)
        out = qk @ v  # (b t c)
        return out


class MultiHeadedAttention(nn.Module):
    def __init__(self, n_heads, head_size, n_embd, dropout, block_size):
        super().__init__()
        self.heads = nn.ModuleList(
            [
                SelfAttention(head_size, n_embd, block_size, dropout)
                for _ in range(n_heads)
            ]
        )
        self.projection = nn.Linear(n_embd, n_embd)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        out = torch.cat([h(x) for h in self.heads], dim=-1)
        out = self.dropout(self.projection(out))
        return out


class FeedForward(nn.Module):
    def __init__(self, n_embd, dropout):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_embd, 4 * n_embd),
            nn.ReLU(),
            nn.Linear(4 * n_embd, n_embd),
            nn.Dropout(dropout),
        )

    def forward(self, x):
        return self.net(x)


class TransformerBlock(nn.Module):
    def __init__(self, n_embd, n_heads, dropout, block_size):
        super().__init__()
        self.head = MultiHeadedAttention(
            n_heads, n_embd // n_heads, n_embd, dropout, block_size
        )
        self.ff = FeedForward(n_embd, dropout)
        self.layernorm1 = nn.LayerNorm(n_embd)
        self.layernorm2 = nn.LayerNorm(n_embd)

    def forward(self, x):
        x = x + self.head(self.layernorm1(x))
        x = x + self.ff(self.layernorm2(x))
        return x


class HandBoard(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.suit_emb = nn.Embedding(5, 8, padding_idx=0)
        self.rank_emb = nn.Embedding(14, 8, padding_idx=0)
        self.process_hand = nn.Sequential(
            nn.Linear(64, 64),
            nn.LeakyReLU(),
            nn.Linear(64, 64),
            nn.LeakyReLU(),
            nn.Linear(64, 64),
        )
        self.process_board = nn.Sequential(
            nn.Linear(80, 80),
            nn.LeakyReLU(),
            nn.Linear(80, 80),
            nn.LeakyReLU(),
            nn.Linear(80, 80),
        )
        self.process_hand_board = nn.Sequential(
            nn.Linear(144, 144),
            nn.LeakyReLU(),
            nn.Linear(144, 64),
            nn.LeakyReLU(),
            nn.Linear(64, 64),
        )

    def forward(self, state):
        B, M, C = state.shape
        hand = state[
            :, :, state_mapping["hand_range"][0] : state_mapping["hand_range"][1]
        ]
        board = state[
            :, :, state_mapping["board_range"][0] : state_mapping["board_range"][1]
        ]
        # hand torch.Size([B, 24, 8])
        # board torch.Size([B, 24, 10])
        hand_suit = hand[:, :, 1::2]
        hand_rank = hand[:, :, ::2]
        board_suit = board[:, :, 1::2]
        board_rank = board[:, :, ::2]
        hand_suit = self.suit_emb(hand_suit.long())
        # size (B, M, 4, 8)
        hand_rank = self.rank_emb(hand_rank.long())
        # size (B, M, 4, 8)
        board_suit = self.suit_emb(board_suit.long())
        # size (B, M, 5, 8)
        board_rank = self.rank_emb(board_rank.long())
        # size (B, M, 5, 8)
        hand = torch.cat((hand_suit, hand_rank), dim=-1)
        # size (B, M, 4, 16)
        board = torch.cat((board_suit, board_rank), dim=-1)
        # size (B, M, 5, 16)
        hand = self.process_hand(hand.view(B, M, 64))
        # size (B, M, 64)
        board = self.process_board(board.view(B, M, 80))
        # size (B, M, 80)
        hand_board = torch.cat((hand, board), dim=-1)
        # size (B, M, 144)
        return self.process_hand_board(hand_board)


class PreProcess(nn.Module):
    def __init__(self):
        super().__init__()
        self.process_hand_board = HandBoard()
        self.emb_position = nn.Embedding(7, 8, padding_idx=0)
        self.emb_action = nn.Embedding(12, 8, padding_idx=0)
        self.emb_active = nn.Embedding(2, 8, padding_idx=0)
        self.emb_street = nn.Embedding(5, 8, padding_idx=0)
        self.emb_num_players = nn.Embedding(7, 8, padding_idx=0)
        self.emb_is_blind = nn.Embedding(2, 8, padding_idx=0)
        self.process_pot = nn.Linear(1, 8)
        self.process_last_agro_amount = nn.Linear(1, 8)
        self.process_amount_to_call = nn.Linear(1, 8)
        self.process_pot_odds = nn.Linear(1, 8)
        self.process_stack = nn.Linear(1, 8)
        self.process_previous_amount = nn.Linear(1, 8)

    def forward(self, state):
        B, M, C = state.shape
        # Ordinal features
        hand_board = self.process_hand_board(state)
        # size (B, M, 64)
        street_emb = self.emb_street(state[:, :, state_mapping["street"]].long())
        num_players_emb = self.emb_num_players(
            state[:, :, state_mapping["num_players"]].long()
        )
        hero_pos_emb = self.emb_position(
            state[:, :, state_mapping["hero_position"]].long()
        )
        hero_active_emb = self.emb_active(
            state[:, :, state_mapping["hero_active"]].long()
        )
        vil1_active_emb = self.emb_active(
            state[:, :, state_mapping["vil1_active"]].long()
        )
        vil2_active_emb = self.emb_active(
            state[:, :, state_mapping["vil2_active"]].long()
        )
        vil3_active_emb = self.emb_active(
            state[:, :, state_mapping["vil3_active"]].long()
        )
        vil4_active_emb = self.emb_active(
            state[:, :, state_mapping["vil4_active"]].long()
        )
        vil5_active_emb = self.emb_active(
            state[:, :, state_mapping["vil5_active"]].long()
        )
        vil1_position_emb = self.emb_position(
            state[:, :, state_mapping["vil1_position"]].long()
        )
        vil2_position_emb = self.emb_position(
            state[:, :, state_mapping["vil2_position"]].long()
        )
        vil3_position_emb = self.emb_position(
            state[:, :, state_mapping["vil3_position"]].long()
        )
        vil4_position_emb = self.emb_position(
            state[:, :, state_mapping["vil4_position"]].long()
        )
        vil5_position_emb = self.emb_position(
            state[:, :, state_mapping["vil5_position"]].long()
        )
        last_agro_action_emb = self.emb_action(
            state[:, :, state_mapping["last_agro_action"]].long()
        )
        last_agro_position_emb = self.emb_position(
            state[:, :, state_mapping["last_agro_position"]].long()
        )
        last_agro_is_blind_emb = self.emb_is_blind(
            state[:, :, state_mapping["last_agro_is_blind"]].long()
        )
        previous_position_emb = self.emb_position(
            state[:, :, state_mapping["previous_position"]].long()
        )
        previous_action_emb = self.emb_action(
            state[:, :, state_mapping["previous_action"]].long()
        )
        previous_bet_is_blind_emb = self.emb_is_blind(
            state[:, :, state_mapping["previous_bet_is_blind"]].long()
        )
        next_player_emb = self.emb_position(
            state[:, :, state_mapping["next_player"]].long()
        )

        # Continuous features
        last_agro_amount = self.process_last_agro_amount(
            state[:, :, state_mapping["last_agro_amount"]].unsqueeze(-1).float().float()
        )
        pot = self.process_pot(state[:, :, state_mapping["pot"]].unsqueeze(-1).float())
        amount_to_call = self.process_amount_to_call(
            state[:, :, state_mapping["amount_to_call"]].unsqueeze(-1).float()
        )
        pot_odds = self.process_pot_odds(
            state[:, :, state_mapping["pot_odds"]].unsqueeze(-1).float()
        )
        previous_amount = self.process_previous_amount(
            state[:, :, state_mapping["previous_amount"]].unsqueeze(-1).float()
        )
        hero_stack = self.process_stack(
            state[:, :, state_mapping["hero_stack"]].unsqueeze(-1).float()
        )
        vil1_stack = self.process_stack(
            state[:, :, state_mapping["vil1_stack"]].unsqueeze(-1).float()
        )
        vil2_stack = self.process_stack(
            state[:, :, state_mapping["vil2_stack"]].unsqueeze(-1).float()
        )
        vil3_stack = self.process_stack(
            state[:, :, state_mapping["vil3_stack"]].unsqueeze(-1).float()
        )
        vil4_stack = self.process_stack(
            state[:, :, state_mapping["vil4_stack"]].unsqueeze(-1).float()
        )
        vil5_stack = self.process_stack(
            state[:, :, state_mapping["vil5_stack"]].unsqueeze(-1).float()
        )

        x = torch.cat(
            (
                hand_board,
                street_emb,
                hero_pos_emb,
                vil1_active_emb,
                vil2_active_emb,
                vil3_active_emb,
                vil4_active_emb,
                vil5_active_emb,
                vil1_position_emb,
                vil2_position_emb,
                vil3_position_emb,
                vil4_position_emb,
                vil5_position_emb,
                pot,
                amount_to_call,
                pot_odds,
                previous_amount,
                previous_position_emb,
                previous_action_emb,
                previous_bet_is_blind_emb,
                last_agro_amount,
                last_agro_action_emb,
                last_agro_position_emb,
                last_agro_is_blind_emb,
                num_players_emb,
                next_player_emb,
                hero_stack,
                vil1_stack,
                vil2_stack,
                vil3_stack,
                vil4_stack,
                vil5_stack,
            ),
            dim=-1,
        ).float()
        # post process torch.Size([B, 24, 256])
        return x


class Transformer(nn.Module):
    def __init__(
        self, n_embd, n_heads, dropout, block_size, action_size, n_layers, device
    ):
        super().__init__()
        print("n_embd", n_embd)
        self.device = device
        self.preprocess = PreProcess()
        self.position_embedding = nn.Embedding(block_size, n_embd)
        self.tblocks = nn.Sequential(
            *[
                TransformerBlock(n_embd, n_heads, dropout, block_size)
                for _ in range(n_layers)
            ]
        )
        self.ln_f = nn.LayerNorm(n_embd)
        self.lm_head = nn.Linear(n_embd, action_size)
        self.emb_position = nn.Embedding(7, 8, padding_idx=0)
        self.emb_action = nn.Embedding(12, 8, padding_idx=0)
        self.positions = torch.arange(24)
        self.positions = self.positions.to(self.device)

    def forward(self, state):
        state = state.to(self.device)
        B, M, C = state.shape
        # state torch.Size([B, 24, 50])
        x = self.preprocess(state)
        # x size (B, 24, 64)
        pos_emb = self.position_embedding(self.positions)  # (T,C)
        # pos_emb torch.Size([B, 24, 256])
        x = x + pos_emb
        x = self.tblocks(x)
        x = self.ln_f(x)
        # output 24 actions. one for each state. mask out the ones that are not valid
        x = self.lm_head(x)
        return x
