"""
Team generation and balancing algorithms for Valorant tournaments.

This module contains the core team balancing algorithms:
- Hybrid Snake Draft + Local Optimization (recommended)
- Pure Snake Draft
- Fairness calculation
- Player replacement functionality
"""

import random
from typing import Tuple, List

from .models import Player, TeamConfiguration
from .config import get_config


def compute_fairness_score(teams: List[List[Player]]) -> Tuple[float, List[float], float]:
    """
    Compute fairness score for a team configuration.
    
    Lower score = more balanced teams.
    
    Args:
        teams: List of teams, each team is a list of Player objects
    
    Returns:
        Tuple of:
        - fairness_score: sum of squared deviations from average
        - team_total_skills: list of total skill for each team
        - average_team_skill: mean of all team totals
    """
    team_total_skills = []
    
    for team in teams:
        team_total = sum(player.final_skill_score for player in team)
        team_total_skills.append(team_total)
    
    average_team_skill = sum(team_total_skills) / len(team_total_skills)
    
    # Sum of squared deviations
    fairness_score = sum((total - average_team_skill) ** 2 
                        for total in team_total_skills)
    
    return fairness_score, team_total_skills, average_team_skill


def generate_balanced_teams(
    players: List[Player],
    num_teams: int,
    team_size: int,
    num_iterations: int = 5000,
    verbose: bool = True
) -> TeamConfiguration:
    """
    Generate balanced teams using hybrid Snake Draft + Local Optimization.
    
    This hybrid approach:
    1. Snake draft (intelligent base distribution - naturally homogeneous)
    2. Local optimization (light swaps to reduce fairness without polarizing teams)
    
    Args:
        players: List of Player objects with computed final_skill_scores
        num_teams: Number of teams to create
        team_size: Number of players per team
        num_iterations: Number of optimization iterations (default: 5000)
        verbose: Whether to print progress
    
    Returns:
        TeamConfiguration with hybrid balanced team assignment
    
    Raises:
        ValueError: If player count doesn't match num_teams * team_size
    """
    # Validate input
    expected_player_count = num_teams * team_size
    if len(players) != expected_player_count:
        raise ValueError(
            f"Player count mismatch: expected {expected_player_count} "
            f"({num_teams} teams × {team_size} players), got {len(players)}"
        )
    
    if verbose:
        print(f"Generating balanced teams with Hybrid Snake Draft + Optimization...")
        print(f"Configuration: {len(players)} players, {num_teams} teams, {team_size} per team\n")
    
    # Step 1: Start with snake draft (natural homogeneity)
    current_config = generate_balanced_teams_snake(players, num_teams, team_size)
    current_fairness = current_config.fairness_score
    
    if verbose:
        print(f"Initial fairness (snake draft): {current_fairness:.2f}")
    
    best_config = current_config
    best_fairness = current_fairness
    
    # Step 2: Local optimization - only accept swaps that improve fairness
    # AND don't create excessive internal polarization
    max_acceptable_range = get_config("max_acceptable_skill_range", 50.0)
    improvements = 0
    
    for iteration in range(num_iterations):
        # Try a random swap between two teams
        team_idx_1, team_idx_2 = random.sample(range(num_teams), 2)
        player_idx_1 = random.randint(0, team_size - 1)
        player_idx_2 = random.randint(0, team_size - 1)
        
        # Copy current teams
        new_teams = [team.copy() for team in current_config.teams]
        
        # Perform swap
        player_1 = new_teams[team_idx_1][player_idx_1]
        player_2 = new_teams[team_idx_2][player_idx_2]
        
        new_teams[team_idx_1][player_idx_1] = player_2
        new_teams[team_idx_2][player_idx_2] = player_1
        
        # Compute new fairness
        new_fairness, new_team_totals, new_avg_skill = compute_fairness_score(new_teams)
        
        # Check internal ranges for both affected teams
        team1_skills = [p.final_skill_score for p in new_teams[team_idx_1]]
        team2_skills = [p.final_skill_score for p in new_teams[team_idx_2]]
        team1_range = max(team1_skills) - min(team1_skills)
        team2_range = max(team2_skills) - min(team2_skills)
        
        # Accept swap only if:
        # 1. It improves fairness (lower total deviation)
        # 2. It doesn't create excessive polarization in either team
        if (new_fairness < current_fairness and 
            team1_range <= max_acceptable_range and 
            team2_range <= max_acceptable_range):
            
            current_config = TeamConfiguration(
                teams=new_teams,
                fairness_score=new_fairness,
                team_total_skills=new_team_totals,
                average_team_skill=new_avg_skill
            )
            current_fairness = new_fairness
            improvements += 1
            
            # Update best
            if new_fairness < best_fairness:
                best_config = current_config
                best_fairness = new_fairness
        
        # Progress update
        if verbose and (iteration + 1) % 1000 == 0:
            print(f"  Iteration {iteration + 1:,}/{num_iterations:,} - Current: {current_fairness:.2f}, Best: {best_fairness:.2f}, Improvements: {improvements}")
    
    if verbose:
        print(f"\nOptimization complete!")
        print(f"Final fairness: {best_fairness:.2f}")
        print(f"Improvement from snake draft: {current_config.fairness_score - best_fairness:.2f}")
        print(f"Total successful swaps: {improvements}")
    
    return best_config


