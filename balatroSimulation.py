import random

class Card:
    def __init__(self, rank, suit = None):
        self.rank = rank
        self.suit = suit
        self.chips = 0

        if self.rank == 1:
            self.chips = 11
        elif self.rank in [11, 12, 13]:
            self.chips = 10
        else:
            self.chips = self.rank
            
    def __str__(self):
        rank_names = {1: 'Ace', 11: 'Jack', 12: 'Queen', 13: 'King'}
        rank_name = rank_names.get(self.rank, str(self.rank))
        suit_symbols = {'hearts': '♥', 'diamonds': '♦', 'clubs': '♣', 'spades': '♠'}
        suit_symbol = suit_symbols.get(self.suit, self.suit)
        return f"{suit_symbol} {rank_name}"

class Deck:
    def __init__(self):
        self.cards = []
        for suit in ['hearts', 'diamonds', 'clubs', 'spades']:
            for rank in range(1, 14):
                self.cards.append(Card(rank, suit))
                
    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        try:
            return self.cards.pop()
        except IndexError:
            return "no cards remaining"
    

TARGET_SCORE = 600



class player:
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
        self.history = []

        for i in range(8):
            self.hand.append(self.deck.draw())
    
    def checkScore(self, playing_hand):
        score = 0

        def scoreHighCard(hand):
            score = 0
            base_score = 5
            multiplier = 1
            high_card = max(hand, key=lambda x: x.chips)
            score = (base_score + high_card.chips) * multiplier
            return score

        def scorePair(hand):
            score = 0
            base_score = 10
            multiplier = 2
            
            cardCount = {}
            for card in hand:
                if card.rank in cardCount:
                    cardCount[card.rank] += 1
                else:
                    cardCount[card.rank] = 1

            highest_pair = 0
            for rank, count in cardCount.items():
                if count >= 2:
                    temp = Card(rank)
                    if temp.chips > highest_pair:
                        highest_pair = temp.chips

            if highest_pair == 0:
                return 0
            
            score = (base_score + highest_pair * 2) * multiplier
            return score

        def scoreTwoPair(hand):
            score = 0
            base_score = 20
            multiplier = 2

            cardCount = {}
            for card in hand:
                if card.rank in cardCount:
                    cardCount[card.rank] += 1
                else:
                    cardCount[card.rank] = 1

            highest_pair = 0
            second_highest_pair = 0
            for rank, count in cardCount.items():
                if count >= 2:
                    temp = Card(rank)
                    if temp.chips > highest_pair:
                        second_highest_pair = highest_pair
                        highest_pair = temp.chips
                    elif temp.chips > second_highest_pair:
                        second_highest_pair = rank

            if second_highest_pair == 0:
                return 0
            
            score = (base_score + highest_pair * 2 + second_highest_pair * 2) * multiplier
            return score
            
        def scoreTriple(hand):
            score = 0
            base_score = 30
            multiplier = 3

            cardCount = {}
            for card in hand:
                if card.rank in cardCount:
                    cardCount[card.rank] += 1
                else:
                    cardCount[card.rank] = 1

            highest_triple = 0
            for rank, count in cardCount.items():
                temp = Card(rank)
                if count >= 3:
                    if temp.chips > highest_triple:
                        highest_triple = temp.chips

            if highest_triple == 0:
                return 0
            
            score = (base_score + highest_triple * 3) * multiplier
            return score

        def scoreStraight(hand):
            score = 0
            base_score = 30
            multiplier = 4

            ranks = [card.rank for card in hand]
            sorted_ranks = sorted(ranks, reverse=True)
            if {1, 10, 11, 12, 13} in set(sorted_ranks):
                score = base_score * multiplier
                for i in {1, 10, 11, 12, 13}:
                    temp = Card(i)
                    score += temp.chips * multiplier
                return score

            for i in range(len(sorted_ranks) - 4):
                if sorted_ranks[i] - 1 in sorted_ranks and sorted_ranks[i] - 2 in sorted_ranks and sorted_ranks[i] - 3 in sorted_ranks and sorted_ranks[i] - 4 in sorted_ranks:
                    score = base_score * multiplier
                    for j in range(4):
                        temp = Card(sorted_ranks[i] - j)
                        score += temp.chips * multiplier
                    return score

            return score

        def scoreFlush(hand):
            score = 0
            base_score = 35
            multiplier = 4

            suitCount = {}
            for card in hand:
                if card.suit in suitCount:
                    suitCount[card.suit] += 1
                else:
                    suitCount[card.suit] = 1

            for suit, count in suitCount.items():
                if count >= 5:
                    score = base_score * multiplier
                    # Get the top 5 cards of the same suit
                    cards = [card for card in hand if card.suit == suit]
                    cards.sort(key=lambda x: x.rank, reverse=True)
                    top_cards = cards[:5]
                    for card in top_cards:
                        score += card.chips * multiplier
                    return score
            return score

        def scoreFullHouse(hand):
            score = 0
            base_score = 40
            multiplier = 4

            ranks = [card.rank for card in hand]

            cardCount = {}
            for card in ranks:
                if card in cardCount:
                    cardCount[card] += 1
                else:
                    cardCount[card] = 1
            
            triplerank = 0
            triplechips = 0
            pairchips = 0

            for rank, count in cardCount.items():
                if count >= 3:
                    temp = Card(rank)
                    if temp.chips > triplechips:
                        triplechips = temp.chips
                        triplerank = rank
            ranks = [card for card in ranks if card != triplerank]

            cardCount = {}
            for card in ranks:
                if card in cardCount:
                    cardCount[card] += 1
                else:
                    cardCount[card] = 1

            for rank, count in cardCount.items():
                if count >= 2:
                    temp = Card(rank)
                    if temp.chips > pairchips:
                        pairchips = temp.chips
            
            if triplechips and pairchips:
                return (base_score + triplechips * 3 + pairchips * 2) * multiplier
            
            return score
                    
        def scoreFourOfAKind(hand):
            score = 0
            base_score = 60
            multiplier = 7

            cardCount = {}
            for card in hand:
                if card.rank in cardCount:
                    cardCount[card.rank] += 1
                else:
                    cardCount[card.rank] = 1

            fourchips = 0

            for rank, count in cardCount.items():
                if count >= 4:
                    temp = Card(rank)
                    if temp.chips > fourchips:
                        fourchips = temp.chips
            
            if fourchips == 0:
                return 0
            
            return (base_score + fourchips * 4) * multiplier

        def scoreStraightFlush(hand):
            score = 0
            base_score = 100
            multiplier = 8

            ranks = [card.rank for card in hand]
            suits = [card.suit for card in hand]

            if scoreStraight(hand) and scoreFlush(hand):
                return (base_score + sum(card.chips for card in hand)) * multiplier
            
            return score
        
        scores = {
            "High Card": scoreHighCard(playing_hand),
            "Pair": scorePair(playing_hand),
            "Two Pair": scoreTwoPair(playing_hand),
            "Triple": scoreTriple(playing_hand),
            "Straight": scoreStraight(playing_hand),
            "Flush": scoreFlush(playing_hand),
            "Full House": scoreFullHouse(playing_hand),
            "Four of a Kind": scoreFourOfAKind(playing_hand),
            "Straight Flush": scoreStraightFlush(playing_hand)
        }

        played_hand = max(scores, key=scores.get)
        played_score = scores[played_hand]

        return played_hand, played_score
    
    def discard(self, indices):
        if self.discardsRemaining == 0:
            print("No discards remaining")
            return None

        for index in indices:
            if index < 0 or index >= len(self.hand):
                print("Invalid index")
                continue
            self.hand[index] = self.deck.draw()
        
        self.discardsRemaining -= 1

        return self.hand
    
    def play(self, indices):
        if self.handsRemaining == 0:
            print("No hands remaining")
            return None
        
        play_card = []
        for index in indices:
            play_card.append(self.hand[index])
            self.hand[index] = self.deck.draw()
        self.handsRemaining -= 1
        played_hand, played_score = self.checkScore(play_card)
        self.history.append((play_card, played_hand, played_score))
        self.currentScore += played_score


        return self.currentScore






