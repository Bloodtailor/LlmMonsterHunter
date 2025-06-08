# Use Cases

**Date:** February 28, 2025  
**Document Type:** Analysis Phase Deliverable

## Use Case Overview

This document defines the functional use cases for the Monster Hunter Game system. Each use case describes a specific interaction between the player (actor) and the system to accomplish a particular goal.

---

## UC-1: Starting The Game

**Use Case Name:** Starting The Game  
**ID:** UC-1  
**Priority:** Medium  
**Actor:** Player  
**Description:** The player starts the game and loads their saved progress  
**Trigger:** The player opens the game launcher  
**Type:** External

### Preconditions
1. The game is installed and the player has a saved game

### Normal Course
1. Player launches the game
2. The game loads and displays the main menu
3. Player selects "Load Game"
4. The game loads the player's saved progress and displays the home base screen

### Postconditions
1. The player is taken to the home base screen with their saved progress loaded

### Exceptions
1. If no saved game exists, the player selects "New Game"
2. The game initializes a new game and displays the home base screen

---

## UC-2: Managing Monsters

**Use Case Name:** Managing Monsters at Home Base  
**ID:** UC-2  
**Priority:** Medium  
**Actor:** Player  
**Description:** The player manages their party of monsters at the home base  
**Trigger:** The player interacts with monsters at home base  
**Type:** External

### Preconditions
1. The player is on the home base screen
2. The player has monsters at the home base

### Normal Course
1. Player views the monsters on the home base screen
2. The player selects a slot in their party, and selects a monster at base to add the monster to their party
3. Player selects a monster to view its details
4. Player performs actions such as renaming, evolving, or viewing details
5. Changes are saved and visible to the player

### Postconditions
1. The player's party of monsters is updated based on their actions

---

## UC-3: Entering The Dungeon

**Use Case Name:** Entering the Dungeon  
**ID:** UC-3  
**Priority:** High  
**Actor:** Player  
**Description:** The player enters a dungeon to explore and encounter monsters  
**Trigger:** The player selects "Enter The Dungeon" from the home screen, or is returning to the dungeon from an encounter  
**Type:** External

### Preconditions
1. The player has at least one living monster in their party

### Normal Course
1. Player is moved to the Dungeon Screen
2. The game generates a dungeon and displays the dungeon screen with three doors
3. Player selects a door to proceed

### Postconditions
1. The player navigates through the dungeon, encountering various events

---

## UC-4: Exploring The Dungeon

**Use Case Name:** Exploring the Dungeon  
**ID:** UC-4  
**Priority:** Medium  
**Actor:** Player  
**Description:** The player explores the dungeon, encountering traps, treasures, or monsters  
**Trigger:** The player selects a door in the dungeon  
**Type:** External

### Preconditions
1. The player is on the dungeon screen

### Normal Course
1. Player selects a door on the dungeon screen
2. The game randomly determines the outcome (trap, treasure, or monster)
3. If a trap is encountered, the player deals with the trap
4. If a treasure is encountered, the player collects the treasure
5. If a monster is encountered, the game transitions to the battle screen
6. If the exit door is opened, the player exits the dungeon keeping their treasure and monsters

### Postconditions
1. The player navigates through the dungeon, encountering various events

---

## UC-5: Battling Monsters

**Use Case Name:** Battling Monsters  
**ID:** UC-5  
**Priority:** High  
**Actor:** Player  
**Description:** The player engages in a turn-based battle against enemy monsters  
**Trigger:** The player encounters monsters in the dungeon  
**Type:** External

### Preconditions
1. The player is on the dungeon screen

### Normal Course
1. The game transitions to the battle screen
2. Player selects actions for each of their monsters
3. Player clicks the "Execute" button to initiate the turn
4. The game processes actions for both player's and enemy's monsters one by one by clicking the next button
5. The player views the battle log to see the outcome of each action
6. Steps 2-5 repeat until one side is defeated or the player escapes

### Postconditions
1. The battle is resolved, and the player either wins, loses, or escapes

---

## UC-6: Using Inventory Items In Battle

**Use Case Name:** Using Inventory Items in Battle  
**ID:** UC-6  
**Priority:** Low  
**Actor:** Player  
**Description:** The player uses items from their inventory during a battle  
**Trigger:** The player selects an item in their inventory during battle  
**Type:** External

### Preconditions
1. The player is in the battle screen with items in their inventory

### Normal Course
1. Player selects an inventory item during battle
2. If the item is to be used on a monster, the player selects a monster to use it on
3. The item is used, and its effects are applied immediately
4. Player continues with the battle

### Postconditions
1. The selected item is used, affecting the battle outcome

---

## UC-7: Player Chats with Monster

**Use Case Name:** Player Chats with Monster  
**ID:** UC-7  
**Priority:** Medium  
**Actor:** Player  
**Description:** The player engages in conversation with a captured monster  
**Trigger:** The player selects a monster to chat with  
**Type:** External

### Preconditions
1. The player is at the home base screen

