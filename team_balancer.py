#!/usr/bin/env python3
"""
Valorant Tournament Team Balancer - CLI Entry Point

A comprehensive team balancing system for Valorant tournaments.
Uses hybrid Snake Draft + Local Optimization for fair team generation.
"""

import sys
import os
import random
import argparse

from src import (
    load_config,
    load_players_from_json,
    save_teams_to_json,
    save_teams_to_txt_file,
    compute_all_scores,
    generate_balanced_teams
)


def main():
    parser = argparse.ArgumentParser(description='Valorant Tournament Team Balancer')
    parser.add_argument('--input', default='data/players_example.json', help='Input JSON file')
    parser.add_argument('--output', default='output/balanced_teams.json', help='Output JSON file')
    parser.add_argument('--config', default='data/config.json', help='Config JSON file')
    parser.add_argument('--teams', type=int, default=8, help='Number of teams')
    parser.add_argument('--size', type=int, default=5, help='Players per team')
    parser.add_argument('--iterations', type=int, default=5000, help='Optimization iterations')
    parser.add_argument('--seed', type=int, help='Random seed')
    parser.add_argument('--quiet', action='store_true', help='Suppress output')
    
    args = parser.parse_args()
    
    if args.seed is not None:
        random.seed(args.seed)
        if not args.quiet:
            print(f"Random seed set to: {args.seed}")
    
    if not args.quiet:
        print(f"Loading configuration from {args.config}...")
    try:
        load_config(args.config)
    except FileNotFoundError:
        print(f"Error: Config file '{args.config}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)
    
    if not args.quiet:
        print(f"Loading players from {args.input}...")
    try:
        players = load_players_from_json(args.input)
        if not args.quiet:
            print(f"Loaded {len(players)} players.")
    except FileNotFoundError:
        print(f"Error: File '{args.input}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading players: {e}")
        sys.exit(1)
    
    if not args.quiet:
        print("Computing player scores...")
    for player in players:
        compute_all_scores(player)
    
    try:
        config = generate_balanced_teams(
            players=players,
            num_teams=args.teams,
            team_size=args.size,
            num_iterations=args.iterations,
            verbose=not args.quiet
        )
        
        if not args.quiet:
            print(f"\nFinal Fairness Score: {config.fairness_score:.2f}")
            print(f"Average Team Skill: {config.average_team_skill:.2f}")
        
        save_teams_to_json(config, args.output)
        if not args.quiet:
            print(f"\nTeams saved to {args.output}")
            
        txt_output = os.path.splitext(args.output)[0] + '.txt'
        save_teams_to_txt_file(config, txt_output)
        if not args.quiet:
            print(f"Text report saved to {txt_output}")
        
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
