from player import Player
from card import Card
import random
from deck import Deck
import math
from collections import Counter
import itertools

# Helper functions to check the deck and hand for suits and ranks for better strategy
def checkdeckforsuits(deck: Deck) -> dict:
    suits = {
        "hearts": 0,
        "diamonds": 0,
        "clubs": 0,
        "spades": 0
    }
    for card in deck.cards:
        suits[card.suit] += 1
    return suits

def checkdeckforranks(deck: Deck) -> dict:
    ranks = {
        "1": 0,
        "2": 0,
        "3": 0,
        "4": 0,
        "5": 0,
        "6": 0,
        "7": 0,
        "8": 0,
        "9": 0,
        "10": 0,
        "11": 0,
        "12": 0,
        "13": 0
    }
    for card in deck.cards:
        ranks[str(card.rank)] += 1
    return ranks

def checkhandforsuits(hand: list[Card]) -> dict:
    suits = {
        "hearts": 0,
        "diamonds": 0,
        "clubs": 0,
        "spades": 0
    }
    for card in hand:
        suits[card.suit] += 1
    return suits

def checkhandforranks(hand: list[Card]) -> dict:
    ranks = {
        "1": 0,
        "2": 0,
        "3": 0,
        "4": 0,
        "5": 0,
        "6": 0,
        "7": 0,
        "8": 0,
        "9": 0,
        "10": 0,
        "11": 0,
        "12": 0,
        "13": 0
    }
    for card in hand:
        ranks[str(card.rank)] += 1
    return ranks

# Base class for all card selection strategies
class Strategy:
    def __init__(self, name, verbose=False):
        self.name = name
        self.history = []
        self.verbose = verbose
    
    def select_play_cards(self, player):
        """
        Decides which cards to play based on the strategy
        Returns indices of cards to play
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    def select_discard_cards(self, player):
        """
        Decides which cards to discard based on the strategy
        Returns indices of cards to discard
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    def _fallback_strategy(self, player):
        """
        Fallback strategy for when no other strategy is applicable
        Returns indices of cards to play
        """
        best_indices = []
        best_score = 0
        for i in range(len(player.hand)):
            for j in range(i+1, len(player.hand)):
                for k in range(j+1, len(player.hand)):
                    for l in range(k+1, len(player.hand)):
                        for m in range(l+1, len(player.hand)):
                            _, score = player.checkScore([player.hand[i], player.hand[j], player.hand[k], player.hand[l], player.hand[m]])
                            if score > best_score:
                                best_score = score
                                best_indices = [i, j, k, l, m]
        return best_indices

class RandomStrategy(Strategy):
    """Randomly selects cards to play or discard"""
    def __init__(self):
        super().__init__("Random")
    
    def select_play_cards(self, player):
        # Play 1-5 random cards
        hand_size = len(player.hand)
        if hand_size == 0:
            return []
        
        num_cards = random.randint(1, min(5, hand_size))
        return random.sample(range(hand_size), num_cards)
    
    def select_discard_cards(self, player):
        # Discard 1-5 random cards
        hand_size = len(player.hand)
        if hand_size == 0:
            return []
        
        num_cards = random.randint(1, min(5, hand_size))
        return random.sample(range(hand_size), num_cards)


