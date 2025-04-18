# Balatro Strategy Simulation

This project simulates different strategies for playing the card game Balatro and compares their performance.

## Strategies

The following strategies are implemented:

1. **Flush Strategy**: Prioritizes collecting cards of the same suit to make flush hands. If a flush isn't possible with the current hand, it will try to discard cards that don't contribute to a potential flush.

2. **Straight Strategy**: Focuses on creating straight hands by keeping cards with sequential ranks. It will try to discard cards that don't contribute to a potential straight.

3. **Full House Strategy**: Aims to create full house hands by collecting three cards of one rank and two of another. It will prioritize keeping cards that contribute to pairs and three-of-a-kinds.

4. **Straight Flush Strategy**: The most ambitious strategy, which tries to create straight flush hands (both a straight and a flush). If that's not possible, it will fall back to either flush or straight depending on which is more likely.

5. **Hybrid Strategy**: A combination approach that evaluates each potential hand type and chooses the one with the highest probability of success based on the current hand and remaining deck.

6. **Random Strategy**: Makes completely random decisions for comparison purposes.

## Enhanced Strategy Features

All strategies have been enhanced with the following features:

- **Selective Play as Discard**: When a player has no discards left but multiple plays remaining, strategies will intelligently use play actions to discard unwanted cards *only when* their desired hand pattern hasn't been achieved yet. This helps optimize the hand when regular discards are no longer available, without wasting play actions when a good hand is already formed.

- **Smart Decision Making**: The simulation uses SmartAutoPlayer which makes intelligent decisions about when to play vs. discard based on the current game state, including:
  - Evaluating hand potential before making decisions
  - Being more aggressive with discarding when far from the target score
  - Saving discards when close to winning with a good hand

## Running the Simulation

Simply run the simulation script:

```bash
python run_simulation.py
```

This will run a full simulation with 1000 seeds (1-1000) for each strategy, comparing their performance.

## Output

The simulation produces the following outputs:

1. A CSV file with detailed results for each strategy and seed
2. A summary of statistics for each strategy
3. Visualizations comparing the strategies:
   - Box plot of score distributions
   - Bar chart of win rates
   - Box plot of plays required to win
   - Histogram of final scores
   - Heatmap showing head-to-head comparisons between strategies

## Metrics

The strategies are compared using several metrics:

- **Final Score**: The total score achieved by each strategy
- **Win Rate**: The percentage of games where the strategy reached the target score (600)
- **Plays to Reach Target**: How many plays it took to reach the target score (for winning games)

## Fair Comparison

To ensure a fair comparison, all strategies play with the same deck (generated from the same seed) for each simulation run. This approach uses Common Random Numbers to reduce variance and better isolate the effect of different strategies. 