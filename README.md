# Description

Poker hand converter for Bovada/Ignition Poker. Converts hand histories into a data format for training neural networks. It can also load hand histories into Postgres for analysis. It also contains the ability to train a model with pytorch. And visualize the outputs of the model while walking through the hands it was trained on.

Goal is to first behavioral clone on the hand data, then extend cabilities via self play.

## Usage

Convert hands into ML format
`python main.py -c`
Train a model
`python main.py -t`

## Model

The model is ~GPT2

## Future work

- [ ] Double check hand board network can understand hand strength.
- [ ] Self play with player pool
- [ ] Check training stability with self play
- [ ] Get more hands
- [ ] Train a player model that can model the opponent for exploitive play.