class FlushStrategy(Strategy):
    """Prioritizes flush hands"""
    def __init__(self):
        super().__init__("Flush")
    
    def select_play_cards(self, player):
        # Get suits in hand
        suits = checkhandforsuits(player.hand)
        # Find suit with most cards
        best_suit = max(suits.items(), key=lambda x: x[1], default=(None, 0)) # (suit, count)
        
        # Check if we already have a flush (5+ cards of same suit)
        has_flush = best_suit[0] and best_suit[1] >= 5
        
        # If no discards remain and we don't have a flush yet, use play as discard
        if player.discardsRemaining == 0 and player.playsRemaining > 1 and not has_flush:
            return self.select_discard_cards(player)
        
        # If we have 5+ cards of the same suit, play them
        if has_flush:
            # Return up to 5 highest value cards of that suit
            suit_cards = [(i, player.hand[i].chips) for i, _ in enumerate(player.hand) if player.hand[i].suit == best_suit[0]]
            suit_cards.sort(key=lambda x: x[1], reverse=True)
            return [i for i, _ in suit_cards[:5]] # Return the indices of the cards to play
        
        # Otherwise, look for any other good hand pattern
        return self._fallback_strategy(player)
    
    def select_discard_cards(self, player):
        # Find the suit with most cards
        suits = checkhandforsuits(player.hand)
        
        if not suits:
            return []
        
        ordered_suits = sorted(suits.items(), key=lambda x: x[1], reverse=True) # [(suit, count), (suit, count), ...]
        counts = [count for _, count in ordered_suits]
        # Check for ties
        if counts.count(counts[0]) > 1:
            suits_to_consider = [suit for suit, count in ordered_suits if count == counts[0]]
            # Check the deck for the suit with the least cards
            deck_suits = checkdeckforsuits(player.deck)
            deckcounts = [(suit, deck_suits[suit]) for suit in suits_to_consider]
            deckcounts.sort(key=lambda x: x[1], reverse=True) # sorts by most cards in deck
            suit_to_keep = deckcounts[0][0] # keep the suit with the most cards in the deck
        else:
            suit_maybe_keep = ordered_suits[0][0] 
            deck_suits = checkdeckforsuits(player.deck)
            if deck_suits[suit_maybe_keep] + suits[suit_maybe_keep] >= 5:
                suit_to_keep = suit_maybe_keep
            else:
                suit_to_keep =  ordered_suits[1][0]
        cards_to_discard = [(i, card) for i, card in enumerate(player.hand) if card.suit != suit_to_keep]
        cards_to_discard.sort(key=lambda x: x[1].chips, reverse=False) # discards lowest value cards
        if len(cards_to_discard) > 5:
            return [i for i, _ in cards_to_discard[:5]]
        else:
            return [i for i, _ in cards_to_discard]

