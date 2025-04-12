from player import Player, TARGET_SCORE
from strategy import RandomStrategy, FlushStrategy, StraightStrategy, FullHouseStrategy
import random
import time
import matplotlib.pyplot as plt
import numpy as np

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
        
        while not self.win and (self.handsRemaining > 0 or self.discardsRemaining > 0):
            # Decide whether to play or discard
            if self.discardsRemaining > 0 and random.random() < 0.3:  # 30% chance to discard
                # Get indices to discard from strategy
                indices = self.strategy.select_discard_cards(self)
                if indices:
                    self.discard(indices)
            
            elif self.handsRemaining > 0:
                # Get indices to play from strategy
                indices = self.strategy.select_play_cards(self)
                if indices:
                    if self.play(indices):
                        hands_played += 1
            
            # If we can't do anything, break
            if self.handsRemaining == 0 and self.discardsRemaining == 0:
                break
        
        return self.currentScore, hands_played


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
        player = AutoPlayer(strategy_obj)
        
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
        FullHouseStrategy()
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
    
    bars = plt.bar(strategies, avg_scores, color=['#3498db', '#2ecc71', '#e74c3c', '#f39c12'])
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
    
    bars = plt.bar(strategies, win_rates, color=['#3498db', '#2ecc71', '#e74c3c', '#f39c12'])
    
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


if __name__ == "__main__":
    # Number of games to simulate for each strategy
    num_games = 100
    print(f"Running {num_games} simulations for each strategy...")
    
    # Run the simulations
    results = compare_strategies(num_games)
    
    # Plot the results
    try:
        plot_results(results)
        print("Results plotted and saved to 'strategy_comparison.png' and 'score_distribution.png'")
    except Exception as e:
        print(f"Error plotting results: {e}")
    
    # Print the final comparison
    print("\nFinal Results:")
    print("-" * 50)
    print(f"{'Strategy':<15} {'Avg Score':<12} {'Win Rate':<12} {'Avg Hands':<12}")
    print("-" * 50)
    
    # Sort strategies by average score
    sorted_strategies = sorted(results.keys(), key=lambda s: results[s]['avg_score'], reverse=True)
    
    for strategy in sorted_strategies:
        res = results[strategy]
        print(f"{strategy:<15} {res['avg_score']:<12.2f} {res['win_rate']:<12.2f}% {res['avg_hands']:<12.2f}") 