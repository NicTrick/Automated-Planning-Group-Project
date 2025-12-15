from maze import Maze, parse_maze_file
from state import State, state_key, boxes_dict, keys_floor_dict

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
    
    # Reading file and parsing maze
    maze, initial_state = parse_maze_file(file_path, debug)
    
    if debug:
        print("Parsed Elements:")
        print(f"Walls: {len(maze.walls)}")

        print("Maze:")
        print(maze)

        print("Initial State:")
        print(initial_state)

    # Placeholder for Running the search algorithm
          

if __name__ == "__main__":
    main()