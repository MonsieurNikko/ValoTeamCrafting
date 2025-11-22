"""
Input/Output utilities for the team balancer.

Handles loading player data from JSON, saving team configurations to JSON/text files.
"""

import json
from typing import List

from .models import Player, TeamConfiguration


def load_players_from_json(filepath: str) -> List[Player]:
    """
    Load players from a JSON file.
    
    Expected JSON format:
    {
        "players": [
            {
                "player_id": "player001",
                "player_name": "PlayerName",
                "rank_current": "Gold 2",
                "rank_peak_recent": "Platinum 1",
                "kd_ratio": 1.15,
                "average_combat_score": 205,         // optional
                "win_rate": 52.5,                    // optional, win % (0-100)
                "headshot_rate": 24.8,               // optional, headshot % (0-100)
                "admin_skill_rating": 6,             // optional, 1-10 scale
                "admin_familiarity": 3,              // optional, 1-3 scale
                "account_level": 50,                 // optional, for smurf detection
                "total_ranked_matches": 120,         // optional, for smurf detection
                "ranked_matches_last_30_days": 35    // optional, for smurf detection
            },
            ...
        ]
    }
    
    Args:
        filepath: Path to JSON file containing player data
    
    Returns:
        List of Player objects
    
    Raises:
        FileNotFoundError: If filepath doesn't exist
        json.JSONDecodeError: If JSON is malformed
        KeyError: If required fields are missing
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Support both formats: {"players": [...]} and [...]
    if isinstance(data, dict) and 'players' in data:
        player_list = data['players']
    elif isinstance(data, list):
        player_list = data
    else:
        raise ValueError("Invalid JSON format: expected {'players': [...]} or [...]")
    
    players = []
    for idx, p_data in enumerate(player_list):
        player = Player(
            player_id=p_data.get('player_id', f'player{idx+1:03d}'),
            player_name=p_data['player_name'],
            rank_current=p_data['rank_current'],
            rank_peak_recent=p_data['rank_peak_recent'],
            kd_ratio=p_data['kd_ratio'],
            average_combat_score=p_data.get('average_combat_score'),
            win_rate=p_data.get('win_rate'),
            headshot_rate=p_data.get('headshot_rate'),
            admin_skill_rating=p_data.get('admin_skill_rating'),
            admin_familiarity=p_data.get('admin_familiarity'),
            account_level=p_data.get('account_level'),
            total_ranked_matches=p_data.get('total_ranked_matches'),
            ranked_matches_last_30_days=p_data.get('ranked_matches_last_30_days')
        )
        players.append(player)
    
    return players


def save_teams_to_json(config: TeamConfiguration, filepath: str) -> None:
    """
    Save team configuration to a JSON file.
    
    Output format:
    {
        "fairness_score": 1.23,
        "average_team_skill": 65.4,
        "teams": [
            {
                "team_number": 1,
                "total_skill": 327.5,
                "players": [
                    {
                        "player_id": "player001",
                        "player_name": "PlayerName",
                        "rank_current": "Gold 2",
                        "final_skill_score": 65.2
                    },
                    ...
                ]
            },
            ...
        ]
    }
    
    Args:
        config: TeamConfiguration object with teams and stats
        filepath: Path where JSON file will be saved
    """
    output = {
        "fairness_score": config.fairness_score,
        "average_team_skill": config.average_team_skill,
        "teams": []
    }
    
    for i, team in enumerate(config.teams, 1):
        team_data = {
            "team_number": i,
            "total_skill": config.team_total_skills[i-1],
            "players": [
                {
                    "player_id": p.player_id,
                    "player_name": p.player_name,
                    "rank_current": p.rank_current,
                    "final_skill_score": p.final_skill_score
                }
                for p in team
            ]
        }
        output["teams"].append(team_data)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)


def save_teams_to_txt_file(config: TeamConfiguration, output_file: str) -> None:
    """
    Save team configuration to a human-readable text file with detailed stats.
    
    Creates a formatted table showing:
    - Team balancing statistics (fairness, average skill, deviation)
    - Player details (rank, KD, ACS, stats, scores, smurf flags)
    - Team-by-team breakdown
    
    Args:
        config: TeamConfiguration object with teams and stats
        output_file: Path where text file will be saved
    """
    def shorten_rank(rank: str) -> str:
        """Shorten rank names for better alignment."""
        replacements = {
            'Ascendant': 'Asc',
            'Immortal': 'Imm',
            'Diamond': 'Dia',
            'Platinum': 'Plat',
            'Bronze': 'Brz',
            'Silver': 'Slv',
            'Radiant': 'Rad'
        }
        for full, short in replacements.items():
            rank = rank.replace(full, short)
        return rank
    
    num_teams = len(config.teams)
    team_size = len(config.teams[0]) if config.teams else 0
    total_players = sum(len(team) for team in config.teams)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("VALORANT TOURNAMENT - BALANCED TEAMS\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"Number of Teams: {num_teams}\n")
        f.write(f"Team Size: {team_size}\n")
        f.write(f"Total Players: {total_players}\n")
        f.write(f"Average Team Skill: {config.average_team_skill:.2f}\n")
        f.write(f"Fairness Score (lower = better): {config.fairness_score:.2f}\n\n")
        
        # Team details
        for i, team in enumerate(config.teams, 1):
            team_total = config.team_total_skills[i-1]
            deviation = team_total - config.average_team_skill
            
            f.write("="*158 + "\n")
            f.write(f"\nTeam {i} (Total Skill: {team_total:.2f}, Deviation: {deviation:+.2f})\n")
            f.write("=" * 158 + "\n")
            f.write(f"{'Player':20s} | {'Rank (Cur->Peak)':22s} | {'KD':>5s} | {'ACS':>4s} | {'WR%':>5s} | {'HS%':>5s} | {'Lvl':>4s} | {'Mat':>4s} | {'R':>4s} | {'S':>4s} | {'C':>4s} | {'Smurf':>6s} | {'Final':>5s}\n")
            f.write("-" * 158 + "\n")
            
            for player in team:
                rank_display = f"{shorten_rank(player.rank_current)}->{shorten_rank(player.rank_peak_recent)}"
                acs_display = f"{player.average_combat_score:4.0f}" if player.average_combat_score is not None else "  --"
                wr_display = f"{player.win_rate:5.1f}" if player.win_rate is not None else "   --"
                hs_display = f"{player.headshot_rate:5.1f}" if player.headshot_rate is not None else "   --"
                lvl_display = f"{player.account_level:4d}" if player.account_level is not None else "  --"
                mts_display = f"{player.total_ranked_matches:4d}" if player.total_ranked_matches is not None else "  --"
                smurf_display = f"{player.smurf_suspicion_score:5.0f}{'!' if player.is_smurf_suspected else ' '}"
                
                f.write(f"{player.player_name:20s} | {rank_display:22s} | {player.kd_ratio:5.2f} | {acs_display:>4s} | {wr_display:>5s} | {hs_display:>5s} | {lvl_display:>4s} | {mts_display:>4s} | {player.rank_score:4.0f} | {player.stats_score:4.0f} | {player.community_score:4.0f} | {smurf_display:>6s} | {player.final_skill_score:5.1f}\n")
        
        f.write("\n" + "="*80 + "\n")
