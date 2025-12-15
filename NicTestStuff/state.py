from dataclasses import dataclass
from typing import Dict, Tuple, FrozenSet, Optional, List

@dataclass(frozen=True)
class State:
    robot_pos: Tuple[int, int]
    carried_box: Optional[str]
    box_positions: Tuple[Tuple[str, Tuple[int, int]], ...]
    keys_owned: FrozenSet[str]
    keys_on_floor: Tuple[Tuple[str, Tuple[int, int]], ...]
    g: int = 0  # Cost to reach this state / of path

def state_key(state: State):
    """
    Returns a key representing the state for use in explored sets. (Duplicate Avoidance)
    """
    return (
        state.robot_pos,
        state.carried_box,
        state.box_positions,
        state.keys_owned,
        state.keys_on_floor
    )

def make_initial_state(
    robot_pos: Tuple[int, int],
    boxes: Dict[str, Tuple[int, int]],
    keys: Dict[str, Tuple[int, int]]
) -> State:
    """
    Constructs the initial state from parsed maze data.
    """

    return State(
        robot_pos=robot_pos,
        carried_box=None,
        box_positions=tuple(sorted(boxes.items())),
        keys_owned=frozenset(),
        keys_on_floor=tuple(sorted(keys.items())),
        g=0
    )


def boxes_dict(state: State) -> Dict[str, Tuple[int, int]]:
    """
    Returns a dictionary view of box positions for algorithms if needed.
    """
    return dict(state.box_positions)


def keys_floor_dict(state: State) -> Dict[str, Tuple[int, int]]:
    """
    Returns a dictionary view of keys on the floor for algorithms if needed.
    """
    return dict(state.keys_on_floor)