### Normal Course
1. Player selects a monster to chat with
2. The game generates monster greeting dialog
3. Player types something to say to the monster
4. The game generates monster response
5. Steps 3 and 4 repeat until player ends chat

### Postconditions
1. Chat is saved
2. Summary of chat is added to monster's context

---

## UC-8: Saving Game State

**Use Case Name:** Saving Game State  
**ID:** UC-8  
**Priority:** Low  
**Actor:** Player  
**Description:** The player saves the game allowing them to exit the game and return where they left off  
**Trigger:** The player clicks the save button  
**Type:** External

### Preconditions
1. The player is at the home base screen

### Normal Course
1. Player selects the "Save Game" option from the home base screen
2. The game saves the current state to a file
3. Player can later select "Load Game" from the main menu to resume from the saved state

### Postconditions
1. The game's current state is saved, and the player can resume from this point later

---

## UC-9: Selecting Monster Actions in Battle

**Use Case Name:** Selecting Monster Actions in Battle  
**ID:** UC-9  
**Priority:** High  
**Actor:** Player  
**Description:** The player selects actions for their monsters during a battle by interacting with the monster's card, flipping it to reveal available actions, and selecting a specific action  
**Trigger:** The player is on the battle screen and is prompted to select actions for their monsters  
**Type:** External

### Preconditions
- The player is on the battle screen
- The player's monsters have sufficient energy to perform actions

### Normal Course
1. The player clicks on a monster's card
2. The monster's card flips over and grows larger, covering the friendly side of the battlefield
3. The enlarged card displays categories of actions: Ability, Defense, Capture, Item, and Pass
4. The player clicks on one of the categories (e.g., Ability)
5. The card flips again to reveal the specific actions available within the selected category
6. The player selects a specific action (e.g., Fireball)
7. The card returns to its original size and position, flipping back to its main side
8. If the selected action requires a target, the potential target monsters are highlighted
9. The player selects the target monster(s) for the action
10. The monster gains an icon indicating the selected category of action (e.g., an Ability icon)
11. The player repeats steps 1-10 for each of their monsters
12. The player clicks the "Execute" button to lock in all moves and continue the battle

### Postconditions
- All selected actions for the player's monsters are locked in
- The battle proceeds with the execution of the selected actions

### Exceptions
- If a monster does not have sufficient energy for an action, the game prevents the action from being selected
- If the player attempts to target an invalid monster, the game provides feedback and prompts for a valid target

---

## UC-10: Viewing Monster Details in Home Base

**Use Case Name:** Viewing Monster Details in Home Base  
**ID:** UC-10  
**Priority:** Low  
**Actor:** Player  
**Description:** The player views detailed information about their monsters at the home base  
**Trigger:** The player clicks on a monster in the home base screen  
**Type:** External

### Preconditions
- The player is on the home base screen
- The player has monsters at their base

### Normal Course
1. The player clicks on a monster at their base in the home screen
2. The monster's card grows larger and flips over to the "Card Management" side of the card
3. The card management side displays basic information and options to evolve, rename, or view more information
4. The player clicks "More Information" and the card flips over to the "Information Categories" side
5. The card displays categories of information about the selected monster (e.g., stats, abilities, current status)
6. The player clicks on one of the categories (e.g., stats)
7. The card flips again to reveal the specific information within that category
8. The player clicks a back button to turn the card back over and select another category
9. The card has a fixed height and width. Additional information that does not fit within the card can be viewed by scrolling
10. The player either clicks outside of the card area or clicks the back button on the information categories side
11. The card returns to its original size and position, flipping back to its main side

### Postconditions
- The player views detailed information about their monsters
- Any changes made (e.g., renaming) are saved and reflected in the home base screen

### Exceptions
- If a monster does not meet the conditions to evolve, the game prevents evolve from being selected

---

## UC-11: Handling Trap Encounters in Dungeon

**Use Case Name:** Handling Trap Encounters in Dungeon  
**ID:** UC-11  
**Priority:** Low  
**Actor:** Player  
**Description:** The player encounters and handles traps while exploring the dungeon  
**Trigger:** The player selects a door that leads to a trap  
**Type:** External

### Preconditions
- The player is on the dungeon screen
- The player selects a door that triggers a trap

### Normal Course
1. The player selects a door in the dungeon screen
2. The game randomly determines that the door leads to a trap
3. The game displays a trap encounter screen with details about the trap
4. The player chooses an action to handle the trap (e.g., disarm, avoid)
5. The game processes the player's action and determines the outcome
6. The player either successfully handles the trap or suffers consequences (e.g., monsters receive debuff for next fight)
7. The player continues exploring the dungeon

### Postconditions
- The trap encounter is resolved based on the player's actions
- The player either successfully avoids the trap or deals with the consequences

---

## UC-12: Handling Treasure Encounters in Dungeon

**Use Case Name:** Handling Treasure Encounters in Dungeon  
**ID:** UC-12  
**Priority:** Low  
**Actor:** Player  
**Description:** The player encounters and collects treasure while exploring the dungeon  
**Trigger:** The player selects a door that leads to treasure  
**Type:** External

