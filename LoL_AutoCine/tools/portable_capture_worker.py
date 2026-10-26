"""Frozen entry point for the existing isolated WGC capture worker."""
import argparse
import sys
import traceback

from core.capture_worker import run


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--memory', required=True)
    parser.add_argument('--title', required=True)
    args = parser.parse_args()
    try:
        run(args.memory, args.title)
    except Exception:
        traceback.print_exc()
        sys.stderr.flush()
        raise SystemExit(2)


if __name__ == '__main__':
    main()
