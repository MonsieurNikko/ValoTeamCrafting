# 🎮 GUIDE D'UTILISATION - Scraper + Team Balancer

## 📋 Vue d'ensemble

Ce guide explique comment utiliser le scraper automatique de stats Valorant avec le système de balance d'équipes.

## 🚀 Workflow complet

### **Étape 1 : Créer la liste des joueurs**

Crée un fichier texte (ex: `players_list.txt`) avec les noms des joueurs :

```
Ｎｉｋｋｏ#Han
PlayerName#TAG
AnotherPlayer#EUW
SomeGuy#NA1
```

**Format** : Un joueur par ligne, format `Nom#TAG`

---

### **Étape 2 : Scraper les stats**

```bash
python tracker_scraper.py --input players_list.txt --output data/scraped_players.json
```

**Ce qui se passe :**
- Le navigateur s'ouvre (mode visible par défaut)
- Visite tracker.gg pour chaque joueur
- Attend 3-6 secondes entre chaque joueur (rate limiting)
- Extrait toutes les stats automatiquement
- Sauvegarde dans `data/scraped_players.json`

**Temps estimé :** ~15-20 secondes par joueur

**Options utiles :**
```bash
# Mode headless (invisible) - peut manquer des stats
python tracker_scraper.py --input players_list.txt --headless

# Scraper des joueurs directement sans fichier
python tracker_scraper.py --players "Player1#TAG" "Player2#EUW" --output data/players.json
```

---

### **Étape 3 : Remplir les champs admin (optionnel)**

Ouvre `data/scraped_players.json` et remplis les champs admin si tu veux :

```json
{
  "players": [
    {
      "player_name": "Ｎｉｋｋｏ#Han",
      "rank_current": "Ascendant 2",
      "rank_peak_recent": "Immortal 1",
      "kd_ratio": 0.97,
      "average_combat_score": 218,
      "win_rate": 47.6,
      "headshot_rate": 27.7,
      "account_level": 463,
      "total_ranked_matches": 164,
      
      // Remplis ces champs manuellement :
      "player_id": 1,              // ID unique (1, 2, 3...)
      "admin_skill_rating": 8,     // 1-10 (ton estimation)
      "admin_familiarity": 3       // 1-5 (combien ils se connaissent)
    }
  ]
}
```

**Champs admin :**
- `player_id` : Numéro unique pour chaque joueur (1, 2, 3, etc.)
- `admin_skill_rating` : Note de skill de 1 à 10 (10 = meilleur)
- `admin_familiarity` : Niveau de familiarité 1 à 5 (5 = jouent toujours ensemble)

**Tu peux laisser `null` si tu n'as pas d'ajustements à faire.**

---

### **Étape 4 : Balancer les équipes**

```bash
python team_balancer.py --input data/scraped_players.json --teams 2
```

**Résultat :**
- Fichier créé dans `output/teams_YYYYMMDD_HHMMSS.json`
- Affiche les équipes dans le terminal
- Les équipes sont balancées selon les stats

**Options utiles :**
```bash
# 4 équipes au lieu de 2
python team_balancer.py --input data/scraped_players.json --teams 4

# Taille personnalisée (3 joueurs par équipe)
python team_balancer.py --input data/scraped_players.json --teams 3 --size 3

# Plus d'itérations pour meilleur balance (défaut: 10000)
python team_balancer.py --input data/scraped_players.json --teams 2 --iterations 50000
```

---

### **Étape 5 : Analyser le balance (optionnel)**

```bash
python analyze_balance.py data/scraped_players.json output/teams_20241123_153045.json
```

**Affiche :**
- Scores moyens de chaque équipe
- Distribution des stats (K/D, ACS, Win%, etc.)
- Graphiques de comparaison

---

## 📊 Format JSON complet

```json
{
  "players": [
    {
      "player_name": "Ｎｉｋｋｏ#Han",
      "rank_current": "Ascendant 2",         // Rank actuel
      "rank_peak_recent": "Immortal 1",       // Peak rank
      "kd_ratio": 0.97,                       // Kill/Death ratio
      "average_combat_score": 218,            // ACS moyen
      "win_rate": 47.6,                       // % de victoires
      "headshot_rate": 27.7,                  // % headshots
      "account_level": 463,                   // Niveau du compte
      "total_ranked_matches": 164,            // Parties jouées
      "player_id": null,                      // À remplir manuellement
      "admin_skill_rating": null,             // À remplir manuellement
      "admin_familiarity": null               // À remplir manuellement
    }
  ]
}
```

