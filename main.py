from maze import Maze, parse_maze_file
from state import State, state_key, boxes_dict, keys_floor_dict
from search import run_search
from heuristics import heuristic_manhattan, heuristic_euclidean
from actions import is_goal_state, get_successors
import os

debug = False

# Clears terminal screen
def clear_screen():
    os.system('clear' if os.name != 'nt' else 'cls')
    
# Clears the last line in terminal
def clear_line():
    print('\033[2K\r', end='', flush=True)
    
# Prints debug messages
def print_debug(message: str):
    if debug:
        print("\t[DEBUG]", message)


def validate_plan(maze: Maze, initial_state: State, plan: list) -> bool:
    current_state = initial_state
    
    print("\n======= Plan Validation =======")
    print(f"Executing {len(plan)} actions...")
    
    for i, action in enumerate(plan):
        print_debug(f"Step {i+1}: {action}")
        
        # Get all possible successors from current state
        successors = get_successors(maze, current_state)
        
        # Find the successor that matches this action
        next_state = None
        for successor, successor_action in successors:
            if successor_action == action:
                next_state = successor
                break
        
        # No valid successor found for this action
        if next_state is None:
            print_debug(f"ERROR: Action '{action}' is not applicable in current state!")
            return False
        
        # Increment to next state
        current_state = next_state
    
    # Check if final state is goal
    if is_goal_state(maze, current_state):
        print("Plan successfully reaches goal state!")
        return True
    else:
        print("Plan does not reach goal state!")
        return False

# Make a visualized representation of the maze and current states
def visualize_maze(maze: Maze, state: State):
    
    # Create grid
    grid = [[' ' for _ in range(maze.width)] for _ in range(maze.height)]
    
    # Add walls
    for x, y in maze.walls:
        grid[y][x] = '█'
    
    # Add zones
    for zone_id, zone_pos in maze.zones.items():
        x, y = zone_pos
        grid[y][x] = f'[Z{zone_id}]'
            
    
    # Add doors
    for door_id, door_pos in maze.doors.items():
        x, y = door_pos
        grid[y][x] = f'|D{door_id}|'
    
    # Add keys on floor
    keys_dict = keys_floor_dict(state)
    for key_id, key_pos in keys_dict.items():
        x, y = key_pos
        grid[y][x] = f'[K{key_id}]'
    
    # Add boxes
    boxes = boxes_dict(state)
    for box_id, box_pos in boxes.items():
        x, y = box_pos
        
        # Check if Soko is carrying this box
        if ((x, y) == state.soko_pos) and (state.carried_box == box_id):
            continue
        
        grid[y][x] = f'[B{box_id}]'
    
    # Add Soko
    rx, ry = state.soko_pos
    if state.carried_box: # Check if Soko is carrying a box
        grid[ry][rx] = f'SO-{state.carried_box}'
    else: # Soko is not carrying a box
        grid[ry][rx] = 'SOKO'
    
    # Print grid
    for row in grid:
        formatted_row = ""
        for cell in row:
            if cell == '█':
                formatted_row += '████'  # Wall takes full 4 chars
            else:
                formatted_row += f"{cell:^4}"
        print(formatted_row)
    
    inventory = "\n======= INVENTORY ======="
    if state.keys_owned:
        inventory += "\n\n    Keys: [" + ", ".join(sorted(state.keys_owned)) + "]  "
    else:
        inventory += "\n\n    Keys: []"
    
    if state.carried_box:
        inventory += f"\n    Carrying: Box {state.carried_box}"
    else:
        inventory += "\n    Carrying:"
    
    print(inventory)

# Shows a step-by-step visualization of the plan execution
def execute_plan_with_visualization(maze: Maze, initial_state: State, plan: list):
    current_state = initial_state
    
    for i, action in enumerate(plan):
        clear_screen()
        print("======= Plan Execution Visualization =======\n")
        
        # Get next state
        successors = get_successors(maze, current_state)
        for successor, succ_action in successors:
            if succ_action == action:
                current_state = successor
                break
        visualize_maze(maze, current_state)
        
        print(f"\nStep {i+1}/{len(plan)}: {action}")
        input("Press Enter for next step...\n")
    
    print("\nPlan execution complete!")

