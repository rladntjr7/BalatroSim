import unittest
import sys
import os

# Add the Simulation directory to the sys.path
sys.path.append(os.path.abspath('Simulation'))

from player import Player
from strategy import FlushStrategy, checkhandforsuits, checkdeckforsuits
from card import Card
from deck import Deck

class TestFlushStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = FlushStrategy()
        
    def test_select_play_cards_with_flush(self):
        """Test that strategy correctly selects cards when flush is available"""
        # Create a player with a hand containing flush
        player = Player("Test Player", 100)
        # Add 6 hearts to the hand
        player.hand = [
            Card("hearts", 2, 2),
            Card("hearts", 5, 5),
            Card("hearts", 7, 7),
            Card("hearts", 10, 10),
            Card("hearts", 13, 13),
            Card("hearts", 1, 15),  # Ace of hearts
            Card("spades", 12, 12)  # Random card
        ]
        
        # Get the play selection
        selection = self.strategy.select_play_cards(player)
        
        # Should select 5 heart cards with highest value
        self.assertEqual(len(selection), 5)
        for idx in selection:
            self.assertEqual(player.hand[idx].suit, "hearts")
        
        # Should include the Ace (highest value)
        self.assertIn(5, selection)  # Ace is at index 5
        
    def test_select_play_cards_no_flush(self):
        """Test when no flush is available but fallback strategy works"""
        player = Player("Test Player", 100)
        # Add cards of different suits
        player.hand = [
            Card("hearts", 2, 2),
            Card("hearts", 5, 5),
            Card("diamonds", 7, 7),
            Card("clubs", 10, 10),
            Card("spades", 13, 13)
        ]
        player.playsRemaining = 5
        player.discardsRemaining = 3
        
        # Get the play selection - should use fallback
        selection = self.strategy.select_play_cards(player)
        
        # Should still select some cards
        self.assertTrue(len(selection) > 0)
        
    def test_select_discard_cards_single_suit(self):
        """Test discard selection when only one suit is present in hand"""
        player = Player("Test Player", 100)
        # Create a hand with only hearts
        player.hand = [
            Card("hearts", 2, 2),
            Card("hearts", 5, 5),
            Card("hearts", 7, 7)
        ]
        
        # Create a deck with various cards
        player.deck = Deck()
        player.deck.cards = [
            Card("hearts", 10, 10),
            Card("hearts", 13, 13),
            Card("diamonds", 1, 15),
            Card("spades", 12, 12)
        ]
        
        # Get the discard selection
        selection = self.strategy.select_discard_cards(player)
        
        # Should return empty list since all cards are the same suit
        self.assertEqual(selection, [])
        
    def test_select_discard_cards_multiple_suits(self):
        """Test discard selection with multiple suits"""
        player = Player("Test Player", 100)
        # Create a hand with mixed suits (2 hearts, 2 spades, 1 diamond)
        player.hand = [
            Card("hearts", 2, 2),
            Card("hearts", 5, 5),
            Card("spades", 7, 7),
            Card("spades", 10, 10),
            Card("diamonds", 13, 13)
        ]
        
        # Create a deck with various cards
        player.deck = Deck()
        player.deck.cards = [
            Card("hearts", 10, 10),
            Card("hearts", 13, 13),
            Card("spades", 1, 15),
            Card("spades", 12, 12)
        ]
        
        # Get the discard selection
        selection = self.strategy.select_discard_cards(player)
        
        # Should discard the diamond card (index 4)
        self.assertIn(4, selection)
        
    def test_select_discard_cards_tie_suits(self):
        """Test discard with tied suit counts"""
        player = Player("Test Player", 100)
        # Create a hand with equal number of hearts and spades
        player.hand = [
            Card("hearts", 2, 2),
            Card("hearts", 5, 5),
            Card("spades", 7, 7),
            Card("spades", 10, 10),
            Card("diamonds", 13, 13)
        ]
        
        # Create a deck with more hearts than spades
        player.deck = Deck()
        player.deck.cards = [
            Card("hearts", 10, 10),
            Card("hearts", 13, 13),
            Card("hearts", 1, 15),
            Card("spades", 12, 12)
        ]
        
        # Get the discard selection
        selection = self.strategy.select_discard_cards(player)
        
        # Should not discard hearts (indices 0,1) as there are more in deck
        for idx in selection:
            self.assertNotEqual(player.hand[idx].suit, "hearts")
            
    def test_hand_suit_counting(self):
        """Test the checkhandforsuits helper function"""
        hand = [
            Card("hearts", 2, 2),
            Card("hearts", 5, 5),
            Card("spades", 7, 7),
            Card("clubs", 10, 10)
        ]
        
        suits = checkhandforsuits(hand)
        self.assertEqual(suits["hearts"], 2)
        self.assertEqual(suits["spades"], 1)
        self.assertEqual(suits["clubs"], 1)
        self.assertEqual(suits["diamonds"], 0)
        
    def test_deck_suit_counting(self):
        """Test the checkdeckforsuits helper function"""
        deck = Deck()
        deck.cards = [
            Card("hearts", 2, 2),
            Card("hearts", 5, 5),
            Card("spades", 7, 7),
            Card("clubs", 10, 10)
        ]
        
        suits = checkdeckforsuits(deck)
        self.assertEqual(suits["hearts"], 2)
        self.assertEqual(suits["spades"], 1)
        self.assertEqual(suits["clubs"], 1)
        self.assertEqual(suits["diamonds"], 0)

if __name__ == "__main__":
    unittest.main() 