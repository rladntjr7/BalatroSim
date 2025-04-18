#!/usr/bin/env python3

"""
Balatro Simulation Runner
-------------------------
This script runs a simulation of 1000 games of Balatro with different strategies,
using seeds 1-1000 to ensure all strategies play with the same deck for fair comparison.
"""

from simulation import compare_strategies_with_seeds
import time

def main():
    # Fixed parameters
    num_simulations = 1000
    start_seed = 1
    output_prefix = ""
    
    # Print simulation info
    print(f"Starting Balatro simulation with {num_simulations} games")
    print(f"Using seeds {start_seed} to {start_seed + num_simulations - 1}")
    print()
    
    # Start timer
    start_time = time.time()
    
    # Run the simulations
    results, summary = compare_strategies_with_seeds(
        num_simulations=num_simulations,
        start_seed=start_seed,
        output_prefix=output_prefix
    )
    
    # Calculate total time
    elapsed_time = time.time() - start_time
    
    # Print summary
    print(f"\nSimulations completed in {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
    print(f"Results saved to 'simulation_results.csv'")
    print(f"Visualizations saved to 'strategy_comparison_results.png' and 'strategy_pairwise_comparison.png'")
    
    # Print strategy rankings
    print("\nStrategy Rankings (by Mean Score):")
    print("-" * 50)
    print(f"{'Rank':<5} {'Strategy':<15} {'Mean Score':<12} {'Win Rate':<12} {'Avg Plays':<12}")
    print("-" * 50)
    
    # Sort strategies by mean score
    sorted_summary = summary.sort_values(by="Mean Score", ascending=False).reset_index(drop=True)
    
    for i, (_, row) in enumerate(sorted_summary.iterrows(), 1):
        strategy = row["Strategy"]
        mean_score = row["Mean Score"]
        win_rate = row["Win Rate"] * 100  # Convert to percentage
        mean_plays = row["Mean Plays"]
        print(f"{i:<5} {strategy:<15} {mean_score:<12.2f} {win_rate:<12.2f}% {mean_plays:<12.2f}")

if __name__ == "__main__":
    main() 