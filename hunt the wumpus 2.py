import random

# Class that generates the cave layout
class CaveLayout:
    def __init__(self):
        # Define the cave layout with room connections
        self.cave = {
            1: [2, 5, 8],  2: [1, 3, 10],  3: [2, 4, 12],  4: [3, 5, 14],
            5: [1, 4, 6],  6: [5, 7, 15],  7: [6, 8, 17],  8: [1, 7, 9],
            9: [8, 10, 18], 10: [2, 9, 11], 11: [10, 12, 19], 12: [3, 11, 13],
            13: [12, 14, 20], 14: [4, 13, 15], 15: [6, 14, 16], 16: [15, 17, 20],
            17: [7, 16, 18], 18: [9, 17, 19], 19: [11, 18, 20], 20: [13, 16, 19]
        }

# Class that handles saving and loading game data
class DataManager:
    # Save the current game data to a file
    def save_data(self, filename, game_data):
        with open(filename, "w") as f:
            # Write the number of bullets and player position
            f.write(f"{game_data['bullets']}\n")
            f.write(f"{game_data['player_pos']}\n")
            
            # Write the cave layout, with each room and its connections
            for room, exits in game_data['cave'].items():
                exits_str = ','.join(map(str, exits))  # Convert list of exits to comma-separated string
                f.write(f"{room}:{exits_str}\n")
            
            # Write threats (bats, pits, wumpus) in each room
            for room, threat in game_data['threats'].items():
                f.write(f"{room}={threat}\n")

    # Load game data from a file
    def load_data(self, filename):
        with open(filename, "r") as f:
            lines = f.readlines()  # Read all lines from the file

        # Extract bullets and player position from the file
        bullets = int(lines[0].strip())
        player_pos = int(lines[1].strip())

        # Extract cave layout from the file
        cave = {
            int(room): [int(x) for x in exits.split(',')]  # Convert comma-separated string back to list of integers
            for line in lines[2:] if ':' in line
            for room, exits in [line.strip().split(':')]
        }

        # Extract threats from the file
        threats = {
            int(room): threat
            for line in lines[2:] if '=' in line
            for room, threat in [line.strip().split('=')]
        }

        return {
            'bullets': bullets,
            'player_pos': player_pos,
            'cave': cave,
            'threats': threats
        }

