import unittest
import json
from src import (
    Player, compute_rank_score, compute_stats_score,
    compute_smurf_suspicion, compute_engine_score,
    compute_fairness_score, load_config, CONFIG
)

class TestTeamBalancer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load default config for tests
        load_config('data/config.json')

    def setUp(self):
        self.player = Player(
            player_id="1",
            player_name="TestPlayer",
            rank_current="Gold 2",
            rank_peak_recent="Gold 3",
            kd_ratio=1.0,
            average_combat_score=200,
            win_rate=50.0,
            headshot_rate=20.0,
            account_level=100,
            total_ranked_matches=200,
            rank_group="mid"
        )

    def test_compute_rank_score(self):
        # Gold 2 = 37, Gold 3 = 40
        # Score = 0.6 * 37 + 0.4 * 40 = 22.2 + 16 = 38.2
        score = compute_rank_score(self.player)
        self.assertAlmostEqual(score, 38.2)

    def test_compute_stats_score(self):
        # Mid rank group
        # KD 1.0 -> 50
        # ACS 200 -> 50
        # Score = 0.6 * 50 + 0.4 * 50 = 50
        score = compute_stats_score(self.player)
        self.assertAlmostEqual(score, 50.0)

    def test_compute_smurf_suspicion_low(self):
        # Normal stats, should be 0 suspicion
        suspicion = compute_smurf_suspicion(self.player)
        self.assertEqual(suspicion, 0.0)

    def test_compute_smurf_suspicion_high(self):
        # Smurf stats
        smurf = Player(
            player_id="2",
            player_name="Smurf",
            rank_current="Silver 1",
            rank_peak_recent="Silver 1",
            kd_ratio=2.0,  # High KD
            average_combat_score=350,
            win_rate=80.0, # High WR
            headshot_rate=40.0, # High HS
            account_level=20, # Low level
            total_ranked_matches=10, # Low matches
            rank_group="low"
        )
        suspicion = compute_smurf_suspicion(smurf)
        self.assertGreater(suspicion, 60.0)  # Updated threshold
        self.assertTrue(smurf.is_smurf_suspected)

    def test_compute_smurf_suspicion_admin_criteria(self):
        # Test admin-based smurf detection
        
        # Criterion 6a: Friend's smurf (high familiarity + high skill + low rank)
        friend_smurf = Player(
            player_id="3",
            player_name="FriendSmurf",
            rank_current="Gold 2",
            rank_peak_recent="Gold 3",
            kd_ratio=1.1,
            average_combat_score=200,
            admin_skill_rating=9,  # Admin knows he's actually Immortal
            admin_familiarity=3,   # Knows him well
            account_level=100,
            total_ranked_matches=200,
            rank_group="low"
        )
        friend_smurf.rank_score = 37  # Gold 2
        friend_smurf.stats_score = 50
        suspicion_6a = compute_smurf_suspicion(friend_smurf)
        self.assertGreater(suspicion_6a, 20.0)  # Should trigger 6a
        
        # Criterion 6c: New account that impressed admin
        new_impressive = Player(
            player_id="4",
            player_name="NewImpressive",
            rank_current="Silver 2",
            rank_peak_recent="Silver 2",
            kd_ratio=1.2,
            average_combat_score=210,
            admin_skill_rating=8,   # Seems very skilled
            admin_familiarity=1,    # Only played 1-2 games with him
            account_level=25,       # New account
            total_ranked_matches=30,
            rank_group="low"
        )
        new_impressive.rank_score = 28
        new_impressive.stats_score = 55
        suspicion_6c = compute_smurf_suspicion(new_impressive)
        self.assertGreater(suspicion_6c, 10.0)  # Should trigger 6c

    def test_compute_engine_score(self):
        # Test engine score calculation
        # Engine score = 0.6 * rank_score + 0.4 * stats_score
        # With clamping applied
        self.player.rank_score = 50.0
        self.player.stats_score = 60.0
        self.player.smurf_suspicion_score = 0.0
        
        # Base: 0.6 * 50 + 0.4 * 60 = 30 + 24 = 54
        # Clamp: rank_score (50) + offset (15 for mid) = 65
        # 54 < 65, so no clamping applied
        score = compute_engine_score(self.player)
        self.assertAlmostEqual(score, 54.0)
        
        # Test with high stats that should trigger clamping
        self.player.stats_score = 100.0
        # Base: 0.6 * 50 + 0.4 * 100 = 30 + 40 = 70
        # Clamp: 50 + 15 = 65
        # Should be clamped to 65
        score_clamped = compute_engine_score(self.player)
        self.assertAlmostEqual(score_clamped, 65.0)

    def test_compute_fairness_score(self):
        # 2 teams, perfect balance
        p1 = Player("1", "P1", "G1", "G1", 1.0, 200, 50, 20)
        p1.final_skill_score = 50
        p2 = Player("2", "P2", "G1", "G1", 1.0, 200, 50, 20)
        p2.final_skill_score = 50
        
        teams = [[p1], [p2]]
        fairness, _, _ = compute_fairness_score(teams)
        self.assertEqual(fairness, 0.0)

        # Imbalanced
        p3 = Player("3", "P3", "G1", "G1", 1.0, 200, 50, 20)
        p3.final_skill_score = 100
        teams_imbalanced = [[p1], [p3]]
        fairness_imbalanced, _, _ = compute_fairness_score(teams_imbalanced)
        self.assertGreater(fairness_imbalanced, 0.0)

if __name__ == '__main__':
    unittest.main()
