from player import Player, TARGET_SCORE
from card import Card

def printHand(hand):
    """Prints the player's hand with indices and colors."""
    if not hand:
        print("(Hand is empty)")
        return
    for i, card in enumerate(hand):
        color_code = '\033[0m' # Default color
        if card and card.suit == "hearts":
            color_code = '\033[31m' # Red
        elif card and card.suit == "diamonds":
            color_code = '\033[33m' # Yellow (often used for diamonds)
        elif card and card.suit == "clubs":
            color_code = '\033[32m' # Green
        elif card and card.suit == "spades":
            color_code = '\033[34m' # Blue
        reset_code = '\033[0m'
        print(f"Index {i}: {color_code}{card}{reset_code}")

def print_game_state(player):
    """Prints the current state of the game."""
    print("\n---------------------")
    print(f"Score: {player.currentScore} / {TARGET_SCORE}")
    print(f"Hands Remaining: {player.handsRemaining}")
    print(f"Discards Remaining: {player.discardsRemaining}")
    print("Cards in deck: ", len(player.deck.cards))
    print("Current Hand:")
    printHand(player.hand)
    print("---------------------")

def get_player_input(prompt, max_value):
    """Safely gets integer list input from the player."""
    while True:
        try:
            raw_input = input(prompt).strip()
            if not raw_input: # Handle empty input
                return []
            indices = [int(index.strip()) for index in raw_input.split(",")]
            # Basic validation
            if any(i < 0 or i >= max_value for i in indices):
                print(f"Error: Indices must be between 0 and {max_value - 1}.")
                continue
            return indices
        except ValueError:
            print("Error: Invalid input. Please enter comma-separated numbers.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

def main():
    """Main game loop."""
    # Initialize player (can add strategy selection later)
    player = Player("manual") 

    print("Welcome to Balatro Simulation!")

    # Game Loop
    while not player.win and (player.handsRemaining > 0 or player.discardsRemaining > 0):
        print_game_state(player)
        
        action = input("Choose action: [P]lay, [D]iscard, [Q]uit? ").upper()

        if action == 'D':
            if player.discardsRemaining > 0:
                indices = get_player_input("Enter indices to discard (comma-separated, e.g., 0,2,4): ", len(player.hand))
                if indices is not None:
                    player.discard(indices)
            else:
                print("No discards remaining.")
        
        elif action == 'P':
            if player.handsRemaining > 0:
                 indices = get_player_input("Enter indices to play (comma-separated, e.g., 1,3,5): ", len(player.hand))
                 if indices is not None:
                     if player.play(indices):
                         # Print last played hand details
                         if player.history:
                             last_played, hand_name, score = player.history[-1]
                             print("\n--- Last Play ---")
                             print("Played Cards:")
                             printHand(last_played)
                             print(f"Hand Type: {hand_name}")
                             print(f"Score Gained: {score}")
                             print("-----------------")
            else:
                print("No hands remaining.")

        elif action == 'Q':
            print("Quitting game.")
            break
        
        else:
            print("Invalid action. Choose P, D, or Q.")

    # End of game message
    print("\n===== Game Over =====")
    if player.win:
        print(f"Congratulations! You reached the target score of {TARGET_SCORE}!")
    else:
        print(f"Game over. Final Score: {player.currentScore}")
        if player.handsRemaining == 0 and player.discardsRemaining == 0:
            print("You ran out of hands and discards.")
        elif player.handsRemaining == 0:
             print("You ran out of hands.")

    print("=====================")

# Run the game
if __name__ == "__main__":
    main() 