def generate_balanced_teams_snake(
    players: List[Player],
    num_teams: int,
    team_size: int
) -> TeamConfiguration:
    """
    Generate balanced teams using snake draft algorithm.
    
    Algorithm:
    1. Sort players by final_skill_score in descending order (best to worst)
    2. Assign players in snake pattern:
       - Round 1: Team 1 → 2 → 3 → ... → N
       - Round 2: Team N → ... → 3 → 2 → 1
       - Round 3: Team 1 → 2 → 3 → ... → N
       - Repeat until all players assigned
    
    Args:
        players: List of Player objects with computed final_skill_scores
        num_teams: Number of teams to create
        team_size: Number of players per team
    
    Returns:
        TeamConfiguration with snake draft team assignment
    
    Raises:
        ValueError: If player count doesn't match num_teams * team_size
    """
    # Validate input
    expected_player_count = num_teams * team_size
    if len(players) != expected_player_count:
        raise ValueError(
            f"Player count mismatch: expected {expected_player_count} "
            f"({num_teams} teams × {team_size} players), got {len(players)}"
        )
    
    # Sort players by skill (descending: best first)
    sorted_players = sorted(players, key=lambda p: p.final_skill_score, reverse=True)
    
    # Initialize teams
    teams = [[] for _ in range(num_teams)]
    
    # Snake draft assignment
    player_idx = 0
    for round_num in range(team_size):
        if round_num % 2 == 0:
            # Even rounds: left to right (Team 1 → N)
            for team_idx in range(num_teams):
                teams[team_idx].append(sorted_players[player_idx])
                player_idx += 1
        else:
            # Odd rounds: right to left (Team N → 1)
            for team_idx in range(num_teams - 1, -1, -1):
                teams[team_idx].append(sorted_players[player_idx])
                player_idx += 1
    
    # Compute fairness
    fairness, team_totals, avg_skill = compute_fairness_score(teams)
    
    return TeamConfiguration(
        teams=teams,
        fairness_score=fairness,
        team_total_skills=team_totals,
        average_team_skill=avg_skill
    )


def replace_player_in_team(
    config: TeamConfiguration,
    player_to_replace_name: str,
    replacement_player: Player,
    all_players: List[Player]
) -> TeamConfiguration:
    """
    Replace a player who quit the tournament with a replacement player.
    Keeps the team structure intact, only swaps the player.
    
    Args:
        config: Current team configuration
        player_to_replace_name: Name of the player who is leaving
        replacement_player: The replacement player
        all_players: List of all players (to recompute scores if needed)
    
    Returns:
        Updated TeamConfiguration with the replacement
    
    Raises:
        ValueError: If player_to_replace_name not found in any team
    """
    from .scoring import compute_all_scores
    
    # Compute scores for replacement player if not done
    if replacement_player.final_skill_score == 0:
        compute_all_scores(replacement_player)
    
    # Find which team and position the leaving player is in
    team_index = None
    player_index = None
    
    for t_idx, team in enumerate(config.teams):
        for p_idx, player in enumerate(team):
            if player.player_name == player_to_replace_name:
                team_index = t_idx
                player_index = p_idx
                break
        if team_index is not None:
            break
    
    if team_index is None:
        raise ValueError(f"Player '{player_to_replace_name}' not found in any team")
    
    # Create new teams list with replacement
    new_teams = []
    for t_idx, team in enumerate(config.teams):
        if t_idx == team_index:
            # Replace the player in this team
            new_team = team.copy()
            new_team[player_index] = replacement_player
            new_teams.append(new_team)
        else:
            new_teams.append(team.copy())
    
    # Recalculate team totals
    new_team_totals = [
        sum(player.final_skill_score for player in team)
        for team in new_teams
    ]
    
    # Recalculate fairness
    avg_skill = sum(new_team_totals) / len(new_team_totals)
    new_fairness = sum((total - avg_skill) ** 2 for total in new_team_totals)
    
    # Return updated configuration
    return TeamConfiguration(
        teams=new_teams,
        team_total_skills=new_team_totals,
        fairness_score=new_fairness,
        average_team_skill=avg_skill
    )
