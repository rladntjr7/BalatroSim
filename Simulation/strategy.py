from player import Player
from card import Card
from deck import Deck
import itertools

# Helper functions to check the deck and hand for suits and ranks for better strategy
def checkdeckforsuits(deck: Deck) -> dict:
    suits = {}
    for card in deck.cards:
        suits[card.suit] = suits.get(card.suit, 0) + 1
    return suits

def checkdeckforranks(deck: Deck) -> dict:
    ranks = {}
    for card in deck.cards:
        ranks[card.rank] = ranks.get(card.rank, 0) + 1
    return ranks

def checkhandforsuits(hand: list[Card]) -> dict:
    suits = {}
    for card in hand:
        suits[card.suit] = suits.get(card.suit, 0) + 1
    return suits

def checkhandforranks(hand: list[Card]) -> dict:
    ranks = {}
    for card in hand:
        ranks[card.rank] = ranks.get(card.rank, 0) + 1
    return ranks

# Base class for all card selection strategies
class Strategy:
    def __init__(self, name, target_hand=None, verbose=False):
        self.name = name
        self.history = []
        self.verbose = verbose
        self.target_hand = target_hand
    
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

class FlushStrategy(Strategy):
    """Prioritizes flush hands"""
    def __init__(self):
        super().__init__("Flush", ["Flush", "Straight Flush"])
    
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
            deckcounts = [(suit, deck_suits.get(suit, 0)) for suit in suits_to_consider]
            deckcounts.sort(key=lambda x: x[1], reverse=True) # sorts by most cards in deck
            suit_to_keep = deckcounts[0][0] # keep the suit with the most cards in the deck
        else:
            suit_maybe_keep = ordered_suits[0][0] 
            deck_suits = checkdeckforsuits(player.deck)
            if deck_suits.get(suit_maybe_keep, 0) + suits.get(suit_maybe_keep, 0) >= 5:
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
        super().__init__("Straight", ["Straight", "Straight Flush"])
    
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
                if ranks[j] != ranks[j-1] - 1:
                    is_straight = False
                    break
            if is_straight:
                return get_indices_for_rank(ranks[i:i+5])
        
        if player.discardsRemaining == 0 and player.playsRemaining > 1:
            return self.select_discard_cards(player)
        elif player.playsRemaining == 1:
            return self._fallback_strategy(player)
    
    def select_discard_cards(self, player):
        # If hand is empty, return empty list
        if not player.hand:
            return []
            
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
        
        deck_ranks = checkdeckforranks(player.deck) # {1: a, 2: b, 3: c, ...} rank: count

        def straight_probability(hold_hands, deck_ranks, d, verbose=False):
            # hold_hands will be list of cards less than size of 5
            if verbose:
                print("calculating probability of straight\nhand:", ", ".join([str(card) for card in hold_hands]), "\ndiscard:", d)
            # calculate probability of straight
            deck_size = sum(deck_ranks.values())

            # Get the ranks actually in hand
            hand_ranks = set(checkhandforranks(hold_hands).keys())
            
            # We'll calculate the probability for each possible straight window
            total_probability = 0.0
            
            for window in STRAIGHT_WINDOWS:
                # Check how many cards are needed and calculate probability of straight        
                cards_needed = set(window) - hand_ranks
                
                # Check if all needed cards exist in the deck
                in_deck = True
                for card in cards_needed:
                    if deck_ranks.get(card, 0) == 0:
                        in_deck = False
                        break
                    
                if not in_deck or len(cards_needed) > d:
                    continue  # Impossible to make this straight
                
                # Calculate the multivariate hypergeometric probability
                # P(success) = [∏ C(Ki, ki)] / C(N, n)
                # Where:
                # - Ki is the number of each needed card in the deck
                # - ki is how many of each card we need (1 per rank for straights)
                # - N is the deck size
                # - n is the number of cards drawn (d)
                
                # Numerator: product of ways to choose each needed card
                numerator = 1.0
                for card in cards_needed:
                    numerator *= deck_ranks.get(card, 0)
                
                # Denominator: ways to choose d cards from deck_size
                denominator = 1.0
                for i in range(0, d):
                    denominator *= (deck_size - i)
                    
                # Adjust for cards we don't need but will draw
                remaining_draws = d - len(cards_needed)
                if remaining_draws > 0:
                    remaining_cards = deck_size - sum(deck_ranks.get(card, 0) for card in cards_needed)
                    
                    # Calculate combinations for remaining cards
                    for i in range(1, remaining_draws + 1):
                        numerator *= (remaining_cards - (i - 1))
                
                # Calculate probability for this window
                if denominator > 0:
                    window_probability = numerator / denominator
                    total_probability += window_probability
                    
            # Cap at 1.0 since we may double-count some successful outcomes
            total_probability = min(1.0, total_probability)
            if verbose:
                print("total probability of straight:", total_probability)
            return total_probability

        
        
        # Find the best cards to hold for a straight
        best_probability = 0.0
        best_hold = None
        
        # Number of cards in hand
        H = len(player.hand)
        
        # Iterate over combination of cards to hold
        for d in range(4, 5 + 1):  # discard 4-5 cards, hold hands must not be bigger than 5, since then the hand will already be a straight
            for hold_indices in itertools.combinations(range(H), H-d): # iterating over all possible combinations
                hold_hands = [player.hand[i] for i in hold_indices] # [card1, card2, card3, ...]
                hand_prob = straight_probability(hold_hands, deck_ranks, d, verbose=self.verbose)
                if hand_prob > best_probability:
                    best_probability = hand_prob
                    best_hold = hold_indices
        
        # If no good hold was found, use a fallback strategy
        if best_hold is None:
            return self._fallback_strategy(player)
        # Otherwise, return the indices to discard based on best hold
        if self.verbose:
            print("best hold:", (", ".join([str(player.hand[i]) for i in best_hold])))
        cards_to_discard = [i for i in range(H) if i not in best_hold]
        return cards_to_discard