# Class that handles the Wumpus game logic
class WumpusAdventure(CaveLayout):
    def __init__(self):
        CaveLayout.__init__(self)  # Initialize the cave layout from the parent class
        self.bullets = 5  # Initial number of bullets
        self.threats = {}  # Dictionary to store threats in rooms
        self.player_pos = -1  # Initial player position (will be set later)

    # Handle shooting a bullet into a specified room
    def shoot_room(self, room_number):
        # Check if the room is connected to the player's current room
        if room_number not in self.cave[self.player_pos]:
            print(f"You can't shoot a bullet into room {room_number} because it's not connected.")
            return self.player_pos

        print(f"Shooting a bullet into room {room_number}...")
        self.bullets -= 1  # Decrease the number of bullets

        # Check if the shot hits a threat
        if room_number in self.threats:
            threat = self.threats.pop(room_number)  # Remove the threat from the room
            if threat == 'wumpus':
                print("YAY, you killed the wumpus!")
                return -1  # Game over if the Wumpus is killed
            elif threat == 'bat':
                print("You killed a bat.")
                return self.player_pos  # Player remains in the same room
        
        print("You missed the target.")

        # Check if there are no bullets left
        if self.bullets < 1:
            print("Your gun is empty. Game Over!")
            return -1  # Game over if no bullets

        return self.relocate_wumpus()  # Relocate the Wumpus with a chance

    # Handle the chance of relocating the Wumpus after a shot
    def relocate_wumpus(self):
        # 75% chance to relocate the Wumpus
        if random.random() < 0.75:
            # Find the current Wumpus position
            current_wumpus_pos = next((room for room, threat in self.threats.items() if threat == 'wumpus'), None)
            if current_wumpus_pos:
                # Find new positions for the Wumpus that are not already occupied by threats
                possible_new_positions = [room for room in self.cave[current_wumpus_pos] if room not in self.threats]
                if possible_new_positions:
                    # Randomly choose a new position for the Wumpus
                    new_wumpus_pos = random.choice(possible_new_positions)
                    self.threats.pop(current_wumpus_pos)  # Remove Wumpus from the old position
                    self.threats[new_wumpus_pos] = 'wumpus'  # Place Wumpus in the new position
                    # Check if the new position is where the player is
                    if new_wumpus_pos == self.player_pos:
                        print("The wumpus enters your room and eats you!")
                        return -1  # Game over if the Wumpus is in the player's room
        return self.player_pos  # Return the player's position

    # Get a list of rooms that are not occupied by threats
    def get_safe_rooms(self):
        return [room for room in self.cave if room not in self.threats]

    # Spawn entities (bats, pits, Wumpus) in random safe rooms
    def spawn_entities(self):
        for threat in ["bat", "bat", "pit", "pit", "wumpus"]:
            pos = random.choice(self.get_safe_rooms())  # Choose a random safe room for the threat
            self.threats[pos] = threat  # Assign the threat to the room
        self.player_pos = random.choice(self.get_safe_rooms())  # Choose a random safe room for the player

    # Warn the player about nearby threats
    def warn_player(self, threat):
        warnings = {
            "bat": "You hear a rustling.",
            "pit": "You feel a cold wind from a nearby cavern.",
            "wumpus": "You smell something terrible nearby."
        }
        print(warnings.get(threat, ""))  # Print warning message if there is a threat

    # Handle player input for actions and target rooms
    def player_input(self):
        while True:
            action = input("Shoot (S) or move (M). (Q) to Quit: ").lower()
            # Ensure the action is valid
            if action in ['s', 'm', 'q']:
                break
            print("Please select a valid action: 'S' to shoot, 'M' to move.")

        if action == 'q':
            return action, None

        while True:
            try:
                target = int(input("Where to? "))  # Get the target room number
                # Ensure the target is connected to the current room
                if action == 'm' and target in self.cave[self.player_pos]:
                    break
                elif action == 's' and target in self.cave[self.player_pos]:
                    break
                print("Invalid target. Please choose a connected room.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        return action, target
    
    # Enter a specified room and handle encounters with threats
    def enter_room(self, room_num):
        print(f"Entering room {room_num}...")
        if room_num in self.threats:
            if self.threats[room_num] == 'bat':
                print("You encounter a bat, it transports you to a random empty room.")
                return self.enter_room(random.choice(self.get_safe_rooms()))  # Transport to a new room
            elif self.threats[room_num] == 'wumpus':
                print("Wumpus eats you.")
                return -1  # Game over if Wumpus is encountered
            elif self.threats[room_num] == 'pit':
                print("You fall into a pit.")
                return -1  # Game over if pit is encountered
        
        # Warn the player about threats in neighboring rooms
        for neighbor in self.cave[room_num]:
            if neighbor in self.threats:
                self.warn_player(self.threats[neighbor])

        return room_num  # Return the room number after entering

    # Display the number of remaining bullets
    def display_quiver(self):
        print(f"You have {self.bullets} bullets remaining.")

    # Main game loop to run the game
    def game_loop(self):
        print("HUNT THE WUMPUS")
        self.spawn_entities()  # Spawn entities and set player position
        self.enter_room(self.player_pos)  # Enter the initial room

        while self.player_pos != -1:  # Continue the game until game over
            self.display_quiver()
            print(f"You are in room {self.player_pos}. Tunnels lead to: {self.cave[self.player_pos]}")
            action, target = self.player_input()  # Get player action and target room
            if action == 'm':
                self.player_pos = self.enter_room(target)  # Move to the target room
            elif action == 's':
                self.player_pos = self.shoot_room(target)  # Shoot into the target room
                if self.player_pos == -1:  # Check if game over after shooting
                    break
            elif action == 'q':
                # Optionally save the game before quitting
                if input("Do you want to save the game before quitting? (Y/N) ").lower() == 'y':
                    filename = input("Enter the filename to save: ")
                    DataManager().save_data(filename, {
                        'bullets': self.bullets,
                        'player_pos': self.player_pos,
                        'cave': self.cave,
                        'threats': self.threats
                    })
                break
        print("\nGame Over!")  # Notify the end of the game

# Main function to start or load the game
def main():
    while True:
        print("Welcome to HUNT THE WUMPUS!")
        choice = input("Do you want to start a new game (N) or load an existing game (L)? ").lower()
        
        if choice == 'n':
            game = WumpusAdventure()  # Create a new game instance
            game.spawn_entities()  # Spawn entities
            game.game_loop()  # Run the game loop
            break
        elif choice == 'l':
            filename = input("Enter the filename to load: ")
            try:
                game_data = DataManager().load_data(filename)  # Load game data from file
                game = WumpusAdventure()  # Create a new game instance
                game.bullets = game_data['bullets']
                game.player_pos = game_data['player_pos']
                game.cave = game_data['cave']
                game.threats = game_data['threats']
                game.game_loop()  # Run the game loop with loaded data
            except FileNotFoundError:
                print(f"Error: File '{filename}' not found.")
            except Exception as e:
                print(f"An error occurred: {e}")
            break
        else:
            print("Invalid choice. Please select 'N' for a new game or 'L' to load a game.")

# Run the main function directly
main()
