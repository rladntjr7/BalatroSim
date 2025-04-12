# Balatro Strategy Simulation

This program simulates different strategies for playing Balatro, a popular card game. It allows you to compare the effectiveness of different hand-building strategies.

## Features

- Play the game manually
- Run simulations to compare different card selection strategies
- Visualize results with bar charts and histograms
- Extensible strategy system for creating new approaches

## Available Strategies

1. **Random Strategy**: Randomly selects cards to play or discard
2. **Flush Strategy**: Prioritizes collecting cards of the same suit
3. **Straight Strategy**: Prioritizes building sequential cards
4. **Full House Strategy**: Prioritizes building three-of-a-kind and pairs together

## How to Run

### Manual Play

```
python main.py
```

This allows you to play the game manually, selecting which cards to play or discard.

### Run Simulations

```
python main.py sim [num_games]
```

Where `[num_games]` is optional and defaults to 100 if not specified.

For example:
```
python main.py sim 500
```

This will run 500 simulations for each strategy, comparing their performance.

Alternatively, you can run the simulation module directly:
```
python simulation.py
```

## Simulation Output

The simulation will produce:

1. Terminal output showing performance metrics for each strategy
2. `strategy_comparison.png`: Bar charts comparing average scores and win rates
3. `score_distribution.png`: Histogram showing the distribution of final scores

## Creating New Strategies

To create a new strategy:

1. Create a new class in `strategy.py` that inherits from `Strategy`
2. Implement the required methods:
   - `select_play_cards(player)`: Returns indices of cards to play
   - `select_discard_cards(player)`: Returns indices of cards to discard
3. Add your strategy to the list in `compare_strategies()` in `simulation.py`

## Game Rules

- Each player starts with 4 hands and 4 discards
- The goal is to reach a target score (default: 600 points)
- Different hand combinations give different scores:
  - High Card: Low base score
  - Pair: 2 cards of the same rank
  - Two Pair: 2 sets of pairs
  - Triple: 3 cards of the same rank
  - Straight: 5 cards in sequence
  - Flush: 5 cards of the same suit
  - Full House: 3 cards of one rank + 2 of another
  - Four of a Kind: 4 cards of the same rank
  - Straight Flush: 5 sequential cards of the same suit 