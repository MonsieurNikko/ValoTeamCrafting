"""
Script pour remplacer un joueur qui quitte le tournoi.
Usage: python replace_player.py
"""

import json
from src import (
    Player, TeamConfiguration, load_players_from_json,
    compute_all_scores, replace_player_in_team
)


def load_team_config_from_json(filepath: str, all_players: list[Player]) -> TeamConfiguration:
    """
    Load a saved team configuration from JSON.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create player lookup
    player_lookup = {p.player_name: p for p in all_players}
    
    teams = []
    team_totals = []
    
    for team_data in data['teams']:
        team = []
        for p_data in team_data['players']:
            player = player_lookup.get(p_data['player_name'])
            if player:
                team.append(player)
        teams.append(team)
        team_totals.append(team_data['total_skill'])
    
    return TeamConfiguration(
        teams=teams,
        team_total_skills=team_totals,
        fairness_score=data['fairness_score'],
        average_team_skill=data['average_team_skill']
    )


def save_team_config_to_json(config: TeamConfiguration, filepath: str) -> None:
    """
    Save team configuration to JSON.
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


def interactive_replace_player():
    """
    Interface interactive pour remplacer un joueur.
    """
    print("="*80)
    print("REMPLACEMENT DE JOUEUR - Tournoi Valorant")
    print("="*80)
    
    # 1. Charger tous les joueurs
    print("\n[1/4] Chargement de la liste complète des joueurs...")
    try:
        all_players = load_players_from_json('players_example.json')
        print(f"[OK] {len(all_players)} joueurs chargés")
    except Exception as e:
        print(f"[ERREUR] Impossible de charger players_example.json: {e}")
        return
    
    # Calculer les scores pour tous
    for player in all_players:
        compute_all_scores(player)
    
    # 2. Charger la configuration des équipes
    print("\n[2/4] Chargement de la configuration des équipes...")
    config_file = 'balanced_teams.json'
    try:
        current_config = load_team_config_from_json(config_file, all_players)
        print(f"[OK] Configuration chargée: {len(current_config.teams)} équipes")
    except FileNotFoundError:
        print(f"[ERREUR] Fichier {config_file} non trouvé!")
        print("Vous devez d'abord générer les équipes avec team_balancer.py")
        return
    except Exception as e:
        print(f"[ERREUR] Impossible de charger la configuration: {e}")
        return
    
    # Afficher les équipes actuelles
    print("\n" + "="*80)
    print("ÉQUIPES ACTUELLES:")
    print("="*80)
    for i, team in enumerate(current_config.teams, 1):
        print(f"\nÉquipe {i} (Total: {current_config.team_total_skills[i-1]:.1f}):")
        for j, player in enumerate(team, 1):
            print(f"  {j}. {player.player_name:20s} - Skill: {player.final_skill_score:.1f}")
    
    # 3. Demander quel joueur remplacer
    print("\n" + "="*80)
    print("[3/4] Sélection du joueur à remplacer")
    print("="*80)
    player_to_replace = input("\nNom du joueur qui quitte le tournoi: ").strip()
    
    # Vérifier que le joueur existe dans les équipes
    found = False
    for team in current_config.teams:
        if any(p.player_name == player_to_replace for p in team):
            found = True
            break
    
    if not found:
        print(f"[ERREUR] Le joueur '{player_to_replace}' n'est dans aucune équipe!")
        return
    
    # 4. Afficher les remplaçants disponibles
    print("\n[4/4] Sélection du remplaçant")
    print("="*80)
    
    # Joueurs déjà dans les équipes
    players_in_teams = set()
    for team in current_config.teams:
        for player in team:
            players_in_teams.add(player.player_name)
    
    # Remplaçants disponibles
    replacements = [p for p in all_players if p.player_name not in players_in_teams]
    
    if not replacements:
        print("[ERREUR] Aucun remplaçant disponible!")
        return
    
    print(f"\nRemplaçants disponibles ({len(replacements)}):")
    print("-"*80)
    for i, player in enumerate(replacements, 1):
        print(f"{i:2d}. {player.player_name:20s} | {player.rank_current:15s} | Skill: {player.final_skill_score:.1f}")
    
    print("\n")
    replacement_name = input("Nom du joueur remplaçant: ").strip()
    
    replacement = None
    for p in replacements:
        if p.player_name == replacement_name:
            replacement = p
            break
    
    if not replacement:
        print(f"[ERREUR] '{replacement_name}' n'est pas dans la liste des remplaçants!")
        return
    
    # 5. Effectuer le remplacement
    print("\n" + "="*80)
    print("REMPLACEMENT EN COURS...")
    print("="*80)
    
    try:
        new_config = replace_player_in_team(
            config=current_config,
            player_to_replace_name=player_to_replace,
            replacement_player=replacement,
            all_players=all_players
        )
        
        # Sauvegarder la nouvelle configuration
        backup_file = 'balanced_teams_backup.json'
        save_team_config_to_json(current_config, backup_file)
        print(f"[OK] Ancienne configuration sauvegardée dans: {backup_file}")
        
        save_team_config_to_json(new_config, config_file)
        print(f"[OK] Nouvelle configuration sauvegardée dans: {config_file}")
        
        # Afficher le résumé
        print("\n" + "="*80)
        print("RÉSUMÉ DU REMPLACEMENT")
        print("="*80)
        print(f"Joueur retiré:    {player_to_replace}")
        print(f"Joueur ajouté:    {replacement.player_name}")
        print(f"Ancien fairness:  {current_config.fairness_score:.2f}")
        print(f"Nouveau fairness: {new_config.fairness_score:.2f}")
        print(f"Différence:       {new_config.fairness_score - current_config.fairness_score:+.2f}")
        
        if new_config.fairness_score > current_config.fairness_score:
            print("\n⚠️  ATTENTION: Le fairness a augmenté (équipes moins équilibrées)")
        else:
            print("\n✓ Le fairness a diminué ou est stable (équipes restent équilibrées)")
        
        print("\n[OK] Remplacement terminé avec succès!")
        
    except Exception as e:
        print(f"[ERREUR] Échec du remplacement: {e}")
        return


if __name__ == "__main__":
    interactive_replace_player()
