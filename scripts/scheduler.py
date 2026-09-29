import time

from datetime import datetime

import scripts.run_pipeline as run_pipeline

INTERVAL_SECONDS = 3600  


def main():
    print("Scheduler started. Press Ctrl+C to stop.")
    next_run = time.time()
    try:
        while True:
            print(f"[{datetime.now():%H:%M:%S}] Running pipeline...")
            try:
                run_pipeline.run()
                print("Done.")
            except Exception as e:
                print(f"Run failed: {e} (see pipeline.log)")

            next_run += INTERVAL_SECONDS
            wait = max(0, next_run - time.time())
            print(f"Next run at {datetime.fromtimestamp(next_run):%H:%M:%S}")
            time.sleep(wait)
    except KeyboardInterrupt:
        print("Scheduler stopped.")


if __name__ == "__main__":
    main()