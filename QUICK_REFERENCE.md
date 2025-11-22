# Quick Reference Guide

## Common Commands

### Run Team Balancer

**Basic (use defaults):**
```powershell
python team_balancer.py
```

**Custom configuration:**
```powershell
python team_balancer.py --teams 6 --size 5 --seed 42 --iterations 5000
```

**Full options:**
```powershell
python team_balancer.py `
  --input data/players_realistic.json `
  --output output/my_teams.json `
  --config data/config.json `
  --teams 8 `
  --size 5 `
  --iterations 10000 `
  --seed 123 `
  --quiet
```

### Analyze Results

**Default file:**
```powershell
python analyze_balance.py
```

**Custom file:**
```powershell
python analyze_balance.py output/my_teams.json
```

### Run Tests

**All tests:**
```powershell
python -m unittest tests/test_team_balancer.py
```

**Specific test:**
```powershell
python -m unittest tests.test_team_balancer.TestTeamBalancer.test_compute_rank_score
```

**Verbose:**
```powershell
python -m unittest tests/test_team_balancer.py -v
```

### Replace Player

```powershell
python replace_player.py
```
(Interactive prompts will guide you)

## Import Examples

### In Python Scripts

**Import everything:**
```python
from src import *
```

**Import specific functions:**
```python
from src import (
    Player,
    TeamConfiguration,
    load_config,
    load_players_from_json,
    compute_all_scores,
    generate_balanced_teams,
    save_teams_to_json
)
```

**Import modules:**
```python
from src import models, scoring, balancing

player = models.Player(...)
balancing.generate_balanced_teams(...)
```

### Example Script

```python
from src import (
    load_config,
    load_players_from_json,
    compute_all_scores,
    generate_balanced_teams,
    save_teams_to_json
)

# Load config
load_config('data/config.json')

# Load players
players = load_players_from_json('data/players_example.json')

# Compute scores
for player in players:
    compute_all_scores(player)

# Generate teams
config = generate_balanced_teams(
    players=players,
    num_teams=6,
    team_size=5,
    num_iterations=5000,
    verbose=True
)

# Save results
save_teams_to_json(config, 'output/my_teams.json')

print(f"Fairness: {config.fairness_score:.2f}")
print(f"Avg skill: {config.average_team_skill:.2f}")
```

## File Paths

### Default Locations

- **Config**: `data/config.json`
- **Player data**: `data/players_example.json` or `data/players_realistic.json`
- **Output**: `output/balanced_teams.json` + `output/balanced_teams.txt`
- **Tests**: `tests/test_team_balancer.py`
- **Docs**: `docs/README.md`

### Project Structure

```
algoValo/
├── team_balancer.py         # Main CLI
├── analyze_balance.py       # Analysis tool
├── replace_player.py        # Player replacement
├── src/                     # Core modules
│   ├── __init__.py
│   ├── models.py
│   ├── config.py
│   ├── scoring.py
│   ├── smurf_detection.py
│   ├── balancing.py
│   └── utils.py
├── tests/
│   └── test_team_balancer.py
├── data/
│   ├── config.json
│   ├── players_example.json
│   └── players_realistic.json
├── output/
│   ├── balanced_teams.json
│   └── balanced_teams.txt
└── docs/
    ├── README.md
    ├── ALGORITHM_OPTIMIZATION.md
    ├── IMPLEMENTATION_VERIFICATION.md
    └── SMURF_DETECTION_UPDATE.md
```

## Configuration

### Edit config.json

```powershell
notepad data\config.json
```

### Key Parameters

**Team balancing:**
- `max_acceptable_skill_range`: 50.0 (prevents polarization)
- `internal_variance_weight`: 10.0 (homogeneity importance)

**Smurf detection:**
- `low_level_threshold`: 30 (below = suspicious)
- `low_matches_threshold`: 50 (below = suspicious)
- `smurf_threshold`: 60.0 (suspicion % to flag)

**Scoring weights:**
- `engine_weight_rank`: 0.5 (rank importance in engine score)
- `engine_weight_stats`: 0.5 (stats importance in engine score)

## Troubleshooting

### Module not found

```powershell
# Make sure you're in the right directory
cd h:\Documents\linhtinh\algoValo

# Check Python can find src/
python -c "import src; print('OK')"
```

### Config file not found

```powershell
# Check file exists
Test-Path data\config.json

# Use absolute path if needed
python team_balancer.py --config "h:\Documents\linhtinh\algoValo\data\config.json"
```

### Player count mismatch

Make sure: `num_teams × team_size = number of players`

Examples:
- 6 teams × 5 players = 30 players ✅
- 8 teams × 5 players = 40 players ✅
- 6 teams × 5 players ≠ 32 players ❌

### Tests failing

```powershell
# Clean Python cache
Remove-Item -Recurse -Force __pycache__, src\__pycache__, tests\__pycache__

# Re-run tests
python -m unittest tests/test_team_balancer.py
```

## Performance Tips

### Faster Balancing

**Reduce iterations** (trade accuracy for speed):
```powershell
python team_balancer.py --iterations 1000  # ~0.5s instead of ~2s
```

**Use quiet mode**:
```powershell
python team_balancer.py --quiet  # No progress output
```

### Better Balance

**Increase iterations** (trade speed for accuracy):
```powershell
python team_balancer.py --iterations 20000  # ~5s but potentially better
```

**Adjust max_acceptable_skill_range** in config.json:
- Lower (e.g., 40): More homogeneous teams, may sacrifice fairness
- Higher (e.g., 60): Better fairness, may allow polarization

## Advanced Usage

### Batch Processing

```powershell
# Generate multiple runs with different seeds
for ($seed = 1; $seed -le 10; $seed++) {
    python team_balancer.py `
        --seed $seed `
        --output "output/teams_seed_$seed.json"
}
```

### Compare Algorithms

**Snake draft only:**
```powershell
python team_balancer.py --iterations 0 --output output/snake_only.json
```

**Hybrid (default):**
```powershell
python team_balancer.py --iterations 5000 --output output/hybrid.json
```

**Heavy optimization:**
```powershell
python team_balancer.py --iterations 50000 --output output/heavy_opt.json
```

Then compare:
```powershell
python analyze_balance.py output/snake_only.json
python analyze_balance.py output/hybrid.json
python analyze_balance.py output/heavy_opt.json
```

## Help

**CLI help:**
```powershell
python team_balancer.py --help
```

**Module documentation:**
```python
from src import generate_balanced_teams
help(generate_balanced_teams)
```

**Read docs:**
- Main: `docs/README.md`
- Architecture: `src/README.md`
- Structure: `PROJECT_STRUCTURE.md`
- Refactoring: `REFACTORING_SUMMARY.md`