flushPlayer = player("flush")

def printHand(hand):
    for i, card in enumerate(hand):
        if card.suit == "hearts":
            print(f"index: {i}, card: \033[31m{card}\033[0m")
        elif card.suit == "diamonds":
            print(f"index: {i}, card: \033[33m{card}\033[0m")
        elif card.suit == "clubs":
            print(f"index: {i}, card: \033[32m{card}\033[0m")
        elif card.suit == "spades":
            print(f"index: {i}, card: \033[34m{card}\033[0m")

print("current hand: ")
printHand(flushPlayer.hand)
print("cards remaining in deck: ", len(flushPlayer.deck.cards))
print("hands remaining: ", flushPlayer.handsRemaining, "discards remaining: ", flushPlayer.discardsRemaining)

while flushPlayer.discardsRemaining > 0:
    indices = input("Enter the indices of the cards to discard: ")
    indices = [int(index) for index in indices.split(",")]
    flushPlayer.discard(indices)
    print("new hand: ")
    printHand(flushPlayer.hand)
    print("cards remaining in deck: ", len(flushPlayer.deck.cards))
    print("current score: ", flushPlayer.currentScore)
    print("remaining discards: ", flushPlayer.discardsRemaining)

while flushPlayer.handsRemaining > 0:
    indices = input("Enter the indices of the cards to play: ")
    indices = [int(index) for index in indices.split(",")]
    flushPlayer.play(indices)
    print("played cards: ")
    printHand(flushPlayer.history[-1][0])
    print("played hand: ", flushPlayer.history[-1][1])
    print("played score: ", flushPlayer.history[-1][2])
    print("new hand: ")
    printHand(flushPlayer.hand)
    print("cards remaining in deck: ", len(flushPlayer.deck.cards))
    print("current score: ", flushPlayer.currentScore)