#!/usr/bin/env python3
"""
Legends of the Hidden Temple - Temple Run Simulator
Navigate through Olmec's temple to find the Jade Serpent's Crown!
"""

import json
import random
import time
import sys
import traceback
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import os
import subprocess
from pathlib import Path

class Color:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

@dataclass
class Player:
    """Represents the player running through the temple"""
    pendants_of_life: int = 2
    path_taken: List[str] = None
    time_remaining: float = 180.0
    has_artifact: bool = False
    guards_encountered: int = 0
    
    def __post_init__(self):
        if self.path_taken is None:
            self.path_taken = []

class PrizeTracker:
    """Track and display prizes won during the game"""
    
    def __init__(self, prize_file: str):
        """Load prize configuration"""
        try:
            with open(prize_file, 'r') as f:
                self.prize_data = json.load(f)['prizes']
        except FileNotFoundError:
            self.prize_data = None
            
    def get_prizes_won(self, player: Player, won: bool, rooms_visited: int, total_rooms: int) -> List[Dict]:
        """Determine which prizes were won based on performance"""
        if not self.prize_data:
            return []
            
        prizes = []
        
        # Everyone gets participation prizes
        prizes.extend(self.prize_data['participation']['items'])
        
        # Assume they made it through earlier rounds
        prizes.extend(self.prize_data['moat_crossing']['items'])
        prizes.extend(self.prize_data['steps_of_knowledge']['items'])
        
        # Temple Games - got 2 pendants (full pendant prize)
        prizes.extend(self.prize_data['temple_games']['full_pendant'])
        
        # Temple Run prizes
        if rooms_visited >= 1:
            prizes.extend(self.prize_data['temple_run']['reached_temple'])
        
        if rooms_visited >= 5:
            prizes.extend(self.prize_data['temple_run']['five_rooms'])
            
        if player.has_artifact:
            prizes.extend(self.prize_data['temple_run']['grabbed_artifact'])
            
        if won:
            # GRAND PRIZE!
            prizes.extend(self.prize_data['temple_run']['temple_completion']['grand_prizes'])
            
        # Bonus prizes
        if 180 - player.time_remaining < 60:
            prizes.append(self.prize_data['consolation_prizes']['speed_bonus_under_60_seconds'])
            
        if player.guards_encountered == 0 and won:
            prizes.append(self.prize_data['consolation_prizes']['no_temple_guards_met'])
            
        if rooms_visited == total_rooms:
            prizes.append(self.prize_data['consolation_prizes']['all_rooms_visited'])
            
        return prizes
    
    def announce_prizes(self, prizes: List[Dict], won: bool):
        """Display prizes in classic game show announcer style"""
        if not prizes:
            return
            
        print(f"\n{Color.YELLOW}{'='*60}")
        print(f"{Color.BOLD}🎁 PRIZES AWARDED! 🎁")
        print(f"{'='*60}{Color.END}\n")
        
        # Kirk Fogg style announcement
        print(f"{Color.CYAN}{Color.BOLD}[KIRK]: Tell them what they've won!{Color.END}\n")
        time.sleep(1)
        
        # Announcer voice
        print(f"{Color.GREEN}{Color.BOLD}[ANNOUNCER]: {Color.END}")
        
        total_value = 0
        for i, prize in enumerate(prizes):
            if isinstance(prize, dict):
                time.sleep(0.5)
                print(f"\n{Color.YELLOW}★ {prize['name'].upper()}{Color.END}")
                print(f"  {prize['description']}")
                print(f"  {Color.CYAN}Provided by: {prize['sponsor']}{Color.END}")
                
                # Special handling for Space Camp
                if 'includes' in prize:
                    print(f"  {Color.GREEN}Package includes:{Color.END}")
                    for item in prize['includes']:
                        print(f"    • {item}")
                
                # Parse value
                value_str = prize.get('value', '$0')
                value_num = int(''.join(c for c in value_str if c.isdigit()))
                total_value += value_num
        
        print(f"\n{Color.YELLOW}{'='*60}")
        print(f"{Color.BOLD}TOTAL PRIZE VALUE: ${total_value:,}{Color.END}")
        print(f"{'='*60}{Color.END}\n")
        
        if won:
            print(f"{Color.GREEN}{Color.BOLD}Congratulations to our TEMPLE CHAMPIONS!{Color.END}")
            print(f"{Color.CYAN}You're going to SPACE CAMP!{Color.END}\n")
        
        # Random sponsor message
        if self.prize_data and 'sponsor_announcements' in self.prize_data:
            sponsor_msg = random.choice(self.prize_data['sponsor_announcements'])
            print(f"{Color.PURPLE}{sponsor_msg}{Color.END}\n")