---

## 🎯 Exemple complet

```bash
# 1. Créer la liste
echo "Ｎｉｋｋｏ#Han" > players.txt
echo "Player2#EUW" >> players.txt
echo "Player3#NA1" >> players.txt
echo "Player4#TAG" >> players.txt
echo "Player5#BR" >> players.txt

# 2. Scraper (va prendre ~1-2 minutes pour 5 joueurs)
python tracker_scraper.py --input players.txt --output data/my_players.json

# 3. Optionnel : éditer data/my_players.json pour ajouter player_id, etc.

# 4. Balancer les équipes
python team_balancer.py --input data/my_players.json --teams 2

# 5. Les équipes sont dans output/teams_*.json
```

---

## ⚠️ Points importants

### **Profils privés**
Si un joueur a son profil en privé sur tracker.gg :
- ❌ Le scraper s'arrête immédiatement
- 💡 Solution : Demander au joueur de rendre son profil public

### **Rate Limiting**
- Le scraper attend 3-6 secondes entre chaque joueur
- C'est normal et nécessaire pour éviter la détection
- Ne pas interrompre le processus

### **Mode visible vs headless**
- **Visible (défaut)** : Le navigateur s'ouvre, tu vois ce qui se passe
  - ✅ Toutes les stats se chargent correctement
  - ✅ Bon pour debugging
  - ⚠️ Un peu plus lent

- **Headless** : Mode invisible
  - ✅ Plus rapide
  - ❌ Peut manquer certaines stats (JavaScript ne charge pas toujours)
  - 💡 Utilise seulement si tu es sûr

### **Encodage Unicode**
Le scraper supporte les caractères spéciaux (Ｎｉｋｋｏ, joueurs asiatiques, etc.)
- Tout est en UTF-8
- Pas besoin de conversion manuelle

---

## 🐛 Dépannage

| Problème | Solution |
|----------|----------|
| Stats montrent `null` | Utilise `--visible` au lieu de `--headless` |
| "Profile is private" | Demande au joueur de rendre son profil public |
| Timeout errors | Internet lent, réessaye |
| Le navigateur ne se ferme pas | Ferme-le manuellement, vérifie le format Name#TAG |
| Team balancer ne marche pas | Vérifie que tu as au moins 5 joueurs (1 team × 5) |

---

## 📁 Structure des fichiers

```
algoValo/
├── tracker_scraper.py          # Scraper automatique
├── team_balancer.py            # Balance d'équipes
├── analyze_balance.py          # Analyse des résultats
├── SCRAPER_GUIDE.md           # Doc détaillée du scraper
├── USAGE_GUIDE.md             # Ce fichier
├── players_list.txt           # Liste des joueurs (à créer)
├── data/
│   ├── config.json            # Configuration du balancer
│   ├── scraped_players.json   # Résultat du scraping
│   └── players_example.json   # Exemple de format
└── output/
    └── teams_*.json           # Équipes balancées
```

---

## 💡 Tips & Astuces

### **Scraping rapide**
```bash
# Si tu as déjà les stats de certains joueurs, ajoute juste les nouveaux :
python tracker_scraper.py --players "NewPlayer#TAG" --output data/new.json
# Puis merge manuellement avec l'ancien fichier
```

### **Tester le balancer avant de scraper**
```bash
# Utilise l'exemple pour tester
python team_balancer.py --input data/players_example.json --teams 2
```

### **Sauvegarder tes configurations**
Garde plusieurs fichiers de joueurs :
```
data/
├── tournament_A_players.json
├── tournament_B_players.json
└── weekly_scrim_players.json
```

---

## 🚀 Workflow pour tournoi

```bash
# Semaine avant le tournoi
python tracker_scraper.py --input tournament_players.txt --output data/tournament.json

# Jour du tournoi : rescrape pour stats à jour
python tracker_scraper.py --input tournament_players.txt --output data/tournament_final.json

# Balance les équipes
python team_balancer.py --input data/tournament_final.json --teams 4

# Analyse le résultat
python analyze_balance.py data/tournament_final.json output/teams_*.json

# Publie les équipes !
```

---

**Bon tournoi ! 🎉**
