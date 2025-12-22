from typing import List, Tuple, Callable, Optional
from collections import deque
import heapq
import time
from state import State, state_key
from maze import Maze
from actions import get_successors, is_goal_state

#Container for search results and statistics.
class SearchResult:
    
    def __init__(self):
        self.plan: List[str] = [] # Sequence of actions forming the solution plan
        self.success: bool = False # Will indicate whether a solution was found
        self.time_taken: float = 0.0 # Time taken for the search to be performed
        self.states_generated: int = 0 # Number of states generated during search
        self.states_expanded: int = 0 # Number of states expanded during search
        self.plan_length: int = 0 # Length of the solution plan
        
# Reconstruct the plan (sequence of actions) from the goal state back to initial state.
def reconstruct_plan(came_from: dict, goal_state: State) -> List[str]:
    plan = []
    current = goal_state
    
    # Backtrack from goal state to start state
    while current in came_from:
        current, action = came_from[current]
        if action:
            plan.append(action)
    
    plan.reverse()
    return plan

# Breadth-First Search - explores all states at depth 'd' before depth 'd+1'. Guarantees optimal solution (shortest plan).
def breadth_first_search(maze: Maze, initial_state: State) -> SearchResult:
    
    result = SearchResult()
    start_time = time.time()
    
    frontier = deque([initial_state]) # Queue of states to be explored
    explored = {state_key(initial_state)} # Set of visited states
    came_from = {} # To reconstruct the plan later
    
    result.states_generated = 1
    
    while frontier:
        current_state = frontier.popleft()
        result.states_expanded += 1
        
        # Check if the current state stisfies the goal condition
        if is_goal_state(maze, current_state):
            result.success = True
            result.plan = reconstruct_plan(came_from, current_state)
            result.plan_length = len(result.plan)
            result.time_taken = time.time() - start_time
            return result
        
        # Generate and process all successor states
        for successor, action in get_successors(maze, current_state):
            successor_key = state_key(successor)
            
            if successor_key not in explored:
                explored.add(successor_key)
                came_from[successor] = (current_state, action)
                frontier.append(successor)
                result.states_generated += 1
    
    result.time_taken = time.time() - start_time
    return result

# Greedy Best-First Search - expands states with lowest heuristic value first. Uses priority queue ordered by h(n).
def greedy_best_first_search(maze: Maze, initial_state: State, heuristic: Callable) -> SearchResult:
    result = SearchResult()
    start_time = time.time()
    
    frontier = [] # Queue of states to be explored
    heapq.heappush(frontier, (heuristic(maze, initial_state), 0, initial_state))
    explored = {state_key(initial_state)} # Set of visited states
    came_from = {} # To reconstruct the plan later
    
    result.states_generated = 1
    counter = 1  # Tie-breaker for heap
    
    while frontier:
        _, _, current_state = heapq.heappop(frontier)
        result.states_expanded += 1
        
        # Check goal condition
        if is_goal_state(maze, current_state):
            result.success = True
            result.plan = reconstruct_plan(came_from, current_state)
            result.plan_length = len(result.plan)
            result.time_taken = time.time() - start_time
            return result
        
        # Expand successors using heuristic ordering
        for successor, action in get_successors(maze, current_state):
            successor_key = state_key(successor)
            
            if successor_key not in explored:
                explored.add(successor_key)
                came_from[successor] = (current_state, action)
                h_value = heuristic(maze, successor)
                heapq.heappush(frontier, (h_value, counter, successor))
                counter += 1
                result.states_generated += 1
    
    result.time_taken = time.time() - start_time
    return result

# A* Search - expands states with lowest f(n) = g(n) + h(n). Guarantees optimal solution if heuristic is admissible.
def a_star_search(maze: Maze, initial_state: State, heuristic: Callable) -> SearchResult:
    result = SearchResult()
    start_time = time.time()
    
    frontier = [] # Queue of states to be explored
    initial_f = initial_state.g + heuristic(maze, initial_state)
    heapq.heappush(frontier, (initial_f, 0, initial_state))
    explored = set() # Set of visited states
    came_from = {} # To reconstruct the plan later
    
    # Keep track of best g-values for each state - The best cost for each state
    g_values = {state_key(initial_state): initial_state.g}
    
    result.states_generated = 1
    counter = 1
    
    while frontier:
        _, _, current_state = heapq.heappop(frontier)
        current_key = state_key(current_state)
        
        # Skip states already expanded
        if current_key in explored:
            continue
        
        explored.add(current_key)
        result.states_expanded += 1
        
        # Check for goal state
        if is_goal_state(maze, current_state):
            result.success = True
            result.plan = reconstruct_plan(came_from, current_state)
            result.plan_length = len(result.plan)
            result.time_taken = time.time() - start_time
            return result
        
        # Expand successors and update costs (g-values)
        for successor, action in get_successors(maze, current_state):
            successor_key = state_key(successor)
            
            if successor_key in explored:
                continue
            
            # Check if this path to successor is better
            if successor_key not in g_values or successor.g < g_values[successor_key]:
                g_values[successor_key] = successor.g
                came_from[successor] = (current_state, action)
                f_value = successor.g + heuristic(maze, successor)
                heapq.heappush(frontier, (f_value, counter, successor))
                counter += 1
                result.states_generated += 1
    
    result.time_taken = time.time() - start_time
    return result

