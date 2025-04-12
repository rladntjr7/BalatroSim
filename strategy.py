from player import Player
from card import Card
import random

class Strategy:
    """Base class for all card selection strategies"""
    def __init__(self, name):
        self.name = name
    
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
        # Discard 1-3 random cards
        hand_size = len(player.hand)
        if hand_size == 0:
            return []
        
        num_cards = random.randint(1, min(3, hand_size))
        return random.sample(range(hand_size), num_cards)


class FlushStrategy(Strategy):
    """Prioritizes flush hands"""
    def __init__(self):
        super().__init__("Flush")
    
    def select_play_cards(self, player):
        # Get suits in hand
        suits = {}
        for i, card in enumerate(player.hand):
            if card.suit not in suits:
                suits[card.suit] = []
            suits[card.suit].append(i)
        
        # Find suit with most cards
        best_suit = max(suits.items(), key=lambda x: len(x[1]), default=(None, []))
        
        # If we have 5+ cards of the same suit, play them
        if best_suit[0] and len(best_suit[1]) >= 5:
            # Return up to 5 highest value cards of that suit
            suit_cards = [(i, player.hand[i].chips) for i in best_suit[1]]
            suit_cards.sort(key=lambda x: x[1], reverse=True)
            return [i for i, _ in suit_cards[:5]]
        
        # Otherwise, look for any other good hand pattern
        return self._fallback_strategy(player)
    
    def select_discard_cards(self, player):
        # Find the suit with most cards
        suits = {}
        for i, card in enumerate(player.hand):
            if card.suit not in suits:
                suits[card.suit] = []
            suits[card.suit].append(i)
        
        if not suits:
            return []
            
        best_suit = max(suits.items(), key=lambda x: len(x[1]), default=(None, []))
        
        # Discard cards not of the dominant suit, especially low value ones
        discard_indices = []
        for i, card in enumerate(player.hand):
            if card.suit != best_suit[0]:
                discard_indices.append(i)
                if len(discard_indices) >= 3:  # Limit to 3 discards
                    break
        
        return discard_indices
    
    def _fallback_strategy(self, player):
        # Look for a pair, three of a kind, etc.
        ranks = {}
        for i, card in enumerate(player.hand):
            if card.rank not in ranks:
                ranks[card.rank] = []
            ranks[card.rank].append(i)
        
        # Find best pattern
        if ranks:
            best_rank = max(ranks.items(), key=lambda x: len(x[1]), default=(None, []))
            if best_rank[0] and len(best_rank[1]) >= 2:
                return best_rank[1][:min(len(best_rank[1]), 5)]
        
        # As a last resort, play highest value cards
        cards_with_value = [(i, card.chips) for i, card in enumerate(player.hand)]
        cards_with_value.sort(key=lambda x: x[1], reverse=True)
        return [i for i, _ in cards_with_value[:min(5, len(cards_with_value))]]


class StraightStrategy(Strategy):
    """Prioritizes straight hands"""
    def __init__(self):
        super().__init__("Straight")
    
    def select_play_cards(self, player):
        # Get all cards by rank
        ranks = {}
        for i, card in enumerate(player.hand):
            if card.rank not in ranks:
                ranks[card.rank] = []
            ranks[card.rank].append(i)
        
        # Look for potential straights
        unique_ranks = sorted(list(ranks.keys()))
        
        # Check for 5+ consecutive ranks (standard straight)
        potential_straights = []
        for i in range(len(unique_ranks)):
            consecutive = [unique_ranks[i]]
            for j in range(i+1, len(unique_ranks)):
                if unique_ranks[j] == consecutive[-1] + 1:
                    consecutive.append(unique_ranks[j])
                    if len(consecutive) >= 5:
                        potential_straights.append(consecutive[:5])
                        break
                elif unique_ranks[j] > consecutive[-1] + 1:
                    break
        
        # Check for Ace high straight (A, K, Q, J, 10)
        if 1 in ranks and all(r in ranks for r in [10, 11, 12, 13]):
            potential_straights.append([1, 13, 12, 11, 10])
        
        if potential_straights:
            # Get indices for the best straight
            straight_indices = []
            for rank in potential_straights[0]:
                straight_indices.append(ranks[rank][0])
            return straight_indices[:5]
        
        # Fallback to any partial straight
        return self._fallback_strategy(player)
    
    def select_discard_cards(self, player):
        # Find cards that don't contribute to a straight
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
                if len(discard_indices) >= 3:  # Limit to 3 discards
                    break
        
        return discard_indices
    
    def _fallback_strategy(self, player):
        # Look for cards that have sequential values
        ranks = sorted([card.rank for card in player.hand])
        best_indices = []
        
        # Look for cards with sequential ranks
        for i, card in enumerate(player.hand):
            if any(abs(card.rank - other_card.rank) <= 4 for other_card in player.hand if card != other_card):
                best_indices.append(i)
        
        if best_indices:
            return best_indices[:min(5, len(best_indices))]
        
        # Play highest value cards as fallback
        cards_with_value = [(i, card.chips) for i, card in enumerate(player.hand)]
        cards_with_value.sort(key=lambda x: x[1], reverse=True)
        return [i for i, _ in cards_with_value[:min(5, len(cards_with_value))]]


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
        
        # If we have both components of a full house, play them
        if three_of_a_kind and pair:
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
    
    def _fallback_strategy(self, player):
        # Look for the highest pair or three of a kind
        ranks = {}
        for i, card in enumerate(player.hand):
            if card.rank not in ranks:
                ranks[card.rank] = []
            ranks[card.rank].append(i)
        
        # Find best pattern
        best_indices = []
        for rank, indices in sorted(ranks.items(), key=lambda x: (len(x[1]), x[0]), reverse=True):
            best_indices.extend(indices)
            if len(best_indices) >= 5:
                break
        
        return best_indices[:min(5, len(best_indices))] 