class FullHouse4CardsStrategy(Strategy):
    """Prioritizes full house hands"""
    def __init__(self):
        super().__init__("Full House 4 Cards", ["Full House", "Four of a Kind"])
    
    def select_play_cards(self, player):
        ranks = checkhandforranks(player.hand)
        # Find ranks with 3+ and 2+ cards
        four_of_a_kind = None
        three_of_a_kind = None
        pair = None
        
        # If we have 4 of a kind, play them
        for rank, count in ranks.items():
            if count >= 4 and (four_of_a_kind is None or rank > four_of_a_kind):
                return [i for i, card in enumerate(player.hand) if card.rank == rank][:4]
        
        # First look for three of a kind
        for rank, count in ranks.items():
            if count >= 3 and (three_of_a_kind is None or rank > three_of_a_kind):
                three_of_a_kind = rank
        # Then look for a pair different from the three of a kind
        if three_of_a_kind:
            for rank, count in ranks.items():
                if rank != three_of_a_kind and count >= 2 and (pair is None or rank > pair):
                    pair = rank
        
        # Check if we have a full house
        has_fullhouse = three_of_a_kind and pair
        
        # If no discards remain and we don't have a full house, use play as discard
        if player.discardsRemaining == 0 and player.playsRemaining > 1 and not has_fullhouse:
            return self.select_discard_cards(player)
        
        # If we have both components of a full house, play them
        if has_fullhouse:
            return [i for i, card in enumerate(player.hand) if card.rank == three_of_a_kind][:3] + [i for i, card in enumerate(player.hand) if card.rank == pair][:2]
        
        # If we have only three of a kind, play that
        if three_of_a_kind:
            return [i for i, card in enumerate(player.hand) if card.rank == three_of_a_kind][:3]
        
        # If we have only a pair, play that
        if pair:
            return [i for i, card in enumerate(player.hand) if card.rank == pair][:2]
        
        # Fallback strategy
        return self._fallback_strategy(player)
    
    def select_discard_cards(self, player):
        ranks = checkhandforranks(player.hand)
        deck_ranks = checkdeckforranks(player.deck)
        
        # Find three of a kind and pairs
        three_of_a_kind = None
        pairs = []
        
        # First look for three of a kind
        for rank, count in ranks.items():
            if count >= 3:
                three_of_a_kind = rank
                break
        
        # Then look for pairs
        for rank, count in ranks.items():
            if count >= 2 and rank != three_of_a_kind:
                pairs.append(rank)
        
        # Case 1: We have a three of a kind
        if three_of_a_kind:
            # Find the card with the highest count in the deck among remaining cards
            possible_pair_ranks = []
            most_copies = 0
            for rank, count in ranks.items():
                if rank != three_of_a_kind and deck_ranks.get(rank, 0) > most_copies:
                    possible_pair_ranks = [rank]
                    most_copies = deck_ranks.get(rank, 0)
                elif rank != three_of_a_kind and deck_ranks.get(rank, 0) == most_copies:
                    possible_pair_ranks.append(rank)
            
            # Get the highest rank among those with the most copies
            best_rank = max(possible_pair_ranks)
            
            # Keep the three of a kind and the best potential pair card
            return [i for i, card in enumerate(player.hand) 
                   if card.rank != three_of_a_kind and card.rank != best_rank]
        
        # Case 2: We have two or more pairs
        elif len(pairs) >= 2:
            # Sort pairs by the number of copies in the deck (descending)
            pairs_with_counts = [(rank, deck_ranks.get(rank, 0)) for rank in pairs]
            pairs_with_counts.sort(key=lambda x: (x[1], x[0]), reverse=True)
            
            # Keep the two best pairs
            pairs_to_keep = [pair[0] for pair in pairs_with_counts[:2]]
            
            # Discard cards that aren't in the two best pairs
            return [i for i, card in enumerate(player.hand) 
                   if card.rank not in pairs_to_keep]
        
        # Case 3: We have one pair
        elif len(pairs) == 1:
            pair_rank = pairs[0]
            
            # For remaining cards, find the one with the most copies in the deck
            remaining_cards = []
            for rank, count in ranks.items():
                if rank != pair_rank:
                    remaining_cards.append((rank, deck_ranks.get(rank, 0)))
            
            # Sort by count in deck (descending), then by rank (descending) for ties
            remaining_cards.sort(key=lambda x: (x[1], x[0]), reverse=True)
            
            # Keep the pair and the best remaining card
            ranks_to_keep = [pair_rank]
            if remaining_cards:
                ranks_to_keep.append(remaining_cards[0][0])
            
            # Discard cards that aren't in ranks_to_keep
            return [i for i, card in enumerate(player.hand) 
                   if card.rank not in ranks_to_keep]
        
        # Case 4: No pairs or three of a kind
        else:
            # For each card, count how many of the same rank are in the deck
            cards_with_deck_counts = [(rank, deck_ranks.get(rank, 0)) for rank in ranks.keys()]
            
            # Sort by count in deck (descending), then by rank (descending) for ties
            cards_with_deck_counts.sort(key=lambda x: (x[1], x[0]), reverse=True)
            
            # Keep the two cards with highest counts in the deck
            ranks_to_keep = [card[0] for card in cards_with_deck_counts[:2]]
            
            # Discard cards that aren't in ranks_to_keep
            return [i for i, card in enumerate(player.hand) 
                   if card.rank not in ranks_to_keep]
        
        