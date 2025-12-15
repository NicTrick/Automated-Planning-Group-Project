import csv
import re
from dataclasses import dataclass
from typing import Dict, Tuple, FrozenSet
from state import State, make_initial_state

@dataclass(frozen=True)
class Maze:
    width: int
    height: int
    walls: FrozenSet[Tuple[int, int]]
    zones: Dict[str, Tuple[int, int]]
    doors: Dict[str, Tuple[int, int]]

def parse_maze_file(file_path: str, debug: bool = False) -> Tuple[Maze, State]:
    """
    The original code to parse the maze file has been moved here.
    Now uses the Maze class and initialises it whilst also creating the initial State.

    Returns a Maze object and the initial State.
    Use it as follows:
    maze, initial_state = parse_maze_file(file_path, debug)
    """
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        map = list(reader)
        
    if debug:
        for row in map:
            print(row)
    
    # Initialize dicts for maze elements
    # Storing coordinates of walls, boxes, zones, keys, doors, and Soku's position
    walls = set()
    boxes = dict()
    zones = dict()
    keys = dict()
    doors = dict()
    soku_coords = tuple()
    
    for y in range(len(map)):
        for x in range(len(map[y])):
            object = map[y][x]
            
            match object:
                case " ":
                    continue
                
                case "S":
                    soku_coords = (x, y)
                    continue

                case "W" | "W ":
                    walls.add((x, y))
                    continue
                
                case _:
                    if re.match(r'^B-[A-Z]$', object):
                        boxes[object[2]] = {'x': x, 'y': y}
                        
                    elif re.match(r'^Z-[A-Z]$', object):
                        zones[object[2]] = {'x': x, 'y': y}
                        
                    elif re.match(r'^K-[0-9]$', object):
                        keys[object[2:]] = {'x': x, 'y': y}
                        
                    elif re.match(r'^D-[0-9]$', object):
                        doors[object[2:]] = {'x': x, 'y': y}

                    else:
                        raise ValueError("Invalid format " + object + " detected in maze file.")
                    continue
    
    if debug:
        print("Parsed Maze Elements:")
        print("Soku's Position:", soku_coords)

        print("Walls:")
        print("Total Walls:", len(walls))
        print(walls)
        
        print("Boxes:")
        for dictionary in boxes.items():
            print("\t", dictionary)
        
        print("Zones:")
        for dictionary in zones.items():
            print("\t", dictionary)
        
        print("Keys:")
        for dictionary in keys.items():
            print("\t", dictionary)
        
        print("Doors:")
        for dictionary in doors.items():
            print("\t", dictionary)

    maze = Maze(
        width=len(map[0]),
        height=len(map),
        walls=frozenset(walls),
        zones=zones,
        doors=doors
    )

    initial_state = make_initial_state(
        robot_pos=soku_coords,
        boxes=boxes,
        keys=keys
    )

    return maze, initial_state

# Utility functions for state expansion

def is_wall(maze: Maze, pos: tuple[int, int]) -> bool:
    """
    Returns True if the position is a wall.
    """
    return pos in maze.walls


def is_door(maze: Maze, pos: tuple[int, int]) -> bool:
    """
    Returns True if the position contains a door (regardless of lock state).
    """
    return pos in maze.doors.values()

# Further utility functions given by ChatGPT

def door_id_at(maze: Maze, pos: tuple[int, int]) -> str | None:
    """
    Returns the door ID at a position, or None if no door is present.
    """
    for door_id, door_pos in maze.doors.items():
        if door_pos == pos:
            return door_id
    return None


def in_bounds(maze: Maze, pos: tuple[int, int]) -> bool:
    """
    Returns True if position is inside the maze boundaries.
    """
    x, y = pos
    return 0 <= x < maze.width and 0 <= y < maze.height
