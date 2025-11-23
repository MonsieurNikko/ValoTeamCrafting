"""Player scoring system for team balancing."""

from src.models import Player
from src.config import get_config
from src.smurf_detection import compute_smurf_suspicion


def get_rank_group(rank: str) -> str:
    """
    Determine which rank group a player belongs to (low/mid/high).
    Used for stats normalization.
    """
    # Handle RR (Radiant Rating) format: "300RR" or "34RR"
    if "RR" in rank:
        try:
            rr_value = int(rank.replace("RR", "").strip())
            # All RR players are high elo (Immortal/Radiant)
            # RR range: 0-99 = Immortal 1, 100-199 = Immortal 2, 200-299 = Immortal 3, 300+ = Radiant
            if rr_value >= 300:
                return "high"  # Radiant
            elif rr_value >= 200:
                return "high"  # Immortal 3
            elif rr_value >= 100:
                return "high"  # Immortal 2
            else:
                return "high"  # Immortal 1
        except ValueError:
            pass
    
    rank_groups = get_config("rank_groups", {})
    for group_name, ranks in rank_groups.items():
        if rank in ranks:
            return group_name
    # Default to mid if rank not found
    return "mid"


def compute_rank_score(player: Player) -> float:
    """
    Compute rank score from current rank and recent peak rank.
    Returns score in range 0-100.
    
    Formula: rank_score = 0.6 * current + 0.4 * peak
    """
    rank_mapping = get_config("rank_score_mapping", {})
    
    # Handle RR (Radiant Rating) format: "300RR" or "34RR"
    def parse_rank_to_score(rank_str: str) -> int:
        # Check if it's RR format (e.g., "300RR", "34RR")
        if "RR" in rank_str:
            try:
                rr_value = int(rank_str.replace("RR", "").strip())
                # RR players are high Immortal/Radiant
                # 0-99 RR = Immortal 1, 100-199 = Immortal 2, 200-299 = Immortal 3, 300+ = Radiant
                if rr_value >= 300:
                    return rank_mapping.get("Radiant", 98)
                elif rr_value >= 200:
                    return rank_mapping.get("Immortal 3", 92)
                elif rr_value >= 100:
                    return rank_mapping.get("Immortal 2", 86)
                else:
                    return rank_mapping.get("Immortal 1", 80)
            except ValueError:
                pass
        
        # Normal rank string (e.g., "Ascendant 2")
        return rank_mapping.get(rank_str, 50)
    
    current_score = parse_rank_to_score(player.rank_current)
    peak_score = parse_rank_to_score(player.rank_peak_recent)
    
    rank_weights = get_config("rank_weights", {"current": 0.6, "peak": 0.4})
    rank_score = (rank_weights["current"] * current_score + 
                  rank_weights["peak"] * peak_score)
    
    return rank_score


def interpolate_score(value: float, thresholds: list[tuple[float, float]]) -> float:
    """
    Linear interpolation between threshold points.
    
    Args:
        value: The value to score (e.g., KD ratio or ACS)
        thresholds: List of (threshold_value, score) tuples, sorted ascending
    
    Returns:
        Interpolated score in range 0-100
    """
    if value <= thresholds[0][0]:
        return thresholds[0][1]
    if value >= thresholds[-1][0]:
        return thresholds[-1][1]
    
    for i in range(len(thresholds) - 1):
        lower_threshold, lower_score = thresholds[i]
        upper_threshold, upper_score = thresholds[i + 1]
        
        if lower_threshold <= value <= upper_threshold:
            ratio = (value - lower_threshold) / (upper_threshold - lower_threshold)
            score = lower_score + ratio * (upper_score - lower_score)
            return score
    
    return 50


def compute_stats_score(player: Player) -> float:
    """
    Compute stats score from KD and ACS, normalized by rank group.
    Returns score in range 0-100.
    
    Formula: stats_score = 0.6 * kd_score + 0.4 * acs_score
    If ACS missing: stats_score = kd_score
    """
    rank_group = player.rank_group
    
    # Compute KD score
    kd_thresholds_map = get_config("kd_thresholds", {})
    kd_thresholds = kd_thresholds_map.get(rank_group, kd_thresholds_map.get("mid", []))
    
    if not kd_thresholds:
        kd_score = 50.0
    else:
        kd_score = interpolate_score(player.kd_ratio, kd_thresholds)
    
    stats_weights = get_config("stats_weights", {"kd": 0.6, "acs": 0.4})

    # Compute ACS score if available
    if player.average_combat_score is not None:
        acs_thresholds_map = get_config("acs_thresholds", {})
        acs_thresholds = acs_thresholds_map.get(rank_group, acs_thresholds_map.get("mid", []))
        
        if not acs_thresholds:
            acs_score = 50.0
        else:
            acs_score = interpolate_score(player.average_combat_score, acs_thresholds)
            
        stats_score = stats_weights["kd"] * kd_score + stats_weights["acs"] * acs_score
    else:
        # No ACS data: use KD only
        stats_score = kd_score
    
    return stats_score


