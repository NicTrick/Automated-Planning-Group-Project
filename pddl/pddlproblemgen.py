import csv
import re
from typing import Dict, Tuple, Set

debug = False

def parse_maze_file(file_path: str):
    # Reads a maze CSV file, extracts all maze objects, and returns:
    #       cells, boxes, zones, keys, doors, soko_coords, adjacencies

    # Attempts to open and read the maze file
    try:
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            map = list(reader)
    except FileNotFoundError: # Occurs if the maze file is not found
        print(f"Maze file not found at {file_path}. Aborting...")
        exit(1)
    
    # If the debug mode is enabled, the maze map is printed
    if debug:
        for row in map:
            print("[DEBUG]", row)
    
    cells = set() # Stores coordinates for all empty cells
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
                    cells.add((x, y))
                
                case "S": # Starting position of Soko
                    soko_coords = (x, y)
                    continue

                case "W" | "W ": # Wall cell which blocks movement
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
    # This time the maze map will include Soko's position, cells, boxes, zones, keys, and doors
    if debug:
        print("Parsed Maze Elements:")
        print("Soko's Position:", soko_coords) # Print the starting position of Soko
 
        print("Cells:")
        print("Total Cells:", len(cells)) # Print the total number of cells
        print(cells)
        
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
    
    # Compute adjacencies for all positions
    # Create a set of all valid positions (cells, boxes, zones, keys, doors, and soko's position)
    all_positions = set(cells)
    all_positions.add(soko_coords)
    all_positions.update(boxes.values())
    all_positions.update(zones.values())
    all_positions.update(keys.values())
    all_positions.update(doors.values())
    
    # Dictionary to store adjacent cells for each position
    adjacencies = dict()
    
    # For each position, find all adjacent valid positions (up, down, left, right)
    for pos in all_positions:
        x, y = pos
        adjacent = []
        
        # Check all four directions
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:  # up, down, left, right
            neighbor = (x + dx, y + dy)
            if neighbor in all_positions:
                adjacent.append(neighbor)
        
        adjacencies[pos] = adjacent
    
    if debug:
        print("\nAdjacencies:")
        for pos, adj in adjacencies.items():
            print(f"\t{pos}: {adj}")
    
    # Return all parsed data
    return cells, boxes, zones, keys, doors, soko_coords, adjacencies


def generate_problem_file(maze_file: str, problem_name: str, output_file: str):
    """Generate a PDDL problem file from a maze CSV file."""
    
    cells, boxes, zones, keys, doors, soko_coords, adjacencies = parse_maze_file(maze_file)
    
    # Start building the PDDL problem file
    pddl_content = []
    pddl_content.append(f"(define (problem {problem_name})")
    pddl_content.append("    (:domain sokodomain)")
    pddl_content.append("")
    
    # Define objects
    pddl_content.append("    (:objects")
    
    # Tiles (all valid positions)
    all_tiles = sorted(cells.union({soko_coords}).union(set(boxes.values())).union(set(zones.values())).union(set(keys.values())).union(set(doors.values())))
    tile_names = {tile: f"tile_{tile[0]}_{tile[1]}" for tile in all_tiles}
    pddl_content.append("        ;; Tiles")
    for tile in all_tiles:
        pddl_content.append(f"        {tile_names[tile]} - tile")
    
    # Agent
    pddl_content.append("        ;; Agent")
    pddl_content.append("        soko - soko")
    
    # Boxes
    if boxes:
        pddl_content.append("        ;; Boxes")
        for box_id in sorted(boxes.keys()):
            pddl_content.append(f"        box{box_id} - box")
    
    # Keys
    if keys:
        pddl_content.append("        ;; Keys")
        for key_id in sorted(keys.keys()):
            pddl_content.append(f"        key{key_id} - key")
    
    # Zones
    if zones:
        pddl_content.append("        ;; Zones")
        for zone_id in sorted(zones.keys()):
            pddl_content.append(f"        zone{zone_id} - zone")
    
    # Doors
    if doors:
        pddl_content.append("        ;; Doors")
        for door_id in sorted(doors.keys()):
            pddl_content.append(f"        door{door_id} - door")
    
    pddl_content.append("    )")
    pddl_content.append("")
    
    # Define initial state
    pddl_content.append("    (:init")
    
    # Soko's position
    pddl_content.append("        ;; Soko's initial position")
    pddl_content.append(f"        (at soko {tile_names[soko_coords]})")
    pddl_content.append("")
    
    # Box positions
    if boxes:
        pddl_content.append("        ;; Box positions")
        for box_id, pos in sorted(boxes.items()):
            pddl_content.append(f"        (boxat box{box_id} {tile_names[pos]})")
        pddl_content.append("")
    
    # Key positions
    if keys:
        pddl_content.append("        ;; Key positions")
        for key_id, pos in sorted(keys.items()):
            pddl_content.append(f"        (keyat key{key_id} {tile_names[pos]})")
        pddl_content.append("")
    
    # Zone positions
    if zones:
        pddl_content.append("        ;; Zone positions")
        for zone_id, pos in sorted(zones.items()):
            pddl_content.append(f"        (zoneat zone{zone_id} {tile_names[pos]})")
        pddl_content.append("")
    
    # Door positions and lock status
    if doors:
        pddl_content.append("        ;; Door positions and lock status")
        for door_id, pos in sorted(doors.items()):
            pddl_content.append(f"        (doorat door{door_id} {tile_names[pos]})")
            pddl_content.append(f"        (doorlocked door{door_id})")
        pddl_content.append("")
    
    # Path adjacencies
    pddl_content.append("        ;; Path adjacencies")
    for pos in sorted(adjacencies.keys()):
        for adjacent_pos in sorted(adjacencies[pos]):
            pddl_content.append(f"        (path {tile_names[pos]} {tile_names[adjacent_pos]})")
    pddl_content.append("")
    
    # Matching relationships (key-door and box-zone)
    if keys and doors:
        pddl_content.append("        ;; Key-Door relationships")
        for key_id in sorted(keys.keys()):
            if key_id in doors:  # Key matches door with same ID
                pddl_content.append(f"        (opens key{key_id} door{key_id})")
        pddl_content.append("")
    
    if boxes and zones:
        pddl_content.append("        ;; Box-Zone relationships")
        for box_id in sorted(boxes.keys()):
            if box_id in zones:  # Box matches zone with same ID
                pddl_content.append(f"        (matches box{box_id} zone{box_id})")
        pddl_content.append("")
    
    pddl_content.append("    )")
    pddl_content.append("")
    
    # Define goal state
    pddl_content.append("    (:goal")
    if boxes and zones:
        pddl_content.append("        (and")
        for box_id in sorted(boxes.keys()):
            if box_id in zones:  # Only require boxes with matching zones
                pddl_content.append(f"            (boxat box{box_id} {tile_names[zones[box_id]]})")
        pddl_content.append("        )")
    else:
        pddl_content.append("        (and)  ;; No goal specified")
    pddl_content.append("    )")
    pddl_content.append(")")
    
    # Write to file
    with open(output_file, 'w') as f:
        f.write('\n'.join(pddl_content))
    
    print(f"Problem file generated: {output_file}")
    return output_file


  
if __name__ == "__main__":
    print("\n\n======= Automated Planning Group Project =======\n")
    
    if input("Enable debug mode? (y/n): ").strip().lower() == "y":
        debug = True
    
    file_path = input("\nPlease enter the path to your maze: ").strip()
    generate_problem_file(file_path, "problem", "problem.pddl")