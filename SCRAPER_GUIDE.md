# 🎮 Valorant Tracker Scraper

**Automated player stats scraper for tracker.gg with human-like browser simulation**

## 📋 Overview

This scraper automatically collects Valorant player statistics from tracker.gg by simulating human browser behavior. It's designed to work with the Valorant Team Balancer to automatically fetch player data without manual input.

## ✨ Features

- **Human Behavior Simulation**: Random delays, mouse movements, anti-bot detection
- **Complete Stats Extraction**:
  - Current Rank & Peak Rank (e.g., "Ascendant 2", "Immortal 1")
  - K/D Ratio
  - Average Combat Score (ACS)
  - Win Rate %
  - Headshot Rate %
  - Account Level
  - Matches played this act
- **Error Handling**: Automatically stops if profile is private or not found
- **Rate Limiting**: 3-6 second delays between players to avoid detection
- **Unicode Support**: Works with special characters in player names (e.g., Ｎｉｋｋｏ)

## 🚀 Usage

### Basic Commands

```bash
# Scrape from a file containing player names
python tracker_scraper.py --input players_list.txt --output data/players.json

# Scrape specific players directly
python tracker_scraper.py --players "PlayerName#TAG" "Player2#EUW" --output data/players.json

# Visible mode (see browser for debugging)
python tracker_scraper.py --input players_list.txt --visible
```

### Input File Format

Create a text file (e.g., `players_list.txt`) with one player per line:

```
Ｎｉｋｋｏ#Han
PlayerName#TAG
AnotherPlayer#NA1
SomeGuy#EUW
```

### Command-Line Options

| Option | Description |
|--------|-------------|
| `--input`, `-i` | Path to input file with player names |
| `--players`, `-p` | List of players to scrape (space-separated) |
| `--output`, `-o` | Output JSON file path (default: `data/players_scraped.json`) |
| `--visible` | Show browser window (default mode for better stats loading) |
| `--headless` | Run in invisible mode (may miss some stats) |

## 📊 Output Format

The scraper generates a JSON file compatible with `team_balancer.py`:

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
      "player_id": null,
      "admin_skill_rating": null,
      "admin_familiarity": null
    }
  ]
}
```

**Admin Fields (to be filled manually):**
- `player_id`: Unique identifier for the player (optional)
- `admin_skill_rating`: Manual skill rating from 1-10 (optional)
- `admin_familiarity`: Team familiarity rating from 1-5 (optional)

These fields are set to `null` by default and can be filled in later to fine-tune team balancing.

## 🔧 How It Works

### 1. **URL Encoding**
The scraper uses `urllib.parse.quote()` to properly encode player names with Unicode characters:
```python
# Input: "Ｎｉｋｋｏ#Han"
# Encoded URL: .../riot/%EF%BC%AE%EF%BD%89%EF%BD%8B%EF%BD%8B%EF%BD%8F%23Han/overview
```

### 2. **Browser Automation**
Uses Playwright to launch a real Chromium browser:
- **Anti-Detection**: Hides webdriver property, adds Chrome runtime
- **User-Agent**: Spoofs as Chrome 120 on Windows
- **Viewport**: 1920x1080 resolution
- **Slow Motion**: 100ms delays between actions

### 3. **JavaScript Rendering**
Tracker.gg is a heavily JavaScript-rendered site:
- Waits for `domcontentloaded` event
- Additional 8-second wait for JavaScript execution
- Doesn't wait for all ads to load (networkidle would timeout)

### 4. **Data Extraction**
Uses two methods for robust extraction:

**Method 1 - CSS Selectors:**
```python
# Find stat elements with specific titles
stats_elements = await page.query_selector_all('.stat .numbers')
# Extract value from .value span
value_el = await stat_el.query_selector('.value')
```

**Method 2 - Regex Fallback:**
```python
# If selectors fail, use regex on HTML content
pattern = r'title="K/D Ratio"[^>]*>.*?<span[^>]*class="value"[^>]*>(\d+\.\d+)'
```

### 5. **Private Profile Detection**
Checks page content for specific strings:
```python
if 'profile is private' in content.lower():
    raise ValueError("Profile is private")
```
Program stops immediately to prevent wasting time.

### 6. **Rate Limiting**
Random delays between players:
```python
wait_time = random.uniform(3, 6)  # 3-6 seconds
await asyncio.sleep(wait_time)
```

## ⚠️ Important Notes

### Why Visible Mode by Default?
Headless mode sometimes doesn't fully execute JavaScript, resulting in missing stats. Visible mode (browser window opens) ensures all data loads correctly.

### Rate Limiting
The scraper intentionally waits 3-6 seconds between players to:
- Avoid triggering anti-bot measures
- Simulate human browsing patterns
- Respect tracker.gg's servers

### Private Profiles
If a profile is private or not found, the scraper will:
1. Display an error message
2. **Stop immediately** (doesn't continue to next player)
3. This prevents wasting time on inaccessible profiles

## 🐛 Troubleshooting

### Stats show `None` values
- **Solution**: Use `--visible` mode instead of `--headless`
- **Reason**: JavaScript doesn't fully execute in headless mode

### "Profile is private" error
- **Cause**: Player has set their profile to private on tracker.gg
- **Solution**: Ask the player to make their profile public
- **Note**: Program stops when encountering private profile

### Timeout errors
- **Cause**: Tracker.gg loads many ads (254+ network requests)
- **Solution**: Scraper already handles this with `domcontentloaded` + manual wait
- **If persists**: Increase wait time in code (line ~75: `await asyncio.sleep(8)`)

### Browser doesn't close after scraping
- **Cause**: Error occurred during scraping
- **Solution**: Manually close browser window
- **Prevention**: Check player names are formatted correctly ("Name#TAG")

## 🔗 Integration with Team Balancer

After scraping, use the data with the team balancer:

```bash
# 1. Scrape players
python tracker_scraper.py --input players_list.txt --output data/players.json

# 2. Balance teams
python team_balancer.py --input data/players.json --num-teams 2

# 3. Analyze balance
python analyze_balance.py data/players.json output/teams.json
```

## 📦 Dependencies

- Python 3.12+
- Playwright (with Chromium browser)
- asyncio (built-in)
- urllib (built-in)

Install dependencies:
```bash
pip install playwright
playwright install chromium
```

## 🎯 Example Workflow

```bash
# Create input file
echo "Ｎｉｋｋｏ#Han" > players.txt
echo "Player2#EUW" >> players.txt

# Scrape players (visible mode for debugging)
python tracker_scraper.py --input players.txt --output data/scraped.json --visible

# Balance teams
python team_balancer.py --input data/scraped.json --num-teams 2

# Done! Teams are in output/teams.json
```

## 📝 Notes

- **Encoding**: All files use UTF-8 to support Unicode characters
- **Execution Time**: ~15-20 seconds per player (including rate limiting)
- **Browser**: Chromium is downloaded automatically by Playwright (~240 MB)
- **GitHub Ready**: Code is in English with proper documentation

## 🚨 Error Messages

| Message | Meaning | Action |
|---------|---------|--------|
| `❌ Profile is private or not found` | Player profile is inaccessible | Check player name/tag, ask player to make profile public |
| `⚠️ Timeout - profile took too long to load` | Network/server issue | Retry, check internet connection |
| `⚠️ Header not found, but continuing...` | Page layout different than expected | Normal, scraper continues anyway |
| `⛔ STOPPING PROGRAM` | Critical error encountered | Check error message above, fix issue |

---

**Made with ❤️ for Valorant tournament organizers**
