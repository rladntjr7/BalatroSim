from card import Card
from deck import Deck

TARGET_SCORE = 600

class Player:
    def __init__(self, strategy):
        self.strategy = strategy
        self.deck = Deck()
        self.deck.shuffle()
        self.hand = []
        self.handsRemaining = 4
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
            score = 0
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
            
            score = (base_score + highest_pair_chips * 2) * multiplier
            return score

        def scoreTwoPair(hand):
            score = 0
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
            
            score = (base_score + highest_pair * 2 + second_highest_pair * 2) * multiplier
            return score
            
        def scoreTriple(hand):
            score = 0
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
            
            score = (base_score + highest_triple_chips * 3) * multiplier
            return score

        def scoreStraight(hand):
            score = 0
            base_score = 30
            multiplier = 4
            if len(hand) < 5: return 0

            ranks = sorted(list(set([card.rank for card in hand])), reverse=True) # Unique sorted ranks
            if len(ranks) < 5: return 0

            # Check for Ace-high straight (A, K, Q, J, 10)
            ace_high_ranks = {1, 13, 12, 11, 10}
            if ace_high_ranks.issubset(set(ranks)):
                score = base_score * multiplier
                for rank in ace_high_ranks:
                    score += get_chips_for_rank(rank) * multiplier
                return score
            
            # Check for other straights (5 consecutive ranks)
            for i in range(len(ranks) - 4):
                # Check if ranks[i] is the start of a 5-card straight
                is_straight = True
                straight_ranks = []
                for j in range(5):
                    if ranks[i] - j not in ranks:
                        is_straight = False
                        break
                    straight_ranks.append(ranks[i] - j)
                
                if is_straight:
                    score = base_score * multiplier
                    for rank in straight_ranks:
                         score += get_chips_for_rank(rank) * multiplier
                    return score # Return score for the highest straight found

            return score

        def scoreFlush(hand):
            score = 0
            base_score = 35
            multiplier = 4
            if len(hand) < 5: return 0

            suitCount = get_suit_counts(hand)
            for suit, count in suitCount.items():
                if count >= 5:
                    score = base_score * multiplier
                    # Get the top 5 cards of the same suit for scoring
                    flush_cards = [card for card in hand if card.suit == suit]
                    flush_cards.sort(key=lambda x: x.chips, reverse=True)
                    top_cards = flush_cards[:5]
                    for card in top_cards:
                        score += card.chips * multiplier
                    return score # Return score for the first flush found
            return score

        def scoreFullHouse(hand):
            score = 0
            base_score = 40
            multiplier = 4
            if len(hand) < 5: return 0

            cardCount = get_rank_counts(hand)
            triple_rank = None
            pair_rank = None

            # Find the highest triple
            highest_triple_chips = 0
            for rank, count in cardCount.items():
                if count >= 3:
                    chips = get_chips_for_rank(rank)
                    if chips > highest_triple_chips:
                         highest_triple_chips = chips
                         triple_rank = rank
            
            if triple_rank is None: return 0

            # Find the highest pair among the remaining cards
            highest_pair_chips = 0
            for rank, count in cardCount.items():
                if rank != triple_rank and count >= 2:
                     highest_pair_chips = max(highest_pair_chips, get_chips_for_rank(rank))

            if highest_pair_chips == 0: return 0
                            
            return (base_score + highest_triple_chips * 3 + highest_pair_chips * 2) * multiplier
                    
        def scoreFourOfAKind(hand):
            score = 0
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
            score = 0
            base_score = 100
            multiplier = 8
            if len(hand) < 5: return 0
            
            # Potential straight flush requires at least 5 cards of the same suit
            suitCount = get_suit_counts(hand)
            potential_suits = [suit for suit, count in suitCount.items() if count >= 5]
            
            highest_sf_score = 0
            for suit in potential_suits:
                suit_cards = [card for card in hand if card.suit == suit]
                # Check if these cards form a straight
                sf_score = scoreStraight(suit_cards) # Use scoreStraight logic on suit cards
                if sf_score > 0: # Found a straight within the suit
                    # Adjust score based on straight flush rules
                    straight_chips = sum(get_chips_for_rank(card.rank) for card in suit_cards if card.rank in {r[0] for r in sf_ranks}) # Sum chips of the straight cards
                    highest_sf_score = max(highest_sf_score, (base_score + straight_chips) * multiplier) 
            
            return highest_sf_score

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
        best_hand_name = "High Card" # Default if all scores are 0
        best_score = 0
        # Iterate in order of hand ranking (high to low)
        for hand_name in self.playable_hands[::-1]: # Reverse order for check
            current_score = scores.get(hand_name, 0)
            if current_score > 0:
                best_hand_name = hand_name
                best_score = current_score
                break # Found the highest ranking hand
        
        # Handle case where only high card is possible
        if best_score == 0 and scoreHighCard(playing_hand) > 0:
             best_hand_name = "High Card"
             best_score = scoreHighCard(playing_hand)

        return best_hand_name, best_score
    
    def discard(self, indices):
        if self.discardsRemaining <= 0:
            print("No discards remaining.")
            return False # Indicate failure

        # Sort indices in descending order to avoid issues when removing
        indices.sort(reverse=True)
        
        discarded_count = 0
        for index in indices:
            if 0 <= index < len(self.hand):
                # Remove card from hand
                self.hand.pop(index)
                discarded_count += 1
            else:
                print(f"Warning: Invalid index {index} ignored.")

        # Draw new cards only if some were discarded
        if discarded_count > 0:
            for _ in range(discarded_count):
                new_card = self.deck.draw()
                if new_card:
                    self.hand.append(new_card)
            self.discardsRemaining -= 1
            return True # Indicate success
        else:
            print("No valid cards were discarded.")
            return False # Indicate failure
    
    def play(self, indices):
        if self.handsRemaining <= 0:
            print("No hands remaining.")
            return False # Indicate failure
        
        # Validate indices
        valid_indices = [i for i in indices if 0 <= i < len(self.hand)]
        if len(valid_indices) != len(indices):
            print("Error: One or more indices are invalid.")
            return False
        if not valid_indices:
             print("Error: No cards selected to play.")
             return False
             
        # Sort indices descending to remove correctly
        valid_indices.sort(reverse=True)
        
        played_cards = []
        for index in valid_indices:
            played_cards.insert(0, self.hand.pop(index)) # Insert at beginning to keep order

        # Draw replacements
        for _ in range(len(played_cards)):
            new_card = self.deck.draw()
            if new_card:
                self.hand.append(new_card)
            
        self.handsRemaining -= 1
        
        # Score the played hand
        played_hand_name, played_score = self.checkScore(played_cards)
        self.history.append((played_cards, played_hand_name, played_score))
        self.currentScore += played_score
        
        print(f"Played: {played_hand_name} for {played_score} score.")

        if self.currentScore >= TARGET_SCORE:
            self.win = True
            print(f"Target score {TARGET_SCORE} reached! You win!")

        return True # Indicate success 