from player import Player, TARGET_SCORE
from strategy import RandomStrategy, FlushStrategy, StraightStrategy, FullHouseStrategy, HybridStrategy, StraightFlushStrategy
import random
import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

class AutoPlayer(Player):
    """Extension of Player class that automatically makes decisions based on strategy"""
    def __init__(self, strategy_obj):
        super().__init__(strategy_obj.name)
        self.strategy = strategy_obj
    
    def auto_play(self):
        """
        Automatically plays a full game using the strategy
        Returns the final score and number of hands played
        """
        hands_played = 0
        
        while not self.win and (self.playsRemaining > 0 or self.discardsRemaining > 0):
            # If low on hands but have discards, prioritize discarding
            if self.discardsRemaining > 0 and (random.random() < 0.3 or self.playsRemaining <= 2):
                # Get indices to discard from strategy
                indices = self.strategy.select_discard_cards(self)
                if indices:
                    self.discard(indices)
            
            elif self.playsRemaining > 0:
                # The strategy will decide internally whether to use play as discard
                # based on whether the desired hand pattern has been achieved
                indices = self.strategy.select_play_cards(self)
                if indices:
                    if self.play(indices):
                        hands_played += 1
            
            # If we can't do anything, break
            if self.playsRemaining == 0 and self.discardsRemaining == 0:
                break
        
        return self.currentScore, hands_played


class SmartAutoPlayer(AutoPlayer):
    """An enhanced auto player that makes smarter decisions about when to play vs discard"""
    
    def auto_play(self):
        """
        Plays a full game using more advanced decision making
        Returns the final score and number of hands played
        """
        hands_played = 0
        
        while not self.win and (self.playsRemaining > 0 or self.discardsRemaining > 0):
            # First, evaluate the current hand's play potential
            score_potential = 0
            
            if self.hand:
                # Check what we would score if we played now
                indices_to_play = self.strategy.select_play_cards(self)
                if indices_to_play:
                    play_cards = [self.hand[i] for i in indices_to_play]
                    _, hand_name, potential_score = self._simulate_play(play_cards)
                    score_potential = potential_score
            
            # Decision logic for play vs discard
            should_discard = False
            
            if self.discardsRemaining > 0:
                # Discard if the potential score is low and we have many cards to draw
                if score_potential < 50 and len(self.deck.cards) >= 3:
                    should_discard = True
                # More aggressive discarding if we're far from target and running out of hands
                elif self.currentScore < TARGET_SCORE * 0.7 and self.playsRemaining <= 2:
                    should_discard = True
                # Save discards if we're close to winning
                elif self.currentScore >= TARGET_SCORE * 0.8 and score_potential >= 50:
                    should_discard = False
            
            if should_discard and self.discardsRemaining > 0:
                indices = self.strategy.select_discard_cards(self)
                if indices:
                    self.discard(indices)
            elif self.playsRemaining > 0:
                # The strategy will now decide internally whether to use play as discard
                # based on whether the desired hand pattern has been achieved
                indices = self.strategy.select_play_cards(self)
                if indices:
                    if self.play(indices):
                        hands_played += 1
            
            # If we can't do anything, break
            if self.playsRemaining == 0 and self.discardsRemaining == 0:
                break
        
        return self.currentScore, hands_played
    
    def _simulate_play(self, cards):
        """Simulate playing cards without actually playing them"""
        if not cards:
            return [], "Invalid Hand", 0
            
        # Find the best scoring hand
        best_score = 0
        best_hand_name = "High Card"
        
        for hand_name in self.playable_hands:
            score = self._calculate_hand_score(cards, hand_name)
            if score > best_score:
                best_score = score
                best_hand_name = hand_name
        
        return cards, best_hand_name, best_score
    
    def _calculate_hand_score(self, cards, hand_name):
        """Calculate the score for a specific hand type without changing game state"""
        # This is a simplified version - it would need the actual scoring logic from Player.checkScore
        # For now, returning a rough estimate
        base_scores = {
            "High Card": 5,
            "Pair": 20,
            "Two Pair": 40,
            "Triple": 90,
            "Straight": 120,
            "Flush": 140,
            "Full House": 160,
            "Four of a Kind": 420,
            "Straight Flush": 800
        }
        return base_scores.get(hand_name, 0)


def run_simulation(strategy_obj, num_games=100):
    """
    Run multiple games with the given strategy
    Returns the average score, win rate, and a list of all scores
    """
    total_score = 0
    wins = 0
    all_scores = []
    total_hands = 0
    
    for i in range(num_games):
        # Create a new player with the strategy
        player = SmartAutoPlayer(strategy_obj)
        
        # Run the game
        score, hands_played = player.auto_play()
        
        total_score += score
        total_hands += hands_played
        all_scores.append(score)
        
        if player.win:
            wins += 1
    
    avg_score = total_score / num_games
    win_rate = (wins / num_games) * 100
    avg_hands = total_hands / num_games
    
    return avg_score, win_rate, all_scores, avg_hands


