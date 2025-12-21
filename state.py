from dataclasses import dataclass
from typing import Dict, Tuple, FrozenSet, Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from maze import Maze

# State representation for the planning problem.
@dataclass(frozen=True)
class State:
    soko_pos: Tuple[int, int]
    carried_box: Optional[str]
    box_positions: Tuple[Tuple[str, Tuple[int, int]], ...]
    keys_owned: FrozenSet[str]
    keys_on_floor: Tuple[Tuple[str, Tuple[int, int]], ...]
    g: int = 0  # Cost to reach this state / of path

# Returns a key representing the state for use in explored sets. (Duplicate Avoidance)
def state_key(state: State):
    return (
        state.soko_pos,
        state.carried_box,
        state.box_positions,
        state.keys_owned,
        state.keys_on_floor
    )

# Constructs the initial state from parsed maze data.
def make_initial_state(
    soko_pos: Tuple[int, int],
    boxes: Dict[str, Tuple[int, int]],
    keys: Dict[str, Tuple[int, int]]
) -> State:
    
    return State(
        soko_pos=soko_pos,
        carried_box=None,
        box_positions=tuple(sorted(boxes.items())),
        keys_owned=frozenset(),
        keys_on_floor=tuple(sorted(keys.items())),
        g=0
    )

# Returns a dictionary view of box positions for algorithms if needed.
def boxes_dict(state: State) -> Dict[str, Tuple[int, int]]:
    return dict(state.box_positions)

# Returns a dictionary view of keys on the floor for algorithms if needed.
def keys_floor_dict(state: State) -> Dict[str, Tuple[int, int]]:
    return dict(state.keys_on_floor)

# Goal State - Checking if the positions of the boxes equals the position of the drop zones
# Returns True if all boxes are in their designated drop zones.
def is_goal_state(state: State, maze: "Maze") -> bool:
    # If soko is still carrying a box, goal is not satisfied
    if state.carried_box is not None:
        return False

    boxes = boxes_dict(state)

    for box_id, box_pos in boxes.items():
        # Every box must have a corresponding zone
        if box_id not in maze.zones:
            return False

        # Box must be exactly at its drop zone
        if maze.zones[box_id] != box_pos:
            return False

    return True