class TempleRunner:
    """Main game engine for the temple run"""
    
    def __init__(self, temple_file: str):
        """Load the temple configuration from JSON"""
        with open(temple_file, 'r') as f:
            self.temple_data = json.load(f)
        
        self.rooms = self.temple_data['rooms']
        self.current_room = 'entrance'
        self.player = Player()
        self.temple_guards_remaining = self.temple_data['temple_guards']
        self.guard_rooms = self._place_temple_guards()
        self.visited_rooms = set()
        self.start_time = None
        
        # Initialize prize tracker
        prize_file = temple_file.replace('temple-map-graph.json', 'temple-prizes.json')
        self.prize_tracker = PrizeTracker(prize_file)
        
        # Set up image directory path
        self.image_dir = Path('/home/aaron/Projects/games/maze/room_images')
        self.enable_images = self.check_chafa_available()
        
    def _place_temple_guards(self) -> List[str]:
        """Randomly place temple guards in valid rooms"""
        guard_possible_rooms = [
            room_id for room_id, room in self.rooms.items()
            if room.get('temple_guard_possible', False)
        ]
        return random.sample(guard_possible_rooms, 
                           min(self.temple_guards_remaining, len(guard_possible_rooms)))
    
    def check_chafa_available(self) -> bool:
        """Check if chafa is installed for image display"""
        try:
            result = subprocess.run(['which', 'chafa'], capture_output=True, text=True, stdin=subprocess.DEVNULL)
            if result.returncode == 0:
                print(f"{Color.GREEN}✓ Image support enabled (chafa found){Color.END}")
                return True
        except:
            pass
        print(f"{Color.YELLOW}⚠ Image support disabled (install chafa for room images){Color.END}")
        return False
    
    def display_room_image(self):
        """Display the image for the current room using chafa"""
        if not self.enable_images:
            return
        
        room = self.rooms[self.current_room]
        image_filename = room.get('image_file')
        
        if not image_filename:
            return
        
        image_path = self.image_dir / image_filename
        
        if image_path.exists():
            try:
                # Use chafa to display the image
                # --size: adjust to terminal width
                # --symbols: use block characters for better quality
                # --colors: use 256 colors
                subprocess.run([
                    'chafa',
                    '--size', '60x30',  # Adjust size as needed
                    '--symbols', 'block',
                    '--colors', '256',
                    str(image_path)
                ], check=False, stdin=subprocess.DEVNULL)
                print()  # Add a blank line after the image
            except Exception as e:
                # Silently fail if image can't be displayed
                pass
    
    def olmec_speaks(self, message: str, color: str = Color.YELLOW):
        """Display Olmec's narration"""
        print(f"\n{color}{Color.BOLD}[OLMEC]: {message}{Color.END}")
        time.sleep(0.5)
    
    def display_status(self):
        """Show current game status"""
        # Update time before displaying
        if self.start_time:
            elapsed = time.time() - self.start_time
            self.player.time_remaining = max(0, 180 - elapsed)
        
        print(f"\n{Color.CYAN}{'='*60}")
        minutes = int(self.player.time_remaining // 60)
        seconds = int(self.player.time_remaining % 60)
        print(f"⏱️  Time Remaining: {Color.BOLD}{minutes}:{seconds:02d}{Color.END}")
        print(f"🏅 Pendants of Life: {Color.BOLD}{self.player.pendants_of_life}{Color.END}")
        print(f"📍 Current Location: {Color.BOLD}{self.rooms[self.current_room]['name']}{Color.END}")
        if self.player.has_artifact:
            print(f"👑 {Color.GREEN}{Color.BOLD}YOU HAVE THE JADE SERPENT'S CROWN!{Color.END}")
        print(f"{Color.CYAN}{'='*60}{Color.END}\n")
    
    def describe_room(self):
        """Describe the current room"""
        room = self.rooms[self.current_room]
        
        # Display the room image if available
        self.display_room_image()
        
        print(f"\n{Color.PURPLE}{Color.BOLD}{'~'*60}")
        print(f"You are in: {room['name'].upper()}")
        print(f"{'~'*60}{Color.END}\n")
        print(f"{room['description']}\n")
        
    def check_temple_guard(self) -> bool:
        """Check if there's a temple guard in this room"""
        if self.current_room in self.guard_rooms and self.current_room not in self.visited_rooms:
            self.olmec_speaks("TEMPLE GUARD!", Color.RED)
            print(f"{Color.RED}A Temple Guard emerges from the shadows!{Color.END}")
            self.player.guards_encountered += 1
            
            if self.player.pendants_of_life > 0:
                self.player.pendants_of_life -= 1
                self.guard_rooms.remove(self.current_room)
                print(f"{Color.YELLOW}You give the guard a Pendant of Life and continue...{Color.END}")
                return True
            else:
                print(f"{Color.RED}{Color.BOLD}You're out of Pendants! The Temple Guard captures you!{Color.END}")
                return False
        return True
    
    def show_available_actions(self) -> Dict[str, str]:
        """Display available actions and their corresponding connections"""
        room = self.rooms[self.current_room]
        actions = room.get('actions', [])
        connections = room.get('connections', {})
        
        print(f"\n{Color.GREEN}Available actions:{Color.END}")
        action_map = {}
        
        for i, (key, next_room) in enumerate(connections.items(), 1):
            # Find matching action for this connection
            action_desc = actions[min(i-1, len(actions)-1)] if i <= len(actions) else f"Go to {key}"
            
            # Show if this leads to a visited room
            visited_marker = " ✓" if next_room in self.visited_rooms else ""
            
            # Special marker for the artifact room
            if next_room == 'heart_chamber' and not self.player.has_artifact:
                visited_marker = " 👑"
            
            print(f"  {i}. {action_desc} → [{self.rooms[next_room]['name']}{visited_marker}]")
            action_map[str(i)] = next_room
            
        if 'back' in connections:
            print(f"  B. Go back")
            action_map['b'] = connections['back']
            action_map['B'] = connections['back']
            
        return action_map
    
    def move_to_room(self, new_room: str):
        """Move player to a new room"""
        self.visited_rooms.add(self.current_room)
        self.player.path_taken.append(self.current_room)
        self.current_room = new_room
        
        # Check if we found the artifact!
        if self.current_room == 'heart_chamber' and not self.player.has_artifact:
            self.olmec_speaks("YOU'VE FOUND THE JADE SERPENT'S CROWN!", Color.GREEN)
            print(f"\n{Color.GREEN}{Color.BOLD}🎉 The crown glimmers with ancient power! 🎉{Color.END}")
            print(f"{Color.YELLOW}Now race back to the temple entrance!{Color.END}")
            self.player.has_artifact = True
            time.sleep(2)
    
    def update_time(self) -> bool:
        """Update remaining time and check if time's up"""
        if self.start_time:
            elapsed = time.time() - self.start_time
            self.player.time_remaining = max(0, 180 - elapsed)
            
            if self.player.time_remaining <= 0:
                return False
                
            # Time warnings at specific thresholds (only warn once)
            if self.player.time_remaining <= 30 and not hasattr(self, 'warned_30'):
                self.olmec_speaks("THIRTY SECONDS!", Color.RED)
                self.warned_30 = True
            elif self.player.time_remaining <= 60 and not hasattr(self, 'warned_60'):
                self.olmec_speaks("ONE MINUTE REMAINING!", Color.YELLOW)  
                self.warned_60 = True
                
        return True
    
    def check_win_condition(self) -> bool:
        """Check if player has won"""
        return self.player.has_artifact and self.current_room == 'entrance'
    
    def run_temple(self):
        """Main game loop"""
        # Opening narration
        self.olmec_speaks("Welcome to my temple!", Color.YELLOW)
        self.olmec_speaks(f"You have THREE MINUTES to retrieve the {self.temple_data['artifact']} "
                         f"and return to the temple gates...")
        self.olmec_speaks("Or you will be locked in my temple... FOREVER!", Color.RED)
        print(f"\n{Color.CYAN}The temple doors open with a grinding sound of ancient stone...{Color.END}")
        time.sleep(2)
        
        self.start_time = time.time()
        
        # Main game loop
        while True:
            # Update and check time
            if not self.update_time():
                self.olmec_speaks("TIME'S UP!", Color.RED)
                print(f"\n{Color.RED}{Color.BOLD}The temple doors seal shut! "
                      f"You are trapped forever!{Color.END}")
                self.show_final_stats(won=False)
                break
            
            # Display current state
            self.display_status()
            self.describe_room()
            
            # Check for temple guard
            if not self.check_temple_guard():
                self.show_final_stats(won=False)
                break
            
            # Check win condition
            if self.check_win_condition():
                self.olmec_speaks("CONGRATULATIONS! You've escaped with the crown!", Color.GREEN)
                print(f"\n{Color.GREEN}{Color.BOLD}🏆 TEMPLE RUN SUCCESSFUL! 🏆{Color.END}")
                self.show_final_stats(won=True)
                break
            
            # Show available actions
            action_map = self.show_available_actions()
            
            # Get player choice (simple blocking input)
            try:
                choice = input(f"\n{Color.YELLOW}What do you do? (Enter number): {Color.END}").strip()
            except (KeyboardInterrupt, EOFError):
                print(f"\n\n{Color.YELLOW}Temple run ended!{Color.END}")
                break
            
            if not choice:
                print(f"{Color.RED}Please enter a number.{Color.END}")
                continue
            
            if choice in action_map:
                next_room = action_map[choice]
                
                # Dramatic pause for effect
                print(f"\n{Color.CYAN}You make your choice...{Color.END}")
                time.sleep(1)
                
                # Random flavor text
                if random.random() < 0.3:
                    flavor = random.choice([
                        "The ancient mechanisms groan as a door opens...",
                        "Stone grinds against stone...",
                        "You hear whispers from the temple spirits...",
                        "The path ahead beckons...",
                        "Your footsteps echo through the ancient halls..."
                    ])
                    print(f"{Color.PURPLE}{flavor}{Color.END}")
                    time.sleep(1)
                
                self.move_to_room(next_room)
            else:
                print(f"{Color.RED}Invalid choice! Choose a number from the list.{Color.END}")
    
    def show_final_stats(self, won: bool):
        """Display final game statistics"""
        print(f"\n{Color.CYAN}{'='*60}")
        print(f"{Color.BOLD}FINAL STATISTICS{Color.END}")
        print(f"{'='*60}{Color.END}")
        
        if won:
            print(f"Result: {Color.GREEN}{Color.BOLD}VICTORY!{Color.END}")
        else:
            print(f"Result: {Color.RED}{Color.BOLD}DEFEAT{Color.END}")
            
        print(f"Time Used: {180 - self.player.time_remaining:.1f} seconds")
        print(f"Pendants Remaining: {self.player.pendants_of_life}")
        print(f"Temple Guards Encountered: {self.player.guards_encountered}")
        print(f"Rooms Explored: {len(self.visited_rooms)}/{len(self.rooms)}")
        print(f"\nPath Taken: {' → '.join(self.player.path_taken[:10])}")
        if len(self.player.path_taken) > 10:
            print(f"            → ... → {self.player.path_taken[-1]}")
        
        # Award and announce prizes!
        prizes = self.prize_tracker.get_prizes_won(
            self.player, won, len(self.visited_rooms), len(self.rooms)
        )
        self.prize_tracker.announce_prizes(prizes, won)
        
        print(f"\n{Color.YELLOW}Thanks for playing Legends of the Hidden Temple!{Color.END}")

def main():
    """Main entry point"""
    print(f"{Color.BOLD}{Color.YELLOW}")
    print("=" * 60)
    print("  LEGENDS OF THE HIDDEN TEMPLE - TEMPLE RUN SIMULATOR")
    print("=" * 60)
    print(f"{Color.END}")
    
    try:
        runner = TempleRunner('/home/aaron/Projects/games/maze/temple-map-graph.json')
        runner.run_temple()
    except FileNotFoundError:
        print(f"{Color.RED}Error: Could not find temple-map-graph.json{Color.END}")
        print("Make sure the file exists at: /home/aaron/Projects/games/maze/temple-map-graph.json")
    except KeyboardInterrupt:
        print(f"\n\n{Color.YELLOW}Temple run aborted! The temple keeps its secrets...{Color.END}")
    except Exception as e:
        print(f"{Color.RED}An error occurred: {e}{Color.END}")
        print(f"{Color.RED}Error type: {type(e).__name__}{Color.END}")
        print(f"{Color.RED}Traceback:{Color.END}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
