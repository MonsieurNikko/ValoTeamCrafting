"""
Valorant Tracker.gg Stats Scraper with Human Simulation
Scrapes player statistics from tracker.gg by simulating human browser behavior.
"""

import asyncio
import json
import re
import random
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from urllib.parse import quote
from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeout


class TrackerScraperHuman:
    """Scraper for Valorant tracker.gg with human behavior simulation"""
    
    BASE_URL = "https://tracker.gg/valorant/profile/riot"
    
    def __init__(self, headless: bool = False, slow_mo: int = 100):
        """
        Initialize the scraper with human-like settings
        
        Args:
            headless: Run browser in headless mode (invisible)
            slow_mo: Delay in milliseconds between actions (simulates human speed)
        """
        self.headless = headless
        self.slow_mo = slow_mo
        self.players_data = []
    
    def build_profile_url(self, player_name: str, tag: str) -> str:
        """
        Build tracker.gg profile URL with proper Unicode encoding
        
        Args:
            player_name: Player name (can contain Unicode characters)
            tag: Player tag (without #)
            
        Returns:
            Encoded URL for tracker.gg profile
        """
        tag = tag.replace("#", "")
        player_identifier = f"{player_name}#{tag}"
        # quote() automatically encodes Unicode characters (Ｎｉｋｋｏ → %EF%BC%AE...)
        encoded = quote(player_identifier, safe='')
        return f"{self.BASE_URL}/{encoded}/overview"
    
    async def human_delay(self, min_ms: int = 500, max_ms: int = 1500):
        """Add random delay to simulate human behavior"""
        delay = random.uniform(min_ms / 1000, max_ms / 1000)
        await asyncio.sleep(delay)
    
    async def wait_for_profile_load(self, page: Page) -> bool:
        """
        Wait for the profile to fully load with JavaScript execution.
        
        Returns:
            True if loaded successfully, False if profile is private/not found
        """
        try:
            # Wait for DOM to load (don't wait for all ads)
            await page.wait_for_load_state('domcontentloaded', timeout=20000)
            
            # Wait longer for JavaScript execution (especially in headless mode)
            await asyncio.sleep(8)
            
            # Check if profile is private or not found
            content = await page.content()
            if 'profile is private' in content.lower():
                return False
            if 'not found' in content.lower() or 'player not found' in content.lower():
                return False
            
            # Try to wait for profile header (with short timeout)
            try:
                await page.wait_for_selector('.trn-profile__header, .valorant-profile, .profile-header', timeout=10000)
            except:
                # If header doesn't appear, continue anyway
                print("  ⚠️  Header not found, but continuing...")
            
            # Additional delay for stats to load
            await self.human_delay(2000, 3000)
            
            return True
            
        except PlaywrightTimeout:
            print("  ⚠️  Timeout - profile took too long to load")
            return False
        except Exception as e:
            print(f"  ⚠️  Error during loading: {e}")
            return False
    
    async def extract_text_from_selector(self, page: Page, selector: str, default: str = "") -> str:
        """Safely extract text from a CSS selector"""
        try:
            element = await page.query_selector(selector)
            if element:
                text = await element.inner_text()
                return text.strip()
            return default
        except Exception as e:
            print(f"  ⚠️  Error extracting '{selector}': {e}")
            return default
    
    async def extract_rank(self, page: Page) -> Tuple[str, str]:
        """
        Extract current rank and peak rank.
        
        Returns:
            Tuple of (current_rank, peak_rank)
        """
        # Try different selectors for current rank
        selectors_current = [
            '.valorant-rank-tile__value',
            '.rank-text',
            '.rating-entry__rank-info .value',
            '[data-v-tooltip*="Rank"]'
        ]
        
        current_rank = ""
        for selector in selectors_current:
            rank_text = await self.extract_text_from_selector(page, selector)
            if rank_text and rank_text != "Unrated":
                # Clean up text (remove "Rating", newlines, etc.)
                rank_text = rank_text.replace("Rating", "").replace("\n", " ").strip()
                current_rank = rank_text
                break
        
        # If not found, search in page content with regex
        if not current_rank:
            content = await page.content()
            # Pattern: "Gold 2", "Platinum 1", etc.
            rank_match = re.search(
                r'(Radiant|Immortal [1-3]|Ascendant [1-3]|Diamond [1-3]|Platinum [1-3]|Gold [1-3]|Silver [1-3]|Bronze [1-3]|Iron [1-3])', 
                content
            )
            if rank_match:
                current_rank = rank_match.group(1)
        
        # Clean up multiple spaces
        current_rank = " ".join(current_rank.split())
        
        # Extract peak rank
        peak_rank = current_rank  # Default to current rank
        try:
            # Look for "Peak Rating" section
            content = await page.content()
            peak_match = re.search(
                r'Peak Rating.*?(Radiant|Immortal [1-3]|Ascendant [1-3]|Diamond [1-3]|Platinum [1-3]|Gold [1-3]|Silver [1-3]|Bronze [1-3]|Iron [1-3])',
                content,
                re.DOTALL
            )
            if peak_match:
                peak_rank = peak_match.group(1)
        except Exception as e:
            print(f"  ⚠️  Could not extract peak rank: {e}")
        
        return current_rank or "Gold 2", peak_rank or "Gold 2"
    
    async def extract_stat_value(self, page: Page, stat_name: str) -> Optional[float]:
        """
        Extract a stat value from the page using CSS selectors.
        Searches for elements with class="stat" containing title="{stat_name}"
        
        Args:
            stat_name: Name of the stat to extract (kd, acs, winrate, headshot)
            
        Returns:
            Float value of the stat, or None if not found
        """
        try:
            # Mapping of stat names to tracker.gg search patterns
            stat_titles = {
                'kd': ['K/D Ratio', 'K/D', 'KD'],
                'acs': ['ACS'],
                'winrate': ['Win %', 'Win Rate'],
                'headshot': ['Headshot %', 'HS %'],
            }
            
            titles_to_search = stat_titles.get(stat_name.lower(), [stat_name])
            
            # Search all stat elements
            stats_elements = await page.query_selector_all('.stat .numbers')
            
            for stat_el in stats_elements:
                # Get stat name
                name_el = await stat_el.query_selector('.name')
                if name_el:
                    name_text = await name_el.get_attribute('title')
                    if not name_text:
                        name_text = await name_el.inner_text()
                    
                    # Check if this is the stat we're looking for
                    for title in titles_to_search:
                        if title.lower() in name_text.lower():
                            # Extract the value
                            value_el = await stat_el.query_selector('.value')
                            if value_el:
                                value_text = await value_el.inner_text()
                                # Clean and convert (remove % if present)
                                value_clean = value_text.strip().replace('%', '').replace(',', '')
                                try:
                                    return float(value_clean)
                                except ValueError:
                                    continue
            
            # Fallback: search in raw HTML with regex
            content = await page.content()
            patterns = {
                'kd': r'title="K/D Ratio"[^>]*>.*?<span[^>]*class="value"[^>]*>(\d+\.\d+)',
                'acs': r'title="ACS"[^>]*>.*?<span[^>]*class="value"[^>]*>(\d+\.?\d*)',
                'winrate': r'title="Win %"[^>]*>.*?<span[^>]*class="value"[^>]*>(\d+\.?\d*)%',
                'headshot': r'title="Headshot %"[^>]*>.*?<span[^>]*class="value"[^>]*>(\d+\.?\d*)%',
            }
            
            pattern = patterns.get(stat_name.lower())
            if pattern:
                match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
                if match:
                    value = match.group(1)
                    return float(value)
            
            return None
            
        except Exception as e:
            print(f"  ⚠️  Error extracting stat '{stat_name}': {e}")
            return None
    
    async def extract_account_level(self, page: Page) -> Optional[int]:
        """Extract account level from the profile"""
        try:
            # Look for "Level" stat in highlighted section
            content = await page.content()
            level_match = re.search(
                r'<span[^>]*class="stat__label"[^>]*>Level</span>\s*<span[^>]*class="stat__value"[^>]*>(\d+)',
                content,
                re.IGNORECASE | re.DOTALL
            )
            if level_match:
                return int(level_match.group(1))
            
            return None
        except Exception as e:
            print(f"  ⚠️  Error extracting level: {e}")
            return None
    
    async def extract_matches_played(self, page: Page) -> Optional[int]:
        """Extract number of matches played this act"""
        try:
            # Look for "XXX Matches" text in the overview header
            content = await page.content()
            matches_match = re.search(
                r'<span[^>]*class="matches"[^>]*>(\d+)\s+Matches',
                content,
                re.IGNORECASE | re.DOTALL
            )
            if matches_match:
                return int(matches_match.group(1))
            
            # Alternative pattern
            matches_match = re.search(r'(\d+)\s+Matches', content)
            if matches_match:
                return int(matches_match.group(1))
            
            return None
        except Exception as e:
            print(f"  ⚠️  Error extracting matches played: {e}")
            return None
    
    async def extract_stats(self, page: Page) -> Dict:
        """
        Extract all stats from the loaded page.
        
        Returns:
            Dictionary containing all player stats
        """
        print("  📊 Extracting stats...")
        
        # Extract rank (current and peak)
        current_rank, peak_rank = await self.extract_rank(page)
        print(f"    - Rank: {current_rank} (Peak: {peak_rank})")
        
        # Extract main stats
        kd = await self.extract_stat_value(page, 'kd')
        acs = await self.extract_stat_value(page, 'acs')
        winrate = await self.extract_stat_value(page, 'winrate')
        headshot = await self.extract_stat_value(page, 'headshot')
        
        print(f"    - K/D: {kd}")
        print(f"    - ACS: {acs}")
        print(f"    - Win%: {winrate}")
        print(f"    - HS%: {headshot}")
        
        # Extract account info
        level = await self.extract_account_level(page)
        matches = await self.extract_matches_played(page)
        
        print(f"    - Level: {level}")
        print(f"    - Matches: {matches}")
        
        # Build stats dictionary (matching team_balancer.py format)
        stats = {
            "player_name": "",  # Will be set in scrape_player()
            "rank_current": current_rank,
            "rank_peak_recent": peak_rank,
            "kd_ratio": kd or 1.0,
            "average_combat_score": int(acs) if acs else 200,
            "win_rate": winrate or 50.0,
            "headshot_rate": headshot or 20.0,
            "account_level": level or 100,
            "total_ranked_matches": matches or 50,
            "player_id": None,  # To be filled manually by admin
            "admin_skill_rating": None,  # To be filled manually by admin
            "admin_familiarity": None  # To be filled manually by admin
        }
        
        return stats
    
    async def scrape_player(self, player_name: str, tag: str) -> Dict:
        """
        Scrape a single player with human simulation.
        
        Args:
            player_name: Player name
            tag: Player tag (with or without #)
            
        Returns:
            Dictionary with player stats
            
        Raises:
            ValueError: If profile is private or not found
        """
        url = self.build_profile_url(player_name, tag)
        
        async with async_playwright() as p:
            # Launch browser with "human" options
            browser = await p.chromium.launch(
                headless=self.headless,
                slow_mo=self.slow_mo,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                ]
            )
            
            # Context with realistic User-Agent
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            page = await context.new_page()
            
            # Hide bot detection
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                window.navigator.chrome = {runtime: {}};
            """)
            
            print(f"  🌐 Navigating to: {url}")
            
            # Navigation with permissive strategy
            try:
                await page.goto(url, wait_until='domcontentloaded', timeout=15000)
            except Exception as e:
                print(f"  ⚠️  Initial timeout, continuing anyway...")
            
            # Wait a bit for JavaScript to load
            await asyncio.sleep(3)
            
            # Simulate human scroll
            await page.mouse.move(random.randint(100, 500), random.randint(100, 500))
            await self.human_delay(1000, 2000)
            
            # Wait for profile to load
            is_loaded = await self.wait_for_profile_load(page)
            
            if not is_loaded:
                await browser.close()
                raise ValueError(f"❌ Profile is private or not found: {player_name}#{tag}")
            
            # Extract stats
            stats = await self.extract_stats(page)
            stats["player_name"] = f"{player_name}#{tag}"
            
            await browser.close()
            
        return stats
    
    async def scrape_multiple_players(self, players: List[tuple]) -> List[Dict]:
        """
        Scrape multiple players with rate limiting.
        
        Args:
            players: List of (name, tag) tuples
            
        Returns:
            List of player stats dictionaries
        """
        results = []
        
        for i, (name, tag) in enumerate(players, 1):
            print(f"\n[{i}/{len(players)}] 🎮 Scraping {name}#{tag}...")
            
            try:
                stats = await self.scrape_player(name, tag)
                results.append(stats)
                print("  ✅ Success!")
                
                # Rate limiting: wait between requests
                if i < len(players):
                    wait_time = random.uniform(3, 6)
                    print(f"  ⏳ Waiting {wait_time:.1f}s before next player...")
                    await asyncio.sleep(wait_time)
                    
            except ValueError as e:
                print(f"  {e}")
                print("  ⛔ STOPPING PROGRAM")
                break
            except Exception as e:
                print(f"  ❌ Error: {e}")
                print("  ⛔ STOPPING PROGRAM")
                break
        
        return results
    
    def save_to_json(self, output_path: str):
        """Save scraped data to JSON file"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {"players": self.players_data}
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Data saved to: {output_path}")
        print(f"   Total players: {len(self.players_data)}")


