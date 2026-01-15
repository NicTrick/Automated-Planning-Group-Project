from typing import List, Tuple, Optional
from state import State
from maze import Maze

# Check if Soko can move to a position (no wall, no locked door).
def can_move_to(maze: Maze, state: State, new_pos: Tuple[int, int]) -> bool:
    from maze import is_wall, in_bounds, door_id_at
    
    if not in_bounds(maze, new_pos):
        return False
    
    if is_wall(maze, new_pos):
        return False
    
    # Check if there's a locked door
    door_id = door_id_at(maze, new_pos)
    if door_id and door_id not in state.keys_owned:
        return False
    
    return True

# Move Soko to a new position.
def move_soko(state: State, new_pos: Tuple[int, int], action_name: str) -> State:
    return State(
        soko_pos=new_pos,
        carried_box=state.carried_box,
        box_positions=state.box_positions,
        keys_owned=state.keys_owned,
        keys_on_floor=state.keys_on_floor,
        g=state.g + 1
    )

# Take a key that's on the floor at Soko's location.
def take_key(state: State, key_id: str) -> State:
    # Remove the key from the floor
    new_keys_on_floor = tuple(
        (k_id, pos) for k_id, pos in state.keys_on_floor if k_id != key_id
    )
    
    # Add key to owned keys
    new_keys_owned = state.keys_owned | {key_id}
    
    return State(
        soko_pos=state.soko_pos,
        carried_box=state.carried_box,
        box_positions=state.box_positions,
        keys_owned=new_keys_owned,
        keys_on_floor=new_keys_on_floor,
        g=state.g + 1
    )

# Lift a box at Soko's location.
def lift_box(state: State, box_id: str) -> State:
    return State(
        soko_pos=state.soko_pos,
        carried_box=box_id,
        box_positions=state.box_positions,
        keys_owned=state.keys_owned,
        keys_on_floor=state.keys_on_floor,
        g=state.g + 1
    )

# Drop a box at its designated drop zone
def drop_box(state: State, box_id: str, zone_pos: Tuple[int, int]) -> State:
    # Update box position to zone position
    new_box_positions = tuple(
        (b_id, zone_pos if b_id == box_id else pos)
        for b_id, pos in state.box_positions
    )
    
    return State(
        soko_pos=state.soko_pos,
        carried_box=None,
        box_positions=new_box_positions,
        keys_owned=state.keys_owned,
        keys_on_floor=state.keys_on_floor,
        g=state.g + 1
    )

# Generate all valid successor states and their corresponding actions. Returns a list of tuples (new_state, action_name)
def get_successors(maze: Maze, state: State) -> List[Tuple[State, str]]:
    successors = []
    x, y = state.soko_pos
    
    # Movement actions (Left, Right, Up, Down)
    movement_actions = [
        ((x - 1, y), "Left"),
        ((x + 1, y), "Right"),
        ((x, y - 1), "Up"),
        ((x, y + 1), "Down")
    ]
    
    # The for loop that makes the movements occur
    for new_pos, action_name in movement_actions:
        if can_move_to(maze, state, new_pos):
            new_state = move_soko(state, new_pos, action_name)
            successors.append((new_state, action_name))
    
    # Take Key action
    for key_id, key_pos in state.keys_on_floor:
        if key_pos == state.soko_pos:
            new_state = take_key(state, key_id)
            successors.append((new_state, f"Take Key {key_id}"))
    
    # Lift Box action
    if state.carried_box is None:  # Not currently carrying
        for box_id, box_pos in state.box_positions:
            if box_pos == state.soko_pos:
                new_state = lift_box(state, box_id)
                successors.append((new_state, f"Lift Box {box_id}"))
    
    # Drop Box action
    if state.carried_box is not None:
        box_id = state.carried_box
        # Find the drop zone for this box
        zone_pos = maze.zones.get(box_id)
        if zone_pos and state.soko_pos == zone_pos:
            new_state = drop_box(state, box_id, zone_pos)
            successors.append((new_state, f"Drop Box {box_id}"))
    
    return successors

# Check if the state is a goal state (all boxes at their zones).
def is_goal_state(maze: Maze, state: State) -> bool:
    for box_id, box_pos in state.box_positions:
        zone_pos = maze.zones.get(box_id)
        if zone_pos != box_pos:
            return False
    
    return True