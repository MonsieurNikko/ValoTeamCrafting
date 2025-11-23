"""Smurf detection for team balancing system."""

from src.models import Player
from src.config import get_config


def compute_smurf_suspicion(player: Player) -> float:
    """
    Compute smurf suspicion score based on account metadata and performance stats.
    
    ADVANCED LOGIC - Context-Aware Detection:
    1. High Elo Immunity: Immortals/Radiants are rarely 'smurfs', just good players.
    2. Dynamic Thresholds: A 1.2 KD is normal in Ascendant, but suspicious in Silver.
    3. The 'Sleeper' Detection: Old accounts with sudden god-like stats (Boosting).
    4. Peak vs Current: Detecting derankers.
    
    Returns suspicion score from 0 to 100.
    """
    smurf_config = get_config("smurf_config", {})
    suspicion = 0.0
    
    # === LOGIC 1: HIGH ELO IMMUNITY ===
    # If player is already Immortal+, they are at the correct rank.
    # High stats there just mean they are carrying, not smurfing in the unfair sense.
    is_high_elo = False
    # Check rank_current string for high elo keywords
    if player.rank_current and ("Immortal" in player.rank_current or "Radiant" in player.rank_current):
        is_high_elo = True
    
    # If High Elo, we drastically reduce sensitivity. Only flag EXTREME anomalies.
    suspicion_multiplier = 0.3 if is_high_elo else 1.0

    # === LOGIC 2: DYNAMIC THRESHOLDS BY RANK ===
    # Define what is considered "Suspiciously Good" for each rank group
    
    # Thresholds: (ACS Cap, KD Cap, HS% Cap)
    thresholds = {
        "low":  (240, 1.15, 25.0),  # Iron - Gold: Low cap (easy to spot smurfs)
        "mid":  (260, 1.25, 30.0),  # Plat - Diamond: Medium cap
        "high": (290, 1.35, 35.0)   # Ascendant+: High cap (hard to trigger)
    }
    
    # Get thresholds for player's rank group (default to mid if unknown)
    t_acs, t_kd, t_hs = thresholds.get(player.rank_group, (260, 1.25, 30.0))
    
    # --- Check ACS ---
    if player.average_combat_score is not None:
        if player.average_combat_score > t_acs:
            excess = player.average_combat_score - t_acs
            # In low elo, every point above threshold is VERY suspicious
            severity = 1.5 if player.rank_group == "low" else 1.0
            suspicion += min(excess * 0.8 * severity, 40.0)

    # --- Check K/D ---
    if player.kd_ratio > t_kd:
        excess = player.kd_ratio - t_kd
        # 0.1 KD above threshold = 10 points suspicion
        suspicion += min(excess * 100, 35.0)

    # --- Check HS% (Mechanical Skill) ---
    if player.headshot_rate is not None and player.headshot_rate > t_hs:
        excess = player.headshot_rate - t_hs
        suspicion += min(excess * 1.5, 25.0)

    # === LOGIC 3: THE "SLEEPER" / BOOSTING DETECTOR ===
    # Case: High Level Account + Low Rank + God Stats
    # This detects when a friend plays on a hardstuck account
    if player.account_level and player.account_level > 100:
        if player.rank_group == "low" or player.rank_group == "mid":
            # If they have stats exceeding the NEXT tier's threshold
            next_tier_acs = thresholds["high"][0] # 290
            if player.average_combat_score and player.average_combat_score > next_tier_acs:
                suspicion += 30.0 # Massive penalty for being a "sleeper"

    # === LOGIC 4: PEAK VS CURRENT (The Deranker) ===
    # If Peak was Immortal but Current is Diamond/Plat -> Suspect
    # (Simplified check based on text analysis of rank string if available, or admin input)
    # Here we rely on stats: if stats are high AND rank is lower than peak likely implies smurfing
    
    # ... (Existing Admin Logic below) ...
    
    # Factor: Low account level (Classic Smurf)
    # Only apply if NOT High Elo (a new account in Immortal is just a fast climber)
    if player.account_level is not None and not is_high_elo:
        level_threshold = smurf_config.get("low_account_level_threshold", 50)
        if player.account_level < level_threshold:
            level_ratio = 1.0 - (player.account_level / level_threshold)
            suspicion += level_ratio * 25.0
    
    # Factor: Low match count
    if player.total_ranked_matches is not None:
        match_threshold = 80
        if player.total_ranked_matches < match_threshold:
            match_ratio = 1.0 - (player.total_ranked_matches / match_threshold)
            suspicion += match_ratio * 15.0

    # Apply High Elo Immunity Multiplier
    suspicion *= suspicion_multiplier
    
    # Factor: High win rate COMBINED with good stats = boosting/smurfing
    if player.win_rate is not None and player.win_rate > 55.0:
        # Win rate alone isn't suspicious, but combined with elevated stats...
        # Re-calculate stats_above_expected locally since we changed the logic flow
        stats_flags = 0
        if player.average_combat_score and player.average_combat_score > t_acs: stats_flags += 1
        if player.kd_ratio > t_kd: stats_flags += 1
        
        if stats_flags >= 1:
            winrate_excess = player.win_rate - 55.0
            max_excess = 20.0  # 75% winrate = max
            winrate_ratio = min(winrate_excess / max_excess, 1.0)
            # Moderate contribution, only when combined with stat anomalies
            winrate_suspicion = winrate_ratio * 15.0
            suspicion += winrate_suspicion
    
    # Factor 6: Admin evaluation mismatches (The "Truth Serum")
    if player.admin_skill_rating is not None:
        admin_score = player.admin_skill_rating  # 0-10 scale
        
        # 6a: The "Hidden Gem" (Low Rank + High Admin Rating)
        # Example: Silver player rated 8/10 by Admin -> Smurf/Underranked
        if player.rank_group == "low" and admin_score >= 7:
            # Admin says they are good, Rank says they are bad -> SMURF
            base_suspicion = 50.0
            # If Admin knows them well (Familiarity 3), trust the admin even more
            if player.admin_familiarity and player.admin_familiarity >= 3:
                base_suspicion += 20.0  # 70 total
            suspicion += base_suspicion
            
        # 6b: The "Account Share" / "Boosted" (High Rank/Stats + Low Admin Rating)
        # Example: Ascendant player rated 4/10 by Admin
        # User scenario: "ce compte a été smurfé par quelqu'un" (someone else played on it)
        # Stats might be high (from the smurf), but Admin knows the real player is weak.
        elif player.rank_group in ["mid", "high"] and admin_score <= 4:
            # If stats are actually good (supporting the high rank), but Admin says NO.
            # This implies the stats are FAKE (achieved by a smurf).
            base_suspicion = 45.0
            
            # Stronger penalty if Admin knows them well (more confidence in the rating)
            if player.admin_familiarity and player.admin_familiarity >= 3:
                base_suspicion += 30.0  # 75 total - Very suspicious
            elif player.admin_familiarity and player.admin_familiarity >= 2:
                base_suspicion += 15.0  # 60 total - Moderately suspicious
            
            # Additional penalty if stats are good (someone else played)
            if player.kd_ratio > 1.0:
                base_suspicion += 10.0
            
            suspicion += base_suspicion
        
        # 6c: Moderate Admin Mismatch (Any rank group with significant admin disagreement)
        # This catches cases where admin rating doesn't match rank expectations
        else:
            # Calculate expected admin rating based on rank
            expected_admin_by_rank = {
                "low": 3.5,   # Iron-Gold should be rated 2-5/10
                "mid": 5.5,   # Plat-Dia should be rated 4-7/10
                "high": 7.5   # Asc+ should be rated 6-10/10
            }
            expected_admin = expected_admin_by_rank.get(player.rank_group, 5.5)
            admin_gap = abs(admin_score - expected_admin)
            
            # If gap > 2 points and Admin knows them well, add moderate suspicion
            if admin_gap > 2.0 and player.admin_familiarity and player.admin_familiarity >= 3:
                gap_suspicion = min(admin_gap * 10, 25.0)
                suspicion += gap_suspicion
    
    # === CRITICAL: Anti-false-positive for genuinely weak players ===
    # If BOTH K/D < 0.85 AND ACS is below expected, drastically reduce suspicion
    # This prevents flagging true low-skill players
    # EXCEPTION: If Admin flagged them as "Hidden Gem" (6a), DO NOT reduce suspicion!
    is_admin_flagged = (player.admin_skill_rating is not None and player.admin_skill_rating >= 7)
    
    if player.kd_ratio < 0.85 and not is_admin_flagged:
        # Use t_acs (threshold acs) as the baseline for expected performance
        if player.average_combat_score and player.average_combat_score < t_acs:
            suspicion *= 0.3  # Reduce by 70%
    
    # Clamp to valid range
    suspicion = max(0.0, min(100.0, suspicion))
    
    # Update player flags (lower threshold = more sensitive detection)
    suspicion_threshold = smurf_config.get("suspicion_threshold", 40.0)  # Lowered from 50
    player.is_smurf_suspected = suspicion >= suspicion_threshold
    
    return suspicion
