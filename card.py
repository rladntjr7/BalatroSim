class Card:
    def __init__(self, rank, suit = None):
        self.rank = rank
        self.suit = suit
        self.chips = 0

        if self.rank == 1:  # Ace
            self.chips = 11
        elif self.rank in [11, 12, 13]: # J, Q, K
            self.chips = 10
        else:
            self.chips = self.rank
            
    def __str__(self):
        rank_names = {1: 'Ace', 11: 'Jack', 12: 'Queen', 13: 'King'}
        rank_name = rank_names.get(self.rank, str(self.rank))
        suit_symbols = {'hearts': '♥', 'diamonds': '♦', 'clubs': '♣', 'spades': '♠'}
        suit_symbol = suit_symbols.get(self.suit, self.suit)
        return f"{suit_symbol} {rank_name}" 