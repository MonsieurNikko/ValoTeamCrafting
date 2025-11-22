"""
Analyze team balance quality - both between teams and within teams.
"""
import json
import sys

def analyze_teams(filename='output/balanced_teams.json'):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("=" * 80)
    print("TEAM BALANCE ANALYSIS")
    print("=" * 80)
    print(f"\nOverall Fairness Score: {data['fairness_score']:.2f}")
    print(f"Average Team Skill: {data['average_team_skill']:.2f}\n")
    
    internal_ranges = []
    
    for team in data['teams']:
        skills = [p['final_skill_score'] for p in team['players']]
        skill_min = min(skills)
        skill_max = max(skills)
        skill_range = skill_max - skill_min
        skill_mean = sum(skills) / len(skills)
        skill_std = (sum((s - skill_mean) ** 2 for s in skills) / len(skills)) ** 0.5
        
        internal_ranges.append(skill_range)
        
        print(f"Team {team['team_number']}:")
        print(f"  Total Skill: {team['total_skill']:.2f}")
        print(f"  Skills: {[round(s, 1) for s in sorted(skills)]}")
        print(f"  Range: {skill_range:.1f} (min={skill_min:.1f}, max={skill_max:.1f})")
        print(f"  Std Dev: {skill_std:.2f}")
        print()
    
    print("=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    print(f"Average internal range: {sum(internal_ranges) / len(internal_ranges):.2f}")
    print(f"Max internal range: {max(internal_ranges):.2f}")
    print(f"Min internal range: {min(internal_ranges):.2f}")
    print(f"Teams with range > 35: {sum(1 for r in internal_ranges if r > 35)}/6")
    print(f"Teams with range > 40: {sum(1 for r in internal_ranges if r > 40)}/6")
    print(f"Teams with range > 45: {sum(1 for r in internal_ranges if r > 45)}/6")

if __name__ == '__main__':
    import sys
    filename = sys.argv[1] if len(sys.argv) > 1 else 'output/balanced_teams.json'
    analyze_teams(filename)
