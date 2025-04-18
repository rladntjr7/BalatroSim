from card import Card
from deck import Deck

TARGET_SCORE = 600

class Player:
    def __init__(self, strategy):
        self.strategy = strategy
        self.deck = Deck()
        self.deck.shuffle()
        self.hand = []
        self.playsRemaining = 4
        self.discardsRemaining = 4
        self.currentScore = 0
        self.win = False
        self.playable_hands = ["High Card", "Pair", "Two Pair", "Triple", "Straight", "Flush", "Full House", "Four of a Kind", "Straight Flush"]
        self.history = [] # Stores tuples of (played_cards, played_hand_name, score)

        for i in range(8):
            card = self.deck.draw()
            if card: # Check if draw was successful
                self.hand.append(card)
    
    def checkScore(self, playing_hand):
        score = 0

        # Helper function to get card counts by rank
        def get_rank_counts(hand):
            cardCount = {}
            for card in hand:
                if card.rank in cardCount:
                    cardCount[card.rank] += 1
                else:
                    cardCount[card.rank] = 1
            return cardCount
        
        # Helper function to get suit counts
        def get_suit_counts(hand):
            suitCount = {}
            for card in hand:
                if card.suit in suitCount:
                    suitCount[card.suit] += 1
                else:
                    suitCount[card.suit] = 1
            return suitCount
        
        # Helper function to get chips for a rank
        def get_chips_for_rank(rank):
            return Card(rank).chips # Create a temporary card to get chip value

        def scoreHighCard(hand):
            score = 0
            base_score = 5
            multiplier = 1
            if not hand: return 0
            high_card = max(hand, key=lambda x: x.chips)
            score = (base_score + high_card.chips) * multiplier
            return score

        def scorePair(hand):
            base_score = 10
            multiplier = 2
            if len(hand) < 2: return 0
            
            cardCount = get_rank_counts(hand)
            highest_pair_chips = 0
            for rank, count in cardCount.items():
                if count >= 2:
                    highest_pair_chips = max(highest_pair_chips, get_chips_for_rank(rank))

            if highest_pair_chips == 0:
                return 0
            
            return (base_score + highest_pair_chips * 2) * multiplier

        def scoreTwoPair(hand):
            base_score = 20
            multiplier = 2
            if len(hand) < 4: return 0

            cardCount = get_rank_counts(hand)
            pairs = []
            for rank, count in cardCount.items():
                if count >= 2:
                    pairs.append(get_chips_for_rank(rank))
            
            if len(pairs) < 2:
                 return 0
            
            pairs.sort(reverse=True)
            highest_pair = pairs[0]
            second_highest_pair = pairs[1]
            
            return (base_score + highest_pair * 2 + second_highest_pair * 2) * multiplier
            
        def scoreTriple(hand):
            base_score = 30
            multiplier = 3
            if len(hand) < 3: return 0

            cardCount = get_rank_counts(hand)
            highest_triple_chips = 0
            for rank, count in cardCount.items():
                if count >= 3:
                     highest_triple_chips = max(highest_triple_chips, get_chips_for_rank(rank))

            if highest_triple_chips == 0:
                return 0
            
            return (base_score + highest_triple_chips * 3) * multiplier

        def scoreStraight(hand):
            base_score = 30
            multiplier = 4
            if len(hand) < 5: return 0

            ranks = sorted(list(set([card.rank for card in hand])), reverse=True) # Unique sorted ranks
            if len(ranks) < 5: return 0

            # Check for Ace-high straight (A, K, Q, J, 10)
            ace_high_ranks = {1, 13, 12, 11, 10}
            if ace_high_ranks == set(ranks):
                score = base_score * multiplier
                for rank in ace_high_ranks:
                    score += get_chips_for_rank(rank) * multiplier
                return score
            
            # Check for other straights (5 consecutive ranks)
            is_straight = True
            straight_ranks = []
            for i in range(5):
                if ranks[0] - i not in ranks:
                    is_straight = False
                    break
                straight_ranks.append(ranks[0] - i)
            
            if is_straight:
                score = base_score * multiplier
                for rank in straight_ranks:
                        score += get_chips_for_rank(rank) * multiplier
                return score # Return score for the highest straight found

            return 0

        def scoreFlush(hand):
            base_score = 35
            multiplier = 4
            if len(hand) < 5: return 0

            suitCount = get_suit_counts(hand)
            for suit, count in suitCount.items():
                if count == 5:
                    score = base_score * multiplier
                    for card in hand:
                        score += card.chips * multiplier
                    return score
            return 0

        def scoreFullHouse(hand):
            base_score = 40
            multiplier = 4
            if len(hand) < 5: return 0

            cardCount = get_rank_counts(hand)

            # Find the highest triple
            highest_triple_chips = 0
            for rank, count in cardCount.items():
                if count >= 3:
                    highest_triple_chips = max(highest_triple_chips, get_chips_for_rank(rank))
            
            if highest_triple_chips == 0: return 0

            # Find the highest pair among the remaining cards
            highest_pair_chips = 0
            for rank, count in cardCount.items():
                if count >= 2:
                     highest_pair_chips = max(highest_pair_chips, get_chips_for_rank(rank))

            if highest_pair_chips == 0: return 0
                            
            return (base_score + highest_triple_chips * 3 + highest_pair_chips * 2) * multiplier
                    
        def scoreFourOfAKind(hand):
            base_score = 60
            multiplier = 7
            if len(hand) < 4: return 0

            cardCount = get_rank_counts(hand)
            four_chips = 0
            for rank, count in cardCount.items():
                if count >= 4:
                     four_chips = max(four_chips, get_chips_for_rank(rank))
            
            if four_chips == 0:
                return 0
            
            return (base_score + four_chips * 4) * multiplier

        def scoreStraightFlush(hand):
            base_score = 100
            multiplier = 8
            if len(hand) < 5: return 0
            
            suitCount = get_suit_counts(hand)
            if 5 not in suitCount.values(): return 0
            
            sf_score = scoreStraight(hand)
            if sf_score > 0:
                score = base_score * multiplier
                for card in hand:
                    score += card.chips * multiplier
                return score
            return 0

        # Determine the best hand score from the played cards
        scores = {
            "Straight Flush": scoreStraightFlush(playing_hand),
            "Four of a Kind": scoreFourOfAKind(playing_hand),
            "Full House": scoreFullHouse(playing_hand),
            "Flush": scoreFlush(playing_hand),
            "Straight": scoreStraight(playing_hand),
            "Triple": scoreTriple(playing_hand),
            "Two Pair": scoreTwoPair(playing_hand),
            "Pair": scorePair(playing_hand),
            "High Card": scoreHighCard(playing_hand) 
        }

        # Find the highest score and corresponding hand name
        best_hand_name = "High Card" # Default if all other scores are 0
        best_score = scoreHighCard(playing_hand) # Default if all other scores are 0
        # Iterate in order of hand ranking (high to low)
        for hand, score in scores.items(): # Reverse order for check
            if score > best_score:
                best_hand_name = hand
                best_score = score

        return best_hand_name, best_score
    
    def discard(self, indices):
        if self.discardsRemaining <= 0:
            print("No discards remaining.")
            return False # Indicate failure

        # Sort indices in descending order to avoid issues when removing
        indices.sort(reverse=True)
        
        for index in indices:
            if 0 <= index < len(self.hand):
                # Remove card from hand
                self.hand[index] = self.deck.draw()
            else:
                print(f"Warning: Invalid index {index} ignored.")
        
        self.discardsRemaining -= 1
        return True # Indicate success
    
    def play(self, indices, verbose=False):
        """Play cards from the hand to form a hand. Returns True if successful."""
        if not indices:
            return False
        
        # Check if we have any plays left
        if self.playsRemaining <= 0:
            if verbose:
                print("No plays remaining.")
            return False
        
        # Get the cards to play
        playing_cards = [self.hand[i] for i in indices]
        
        # Check the score for the played cards
        hand_name, hand_score = self.checkScore(playing_cards)
        
        # Add to current score
        self.currentScore += hand_score
        
        # Check for win
        if self.currentScore >= TARGET_SCORE:
            self.win = True
            if verbose:
                print(f"You win! Final score: {self.currentScore}")
        
        # Remove played cards from hand
        indices = sorted(indices, reverse=True)
        for i in indices:
            self.hand.pop(i)
        
        # Draw new cards
        for _ in range(len(indices)):
            card = self.deck.draw()
            if card:
                self.hand.append(card)
        
        # Decrement plays remaining
        self.playsRemaining -= 1
        
        # Add to history
        self.history.append((playing_cards, hand_name, hand_score))
        
        if verbose:
            print(f"Played {hand_name} for {hand_score} points.")
            print(f"Total score: {self.currentScore}")
        
        return True

    def _get_hand_info(self, cards):
        hand_name, hand_score = self.checkScore(cards)
        return hand_name, hand_score 