# Main fucntion to run the program
def main():
    print
    print("\n\n======= Automated Planning Group Project =======\n")
    
    if input("Enable debug mode? (y/n): ").strip().lower() == "y":
        global debug
        debug = True
    
    file_path = input("\nPlease enter the path to your maze: ").strip()
    
    # User selects search algorithm to use
    print("Available Search Strategies:")
    print("\t1. Breadth-First Search")
    print("\t2. Greedy Best-First Search")
    print("\t3. A* Search")
    print("\t4. Enforced Hill Climb")
    algo_input = input("Enter the number corresponding to your choice: ").strip()
    
    # Map algorithm choice
    algo_map = {
        "1": "bfs",
        "2": "greedy",
        "3": "astar",
        "4": "ehc"
    }
    
    algorithm = algo_map.get(algo_input)
    if not algorithm:
        print("Invalid choice!")
        return
    
    # Get heuristic if needed
    heuristic = None
    if algorithm in ["greedy", "astar", "ehc"]:
        print("Available Heuristics:") # Heuristic choices for search algorithms
        print("\t1. Manhattan Distance (Admissible)")
        print("\t2. Euclidean Distance (Non-admissible, faster)")
        heuristic_input = input("Enter the number corresponding to your choice: ").strip()
        
        heuristic_map = { # Map heuristic choice
            "1": heuristic_manhattan,
            "2": heuristic_euclidean
        }
        
        heuristic = heuristic_map.get(heuristic_input)
        if not heuristic:
            print("Invalid choice!")
            return
    
    # Parse maze
    print("\nParsing maze...", end='')
    maze, initial_state = parse_maze_file(file_path, debug)
    
    print_debug("\nParsed Elements:")
    print_debug(f"Walls: {len(maze.walls)}") # Number of walls
    print_debug(f"Zones: {maze.zones}") # Zones in the maze
    print_debug(f"Doors: {maze.doors}") # Doors in the maze
    print_debug("\nInitial State:") # Initial state details
    print_debug(f"Soko: {initial_state.soko_pos}") # Soko's initial position
    print_debug(f"Boxes: {boxes_dict(initial_state)}") # Boxes' initial positions
    print_debug(f"Keys on floor: {keys_floor_dict(initial_state)}") # Keys on the floor
    
    clear_line()
    print("Parsed maze.")
    
    # Run search
    algo_names = {
        "bfs": "Breadth-First Search",
        "greedy": "Greedy Best-First Search",
        "astar": "A* Search",
        "ehc": "Enforced Hill Climbing"
    }
    
    print(f"Executing {algo_names[algorithm]}...", end='')
    result = run_search(maze, initial_state, algorithm, heuristic)
    clear_line()
    print(f"Executed {algo_names[algorithm]}.")
    
    #Outputting the results of the search
    print("\n======= SEARCH RESULTS =======")
    print(f"Algorithm: {algo_names[algorithm]}") # Algorithm used
    print(f"Heuristic: {"Manhattan Distance" if heuristic == heuristic_manhattan else "Euclidean Distance"}") # Heuristic used
    print(f"Time taken: {result.time_taken:.4f} seconds") # Time taken for search
    print(f"States generated: {result.states_generated}") # States generated during search
    print(f"States expanded: {result.states_expanded}") # States expanded during search
    
    if result.success and result.plan:
        print(f"Plan length: {len(result.plan)} steps") # Length of the plan found
        
        print_debug(f"\nPlan:")
        for i, action in enumerate(result.plan, 1):
            print_debug(f"{i}. {action}")
        
        # Check if the plan is valid
        is_valid = validate_plan(maze, initial_state, result.plan)
        print(f"Plan valid: {'YES' if is_valid else 'NOPE'}")
        
        # Ask the user if they want to visualize the plan execution
        if input("\nVisualize plan execution? (y/n): ").strip().lower() == "y":
            execute_plan_with_visualization(maze, initial_state, result.plan)
    else:
        print("No solution found!")

# Run the main function
if __name__ == "__main__":
    main()