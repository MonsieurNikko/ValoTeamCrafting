# Source Code Architecture

This directory contains the core modules of the Valorant Team Balancer system.

## Module Overview

### `models.py`
Data structures for the system:
- `Player`: Dataclass containing all player attributes (rank, stats, scores, flags)
- `TeamConfiguration`: Dataclass for team assignment results

### `config.py`
Configuration management:
- `load_config(filepath)`: Load JSON configuration file
- `get_config(key, default)`: Safe access to config values
- `CONFIG`: Global configuration dictionary

### `scoring.py`
Player skill rating calculations:
- `get_rank_group(rank)`: Categorize ranks (low/mid/high)
- `compute_rank_score(player)`: Blend current (60%) + peak (40%) rank
- `interpolate_score(value, thresholds)`: Linear interpolation for stats
- `compute_stats_score(player)`: KD (60%) + ACS (40%), rank-normalized
- `compute_community_score_and_familiarity(player)`: Admin ratings processing
- `compute_engine_score(player)`: Rank + stats with smurf adjustment
- `get_familiarity_alpha(familiarity)`: Compute blending coefficient
- `compute_final_skill_score(player)`: Final blend of community/engine scores
- `compute_all_scores(player)`: **Main entry point** - orchestrates all calculations

### `smurf_detection.py`
9-factor smurf detection system:
- `compute_smurf_suspicion(player)`: Returns 0-100 suspicion score
  - 5 stats-based factors (low level, low matches, high KD/WR/HS%)
  - 4 admin-based factors (skill/familiarity/rank/stats mismatches)
  - Sets `player.is_smurf_suspected` flag (>= 60% threshold)

### `balancing.py`
Team generation algorithms:
- `compute_fairness_score(teams)`: Calculate team balance metric (lower = better)
- `generate_balanced_teams(...)`: **Hybrid algorithm** (Snake Draft + local optimization)
  - Phase 1: Snake draft for base distribution
  - Phase 2: 5000 iterations of constrained optimization
  - Constraint: max_acceptable_skill_range = 50.0 (prevents polarization)
- `generate_balanced_teams_snake(...)`: Pure snake draft (no optimization)
- `replace_player_in_team(...)`: Replace a quitting player

### `utils.py`
Input/Output operations:
- `load_players_from_json(filepath)`: Parse player data from JSON
- `save_teams_to_json(config, filepath)`: Save results as JSON
- `save_teams_to_txt_file(config, filepath)`: Generate human-readable report

### `__init__.py`
Module exports for clean imports:
```python
from src import Player, generate_balanced_teams, load_config
```

## Algorithm Flow

1. **Load Configuration**: `load_config('data/config.json')`
2. **Load Players**: `load_players_from_json('data/players.json')`
3. **Compute Scores**: For each player, call `compute_all_scores(player)`
   - Rank score (current 60% + peak 40%)
   - Stats score (KD 60% + ACS 40%, rank-normalized)
   - Community score (admin ratings with familiarity weighting)
   - Smurf detection (9 factors, suspicion 0-100)
   - Engine score (rank + stats, smurf-adjusted clamp)
   - Final score (blend community/engine based on familiarity)
4. **Generate Teams**: `generate_balanced_teams(players, num_teams, team_size, iterations)`
   - Snake draft: Sort by skill, distribute 1-2-3-4-5-6-6-5-4-3-2-1...
   - Local optimization: Greedy swaps with range constraint (max_acceptable_skill_range)
5. **Save Results**: `save_teams_to_json()` and `save_teams_to_txt_file()`

## Key Design Decisions

### Modularity
- Each module has a single responsibility
- Clear separation: data (models), config, scoring, detection, balancing, I/O
- No circular dependencies

### Type Hints
- All functions use Python type hints
- Improves IDE autocomplete and code documentation
- Easier to maintain and debug

### Configuration Externalization
- All tunable parameters in `data/config.json`
- No hardcoded magic numbers in algorithms
- Easy to experiment with different settings

### Error Handling
- ValueError raised for invalid inputs (player count mismatch, etc.)
- FileNotFoundError for missing files
- All errors bubble up to CLI for user-friendly messages

## Performance

- **Hybrid algorithm**: ~2 seconds for 6 teams × 5 players
- **Fairness**: 0.77-20 (teams within ~1-5% of each other)
- **Internal range**: 40-43 (homogeneous teams, no polarization)
- **Execution**: Python 3.12, standard library only (no external deps)

## Testing

All core functions have unit tests in `tests/test_team_balancer.py`:
- Rank scoring accuracy
- Stats interpolation
- Smurf detection (high/low suspicion, admin criteria)
- Engine score clamping
- Snake draft distribution

Run tests:
```powershell
python -m unittest tests/test_team_balancer.py
```