class StraightStrategy(Strategy):
    """Prioritizes straight hands"""
    def __init__(self):
        super().__init__("Straight")
    
    def select_play_cards(self, player):
        # Get all ranks in hand
        ranks = sorted(list(set([card.rank for card in player.hand])), reverse=True)

        # If there are less than 5 ranks, we need to discard or fallback
        if len(ranks) < 5:
            if player.discardsRemaining == 0 and player.playsRemaining > 1:
                return self.select_discard_cards(player)
            else:
                return self._fallback_strategy(player)
        
        def get_indices_for_rank(ranks):
            indices = []
            hands = [card.rank for card in player.hand]
            for rank in ranks:
                indices.append(hands.index(rank))
            return indices
        
        # Check for ace high straight
        ace_high_ranks = {1, 13, 12, 11, 10}
        if ace_high_ranks.issubset(set(ranks)):
            return get_indices_for_rank(ace_high_ranks)
        
        # Check for 5+ consecutive ranks (standard straight)
        for i in range(len(ranks) - 4):
            is_straight = True
            for j in range(i+1, i+5):
                if ranks[j] != ranks[j-1] + 1:
                    is_straight = False
                    break
            if is_straight:
                return get_indices_for_rank(ranks[i:i+5])
        
        if player.discardsRemaining == 0 and player.playsRemaining > 1:
            return self.select_discard_cards(player)
        else:
            return self._fallback_strategy(player)
    
    def select_discard_cards(self, player):
        # Define straight windows using rank numbers (1=Ace, 2-10, 11=Jack, 12=Queen, 13=King)
        STRAIGHT_WINDOWS = [
            [1, 2, 3, 4, 5],    # A-5 straight
            [2, 3, 4, 5, 6],
            [3, 4, 5, 6, 7],
            [4, 5, 6, 7, 8],
            [5, 6, 7, 8, 9],
            [6, 7, 8, 9, 10],
            [7, 8, 9, 10, 11],   # 7-J straight
            [8, 9, 10, 11, 12],  # 8-Q straight
            [9, 10, 11, 12, 13], # 9-K straight
            [10, 11, 12, 13, 1], # 10-A straight
        ]
        
        # Convert hand to list of tuples (rank, index)
        hand_with_indices = [(card.rank, i) for i, card in enumerate(player.hand)]
        
        # Get list of ranks in the hand
        hand_ranks = [card.rank for card in player.hand]
        
        # Get list of ranks in the deck
        deck_ranks = [card.rank for card in player.deck.cards]
        
        # Find the best cards to hold for a straight
        best_probability = 0.0
        best_discard = []
        
        # Count ranks in hand and deck
        hand_rank_counts = Counter(hand_ranks)
        deck_rank_counts = Counter(deck_ranks)
        
        # Number of cards in hand and deck
        H = len(player.hand)
        N = len(player.deck.cards)
        
        # Iterate over possible discard counts
        for d in range(1, min(max_discard, H) + 1):
            # For each way to hold H-d cards
            for hold_indices in itertools.combinations(range(H), H-d):
                hold = [player.hand[i] for i in hold_indices]
                hold_ranks = [card.rank for card in hold]
                
                # Determine probability for best straight window
                best_for_hold = 0.0
                for window in STRAIGHT_WINDOWS:
                    # Count ranks held in this window
                    held_ranks = {rank for rank in hold_ranks if rank in window}
                    m = len(window) - len(held_ranks)  # missing ranks
                    
                    if m > d:
                        continue  # cannot complete this straight
                    
                    # Count good cards in deck
                    G = sum(
                        min(deck_rank_counts[r], 1)  # We only need one of each rank
                        for r in window
                        if r not in held_ranks
                    )
                    
                    # If not enough good cards or deck too small
                    if G < m or N < d:
                        continue
                    
                    # Hypergeometric probability calculation
                    # P = C(G, m) * C(N-G, d-m) / C(N, d)
                    try:
                        numer = math.comb(G, m) * math.comb(N - G, d - m)
                        denom = math.comb(N, d)
                        P = numer / denom
                    except (ValueError, ZeroDivisionError):
                        P = 0
                    
                    if P > best_for_hold:
                        best_for_hold = P
                
                # Update global best
                if best_for_hold > best_probability:
                    best_probability = best_for_hold
                    discard_indices = [i for i in range(H) if i not in hold_indices]
                    best_discard = discard_indices
        
        # If no good discard strategy found, use the original heuristic approach
        if not best_discard:
            ranks = [card.rank for card in player.hand]
            discard_indices = []
            
            for i, card in enumerate(player.hand):
                # Check if this card contributes to any potential straight
                contributes_to_straight = False
                for r in range(card.rank - 4, card.rank + 5):
                    if r <= 0 or r > 13:
                        continue
                    if ranks.count(r) > 0 and ranks.count(r+1) > 0 and ranks.count(r+2) > 0:
                        contributes_to_straight = True
                        break
                
                if not contributes_to_straight:
                    discard_indices.append(i)
                    if len(discard_indices) >= max_discard:  # Limit to max_discard
                        break
            
            best_discard = discard_indices
        
        return best_discard


class FullHouseStrategy(Strategy):
    """Prioritizes full house hands"""
    def __init__(self):
        super().__init__("Full House")
    
    def select_play_cards(self, player):
        ranks = {}
        for i, card in enumerate(player.hand):
            if card.rank not in ranks:
                ranks[card.rank] = []
            ranks[card.rank].append(i)
        
        # Find ranks with 3+ and 2+ cards
        three_of_a_kind = None
        pair = None
        
        # First look for three of a kind
        for rank, indices in ranks.items():
            if len(indices) >= 3 and (three_of_a_kind is None or rank > three_of_a_kind[0]):
                three_of_a_kind = (rank, indices)
        
        # Then look for a pair different from the three of a kind
        if three_of_a_kind:
            for rank, indices in ranks.items():
                if rank != three_of_a_kind[0] and len(indices) >= 2 and (pair is None or rank > pair[0]):
                    pair = (rank, indices)
        
        # Check if we have a full house
        has_fullhouse = three_of_a_kind and pair
        
        # If no discards remain and we don't have a full house, use play as discard
        if player.discardsRemaining == 0 and player.playsRemaining > 1 and not has_fullhouse:
            return self.select_discard_cards(player)
        
        # If we have both components of a full house, play them
        if has_fullhouse:
            return three_of_a_kind[1][:3] + pair[1][:2]
        
        # If we have only three of a kind, play that
        if three_of_a_kind:
            return three_of_a_kind[1][:3]
        
        # If we have only a pair, play that
        if pair:
            return pair[1][:2]
        
        # Fallback strategy
        return self._fallback_strategy(player)
    
    def select_discard_cards(self, player):
        ranks = {}
        for i, card in enumerate(player.hand):
            if card.rank not in ranks:
                ranks[card.rank] = []
            ranks[card.rank].append(i)
        
        # Keep ranks that have multiple cards
        discard_indices = []
        for i, card in enumerate(player.hand):
            if len(ranks[card.rank]) == 1:  # No other cards with this rank
                discard_indices.append(i)
                if len(discard_indices) >= 3:  # Limit to 3 discards
                    break
        
        return discard_indices

