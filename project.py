import csv
import re

debug = False

def main():
    print("=== Soku Solver Group Project ===")
    
    if input("Enable debug mode? (y/n):").strip().lower() == "y":
        global debug
        debug = True
    
    file_path = input("Please enter the path to your maze:").strip()
    
    print("""
    Available Search Strategies:
        1. Breadth-First Search
        2. Greedy Best-First Search
        3. A* Search
        4. Enforced Hill Climb
    """)
    algo_input = input("Enter the number corresponding to your choice:").strip()
    
    print("""
    Available Heuristics:
        1. a
        2. b
    """)
    heuristic_input = input("Enter the number corresponding to your choice:").strip()
    
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        map = list(reader)
        
    if debug:
        for row in map:
            print(row)
    
    # Initialize dicts for maze elements
    # Storing coordinates of boxes, zones, keys, doors, and Soku's position
    boxes = dict()
    zones = dict()
    keys = dict()
    doors = dict()
    soku_coords = dict()
    
    for y in range(len(map)):
        for x in range(len(map[y])):
            object = map[y][x]
            
            match object:
                case " " | "W" | "W ":
                    continue
                
                case "S":
                    soku_coords = {'x': x, 'y': y}
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
        

if __name__ == "__main__":
    main()