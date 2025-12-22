import csv
import re
from dataclasses import dataclass
from typing import Dict, Tuple, FrozenSet
from state import State, make_initial_state

@dataclass(frozen=True)
class Maze:
    width: int # Number of columns in the maze grid
    height: int # Number of rows in the maze grid
    walls: FrozenSet[Tuple[int, int]] # Set of coordinates representing wall positions
    zones: Dict[str, Tuple[int, int]] # Mapping of drop zone IDs (ex: 'A', 'B') to their coordinates
    doors: Dict[str, Tuple[int, int]] # Mapping of door IDs (ex: '1', '2') to their coordinates
    
    
def parse_maze_file(file_path: str, debug: bool = False) -> Tuple[Maze, State]:
    # Reads a maze CSV file, extracts all maze objects, and returns a Maze object and the initial State.

    # Attempts to open and read the maze file
    try:
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            map = list(reader)
    except FileNotFoundError: # Occurs if the mze file is not found
        print(f"Maze file not found at {file_path}. Aborting...")
        exit(1)
    
    # If the debug mode is enabled, the maze map is printed
    if debug:
        for row in map:
            print(row)
    
    walls = set() # Stores coordinates for all wall cells
    boxes = dict() # Maps box IDs to their initial positions
    zones = dict() # Maps dop zone IDs to their positions
    keys = dict() # Maps key IDs to their positions
    doors = dict() # Maps door IDs to their positions
    soko_coords = tuple() # Stores the starting position of Soko
    
    # Iterates through each cell in the maze map to identify and store maze objects
    for y in range(len(map)):
        for x in range(len(map[y])):
            object = map[y][x]
            
            match object:
                case " ": # An empty cell that Soko can go to
                    continue
                
                case "S": # Starting position of Soko
                    soko_coords = (x, y)
                    continue

                case "W" | "W ": # Wall cell which blocks movement
                    walls.add((x, y))
                    continue
                
                case _: # Other objects (boxes, zones, keys, doors)
                    if re.match(r'^B-[A-Z]$', object):
                        boxes[object[2]] = (x, y) # Store box with its ID and coordinates
                        
                    elif re.match(r'^Z-[A-Z]$', object):
                        zones[object[2]] = (x, y) # Store drop zone locations
                        
                    elif re.match(r'^K-[0-9]$', object):
                        keys[object[2:]] = (x, y) # Store keys that open matching doors (Respective of number)
                        
                    elif re.match(r'^D-[0-9]$', object):
                        doors[object[2:]] = (x, y) # Door which can be opened by matching key (Respective of number)

                    else: # Invalid maze object
                        raise ValueError("Invalid format " + object + " detected in maze file.")
                    continue
    
    # If debug mode is enabled, the parsed maze elements will be printed
    # This time the maze map will include Soko's position, walls, boxes, zones, keys, and doors
    if debug:
        print("Parsed Maze Elements:")
        print("Soko's Position:", soko_coords) # Print the starting position of Soko
 
        print("Walls:")
        print("Total Walls:", len(walls)) # Print the total number of walls
        print(walls)
        
        print("Boxes:")
        for dictionary in boxes.items():
            print("\t", dictionary) # Print each box ID and its position
        
        print("Zones:")
        for dictionary in zones.items():
            print("\t", dictionary) # Print each zone ID and its position
        
        print("Keys:")
        for dictionary in keys.items():
            print("\t", dictionary) # Print each key ID and its position
        
        print("Doors:")
        for dictionary in doors.items():
            print("\t", dictionary) # Print each door ID and its position

    # Create the Maze object from the parsed data
    maze = Maze(
        width=len(map[0]),
        height=len(map),
        walls=frozenset(walls),
        zones=zones,
        doors=doors
    )
    # Create the initial State object representing all dynamic elements
    initial_state = make_initial_state(
        soko_pos=soko_coords,
        boxes=boxes,
        keys=keys
    )

    return maze, initial_state

# Utility functions for state expansion

# Returns True if the position is a wall.
def is_wall(maze: Maze, pos: tuple[int, int]) -> bool:
    return pos in maze.walls

# Returns True if the position contains a door (regardless of lock state).
def is_door(maze: Maze, pos: tuple[int, int]) -> bool:
    # Returns True if the position contains a door (regardless of lock state).
    return pos in maze.doors.values()

# Returns the door ID at a position, or None if no door is present.
def door_id_at(maze: Maze, pos: tuple[int, int]) -> str | None:
    for door_id, door_pos in maze.doors.items():
        if door_pos == pos:
            return door_id
    return None

# Returns True if position is inside the maze boundaries.
def in_bounds(maze: Maze, pos: tuple[int, int]) -> bool:
    x, y = pos
    return 0 <= x < maze.width and 0 <= y < maze.height