def compute_community_score_and_familiarity(player: Player) -> tuple[float, float]:
    """
    Compute community score and familiarity score from admin rating.
    
    Returns:
        (community_score, familiarity_score) tuple
        - community_score: 0-100 (skill rating * 10)
        - familiarity_score: 0-1 (familiarity / 3)
    
    If no admin rating exists, returns defaults.
    """
    defaults = get_config("defaults", {})
    default_community = defaults.get("community_score", 50)
    default_familiarity = defaults.get("familiarity_score", 0.0)

    if player.admin_skill_rating is None or player.admin_familiarity is None:
        return default_community, default_familiarity
    
    # Scale skill rating from 1-10 to 10-100
    community_score = player.admin_skill_rating * 10
    
    # Scale familiarity from 1-3 to 0.33-1.0
    familiarity_score = player.admin_familiarity / 3.0
    
    return community_score, familiarity_score


def compute_engine_score(player: Player) -> float:
    """
    Compute engine score (combination of rank + stats) with clamp.
    Returns score in range 0-100.
    
    Formula: engine_score = 0.6 * rank_score + 0.4 * stats_score
    Then apply clamp to prevent unrealistic inflation from stats.
    
    The clamp is dynamically adjusted based on smurf suspicion:
    - High suspicion → tighter clamp (stats can't push score as high above rank)
    - Low suspicion → normal clamp
    """
    engine_weights = get_config("engine_weights", {"rank": 0.6, "stats": 0.4})
    base_engine_score = (engine_weights["rank"] * player.rank_score + 
                         engine_weights["stats"] * player.stats_score)
    
    # Get base clamp offset for rank group
    clamp_offsets = get_config("engine_clamp_max_offset", {})
    base_offset = clamp_offsets.get(player.rank_group, 15)
    
    # Apply smurf suspicion penalty to clamp
    suspicion_factor = player.smurf_suspicion_score / 100.0
    smurf_config = get_config("smurf_config", {})
    penalty_factor = smurf_config.get("smurf_penalty_factor", 0.7)
    effective_offset = base_offset * (1.0 - penalty_factor * suspicion_factor)
    
    # Apply the dynamic clamp
    max_allowed_engine_score = player.rank_score + effective_offset
    engine_score = min(base_engine_score, max_allowed_engine_score)
    
    return engine_score


def get_familiarity_alpha(familiarity_score: float) -> float:
    """
    Get alpha value for blending community and engine scores based on familiarity.
    
    Returns alpha where:
        final_skill = community + alpha * (engine - community)
    
    High familiarity → low alpha → trust community more
    Low familiarity → high alpha → trust engine more
    """
    alpha_thresholds = get_config("familiarity_alpha_thresholds", [])
    for threshold, alpha in alpha_thresholds:
        if familiarity_score >= threshold:
            return alpha
    return 1.0


def compute_final_skill_score(player: Player) -> float:
    """
    Compute final skill score by blending community and engine scores
    based on familiarity.
    
    Formula: final = community + alpha(familiarity) * (engine - community)
    """
    alpha = get_familiarity_alpha(player.familiarity_score)
    
    final_score = (player.community_score + 
                   alpha * (player.engine_score - player.community_score))
    
    # Ensure score stays in valid range
    final_score = max(0, min(100, final_score))
    
    return final_score


def compute_all_scores(player: Player) -> None:
    """
    Compute all rating components for a player and update the Player object.
    This is the main entry point for rating a player.
    """
    # Step 1: Determine rank group (needed for stats normalization)
    player.rank_group = get_rank_group(player.rank_current)
    
    # Step 2: Compute individual components
    player.rank_score = compute_rank_score(player)
    player.stats_score = compute_stats_score(player)
    player.community_score, player.familiarity_score = compute_community_score_and_familiarity(player)
    
    # Step 3: Compute smurf suspicion (must be done before engine score)
    player.smurf_suspicion_score = compute_smurf_suspicion(player)
    
    # Step 4: Compute engine score (rank + stats with dynamic clamp based on suspicion)
    player.engine_score = compute_engine_score(player)
    
    # Step 5: Compute final blended score
    player.final_skill_score = compute_final_skill_score(player)