def compare_strategies(num_games=100):
    """Compare different strategies and display the results"""
    strategies = [
        RandomStrategy(),
        FlushStrategy(),
        StraightStrategy(),
        FullHouseStrategy(),
        StraightFlushStrategy(),
        HybridStrategy()
    ]
    
    results = {}
    
    for strategy in strategies:
        print(f"Running simulation for {strategy.name} strategy...")
        start_time = time.time()
        avg_score, win_rate, all_scores, avg_hands = run_simulation(strategy, num_games)
        elapsed_time = time.time() - start_time
        
        results[strategy.name] = {
            'avg_score': avg_score,
            'win_rate': win_rate,
            'all_scores': all_scores,
            'avg_hands': avg_hands,
            'time': elapsed_time
        }
        
        print(f"  Average Score: {avg_score:.2f}")
        print(f"  Win Rate: {win_rate:.2f}%")
        print(f"  Average Hands Played: {avg_hands:.2f}")
        print(f"  Time Elapsed: {elapsed_time:.2f} seconds")
        print()
    
    return results


def plot_results(results):
    """Create visualizations of the simulation results"""
    # Bar chart for average scores
    plt.figure(figsize=(12, 6))
    
    # Plot 1: Average Scores
    plt.subplot(1, 2, 1)
    strategies = list(results.keys())
    avg_scores = [results[s]['avg_score'] for s in strategies]
    
    bars = plt.bar(strategies, avg_scores, color=['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6'])
    plt.axhline(y=TARGET_SCORE, color='r', linestyle='--', label=f'Target Score ({TARGET_SCORE})')
    
    # Add values on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 5,
                f'{height:.1f}', ha='center', va='bottom')
    
    plt.ylabel('Average Score')
    plt.title('Average Score by Strategy')
    plt.legend()
    
    # Plot 2: Win Rate
    plt.subplot(1, 2, 2)
    win_rates = [results[s]['win_rate'] for s in strategies]
    
    bars = plt.bar(strategies, win_rates, color=['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6'])
    
    # Add values on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height:.1f}%', ha='center', va='bottom')
    
    plt.ylabel('Win Rate (%)')
    plt.title('Win Rate by Strategy')
    
    plt.tight_layout()
    plt.savefig('strategy_comparison.png')
    plt.close()
    
    # Score distribution
    plt.figure(figsize=(10, 6))
    
    for strategy in strategies:
        scores = results[strategy]['all_scores']
        plt.hist(scores, alpha=0.5, bins=20, label=strategy)
    
    plt.axvline(x=TARGET_SCORE, color='r', linestyle='--', label=f'Target Score ({TARGET_SCORE})')
    plt.xlabel('Final Score')
    plt.ylabel('Frequency')
    plt.title('Score Distribution by Strategy')
    plt.legend()
    plt.savefig('score_distribution.png')
    plt.close()


def run_simulation_with_seed(strategy_obj, seed):
    """
    Run a game with the given strategy and seed
    Returns the score, win status, and hands played
    """
    # Set the random seed
    random.seed(seed)
    
    # Create a new player with the strategy
    player = SmartAutoPlayer(strategy_obj)
    
    # Run the game
    score, hands_played = player.auto_play()
    
    return score, player.win, hands_played

def plot_results_comparison(results, output_prefix=""):
    """
    Create visualizations comparing all strategies
    
    Parameters:
    - results: DataFrame with results
    - output_prefix: prefix to add to output filenames
    """
    # Set the style
    plt.style.use('seaborn-whitegrid')
    
    # 1. Score Distribution (Box Plot)
    plt.figure(figsize=(14, 8))
    plt.subplot(2, 2, 1)
    sns.boxplot(x="Strategy", y="Score", data=results)
    plt.axhline(y=TARGET_SCORE, color='r', linestyle='--', label=f'Target Score ({TARGET_SCORE})')
    plt.title('Score Distribution by Strategy')
    plt.xticks(rotation=45)
    plt.legend()
    
    # 2. Win Rate Comparison (Bar Plot)
    plt.subplot(2, 2, 2)
    win_rates = results.groupby("Strategy")["Win"].mean() * 100
    win_rates.plot(kind='bar', color='green')
    plt.title('Win Rate by Strategy (%)')
    plt.ylabel('Win Rate (%)')
    plt.xticks(rotation=45)
    
    # 3. Plays to Complete (Box Plot) - only for winning games
    plt.subplot(2, 2, 3)
    winning_games = results[results["Win"] == True]
    if not winning_games.empty:
        sns.boxplot(x="Strategy", y="PlaysToComplete", data=winning_games)
        plt.title('Plays Required to Win')
        plt.xticks(rotation=45)
    
    # 4. Score Histogram
    plt.subplot(2, 2, 4)
    for strategy in results["Strategy"].unique():
        strategy_data = results[results["Strategy"] == strategy]
        sns.histplot(strategy_data["Score"], label=strategy, kde=True, alpha=0.4)
    plt.axvline(x=TARGET_SCORE, color='r', linestyle='--', label=f'Target Score ({TARGET_SCORE})')
    plt.title('Score Distribution')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(f'{output_prefix}strategy_comparison_results.png')
    
    # Create a heatmap for pairwise strategy comparison
    plt.figure(figsize=(10, 8))
    
    # Create a matrix of win percentages for strategy A vs strategy B
    strategies = results["Strategy"].unique()
    comparison_matrix = np.zeros((len(strategies), len(strategies)))
    
    for i, strategy_a in enumerate(strategies):
        for j, strategy_b in enumerate(strategies):
            if i == j:
                # Same strategy, set to 0.5 (50%)
                comparison_matrix[i, j] = 0.5
            else:
                # Compare strategies across the same seeds
                seeds = results["Seed"].unique()
                a_wins = 0
                total = 0
                
                for seed in seeds:
                    score_a = results[(results["Strategy"] == strategy_a) & 
                                     (results["Seed"] == seed)]["Score"].values[0]
                    score_b = results[(results["Strategy"] == strategy_b) & 
                                     (results["Seed"] == seed)]["Score"].values[0]
                    
                    if score_a > score_b:
                        a_wins += 1
                    
                    total += 1
                
                comparison_matrix[i, j] = a_wins / total
    
    # Create heatmap
    sns.heatmap(comparison_matrix, annot=True, fmt=".2f", 
                xticklabels=strategies, yticklabels=strategies, 
                cmap="RdYlGn", center=0.5)
    plt.title('Strategy A (row) vs Strategy B (column) - Win Rate')
    plt.savefig(f'{output_prefix}strategy_pairwise_comparison.png')
    
    plt.close('all')  # Close all figures


