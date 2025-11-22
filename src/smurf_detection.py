"""Smurf detection for team balancing system."""

from src.models import Player
from src.config import get_config


def compute_smurf_suspicion(player: Player) -> float:
    """
    Compute smurf suspicion score based on account metadata and performance stats.
    
    Nine factors contribute to suspicion:
    1. Low account level
    2. Low number of ranked matches
    3. KD ratio significantly higher than expected for rank
    4. High win rate (for new accounts)
    5. High headshot percentage
    6. Admin evaluation mismatches (4 sub-criteria):
       6a. High familiarity + High skill + Low rank
       6b. Admin skill >> Stats score (holding back)
       6c. Low familiarity + High skill + New account
       6d. Admin skill >> Expected for rank group
    
    Returns suspicion score from 0 to 100.
    """
    smurf_config = get_config("smurf_config", {})
    suspicion = 0.0
    
    # Factor 1: Low account level (low level = suspicious)
    if player.account_level is not None:
        level_threshold = smurf_config.get("low_account_level_threshold", 50)
        if player.account_level < level_threshold:
            level_ratio = 1.0 - (player.account_level / level_threshold)
            level_suspicion = level_ratio * smurf_config.get("max_suspicion_from_level", 40.0)
            suspicion += level_suspicion
    
    # Factor 2: Low match count (few matches = less reliable data)
    if player.total_ranked_matches is not None:
        match_threshold = smurf_config.get("low_match_count_threshold", 80)
        if player.total_ranked_matches < match_threshold:
            match_ratio = 1.0 - (player.total_ranked_matches / match_threshold)
            match_suspicion = match_ratio * smurf_config.get("max_suspicion_from_matches", 25.0)
            suspicion += match_suspicion
    
    # Factor 3: Abnormally high KD for rank group
    high_kd_thresholds = smurf_config.get("high_kd_thresholds", {})
    kd_threshold = high_kd_thresholds.get(player.rank_group, 1.40)
    if player.kd_ratio > kd_threshold:
        kd_excess = player.kd_ratio - kd_threshold
        max_excess = 0.7
        kd_ratio = min(kd_excess / max_excess, 1.0)
        kd_suspicion = kd_ratio * smurf_config.get("max_suspicion_from_kd", 25.0)
        suspicion += kd_suspicion
    
    # Factor 4: High win rate (especially on new accounts)
    if player.win_rate is not None:
        winrate_threshold = smurf_config.get("high_winrate_threshold", 60.0)
        if player.win_rate > winrate_threshold:
            winrate_excess = player.win_rate - winrate_threshold
            max_excess = 25.0  # 85% winrate = max suspicion
            winrate_ratio = min(winrate_excess / max_excess, 1.0)
            winrate_suspicion = winrate_ratio * smurf_config.get("max_suspicion_from_winrate", 15.0)
            suspicion += winrate_suspicion
    
    # Factor 5: High headshot percentage for rank group
    if player.headshot_rate is not None:
        high_hs_thresholds = smurf_config.get("high_headshot_thresholds", {})
        hs_threshold = high_hs_thresholds.get(player.rank_group, 28.0)
        if player.headshot_rate > hs_threshold:
            hs_excess = player.headshot_rate - hs_threshold
            max_excess = 15.0  # HS% threshold + 15% = max suspicion
            hs_ratio = min(hs_excess / max_excess, 1.0)
            hs_suspicion = hs_ratio * smurf_config.get("max_suspicion_from_headshot", 15.0)
            suspicion += hs_suspicion
    
    # Factor 6: Admin evaluation mismatches (4 sub-criteria)
    if player.admin_skill_rating is not None:
        
        # 6a: High familiarity + High skill + Low rank (friend's smurf account)
        if (player.admin_familiarity is not None and 
            player.admin_familiarity >= 2 and 
            player.admin_skill_rating >= 7 and 
            player.rank_score < 50):  # Below Platinum 3
            gap = (player.admin_skill_rating * 10) - player.rank_score
            admin_rank_gap_suspicion = min(gap / 2, smurf_config.get("max_suspicion_from_admin_rank_gap", 20.0))
            suspicion += admin_rank_gap_suspicion
        
        # 6b: Admin skill >> Stats score (player holding back intentionally)
        if player.admin_skill_rating >= 7:
            admin_expected_stats = player.admin_skill_rating * 10
            stats_gap = admin_expected_stats - player.stats_score
            if stats_gap > 20:
                admin_stats_gap_suspicion = min(stats_gap / 3, smurf_config.get("max_suspicion_from_admin_stats_gap", 15.0))
                suspicion += admin_stats_gap_suspicion
        
        # 6c: Low familiarity + High skill + New account (impressed admin quickly)
        if (player.admin_familiarity is not None and 
            player.admin_familiarity <= 1 and 
            player.admin_skill_rating >= 7):
            is_new_account = (
                (player.account_level is not None and player.account_level < 60) or
                (player.total_ranked_matches is not None and player.total_ranked_matches < 100)
            )
            if is_new_account:
                intensity = (player.admin_skill_rating - 6) * (2 - player.admin_familiarity)
                unfamiliar_new_suspicion = min(intensity * 3, smurf_config.get("max_suspicion_from_unfamiliar_new", 18.0))
                suspicion += unfamiliar_new_suspicion
        
        # 6d: Admin skill >> Expected community score for rank group
        expected_community_by_group = smurf_config.get("expected_community_by_rank_group", {
            "low": 35, "mid": 55, "high": 75
        })
        expected = expected_community_by_group.get(player.rank_group, 50)
        admin_score = player.admin_skill_rating * 10
        
        if admin_score > expected + 25:
            rank_group_gap_suspicion = min((admin_score - expected) / 3, smurf_config.get("max_suspicion_from_rank_group_gap", 15.0))
            suspicion += rank_group_gap_suspicion
    
    # Anti-false-positive: If KD is low (<0.9), reduce suspicion by 50%
    # This prevents flagging true beginners with low level/matches but poor stats
    if player.kd_ratio < 0.9:
        suspicion *= 0.5
    
    # Clamp to valid range
    suspicion = max(0.0, min(100.0, suspicion))
    
    # Update player flags
    suspicion_threshold = smurf_config.get("suspicion_threshold", 50.0)
    player.is_smurf_suspected = suspicion >= suspicion_threshold
    
    return suspicion