class HybridStrategy(Strategy):
    """Combination approach that evaluates the probability of each strategy and picks the best one"""
    def __init__(self):
        super().__init__("Hybrid")
        # Create instances of all the strategies we can use
        self.flush_strategy = FlushStrategy()
        self.straight_strategy = StraightStrategy()
        self.fullhouse_strategy = FullHouseStrategy()
        self.straightflush_strategy = StraightFlushStrategy()
    
    def select_play_cards(self, player):
        # Calculate potential for each hand type
        flush_potential = self._evaluate_flush_potential(player)
        straight_potential = self._evaluate_straight_potential(player)
        fullhouse_potential = self._evaluate_fullhouse_potential(player)
        straightflush_potential = self._evaluate_straightflush_potential(player)
        
        # Determine the best strategy based on the highest potential
        potentials = {
            'Straight Flush': straightflush_potential,
            'Full House': fullhouse_potential,
            'Flush': flush_potential,
            'Straight': straight_potential
        }
        
        best_strategy = max(potentials.items(), key=lambda x: x[1])
        best_potential = best_strategy[1]
        
        # If no discards remain, hands remaining, and no good potential for any hand, use play as discard
        if player.discardsRemaining == 0 and player.playsRemaining > 1 and best_potential < 0.3:
            return self.select_discard_cards(player)
        
        # Use the appropriate strategy based on the highest potential
        if best_strategy[0] == 'Straight Flush' and best_strategy[1] > 0.3:
            return self.straightflush_strategy.select_play_cards(player)
        elif best_strategy[0] == 'Full House' and best_strategy[1] > 0.3:
            return self.fullhouse_strategy.select_play_cards(player)
        elif best_strategy[0] == 'Flush' and best_strategy[1] > 0.3:
            return self.flush_strategy.select_play_cards(player)
        elif best_strategy[0] == 'Straight' and best_strategy[1] > 0.3:
            return self.straight_strategy.select_play_cards(player)
        
        # If no strategy has good potential, play the highest value cards
        cards_with_value = [(i, card.chips) for i, card in enumerate(player.hand)]
        cards_with_value.sort(key=lambda x: x[1], reverse=True)
        return [i for i, _ in cards_with_value[:min(5, len(cards_with_value))]]
    
    def select_discard_cards(self, player):
        # Calculate potential for each hand type
        flush_potential = self._evaluate_flush_potential(player)
        straight_potential = self._evaluate_straight_potential(player)
        fullhouse_potential = self._evaluate_fullhouse_potential(player)
        straightflush_potential = self._evaluate_straightflush_potential(player)
        
        # Determine the best strategy based on the highest potential
        potentials = {
            'Straight Flush': straightflush_potential,
            'Full House': fullhouse_potential,
            'Flush': flush_potential,
            'Straight': straight_potential
        }
        
        best_strategy = max(potentials.items(), key=lambda x: x[1])
        
        # Use the appropriate strategy for discarding
        if best_strategy[0] == 'Straight Flush' and best_strategy[1] > 0.2:
            return self.straightflush_strategy.select_discard_cards(player)
        elif best_strategy[0] == 'Full House' and best_strategy[1] > 0.2:
            return self.fullhouse_strategy.select_discard_cards(player)
        elif best_strategy[0] == 'Flush' and best_strategy[1] > 0.2:
            return self.flush_strategy.select_discard_cards(player)
        elif best_strategy[0] == 'Straight' and best_strategy[1] > 0.2:
            return self.straight_strategy.select_discard_cards(player)
        
        # If no strategy has good potential, discard the lowest value cards
        cards_with_value = [(i, card.chips) for i, card in enumerate(player.hand)]
        cards_with_value.sort(key=lambda x: x[1])  # Sort by ascending value
        return [i for i, _ in cards_with_value[:min(3, len(cards_with_value))]]
    
    def _evaluate_flush_potential(self, player):
        """Evaluates the potential of making a flush hand"""
        # Count cards by suit in hand
        suit_counts = {}
        for card in player.hand:
            if card.suit not in suit_counts:
                suit_counts[card.suit] = 0
            suit_counts[card.suit] += 1
        
        if not suit_counts:
            return 0.0
        
        # Find the suit with the most cards
        best_suit, best_count = max(suit_counts.items(), key=lambda x: x[1])
        
        # Check how many more cards we need for a flush
        cards_needed = max(0, 5 - best_count)
        
        # Count how many cards of that suit remain in the deck
        remaining_cards = 13 - best_count  # 13 cards per suit in a standard deck
        
        # Estimate probability based on cards remaining and cards needed
        if cards_needed == 0:
            return 1.0  # We already have a flush
        elif remaining_cards < cards_needed:
            return 0.0  # Impossible to get a flush
        else:
            # Simple probability estimate
            return min(1.0, remaining_cards / (cards_needed * 2))
    
    def _evaluate_straight_potential(self, player):
        """Evaluates the potential of making a straight hand"""
        # Get all ranks in hand
        ranks = sorted([card.rank for card in player.hand])
        
        if not ranks:
            return 0.0
        
        # Count consecutive sequences
        max_consecutive = 1
        current_consecutive = 1
        
        for i in range(1, len(ranks)):
            if ranks[i] == ranks[i-1] + 1:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            elif ranks[i] == ranks[i-1]:
                # Same rank, continue
                continue
            else:
                current_consecutive = 1
        
        # Check for potential gaps that can be filled
        unique_ranks = sorted(list(set(ranks)))
        gaps = 0
        
        # Count small gaps (1 card) in the sequence
        for i in range(len(unique_ranks) - 1):
            if unique_ranks[i+1] - unique_ranks[i] == 2:  # Gap of 1 card
                gaps += 1
        
        # Calculate how many cards we need for a straight
        cards_needed = max(0, 5 - max_consecutive - gaps)
        
        # Estimate probability
        if cards_needed == 0:
            return 1.0  # We already have a straight
        elif cards_needed > 2:  # Need too many cards, low probability
            return 0.1
        else:
            # Simple probability estimate
            return min(1.0, (13 - len(unique_ranks)) / (cards_needed * 4))
    
    def _evaluate_fullhouse_potential(self, player):
        """Evaluates the potential of making a full house"""
        # Count cards by rank
        rank_counts = {}
        for card in player.hand:
            if card.rank not in rank_counts:
                rank_counts[card.rank] = 0
            rank_counts[card.rank] += 1
        
        if not rank_counts:
            return 0.0
        
        # Check if we already have three of a kind
        has_three = any(count >= 3 for count in rank_counts.values())
        # Check if we have at least one pair
        pairs = sum(1 for count in rank_counts.values() if count >= 2)
        
        if has_three and pairs >= 2:
            return 1.0  # We already have a full house
        elif has_three and pairs == 1:
            # We have three of a kind and need one more pair
            return 0.7
        elif has_three:
            # We have three of a kind but no pairs yet
            return 0.5
        elif pairs >= 2:
            # We have two pairs, need to upgrade one to three of a kind
            return 0.4
        elif pairs == 1:
            # We have one pair, harder to make a full house
            return 0.2
        else:
            # No pairs or three of a kind yet
            return 0.1
    
    def _evaluate_straightflush_potential(self, player):
        """Evaluates the potential of making a straight flush"""
        # Group cards by suit
        suits = {}
        for card in player.hand:
            if card.suit not in suits:
                suits[card.suit] = []
            suits[card.suit].append(card)
        
        if not suits:
            return 0.0
        
        # For each suit with enough cards, evaluate straight potential
        best_potential = 0.0
        
        for suit, cards in suits.items():
            if len(cards) < 3:  # Need at least 3 cards of the same suit to be worth considering
                continue
                
            # Calculate straight potential within this suit
            ranks = sorted([card.rank for card in cards])
            
            # Count consecutive sequences
            max_consecutive = 1
            current_consecutive = 1
            
            for i in range(1, len(ranks)):
                if ranks[i] == ranks[i-1] + 1:
                    current_consecutive += 1
                    max_consecutive = max(max_consecutive, current_consecutive)
                elif ranks[i] == ranks[i-1]:
                    continue
                else:
                    current_consecutive = 1
            
            # Check for potential gaps that can be filled
            unique_ranks = sorted(list(set(ranks)))
            gaps = 0
            
            # Count small gaps (1 card) in the sequence
            for i in range(len(unique_ranks) - 1):
                if unique_ranks[i+1] - unique_ranks[i] == 2:  # Gap of 1 card
                    gaps += 1
            
            # Calculate potential for this suit
            cards_needed = max(0, 5 - max_consecutive - gaps)
            
            if cards_needed == 0:
                suit_potential = 1.0  # We already have a straight flush
            elif cards_needed > 2:  # Need too many cards, low probability
                suit_potential = 0.05
            else:
                # More conservative probability for straight flush
                suit_potential = min(0.7, (13 - len(unique_ranks)) / (cards_needed * 8))
            
            best_potential = max(best_potential, suit_potential)
        
        return best_potential


