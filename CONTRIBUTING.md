# Contributing to Valorant Team Balancer

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/valorant-team-balancer.git
   cd valorant-team-balancer
   ```
3. **Create a branch** for your feature:
   ```bash
   git checkout -b feature/my-awesome-feature
   ```

## 🧪 Before You Start

### Run Tests

Make sure all existing tests pass:

```bash
python -m unittest tests/test_team_balancer.py -v
```

All 7 tests should pass before you make changes.

### Verify Functionality

Run the balancer with example data:

```bash
python team_balancer.py --teams 6 --size 5 --seed 42 --iterations 5000
```

Expected results:
- Fairness score: ~0.77-20
- Average internal range: ~40-43
- Execution time: ~2 seconds

## 📝 Making Changes

### Code Style

- Follow PEP 8 guidelines
- Use type hints for function parameters and return values
- Add docstrings for all public functions
- Keep functions focused and modular

Example:

```python
def compute_fairness_score(teams: List[List[Player]]) -> Tuple[float, List[float], float]:
    """
    Compute fairness score for a team configuration.
    
    Args:
        teams: List of teams, each team is a list of Player objects
    
    Returns:
        Tuple of (fairness_score, team_total_skills, average_team_skill)
    """
    # Implementation here
    pass
```

### Testing

If you add new functionality:

1. **Add unit tests** in `tests/test_team_balancer.py`:
   ```python
   def test_my_new_feature(self):
       # Test implementation
       self.assertEqual(expected, actual)
   ```

2. **Run tests** to ensure they pass:
   ```bash
   python -m unittest tests/test_team_balancer.py
   ```

3. **Test with real data**:
   ```bash
   python team_balancer.py --teams 6 --size 5
   python analyze_balance.py
   ```

### Documentation

Update documentation if needed:

- **README.md**: User-facing features
- **src/README.md**: Code architecture changes
- **QUICK_REFERENCE.md**: New CLI options or usage patterns
- **Docstrings**: All new functions and classes

## 🔍 Code Review Checklist

Before submitting your PR, ensure:

- [ ] All tests pass (`python -m unittest tests/test_team_balancer.py`)
- [ ] Code follows PEP 8 style guidelines
- [ ] New functions have docstrings with type hints
- [ ] New features have corresponding tests
- [ ] Documentation is updated (if applicable)
- [ ] No print statements (use logging or verbose flags)
- [ ] No hardcoded values (use config.json)
- [ ] Performance is not degraded

## 📤 Submitting Changes

1. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add feature: description of your changes"
   ```

2. **Push to your fork**:
   ```bash
   git push origin feature/my-awesome-feature
   ```

3. **Open a Pull Request**:
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your branch
   - Fill in the PR template with:
     - Description of changes
     - Related issues (if any)
     - Testing performed
     - Screenshots (if UI changes)

## 🐛 Reporting Bugs

Use GitHub Issues with the following information:

- **Description**: Clear description of the bug
- **Steps to Reproduce**: Exact steps to trigger the issue
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: Python version, OS, etc.
- **Sample Data**: Minimal JSON example that reproduces the issue (if applicable)

Example:

```markdown
## Bug Description
Team balancing fails with error "list index out of range"

## Steps to Reproduce
1. Run: `python team_balancer.py --teams 6 --size 5`
2. Use attached `players.json` file

## Expected
Teams generated successfully

## Actual
Error: list index out of range at line 234

## Environment
- Python 3.12.0
- Windows 11
- Data: 30 players, 6 teams, 5 per team
```

## 💡 Suggesting Features

Use GitHub Issues with:

- **Feature Description**: What you want to add
- **Use Case**: Why it's useful
- **Proposed Implementation**: Ideas on how to implement (optional)
- **Alternatives Considered**: Other approaches you thought about

## 🎯 Good First Issues

Looking for where to start? Try these:

- Add more unit tests for edge cases
- Improve error messages
- Add input validation
- Optimize performance (profiling)
- Add more documentation examples
- Support additional input formats (CSV, Excel)

## 🏗️ Project Structure

Understanding the codebase:

```
src/
├── models.py         # Data structures (Player, TeamConfiguration)
├── config.py         # Configuration loading
├── scoring.py        # Player rating calculations
├── smurf_detection.py # Anti-smurf system
├── balancing.py      # Team generation algorithms
├── utils.py          # I/O operations
└── __init__.py       # Module exports
```

Key functions to understand:

- `compute_all_scores()`: Main scoring orchestrator
- `generate_balanced_teams()`: Hybrid algorithm entry point
- `compute_fairness_score()`: Team balance metric

## 📊 Performance Guidelines

When making changes:

- **Maintain current performance**: ~2 seconds for 30 players
- **Profile before optimizing**: Use `cProfile` to find bottlenecks
- **Test with larger datasets**: 40, 50, 60+ players
- **Consider algorithm complexity**: O(n log n) preferred over O(n²)

## 🤝 Communication

- **Be respectful**: Follow the code of conduct
- **Be patient**: Maintainers are volunteers
- **Be descriptive**: Provide context in issues/PRs
- **Be collaborative**: Open to feedback and suggestions

## 📜 Code of Conduct

- Be welcoming and inclusive
- Respect differing viewpoints
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards others

## ❓ Questions?

- Check existing [documentation](docs/)
- Search [existing issues](https://github.com/yourusername/valorant-team-balancer/issues)
- Read [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- Ask in a new issue with the "question" label

## 🎉 Thank You!

Every contribution helps make this project better for the Valorant community. We appreciate your time and effort!

---

**Happy coding!** 🚀
