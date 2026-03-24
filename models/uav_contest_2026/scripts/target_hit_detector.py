#!/usr/bin/env python3
"""
Target Hit Detector for UAV Contest 2026

This script monitors contact sensors on targets (F1-F5) and publishes
a message when a tennis ball hits a target.

Replaces TouchPlugin which has issues with nested model detection.

Usage:
    python3 target_hit_detector.py

Topics published:
    /f1/hit, /f2/hit, /f3/hit, /f4/hit, /f5/hit - gz.msgs.Boolean (data: true when hit)
"""

import subprocess
import threading
import time
import re
import signal
import sys

# Target configurations
TARGETS = {
    'f1': {
        'contact_topic': '/world/default/model/f1/link/link/sensor/sensor_contact/contact',
        'hit_topic': '/f1/hit',
        'hit_count': 0,
        'last_hit_time': 0,
    },
    'f2': {
        'contact_topic': '/world/default/model/f2/link/link/sensor/sensor_contact/contact',
        'hit_topic': '/f2/hit',
        'hit_count': 0,
        'last_hit_time': 0,
    },
    'f3': {
        'contact_topic': '/world/default/model/f3/link/link/sensor/sensor_contact/contact',
        'hit_topic': '/f3/hit',
        'hit_count': 0,
        'last_hit_time': 0,
    },
    'f4': {
        'contact_topic': '/world/default/model/f4/link/link/sensor/sensor_contact/contact',
        'hit_topic': '/f4/hit',
        'hit_count': 0,
        'last_hit_time': 0,
    },
    'f5': {
        'contact_topic': '/world/default/model/f5/link/link/sensor/sensor_contact/contact',
        'hit_topic': '/f5/hit',
        'hit_count': 0,
        'last_hit_time': 0,
    },
}

# Tennis ball pattern to match in collision names
TENNIS_BALL_PATTERN = re.compile(r'tennis_ball_\d+.*ball_\d+_collision')

# Minimum time between hit detections (seconds) to avoid duplicate messages
# Set to 2 seconds to avoid counting bounces as multiple hits
HIT_COOLDOWN = 2.0

running = True


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    global running
    print("\n[INFO] Shutting down target hit detector...")
    running = False
    sys.exit(0)


def publish_hit(target_name: str):
    """Publish hit message for a target"""
    topic = TARGETS[target_name]['hit_topic']
    try:
        subprocess.run(
            ['gz', 'topic', '-t', topic, '-m', 'gz.msgs.Boolean', '-p', 'data: true'],
            capture_output=True,
            timeout=1
        )
        print(f"[HIT] {target_name.upper()} - Tennis ball hit detected! Published to {topic}")
    except Exception as e:
        print(f"[ERROR] Failed to publish to {topic}: {e}")


def monitor_target(target_name: str):
    """Monitor a single target's contact sensor"""
    global running
    config = TARGETS[target_name]
    topic = config['contact_topic']
    
    print(f"[INFO] Monitoring {target_name.upper()} on {topic}")
    
    while running:
        try:
            # Subscribe to contact topic and get one message
            result = subprocess.run(
                ['gz', 'topic', '-e', '-t', topic, '-n', '1'],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0 and result.stdout:
                # Check if tennis ball is in the contact
                if TENNIS_BALL_PATTERN.search(result.stdout):
                    current_time = time.time()
                    # Check cooldown to avoid duplicate hits
                    if current_time - config['last_hit_time'] > HIT_COOLDOWN:
                        config['last_hit_time'] = current_time
                        config['hit_count'] += 1
                        publish_hit(target_name)
                        
        except subprocess.TimeoutExpired:
            # No contact data, continue monitoring
            pass
        except Exception as e:
            if running:
                print(f"[WARN] Error monitoring {target_name}: {e}")
            time.sleep(0.5)


def print_status():
    """Print current hit status periodically"""
    global running
    while running:
        time.sleep(10)
        if running:
            status = " | ".join([f"{t.upper()}: {TARGETS[t]['hit_count']}" for t in TARGETS])
            print(f"[STATUS] Hit counts: {status}")


def main():
    """Main entry point"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("=" * 60)
    print("UAV Contest 2026 - Target Hit Detector")
    print("=" * 60)
    print("[INFO] Monitoring targets F1-F5 for tennis ball hits")
    print("[INFO] Press Ctrl+C to stop")
    print("")
    
    # Check if Gazebo is running
    try:
        result = subprocess.run(['gz', 'topic', '-l'], capture_output=True, timeout=5)
        if result.returncode != 0:
            print("[ERROR] Gazebo doesn't seem to be running. Start simulation first.")
            return
    except Exception as e:
        print(f"[ERROR] Cannot connect to Gazebo: {e}")
        return
    
    # Start monitoring threads for each target
    threads = []
    for target_name in TARGETS:
        t = threading.Thread(target=monitor_target, args=(target_name,), daemon=True)
        t.start()
        threads.append(t)
    
    # Start status thread
    status_thread = threading.Thread(target=print_status, daemon=True)
    status_thread.start()
    
    # Keep main thread alive
    try:
        while running:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    
    print("[INFO] Target hit detector stopped.")


if __name__ == '__main__':
    main()
