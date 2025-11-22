"""Models for Valorant team balancing system."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Player:
    """Represents a player with all rating components."""
    # Identity
    player_id: str
    player_name: str
    
    # Rank data
    rank_current: str  # e.g., "Gold 2"
    rank_peak_recent: str  # Peak in last 2-3 acts
    
    # Stats data (from tracker.gg)
    kd_ratio: float
    average_combat_score: Optional[float] = None  # Can be None if not available
    win_rate: Optional[float] = None              # Win percentage (0-100), e.g., 55.5
    headshot_rate: Optional[float] = None         # Headshot % (0-100), e.g., 22.3
    
    # Admin rating (single admin evaluation)
    admin_skill_rating: Optional[int] = None  # 1-10 scale (10 = best player in server)
    admin_familiarity: Optional[int] = None   # 1-3 scale (1=barely know, 2=some games, 3=know well)
    
    # Account metadata (for smurf detection)
    account_level: Optional[int] = None             # Account level (1-500+)
    total_ranked_matches: Optional[int] = None      # Total ranked games played
    ranked_matches_last_30_days: Optional[int] = None  # Recent activity (optional)
    
    # Computed scores (filled by rating functions)
    rank_score: float = 0.0
    stats_score: float = 0.0
    community_score: float = 0.0
    familiarity_score: float = 0.0
    engine_score: float = 0.0
    final_skill_score: float = 0.0
    
    # Smurf detection
    smurf_suspicion_score: float = 0.0  # 0-100, higher = more suspicious
    is_smurf_suspected: bool = False    # True if suspicion > threshold
    
    # Metadata
    rank_group: str = ""  # "low", "mid", or "high"


@dataclass
class TeamConfiguration:
    """Represents a team assignment configuration."""
    teams: list[list[Player]]  # List of teams, each team is list of players
    fairness_score: float
    team_total_skills: list[float]  # Total skill for each team
    average_team_skill: float