# Enforced Hill Climbing - iteratively improves heuristic value using BFS. Performs BFS until a state with better heuristic is found, then repeats.
def enforced_hill_climbing(maze: Maze, initial_state: State, heuristic: Callable) -> SearchResult:
    result = SearchResult()
    start_time = time.time()
    
    current_state = initial_state
    current_h = heuristic(maze, current_state)
    plan = []
    result.states_generated = 1
    
    while not is_goal_state(maze, current_state):
        # BFS to find state with better heuristic or goal state
        frontier = deque([current_state]) # Queue of states to be explored
        explored = {state_key(current_state)} # Set of visited states
        came_from = {} # To reconstruct the plan later
        found_better = False
        
        # Keep on performing BFS until a better state is found
        while frontier and not found_better:
            state = frontier.popleft()
            result.states_expanded += 1
            
            for successor, action in get_successors(maze, state):
                successor_key = state_key(successor)
                
                if successor_key not in explored:
                    explored.add(successor_key)
                    came_from[successor] = (state, action)
                    result.states_generated += 1
                    
                    # Check if this successor is the goal
                    if is_goal_state(maze, successor):
                        # Reconstruct path from current to goal
                        path_actions = []
                        s = successor
                        
                        while s != current_state and s in came_from:
                            prev_state, prev_action = came_from[s]
                            path_actions.append(prev_action)
                            s = prev_state
                        
                        path_actions.reverse()
                        plan.extend(path_actions)
                        
                        result.success = True
                        result.plan = plan
                        result.plan_length = len(plan)
                        result.time_taken = time.time() - start_time
                        return result
                    
                    successor_h = heuristic(maze, successor)
                    
                    # Found a better state
                    if successor_h < current_h:
                        # Reconstruct path from current to successor
                        path_actions = []
                        s = successor
                        
                        #Reconstruct path to improved state
                        while s != current_state and s in came_from:
                            prev_state, prev_action = came_from[s]
                            path_actions.append(prev_action)
                            s = prev_state
                        
                        path_actions.reverse()
                        plan.extend(path_actions)
                        
                        current_state = successor
                        current_h = successor_h
                        found_better = True
                        break
                    
                    # Only add to frontier if we haven't found a better state yet
                    frontier.append(successor)
        
        # Fail if no better state found
        if not found_better:
            result.time_taken = time.time() - start_time
            return result
    
    result.success = True
    result.plan = plan
    result.plan_length = len(plan)
    result.time_taken = time.time() - start_time
    return result

# Run the specified search algorithm. Dispatches execution to the selected search algorithm with the given parameters.
def run_search(maze: Maze, initial_state: State, algorithm: str, heuristic: Optional[Callable] = None) -> SearchResult:
    algorithm = algorithm.lower()
    
    if algorithm == 'bfs': # Breadth-First Search does not require a heuristic
        return breadth_first_search(maze, initial_state)
    
    elif algorithm == 'greedy': # A* Search requires a heuristic to compute f(n) = g(n) + h(n)
        if not heuristic:
            raise ValueError("Heuristic required for Greedy Best-First Search")
        return greedy_best_first_search(maze, initial_state, heuristic)
    
    elif algorithm == 'astar': # A* Search requires a heuristic to compute f(n) = g(n) + h(n)
        if not heuristic:
            raise ValueError("Heuristic required for A* Search")
        return a_star_search(maze, initial_state, heuristic)
    
    elif algorithm == 'ehc': # Enforced Hill Climbing relies on heuristic improvement
        if not heuristic:
            raise ValueError("Heuristic required for Enforced Hill Climbing")
        return enforced_hill_climbing(maze, initial_state, heuristic)
    
    else: # Fail if an unknown algorithm is requested
        raise ValueError(f"Unknown algorithm: {algorithm}")
