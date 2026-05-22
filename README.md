# Forza Horizon 6 Auction House Sniper

lightweight script that scans your screen for the "Y - Buyout" prompt (or any other successful auction indicator). 

the bot works by hitting `Enter -> Enter` to search. it then waits up to X seconds. 
if it sees the "Y" prompt, it executes the buyout macro instantly (`Y -> Down -> Enter -> Enter`) and stops. 
if the timeout passes without seeing the "Y" prompt, it assumes the search failed, presses `Esc` to back out, and searches again.

it doesn't hook into the game or change settings, it just simulates keyboard inputs based on what's visible on the screen.

uses opencv for fast template matching.

## setup

```bash
pip install -r requirements.txt
```

## config options (`config.json`)

- `scan_region`: ratios (0.0 to 1.0) of where to look on screen. leave as `x:0, y:0, w:1, h:1` for full screen. this makes it independent of your monitor resolution (1080p vs 4k).
- `match_threshold`: how strictly the image has to match the template (0.0 to 1.0). default `0.8` is usually perfect.
- `fps_target`: how many times per second to scan the screen while waiting. default `30`.
- `search_timeout_sec`: how long to wait for the auction to load before giving up and pressing `ESC`. (default: `1.5`s)
- `delay_after_esc_sec`: how long to wait after pressing `ESC` before starting the next search. gives the "No auctions found" popup time to fade out. (default: `0.6`s)
- `key_hold_sec`: how long to physically hold a key down before releasing it. prevents the game from swallowing inputs. (default: `0.2`s)
- `key_delay_sec`: how long to wait after releasing a key before pressing the next one. (default: `0.2`s)
- `delay_before_buyout_sec`: delay between finding the car and pressing the first `Y` button. gives the game UI time to become responsive. (default: `0.2`s)

## usage

1. start the bot for the first time:
```bash
python main.py
```
since you don't have a template yet, it will open your screen in a snipping-tool like view. 
- click and drag a box around the `[Y] Auktionsoptionen` (or any other UI element that ONLY appears when a car is found).
- press `ENTER` or `SPACE` to save it. 

2. the bot will tell you it's ready! tab into your game.
3. go to the auction house search menu.
4. press `F4` to start the sniper loop!
(you can always re-do the snipping tool by running `python main.py --setup`).

press `ctrl+q` to quit the script at any time.