def parse_players_from_file(file_path: str) -> List[tuple]:
    """
    Parse players from a text file.
    
    Format: One player per line as "PlayerName#TAG"
    
    Returns:
        List of (name, tag) tuples
    """
    players = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):  # Skip empty lines and comments
                if '#' in line:
                    name, tag = line.split('#', 1)
                    players.append((name.strip(), tag.strip()))
    return players


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Scrape Valorant player stats from tracker.gg with human simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape from a file
  python tracker_scraper.py --input players_list.txt --output data/players.json
  
  # Scrape specific players
  python tracker_scraper.py --players "Ｎｉｋｋｏ#Han" "Player2#EUW" --output data/players.json
  
  # Visible mode (see the browser for debugging)
  python tracker_scraper.py --input players_list.txt --visible

Input file format (players_list.txt):
  Ｎｉｋｋｏ#Han
  PlayerName#TAG
  AnotherPlayer#NA1
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        type=str,
        help='Path to input file containing player names (one per line: Name#TAG)'
    )
    
    parser.add_argument(
        '--players', '-p',
        type=str,
        nargs='+',
        help='List of players to scrape (format: "Name#TAG")'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='data/players_scraped.json',
        help='Output JSON file path (default: data/players_scraped.json)'
    )
    
    parser.add_argument(
        '--visible',
        action='store_true',
        help='Show browser window (non-headless mode for debugging)'
    )
    
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run in headless mode (invisible) - may not load all stats correctly'
    )
    
    args = parser.parse_args()
    
    # Parse players
    players = []
    if args.input:
        players = parse_players_from_file(args.input)
    elif args.players:
        for player_str in args.players:
            if '#' in player_str:
                name, tag = player_str.split('#', 1)
                players.append((name.strip(), tag.strip()))
    else:
        parser.error("You must provide either --input or --players")
    
    if not players:
        print("❌ No players to scrape!")
        return
    
    # By default, use visible mode because headless doesn't always load stats correctly
    # User can force headless with --headless
    use_headless = args.headless and not args.visible
    
    # Display info
    print(f"\n{'='*60}")
    print("🎮 Valorant Tracker Scraper (Human Simulation)")
    print(f"{'='*60}")
    print(f"📊 {len(players)} player(s) to scrape")
    print(f"🌐 Mode: {'Headless' if use_headless else 'Visible'}")
    if not use_headless:
        print("⚠️  Browser will open to scrape (visible mode by default)")
        print("   Use --headless for invisible mode (may miss some stats)")
    print(f"{'='*60}\n")
    
    # Create scraper with appropriate mode
    scraper = TrackerScraperHuman(headless=use_headless, slow_mo=100)
    
    # Scrape players
    try:
        results = await scraper.scrape_multiple_players(players)
        scraper.players_data = results
        
        if results:
            scraper.save_to_json(args.output)
            
            print(f"\n{'='*60}")
            print("✅ SCRAPING COMPLETED SUCCESSFULLY")
            print(f"{'='*60}")
            print(f"   File: {args.output}")
            print(f"   Players: {len(results)}")
            print(f"\n💡 Usage:")
            print(f"   python team_balancer.py --input {args.output}")
            print(f"{'='*60}\n")
        else:
            print(f"\n{'='*60}")
            print("❌ SCRAPING FAILED")
            print(f"{'='*60}")
            print("   Error: No players scraped successfully")
            print(f"{'='*60}\n")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user")
    except Exception as e:
        print(f"\n{'='*60}")
        print("❌ SCRAPING FAILED")
        print(f"{'='*60}")
        print(f"   Error: {e}")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