class StraightFlushStrategy(Strategy):
    """Prioritizes straight flush hands"""
    def __init__(self):
        super().__init__("Straight Flush")
    
    def select_play_cards(self, player):
        # First, group cards by suit
        suits = {}
        for i, card in enumerate(player.hand):
            if card.suit not in suits:
                suits[card.suit] = []
            suits[card.suit].append((i, card))
        
        # Look for potential straight flushes
        has_straightflush = False
        straightflush_indices = []
        
        # Look for potential straight flushes by examining each suit group
        for suit, cards in suits.items():
            if len(cards) >= 5:  # Need at least 5 cards of the same suit
                # Sort cards by rank
                cards.sort(key=lambda x: x[1].rank)
                
                # Try to find 5 consecutive cards
                for i in range(len(cards) - 4):
                    consecutive = [cards[i]]
                    for j in range(i+1, len(cards)):
                        if cards[j][1].rank == consecutive[-1][1].rank + 1:
                            consecutive.append(cards[j])
                            if len(consecutive) >= 5:
                                # Found a straight flush!
                                has_straightflush = True
                                straightflush_indices = [card[0] for card in consecutive[:5]]
                                break
                        elif cards[j][1].rank > consecutive[-1][1].rank + 1:
                            break
                    
                    if has_straightflush:
                        break
                
                # Check for Ace-low straight flush (A, 2, 3, 4, 5)
                if not has_straightflush:
                    has_ace = any(card[1].rank == 1 for card in cards)
                    has_2_to_5 = all(any(card[1].rank == r for card in cards) for r in range(2, 6))
                    
                    if has_ace and has_2_to_5:
                        has_straightflush = True
                        ace_idx = next(card[0] for card in cards if card[1].rank == 1)
                        low_cards = [card[0] for card in cards if 2 <= card[1].rank <= 5]
                        straightflush_indices = [ace_idx] + low_cards
            
            if has_straightflush:
                break
        
        # If no discards remain and we don't have a straight flush, use play as discard
        if player.discardsRemaining == 0 and player.playsRemaining > 1 and not has_straightflush:
            return self.select_discard_cards(player)
        
        # If found a straight flush, play it
        if has_straightflush:
            return straightflush_indices
        
        # If no straight flush found, try for a flush or straight
        return self._fallback_strategy(player)
    
    def select_discard_cards(self, player):
        # Count cards by suit
        suit_counts = {}
        for card in player.hand:
            if card.suit not in suit_counts:
                suit_counts[card.suit] = 0
            suit_counts[card.suit] += 1
        
        # Find the suit with the most cards
        if not suit_counts:
            return []
            
        best_suit = max(suit_counts.items(), key=lambda x: x[1])[0]
        
        # Identify cards to discard (not in the dominant suit)
        discard_indices = []
        for i, card in enumerate(player.hand):
            if card.suit != best_suit:
                discard_indices.append(i)
                if len(discard_indices) >= 3:  # Limit to 3 discards
                    break
        
        return discard_indices