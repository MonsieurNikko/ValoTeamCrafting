# Project Structure

```
algoValo/
├── src/                          # Core source code modules
│   ├── __init__.py              # Module exports
│   ├── models.py                # Data structures (Player, TeamConfiguration)
│   ├── config.py                # Configuration management
│   ├── scoring.py               # Player skill rating system
│   ├── smurf_detection.py       # 9-factor smurf detection
│   ├── balancing.py             # Team generation algorithms
│   ├── utils.py                 # I/O operations (load/save JSON, text reports)
│   └── README.md                # Architecture documentation
│
├── tests/                        # Unit tests
│   └── test_team_balancer.py    # 7 test cases for core functions
│
├── data/                         # Configuration and input data
│   ├── config.json              # All tunable parameters (81 params)
│   ├── players_example.json     # Sample 30-player dataset
│   └── players_realistic.json   # Realistic 40-player dataset
│
├── output/                       # Generated results
│   ├── balanced_teams.json      # Machine-readable team assignments
│   └── balanced_teams.txt       # Human-readable report
│
├── docs/                         # Documentation
│   ├── README.md                # Main documentation (370+ lines)
│   ├── ALGORITHM_OPTIMIZATION.md
│   ├── IMPLEMENTATION_VERIFICATION.md
│   └── SMURF_DETECTION_UPDATE.md
│
├── team_balancer.py             # CLI entry point (100 lines)
├── analyze_balance.py           # Quality analysis tool
├── replace_player.py            # Player replacement utility
│
└── team_balancer_old.py         # Original monolithic version (backup)
```

## File Descriptions

### Core Modules (`src/`)
- **models.py** (53 lines): Player dataclass with 40+ fields, TeamConfiguration
- **config.py** (29 lines): JSON config loader, safe get_config() accessor
- **scoring.py** (217 lines): Complete player rating system (rank, stats, community, final)
- **smurf_detection.py** (141 lines): 9-factor detection (5 stats + 4 admin-based)
- **balancing.py** (254 lines): Hybrid algorithm, snake draft, fairness calculation
- **utils.py** (175 lines): Load/save JSON, generate text reports

**Total source code**: ~870 lines (vs 991 in original monolithic file)

### Entry Points
- **team_balancer.py**: Main CLI (replaces 991-line monolith with 100-line wrapper)
- **analyze_balance.py**: Analyze team quality (fairness, internal ranges, std dev)
- **replace_player.py**: Handle player replacements mid-tournament

### Configuration (`data/`)
- **config.json**: 81 parameters across 6 categories
  - rank_score_mapping: 26 Valorant ranks
  - rank_groups: low/mid/high categories
  - kd_thresholds, acs_thresholds: Per-group stats interpolation
  - team_balance_config: internal_variance_weight, max_acceptable_skill_range
  - smurf_config: 15+ detection parameters
  - familiarity_alpha_thresholds, engine_weights, etc.

### Tests (`tests/`)
- 7 unit tests covering:
  - Rank score blending (60% current + 40% peak)
  - Stats interpolation (linear between thresholds)
  - Smurf detection (high/low suspicion, admin criteria)
  - Engine score clamping (smurf adjustment)
  - Snake draft distribution

**All tests passing** ✅

### Documentation (`docs/`)
- **README.md**: Complete user guide
  - Quick start, CLI commands, config reference
  - PowerShell examples, troubleshooting
  - Library comparison (vs OR-Tools, DEAP, etc.)
- **ALGORITHM_OPTIMIZATION.md**: Evolution from Random Search → Multi-Start SA → Snake Draft → Hybrid
- **IMPLEMENTATION_VERIFICATION.md**: Performance validation (fairness 0.77, range 42)
- **SMURF_DETECTION_UPDATE.md**: 9-factor system documentation

## Code Statistics

### Before Refactoring
- **team_balancer.py**: 991 lines (monolithic)
- All code in one file
- Hard to navigate, test, maintain

### After Refactoring
- **src/**: 6 modules, 870 lines total
- **team_balancer.py**: 100 lines (CLI wrapper)
- **Total reduction**: 991 → 100 (90% reduction in main file)
- **Maintainability**: ⭐⭐⭐⭐⭐
  - Clear separation of concerns
  - Easy to test individual components
  - Simple to extend (add new scoring factors, algorithms, etc.)

## Usage Examples

### Basic
```powershell
python team_balancer.py
# Uses defaults: data/players_example.json, 8 teams, 5 per team, 5000 iterations
```

### Custom Configuration
```powershell
python team_balancer.py --teams 6 --size 5 --seed 42 --iterations 10000
```

### Analyze Results
```powershell
python analyze_balance.py output/balanced_teams.json
```

### Run Tests
```powershell
python -m unittest tests/test_team_balancer.py
```

## Key Improvements

1. **Modularity**: 1 file → 6 specialized modules
2. **Testability**: All core functions unit tested
3. **Organization**: Logical folder structure (src/, tests/, data/, output/, docs/)
4. **Maintainability**: Clear responsibilities, no code duplication
5. **Documentation**: Architecture README in src/, comprehensive docs in docs/
6. **Flexibility**: Easy to import modules: `from src import generate_balanced_teams`

## Migration from Old Version

If you have old scripts using `team_balancer` imports:

**Old:**
```python
from team_balancer import Player, generate_balanced_teams
```

**New:**
```python
from src import Player, generate_balanced_teams
```

**File paths:**
- `config.json` → `data/config.json`
- `players.json` → `data/players.json`
- `balanced_teams.json` → `output/balanced_teams.json`