def compare_strategies_with_seeds(num_simulations=1000, start_seed=1, output_prefix=""):
    """
    Compare different strategies across multiple seeds
    Each seed is used for all strategies for fair comparison
    
    Parameters:
    - num_simulations: number of simulations to run
    - start_seed: the starting seed number
    - output_prefix: prefix to add to output filenames
    """
    strategies = [
        RandomStrategy(),
        FlushStrategy(),
        StraightStrategy(),
        FullHouseStrategy(),
        StraightFlushStrategy(),
        HybridStrategy()
    ]
    
    # Create a DataFrame to store results
    results = pd.DataFrame(columns=["Strategy", "Seed", "Score", "Win", "PlaysToComplete"])
    
    print(f"Running {num_simulations} simulations with seeds {start_seed}-{start_seed+num_simulations-1} for all strategies...")
    
    start_time = time.time()
    
    # Run simulations for each seed
    for seed in range(start_seed, start_seed + num_simulations):
        if (seed - start_seed) % 100 == 0:
            print(f"Running simulations for seed {seed}...")
        
        for strategy in strategies:
            score, win, hands_played = run_simulation_with_seed(strategy, seed)
            
            # Add result to DataFrame using concat instead of append
            new_row = pd.DataFrame({
                "Strategy": [strategy.name],
                "Seed": [seed],
                "Score": [score],
                "Win": [win],
                "PlaysToComplete": [hands_played if win else None]
            })
            results = pd.concat([results, new_row], ignore_index=True)
    
    elapsed_time = time.time() - start_time
    print(f"Simulations completed in {elapsed_time:.2f} seconds")
    
    # Save results to CSV
    results.to_csv(f"{output_prefix}simulation_results.csv", index=False)
    
    # Generate summary statistics
    summary = results.groupby("Strategy").agg({
        "Score": ["mean", "std", "min", "max"],
        "Win": "mean",  # Win percentage
        "PlaysToComplete": ["mean", "std", "min", "max"]
    }).reset_index()
    
    # Rename columns for better readability
    summary.columns = ["Strategy", "Mean Score", "Std Score", "Min Score", "Max Score", 
                      "Win Rate", "Mean Plays", "Std Plays", "Min Plays", "Max Plays"]
    
    # Display summary
    print("\nSummary Statistics:")
    print(summary)
    
    # Create visualizations
    plot_results_comparison(results, output_prefix)
    
    return results, summary


if __name__ == "__main__":
    # Run seed-based simulations
    print("Running seed-based simulations for all strategies...")
    
    # Number of simulations to run
    num_simulations = 1000
    print(f"Running {num_simulations} simulations with seeds 1-{num_simulations} for all strategies...")
    
    # Run the simulations with seeds
    results_with_seeds, summary = compare_strategies_with_seeds(num_simulations)
    
    # Plot the results with seeds
    try:
        plot_results_comparison(results_with_seeds)
        print("Results plotted and saved to 'strategy_comparison_results.png' and 'strategy_pairwise_comparison.png'")
    except Exception as e:
        print(f"Error plotting results: {e}")
    
    # Print the final comparison with seeds
    print("\nFinal Results with Seeds:")
    print("-" * 50)
    print(f"{'Strategy':<15} {'Avg Score':<12} {'Win Rate':<12} {'Avg Plays':<12}")
    print("-" * 50)
    
    # Sort strategies by average score
    for _, row in summary.iterrows():
        strategy = row["Strategy"]
        mean_score = row["Mean Score"]
        win_rate = row["Win Rate"] * 100  # Convert to percentage
        mean_plays = row["Mean Plays"]
        print(f"{strategy:<15} {mean_score:<12.2f} {win_rate:<12.2f}% {mean_plays:<12.2f}") 