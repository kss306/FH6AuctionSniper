import time
import json
import argparse
import sys
import os
import keyboard
import cv2
import numpy as np
import mss
import random

def load_config(path="config.json"):
    if not os.path.exists(path):
        print("config.json not found.")
        sys.exit(1)
    with open(path, "r") as f:
        return json.load(f)

def setup_template():
    print("opening snipping tool mode...")
    with mss.MSS() as sct:
        monitor = sct.monitors[1] 
        img = np.array(sct.grab(monitor))
    
    bgr_img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    
    window_name = "select target (drag, then press ENTER/SPACE)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    roi = cv2.selectROI(window_name, bgr_img, showCrosshair=True, fromCenter=False)
    cv2.destroyAllWindows()
    
    if roi[2] > 0 and roi[3] > 0:
        x, y, w, h = roi
        template = bgr_img[int(y):int(y+h), int(x):int(x+w)]
        cv2.imwrite("template.png", template)
        print("saved selected region as template.png")
        return True
    else:
        print("selection cancelled.")
        return False

def get_region(monitor, ratios):
    return {
        "top": int(monitor["top"] + monitor["height"] * ratios["y_ratio"]),
        "left": int(monitor["left"] + monitor["width"] * ratios["x_ratio"]),
        "width": int(monitor["width"] * ratios["w_ratio"]),
        "height": int(monitor["height"] * ratios["h_ratio"])
    }

def send_key(key, hold_sec, delay_sec):
    keyboard.press(key)
    time.sleep(hold_sec)
    keyboard.release(key)
    time.sleep(delay_sec)

def execute_search(hold_sec, delay_sec):
    send_key('enter', hold_sec, delay_sec)
    send_key('enter', hold_sec, delay_sec)

def execute_buyout(hold_sec, delay_sec):
    send_key('y', hold_sec, delay_sec)
    send_key('down', hold_sec, delay_sec)
    send_key('enter', hold_sec, delay_sec)
    send_key('enter', hold_sec, delay_sec)

def run_bot(config):
    template_path = config["template_image"]
    if not os.path.exists(template_path):
        print(f"template image {template_path} not found. opening setup...")
        if not setup_template():
            sys.exit(1)
            
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        print(f"failed to load template image: {template_path}")
        sys.exit(1)

    threshold = config.get("match_threshold", 0.8)
    fps_target = config.get("fps_target", 30)
    frame_time = 1.0 / fps_target
    timeout_sec = config.get("search_timeout_sec", 1.5)
    delay_after_esc = config.get("delay_after_esc_sec", 0.3)
    key_hold = config.get("key_hold_sec", 0.05)
    key_delay = config.get("key_delay_sec", 0.05)
    delay_before_buyout = config.get("delay_before_buyout_sec", 0.2)
    
    with mss.MSS() as sct:
        monitor = sct.monitors[1]
        region = get_region(monitor, config["scan_region"])
        
        while True:
            print("\n\n--- NEW SESSION ---")
            print("bot is ready! tab into your game now.")
            print("press 'F4' to start the sniper loop.")
            print("press 'ctrl+q' at any time to quit.")
            
            while True:
                if keyboard.is_pressed('f4'):
                    break
                if keyboard.is_pressed('ctrl+q'):
                    print("\nExiting...")
                    sys.exit(0)
                time.sleep(0.05)
            
            print("starting in 3...")
            time.sleep(1)
            print("2...")
            time.sleep(1)
            print("1...")
            time.sleep(1)
            print("GO!")

            start_time_global = time.time()
            search_count = 0
            
            while True:
                if keyboard.is_pressed('ctrl+q'):
                    print("\nExiting...")
                    sys.exit(0)
                    
                search_count += 1
                elapsed_sec = int(time.time() - start_time_global)
                mins, secs = divmod(elapsed_sec, 60)
                time_str = f"{mins:02d}:{secs:02d}"
                
                sys.stdout.write(f"\r[Searches: {search_count} | Time: {time_str}] Status: Searching...          ")
                sys.stdout.flush()
                
                execute_search(key_hold, key_delay)
                
                sys.stdout.write(f"\r[Searches: {search_count} | Time: {time_str}] Status: Waiting for results...")
                sys.stdout.flush()
                
                search_start_t = time.time()
                found_car = False
                
                # waiting for sample to appear OR timeout
                while time.time() - search_start_t < timeout_sec:
                    if keyboard.is_pressed('ctrl+q'):
                        print("\nExiting...")
                        sys.exit(0)
                        
                    loop_start_t = time.perf_counter()
                    
                    # grab screen
                    sct_img = sct.grab(region)
                    img = np.array(sct_img)
                    gray_img = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
                    
                    # match template
                    res = cv2.matchTemplate(gray_img, template, cv2.TM_CCOEFF_NORMED)
                    loc = np.where(res >= threshold)
                    
                    if len(loc[0]) > 0:
                        found_car = True
                        break
                    
                    # maintain fps
                    elapsed = time.perf_counter() - loop_start_t
                    sleep_t = frame_time - elapsed
                    if sleep_t > 0:
                        time.sleep(sleep_t)
                
                if found_car:
                    print(f"\n\n>>> CAR FOUND! <<<")
                    print(f"Total Searches : {search_count}")
                    print(f"Elapsed Time   : {time_str}")
                    print(f"Waiting {delay_before_buyout}s before buyout macro...")
                    time.sleep(delay_before_buyout)
                    execute_buyout(key_hold, key_delay)
                    print("Buyout macro executed! Returning to standby mode...")
                    time.sleep(1.0)
                    break # go back to NEW SESSION
                else:
                    sys.stdout.write(f"\r[Searches: {search_count} | Time: {time_str}] Status: No car. Resetting...  ")
                    sys.stdout.flush()
                    send_key('esc', key_hold, key_delay)
                    # wait for the search menu to become fully active again before searching again
                    time.sleep(delay_after_esc)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--setup", action="store_true", help="open snipping tool mode to select template")
    args = parser.parse_args()
    
    if args.setup:
        setup_template()
    else:
        cfg = load_config()
        run_bot(cfg)
