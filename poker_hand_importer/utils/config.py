class Config:
    batch_size = 64
    block_size = 256
    max_iters = 5000
    eval_interval = 500
    learning_rate = 3e-4
    eval_iters = 200
    n_embd = 256
    flattened_token_size = 6144
    head_size = 16
    n_heads = 2
    n_layers = 2
    dropout = 0.2
    action_size = 11