### Preconditions
- The player is on the dungeon screen
- The player selects a door that triggers a treasure encounter

### Normal Course
1. The player selects a door on the dungeon screen
2. The game randomly determines that the door leads to a treasure
3. The game displays a treasure encounter screen with details about the treasure
4. The player views the treasure details and collects it:
   - The treasure details include the type of treasure, its value, and any special attributes
   - The player clicks the "Collect Treasure" button to add the treasure to their inventory
5. The game updates the player's inventory with the collected treasure
6. The player continues exploring the dungeon

### Postconditions
- The treasure is added to the player's inventory
- The player can use or manage the treasure at the home base or during dungeon exploration

### Exceptions
- If the player's inventory is full, they must discard an item to make space for the new treasure
- If the player does not collect the treasure, it remains in the dungeon for later collection

---

## UC-13: Player Successfully Escapes the Dungeon

**Use Case Name:** Player Successfully Escapes the Dungeon  
**ID:** UC-13  
**Priority:** Medium  
**Actor:** Player  
**Description:** The player successfully navigates through the dungeon and finds the exit door, allowing them to escape with their treasures and monsters  
**Trigger:** The player selects the exit door in the dungeon  
**Type:** External

### Preconditions
- The player is on the dungeon screen
- The player has found and selected the exit door

### Normal Course
1. The player selects the exit door on the dungeon screen
2. The game confirms the player's intention to exit the dungeon
3. The player confirms their choice to exit
4. The game decides which monsters are upgraded and what upgrades they get (e.g., new abilities, upgraded abilities, increased stats)
5. The game displays a summary of the player's treasures, captured monsters and monster upgrades
6. The player's treasure is added to the home base inventory
7. The player's inventory is moved to the home base inventory
8. The captured monsters are moved to the home base
9. The player and monsters gain XP
10. The game transitions the player back to the home base screen
11. The game prompts the player to save the game

### Postconditions
- The treasure is added to the player's inventory
- The monsters are added to the home base
- The player returns to the home base screen
- The game prompts the player to save the game

### Exceptions
- If the player does not confirm their choice to exit, return the player to the dungeon

---

## UC-14: Player is Defeated in the Dungeon

**Use Case Name:** Player is Defeated in the Dungeon  
**ID:** UC-14  
**Priority:** High  
**Actor:** Player  
**Description:** The player is defeated by monsters in the dungeon, losing their treasures and returning to the home base screen  
**Trigger:** The player's monsters are all defeated in battle  
**Type:** External

### Preconditions
- The player is on the battle screen
- The player's monsters are all defeated

### Normal Course
1. The player's last monster is defeated in battle
2. The game displays a defeat screen, informing the player of their loss
3. The player loses all treasures and captured monsters collected during the dungeon run
4. The game transitions the player back to the home base screen
5. The game prompts the player to save the game

### Postconditions
- The player is returned to the home base screen
- The player loses all treasures and captured monsters collected during the dungeon run
- The game prompts the player to save the game

---

## UC-15: Managing Party Inventory

**Use Case Name:** Managing Party Inventory at Home Base  
**ID:** UC-15  
**Priority:** Low  
**Actor:** Player  
**Description:** The player manages their inventory by transferring items between the home base inventory and the party inventory  
**Trigger:** The player clicks on an item in the home base screen  
**Type:** External

### Preconditions
- The player is on the home base screen

### Normal Course
1. The player clicks an item in either inventory on the home base screen
2. If the item is in the home base inventory, it is moved to the party inventory
3. If the item is in the party inventory, it is moved to the home base inventory
4. The inventories are updated to reflect this change

### Postconditions
- The inventories are updated to reflect the new items

### Exceptions
- If the player tries to move an item to the party inventory when the party inventory is full, the game will prevent the action

---

## UC-16: Evolving a Monster

**Use Case Name:** Evolving a Monster  
**ID:** UC-16  
**Priority:** Medium  
**Actor:** Player  
**Description:** The player evolves a monster by giving it an evolve fruit at the home base screen  
**Trigger:** The player clicks the evolve button on the "Card Management" side of a monster card  
**Type:** External

### Preconditions
- The player is at the home base screen
- The player has a monster that is eligible for evolution
- The player has an evolve fruit in their home base inventory

### Normal Course
1. The player clicks on a monster card on the home base screen opening the "Card Management" side of the monster card
2. The player selects evolve
3. An evolve fruit will be consumed from the home base inventory
4. The monster is evolved and its new card, stats and abilities are shown
5. The player views the evolved monster's details

### Postconditions
- The selected monster evolves into a new form with updated stats and abilities
- The evolve fruit is consumed from the player's inventory

### Exceptions
- If the player does not have an evolve fruit, the evolution process cannot be initiated, and the player is informed of the missing item

---

**Previous:** [Requirements Document](../design/requirements.md) | **Next:** [Gameplay Design](../design/gameplay_design.md)