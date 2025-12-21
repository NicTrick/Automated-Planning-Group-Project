"""
Heuristic functions for the Soko Solver.
Provides Manhattan and Euclidean distance-based heuristics.
"""

import math
from typing import Tuple
from state import State, boxes_dict
from maze import Maze


def manhattan_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
    """Calculate Manhattan distance between two positions."""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def euclidean_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
    """Calculate Euclidean distance between two positions."""
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)


def heuristic_manhattan(maze: Maze, state: State) -> int:
    """
    Manhattan Distance Heuristic (Heuristic 1)
    
    Estimates cost to goal using Manhattan distances.
    Considers:
    - If carrying a box: distance to its drop zone
    - If not carrying: distance to nearest misplaced box + box-to-zone distances
    - Penalty for doors that require keys we don't have
    
    Properties:
    - Admissible: Never overestimates (Manhattan is admissible for grid movement)
    - Informative: Considers current carrying state and all misplaced boxes
    """
    total_cost = 0
    robot_pos = state.robot_pos
    box_positions = boxes_dict(state)
    
    # If robot is carrying a box, prioritize dropping it
    if state.carried_box:
        box_id = state.carried_box
        zone_pos = maze.zones.get(box_id)
        if zone_pos:
            # Distance from robot to drop zone
            total_cost += manhattan_distance(robot_pos, zone_pos)
    else:
        # Not carrying - need to get boxes to zones
        misplaced_boxes = []
        
        for box_id, box_pos in box_positions.items():
            zone_pos = maze.zones.get(box_id)
            if zone_pos and box_pos != zone_pos:
                misplaced_boxes.append((box_id, box_pos, zone_pos))
        
        if misplaced_boxes:
            # Distance to nearest misplaced box
            min_robot_to_box = min(
                manhattan_distance(robot_pos, box_pos) 
                for _, box_pos, _ in misplaced_boxes
            )
            total_cost += min_robot_to_box
            
            # Sum of box-to-zone distances for all misplaced boxes
            for _, box_pos, zone_pos in misplaced_boxes:
                total_cost += manhattan_distance(box_pos, zone_pos)
    
    # Penalty for locked doors (keys we don't have)
    # Simple penalty: add extra cost if we need keys we don't own
    keys_needed = set(maze.doors.keys()) - state.keys_owned
    if keys_needed:
        # Small penalty per missing key (conservative to maintain admissibility)
        total_cost += len(keys_needed)
    
    return total_cost


def heuristic_euclidean(maze: Maze, state: State) -> float:
    """
    Euclidean Distance Heuristic (Heuristic 2)
    
    Estimates cost to goal using Euclidean distances.
    Considers:
    - If carrying a box: direct distance to its drop zone
    - If not carrying: distance to nearest misplaced box + box-to-zone distances
    - Weighted penalties for missing keys and doors
    
    Properties:
    - NOT admissible: Euclidean distance can underestimate grid path length
    - More optimistic than Manhattan: May find solutions faster but not guaranteed optimal
    - Better for Greedy search where admissibility isn't required
    """
    total_cost = 0.0
    robot_pos = state.robot_pos
    box_positions = boxes_dict(state)
    
    # If robot is carrying a box, prioritize dropping it
    if state.carried_box:
        box_id = state.carried_box
        zone_pos = maze.zones.get(box_id)
        if zone_pos:
            # Euclidean distance from robot to drop zone
            total_cost += euclidean_distance(robot_pos, zone_pos)
    else:
        # Not carrying - need to get boxes to zones
        misplaced_boxes = []
        
        for box_id, box_pos in box_positions.items():
            zone_pos = maze.zones.get(box_id)
            if zone_pos and box_pos != zone_pos:
                misplaced_boxes.append((box_id, box_pos, zone_pos))
        
        if misplaced_boxes:
            # Euclidean distance to nearest misplaced box
            min_robot_to_box = min(
                euclidean_distance(robot_pos, box_pos) 
                for _, box_pos, _ in misplaced_boxes
            )
            total_cost += min_robot_to_box
            
            # Sum of box-to-zone Euclidean distances
            for _, box_pos, zone_pos in misplaced_boxes:
                total_cost += euclidean_distance(box_pos, zone_pos)
    
    # Penalty for locked doors and missing keys
    keys_on_floor_count = len(state.keys_on_floor)
    keys_needed = set(maze.doors.keys()) - state.keys_owned
    
    if keys_needed:
        # Weighted penalty: consider both missing keys and keys still on floor
        total_cost += len(keys_needed) * 1.5
        
        # Additional penalty if keys are still on the floor
        if keys_on_floor_count > 0:
            total_cost += keys_on_floor_count * 0.5
    
    return total_cost


def get_heuristic(heuristic_name: str):
    """
    Get a heuristic function by name.
    
    Args:
        heuristic_name: 'manhattan' or 'euclidean'
    
    Returns:
        The corresponding heuristic function
    """
    heuristics = {
        'manhattan': heuristic_manhattan,
        'euclidean': heuristic_euclidean,
        '1': heuristic_manhattan,
        '2': heuristic_euclidean,
        'a': heuristic_manhattan,
        'b': heuristic_euclidean
    }
    
    name = heuristic_name.lower().strip()
    if name not in heuristics:
        raise ValueError(f"Unknown heuristic: {heuristic_name}. Choose 'manhattan' or 'euclidean'")
    
    return heuristics[name]
