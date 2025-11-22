# 🎮 Valorant Tournament Team Balancer

An intelligent team balancing system for Valorant tournaments that creates fair, competitive teams using multi-factor player ratings and hybrid optimization algorithms.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-7%2F7%20passing-brightgreen.svg)](tests/)

## ✨ Features

- **🎯 Multi-Factor Player Rating**: Rank, stats, community ratings, and 9-factor smurf detection
- **⚖️ Hybrid Algorithm**: Snake Draft + Local Optimization for fair, homogeneous teams
- **📊 Comprehensive Output**: JSON and human-readable reports with detailed statistics
- **🔄 Player Replacement**: Replace quitting players without full recalculation
- **⚙️ Highly Configurable**: 81 parameters in config.json

## 🚀 Quick Start

```bash
# Generate balanced teams (defaults: 8 teams, 5 players each)
python team_balancer.py

# Custom configuration
python team_balancer.py --teams 6 --size 5 --seed 42 --iterations 5000

# Use your own data
python team_balancer.py --input data/my_players.json
```

## 📋 Installation

```bash
git clone https://github.com/MonsieurNikko/ValoTeamCrafting.git
cd ValoTeamCrafting

# No dependencies needed - uses Python standard library only!
python team_balancer.py --help
```

**Requirements**: Python 3.12+ (standard library only)

## 📊 Player Data Format

Create a JSON file with your players:

```json
{
  "players": [
    {
      "player_name": "RadiantKing",
      "rank_current": "Radiant",
      "rank_peak_recent": "Radiant",
      "kd_ratio": 1.31,
      "average_combat_score": 282,
      "win_rate": 56.2,
      "headshot_rate": 30.1,
      "account_level": 298,
      "total_ranked_matches": 1340,
      "player_id": 1,
      "admin_skill_rating": 10,
      "admin_familiarity": 3
    }
  ]
}
```

**Required fields**: `player_name`, `rank_current`, `rank_peak_recent`, `kd_ratio`, `average_combat_score`, `win_rate`, `headshot_rate`

**Optional fields**: `account_level`, `total_ranked_matches`, `player_id`, `admin_skill_rating`, `admin_familiarity`

See `data/players_example.json` for more examples.

## 🎯 How It Works

### Multi-Factor Rating System

1. **Rank Score** (60% current + 40% peak)
2. **Stats Score** (60% KD + 40% ACS, rank-normalized)
3. **Community Score** (admin ratings with familiarity weighting)
4. **Smurf Detection** (9 factors: level, matches, KD, WR, HS%, admin mismatches)

### Hybrid Balancing Algorithm

1. **Phase 1 - Snake Draft**: Sort players by skill, distribute 1-2-3-4-5-6-6-5-4-3-2-1...
2. **Phase 2 - Local Optimization**: 5000 iterations of greedy swaps with constraints
   - Only accepts improvements in fairness
   - Maintains internal homogeneity (max range = 50)

**Result**: Fairness 0.77-20, Internal range ~42, Execution ~2 seconds

## 📈 Performance

Tested with 30 players, 6 teams, 5 per team:
- **Fairness Score**: 0.77-20 (teams within 1-5%)
- **Internal Range**: 40-43 (homogeneous teams)
- **Execution Time**: ~2 seconds
- **Tests**: 7/7 passing ✅

## 🛠️ Tools Included

### Team Balancer
```bash
python team_balancer.py --teams 6 --size 5 --seed 42
```

### Analysis Tool
```bash
python analyze_balance.py output/balanced_teams.json
```

### Player Replacement
```bash
python replace_player.py
```

## 📚 Documentation

- **[Contributing](CONTRIBUTING.md)**: Guidelines for contributing to the project
- **[Module Architecture](src/README.md)**: Detailed module design and algorithm flow

## 🧪 Testing

```bash
# Run all tests
python -m unittest tests/test_team_balancer.py -v

# Expected: 7/7 tests passing
```

Tests cover:
- Rank/stats scoring
- Smurf detection
- Fairness calculation
- Snake draft distribution

## 🏗️ Project Structure

```
src/              # Core modules (models, config, scoring, balancing, utils)
tests/            # Unit tests
data/             # Configuration and example player data
  ├── config.json              # Algorithm configuration
  ├── players_example.json     # Example dataset (30 players)
  └── players_realistic.json   # Realistic dataset with smurfs
output/           # Generated team results (JSON + TXT)
analyze_balance.py    # Post-generation analysis tool
replace_player.py     # Player replacement utility
team_balancer.py      # Main CLI entry point
```

## ⚙️ Configuration

Edit `data/config.json` to customize:
- `max_acceptable_skill_range`: 50.0 (prevents polarization)
- `smurf_threshold`: 60.0 (suspicion % to flag)
- `engine_weight_rank/stats`: 0.5 each (balance rank vs stats)

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📝 License

MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

Inspired by the competitive Valorant community. Algorithm evolved through multiple iterations to achieve optimal balance.

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/MonsieurNikko/ValoTeamCrafting/issues)
- **Documentation**: See [CONTRIBUTING.md](CONTRIBUTING.md) and `src/README.md`

---

**Made with ❤️ for the Valorant community**
