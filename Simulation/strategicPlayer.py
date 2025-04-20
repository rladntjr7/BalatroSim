from player import Player
from strategy import Strategy
import itertools

class StrategicPlayer(Player):
    def __init__(self, strategy):
        """Initialize the strategic player with a specific strategy"""
        super().__init__(strategy)
        self.target_hand = strategy.target_hand  # The hand type we're currently aiming for
        
    def play_strategically(self, verbose=False):
        """Play the game using the strategy until no moves remain"""
        if verbose:
            print(f"Starting game with {self.strategy.name} strategy")
        
        # Flag to detect when no valid action is possible
        while self.playsRemaining > 0 or self.discardsRemaining > 0:
            if verbose:
                print(f"\nHand: {[str(card) for card in self.hand]}")
                print(f"Plays remaining: {self.playsRemaining}, Discards remaining: {self.discardsRemaining}")
            
            # Check all possible combinations of cards for valid hands
            best_hand = None
            best_score = 0
            best_indices = None
            
            # Check combinations of 5 cards for made hands
            if self.playsRemaining > 0:  # Only check if we can actually play
                for indices in itertools.combinations(range(len(self.hand)), 5):
                    cards = [self.hand[i] for i in indices]
                    hand_name, score = self.checkScore(cards)
                    
                    if score > best_score:
                        best_hand = hand_name
                        best_score = score
                        best_indices = list(indices)
            
            # Flag to track if we took any action
            action_taken = False
            
            # Determine what to do based on whether we have a target hand
            if self.playsRemaining > 0 and best_hand in self.target_hand:
                if verbose:
                    print(f"Found {best_hand} hand with score {best_score}")
                
                # Play the hand
                action_taken = self.play(best_indices, verbose)
            else:
                # No valid hand found, follow discard/play strategy
                if self.discardsRemaining > 0:
                    # Use discard strategy
                    indices_to_discard = self.strategy.select_discard_cards(self)
                    
                    if verbose:
                        print(f"Discarding indices {indices_to_discard}")
                    
                    if indices_to_discard:
                        action_taken = self.discard(indices_to_discard)
                    elif self.playsRemaining > 0:
                        # If no cards to discard, use play as discard
                        indices_to_play = self.strategy.select_play_cards(self)
                        
                        if verbose:
                            print(f"No good discard option, playing indices {indices_to_play}")
                        
                        if indices_to_play:
                            action_taken = self.play(indices_to_play, verbose)
                
                elif self.playsRemaining > 0:
                    # No discards left, use play strategy
                    indices_to_play = self.strategy.select_play_cards(self)
                    
                    if verbose:
                        print(f"Playing indices {indices_to_play}")
                    
                    if indices_to_play:
                        action_taken = self.play(indices_to_play, verbose)
            
            # Break the loop if no action was taken
            if not action_taken:
                if verbose:
                    print("No valid move available, ending game.")
                break
        
        # Game is over, report results
        if verbose:
            print("\nGame Over!")
            print(f"Final score: {self.currentScore}")
            if self.remainingPlaysToWin > 0:
                print(f"Won with {self.remainingPlaysToWin} plays remaining!")
            else:
                print("Did not reach target score.")
            
            print("\nHand History:")
            for i, (cards, hand_name, score) in enumerate(self.history):
                print(f"{i+1}. {hand_name}: {cards} - {score} points")
        
        return {
            "score": self.currentScore,
            "remainingPlaysToWin": self.remainingPlaysToWin,
            "history": self.history
        }
    
    def simulate_games(self, num_games=100, verbose=False):
        """Run multiple simulations and return statistics"""
        results = []
        wins = 0
        total_score = 0
        remaining_plays = 0
        
        for i in range(num_games):
            # Reset player for new game
            self.__init__(self.strategy)
            
            game_result = self.play_strategically(verbose=verbose)
            results.append(game_result)
            
            total_score += game_result["score"]
            if game_result["remainingPlaysToWin"] > 0:
                wins += 1
                remaining_plays += game_result["remainingPlaysToWin"]
        
        # Calculate statistics
        win_rate = wins / num_games
        avg_score = total_score / num_games
        avg_remaining_plays = remaining_plays / wins if wins > 0 else 0
        
        stats = {
            "strategy": self.strategy.name,
            "games_played": num_games,
            "wins": wins,
            "win_rate": win_rate,
            "avg_score": avg_score,
            "avg_remaining_plays": avg_remaining_plays,
            "game_results": results
        }
        
        if verbose:
            print(f"\nStrategy: {self.strategy.name}")
            print(f"Games: {num_games}")
            print(f"Win rate: {win_rate:.2%}")
            print(f"Average score: {avg_score:.2f}")
            print(f"Average remaining plays (when won): {avg_remaining_plays:.2f}")
        
        return stats 