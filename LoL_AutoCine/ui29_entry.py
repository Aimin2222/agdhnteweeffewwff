"""Double-click entry point for the in-app UI29 WebView2 comparison."""
import sys

from app import main


if __name__ == "__main__":
    if "--ui29-backend" not in sys.argv and "--ui29" not in sys.argv:
        sys.argv.insert(1, "--ui29")
    main()
