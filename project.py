from maze import Maze, parse_maze_file
from state import State, state_key, boxes_dict, keys_floor_dict
from search import run_search
from heuristics import heuristic_manhattan, heuristic_euclidean
from actions import is_goal_state, get_successors
import os

debug = False


def clear_screen():
    """Clear the terminal screen."""
    os.system('clear' if os.name != 'nt' else 'cls')


def validate_plan(maze: Maze, initial_state: State, plan: list) -> bool:
    """
    Validates the plan by executing it step-by-step from initial state.
    Returns True if plan reaches goal state.
    """
    current_state = initial_state
    
    print("\n=== Plan Validation ===")
    print(f"Executing {len(plan)} actions...")
    
    for i, action in enumerate(plan):
        if debug:
            print(f"Step {i+1}: {action}")
        
        # Get all possible successors from current state
        successors = get_successors(maze, current_state)
        
        # Find the successor that matches this action
        next_state = None
        for successor, succ_action in successors:
            if succ_action == action:
                next_state = successor
                break
        
        if next_state is None:
            print(f"ERROR: Action '{action}' is not applicable in current state!")
            return False
        
        current_state = next_state
    
    # Check if final state is goal
    if is_goal_state(maze, current_state):
        print("Plan successfully reaches goal state!")
        return True
    else:
        print("Plan does not reach goal state!")
        return False


def visualize_maze(maze: Maze, state: State):
    """
    Displays the current state of the maze in 2D.
    """
    clear_screen()
    
    # Create grid
    grid = [[' ' for _ in range(maze.width)] for _ in range(maze.height)]
    
    # Add walls
    for x, y in maze.walls:
        if 0 <= y < maze.height and 0 <= x < maze.width:
            grid[y][x] = '█'
    
    # Add zones
    for zone_id, zone_pos in maze.zones.items():
        x, y = zone_pos
        if 0 <= y < maze.height and 0 <= x < maze.width:
            grid[y][x] = f'Z{zone_id}'
    
    # Add doors
    for door_id, door_pos in maze.doors.items():
        x, y = door_pos
        if 0 <= y < maze.height and 0 <= x < maze.width:
            grid[y][x] = f'D{door_id}'
    
    # Add keys on floor
    keys_dict = keys_floor_dict(state)
    for key_id, key_pos in keys_dict.items():
        x, y = key_pos
        if 0 <= y < maze.height and 0 <= x < maze.width:
            grid[y][x] = f'K{key_id}'
    
    # Add boxes
    boxes = boxes_dict(state)
    for box_id, box_pos in boxes.items():
        x, y = box_pos
        if (x, y) == state.robot_pos and state.carried_box == box_id:
            continue  # Robot is carrying this box
        if 0 <= y < maze.height and 0 <= x < maze.width:
            grid[y][x] = f'B{box_id}'
    
    # Add robot
    rx, ry = state.robot_pos
    if 0 <= ry < maze.height and 0 <= rx < maze.width:
        if state.carried_box:
            grid[ry][rx] = f'S+{state.carried_box}'
        else:
            grid[ry][rx] = 'S'
    
    # Print grid
    print("+" + "-" * (maze.width * 4) + "+")
    for row in grid:
        print("|" + "".join(f"{cell:^4}" for cell in row) + "|")
    print("+" + "-" * (maze.width * 4) + "+")
    print()


def execute_plan_with_visualization(maze: Maze, initial_state: State, plan: list):
    """
    Visualizes the maze and steps through the plan execution.
    """
    current_state = initial_state
    
    print("\n=== Plan Execution Visualization ===")
    print("Initial State:")
    visualize_maze(maze, current_state)
    input("Press Enter to start execution...")
    
    for i, action in enumerate(plan):
        clear_screen()
        print(f"\nStep {i+1}/{len(plan)}: {action}\n")
        
        # Get next state
        successors = get_successors(maze, current_state)
        for successor, succ_action in successors:
            if succ_action == action:
                current_state = successor
                break
        
        visualize_maze(maze, current_state)
        input("Press Enter for next step...")
    
    print("\n✓ Plan execution complete!")


def main():
    print("=== Soku Solver Group Project ===")
    
    if input("Enable debug mode? (y/n): ").strip().lower() == "y":
        global debug
        debug = True
    
    file_path = input("Please enter the path to your maze: ").strip()
    
    print("""
    Available Search Strategies:
        1. Breadth-First Search
        2. Greedy Best-First Search
        3. A* Search
        4. Enforced Hill Climb
    """)
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
        print("Invalid algorithm choice!")
        return
    
    # Get heuristic if needed
    heuristic = None
    if algorithm in ["greedy", "astar", "ehc"]:
        print("""
    Available Heuristics:
        1. Manhattan Distance (Admissible)
        2. Euclidean Distance (Non-admissible, faster)
    """)
        heuristic_input = input("Enter the number corresponding to your choice: ").strip()
        
        heuristic_map = {
            "1": heuristic_manhattan,
            "2": heuristic_euclidean,
            "a": heuristic_manhattan,
            "b": heuristic_euclidean
        }
        
        heuristic = heuristic_map.get(heuristic_input)
        if not heuristic:
            print("Invalid heuristic choice!")
            return
    
    # Parse maze
    print("\nParsing maze...")
    maze, initial_state = parse_maze_file(file_path, debug)
    
    if debug:
        print("\nParsed Elements:")
        print(f"Walls: {len(maze.walls)}")
        print(f"Zones: {maze.zones}")
        print(f"Doors: {maze.doors}")
        print("\nInitial State:")
        print(f"Robot: {initial_state.robot_pos}")
        print(f"Boxes: {boxes_dict(initial_state)}")
        print(f"Keys on floor: {keys_floor_dict(initial_state)}")
    
    # Run search
    algo_names = {
        "bfs": "Breadth-First Search",
        "greedy": "Greedy Best-First Search",
        "astar": "A* Search",
        "ehc": "Enforced Hill Climbing"
    }
    print(f"\nRunning {algo_names[algorithm]}...")
    result = run_search(maze, initial_state, algorithm, heuristic)
    
    # Display results
    print("\n" + "="*50)
    print("SEARCH RESULTS")
    print("="*50)
    print(f"Algorithm: {algo_names[algorithm]}")
    if heuristic:
        heuristic_name = "Manhattan Distance" if heuristic == heuristic_manhattan else "Euclidean Distance"
        print(f"Heuristic: {heuristic_name}")
    print(f"Time taken: {result.time_taken:.4f} seconds")
    print(f"States generated: {result.states_generated}")
    print(f"States expanded: {result.states_expanded}")
    
    if result.success and result.plan:
        print(f"Plan length: {len(result.plan)} steps")
        print(f"\nPlan:")
        for i, action in enumerate(result.plan, 1):
            print(f"  {i}. {action}")
        
        # Validate plan
        is_valid = validate_plan(maze, initial_state, result.plan)
        print(f"\nPlan valid: {'✓ Yes' if is_valid else '✗ No'}")
        
        # Visualize
        if input("\nVisualize plan execution? (y/n): ").strip().lower() == "y":
            execute_plan_with_visualization(maze, initial_state, result.plan)
    else:
        print("✗ No solution found!")
    
    print("\n" + "="*50)


if __name__ == "__main__":
    main()