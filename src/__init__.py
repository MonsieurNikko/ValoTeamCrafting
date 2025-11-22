"""
Valorant Tournament Team Balancer

A comprehensive team balancing system that uses:
- Multi-factor player rating (rank, stats, community feedback, smurf detection)
- Hybrid Snake Draft + Local Optimization algorithm
- Fairness metrics with internal team homogeneity constraints

Main modules:
- models: Data structures (Player, TeamConfiguration)
- config: Configuration management
- scoring: Player skill rating calculations
- smurf_detection: 9-factor smurf detection system
- balancing: Team generation algorithms (hybrid, snake draft)
- utils: I/O operations (load/save JSON, text reports)
"""

from .models import Player, TeamConfiguration
from .config import load_config, get_config, CONFIG
from .scoring import (
    get_rank_group,
    compute_rank_score,
    interpolate_score,
    compute_stats_score,
    compute_community_score_and_familiarity,
    compute_engine_score,
    get_familiarity_alpha,
    compute_final_skill_score,
    compute_all_scores
)
from .smurf_detection import compute_smurf_suspicion
from .balancing import (
    compute_fairness_score,
    generate_balanced_teams,
    generate_balanced_teams_snake,
    replace_player_in_team
)
from .utils import (
    load_players_from_json,
    save_teams_to_json,
    save_teams_to_txt_file
)

__all__ = [
    # Data models
    'Player',
    'TeamConfiguration',
    
    # Configuration
    'load_config',
    'get_config',
    'CONFIG',
    
    # Scoring functions
    'get_rank_group',
    'compute_rank_score',
    'interpolate_score',
    'compute_stats_score',
    'compute_community_score_and_familiarity',
    'compute_engine_score',
    'get_familiarity_alpha',
    'compute_final_skill_score',
    'compute_all_scores',
    
    # Smurf detection
    'compute_smurf_suspicion',
    
    # Team balancing
    'compute_fairness_score',
    'generate_balanced_teams',
    'generate_balanced_teams_snake',
    'replace_player_in_team',
    
    # I/O utilities
    'load_players_from_json',
    'save_teams_to_json',
    'save_teams_to_txt_file',
]

__version__ = '2.0.0'
__author__ = 'Team Balancer'
