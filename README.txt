==============================================
SIMULATING EARLY-GAME STRATEGIES IN BALATRO: 
A COMPREHENSIVE ANALYSIS OF POPULAR STRATEGIES
==============================================

Wooseok Kim, Group 284

==============================================
PROJECT INTRODUCTION
==============================================
This project aims to simulate early gameplay of game Balatro - a rouguelike card game. This project was written entirely in Python, including the game sturcture and simulations.

==============================================
SIMULATION
==============================================
Simulation folder contains all files related to simulation.
1. card.py, deck.py, and player.py are the basic building blocks of the game. This game can be manually played by making a Player instance and manually inputting cards to play/discard.
2. strategy.py contains all strategies involving playing and discarding cards. Each strategy decides which card to play/discard according to its inner logic.
3. strategicPlayer.py inherits the Player class, adding functions to play and discard cards according to the strategies assigned.

==============================================
RESULTS
==============================================
Results folder contains all data saved from running simulation.

==============================================
ANALYSIS
==============================================
Analysis folder contains all files related to analysis and the output, including box charts.

==============================================
ACKNOWLEDGEMENT
==============================================
Although most of the structures and concepts of this program has been drafted by myself, some details and formatting has been aided by several Generative AI agents and autocompletion features of my IDE. 