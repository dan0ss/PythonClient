#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
import shutil
from pathlib import Path

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

ROOT_DIR = Path(__file__).resolve().parent
DASHBOARD_DIR = ROOT_DIR / "dashboard"

def print_header(msg):
    print(f"{Colors.HEADER}{Colors.BOLD}=== {msg} ==={Colors.ENDC}")

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.ENDC}")

def print_error(msg):
    print(f"{Colors.FAIL}✗ {msg}{Colors.ENDC}")

def run_command(cmd, cwd=None, shell=False):
    try:
        subprocess.check_call(cmd, cwd=cwd, shell=shell)
        return True
    except subprocess.CalledProcessError:
        return False
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        return False

def check_requirements():
    """Check if basic requirements are met."""
    missing = []
    if not shutil.which("npm"):
        missing.append("npm (Node.js)")
    if not shutil.which("python3") and not shutil.which("python"):
        missing.append("python")
    
    if missing:
        print_error(f"Missing requirements: {', '.join(missing)}")
        return False
    return True

def setup_project():
    """Install dependencies for both backend and frontend."""
    print_header("Setting up Project")
    
    # Python setup
    print(f"\n{Colors.BLUE}Installing Python dependencies...{Colors.ENDC}")
    if run_command([sys.executable, "-m", "pip", "install", "-e", "."]):
        print_success("Python dependencies installed")
    else:
        print_error("Failed to install Python dependencies")
        return

    # Dashboard setup
    print(f"\n{Colors.BLUE}Installing Dashboard dependencies...{Colors.ENDC}")
    if run_command(["npm", "install"], cwd=DASHBOARD_DIR):
        print_success("Dashboard dependencies installed")
    else:
        print_error("Failed to install Dashboard dependencies")
        return
        
    print(f"\n{Colors.GREEN}{Colors.BOLD}Setup complete!{Colors.ENDC}")

def run_scraper():
    """Run the SERP scraper."""
    print_header("Running SERP Scraper")
    
    keywords_file = ROOT_DIR / "inputs" / "keywords.txt"
    if not keywords_file.exists():
        print_error(f"Keywords file not found at: {keywords_file}")
        print(f"{Colors.WARNING}Please create inputs/keywords.txt with one keyword per line.{Colors.ENDC}")
        return

    run_command([sys.executable, "run_google_serp.py"])

def start_dashboard():
    """Start the dashboard web server."""
    print_header("Starting Dashboard")
    print(f"{Colors.BLUE}Opening dashboard at http://localhost:5173{Colors.ENDC}")
    run_command(["npm", "run", "dev", "--", "--open"], cwd=DASHBOARD_DIR)

def show_menu():
    """Interactive menu."""
    while True:
        print(f"\n{Colors.BOLD}SERP Analysis Tool CLI{Colors.ENDC}")
        print("1. Run Scraper (collect data)")
        print("2. Start Dashboard (view data)")
        print("3. Setup Project (install dependencies)")
        print("q. Quit")
        
        choice = input(f"\n{Colors.BLUE}Select an option: {Colors.ENDC}").strip().lower()
        
        if choice == '1':
            run_scraper()
        elif choice == '2':
            start_dashboard()
        elif choice == '3':
            setup_project()
        elif choice in ['q', 'quit', 'exit']:
            break
        else:
            print_error("Invalid option")

def main():
    parser = argparse.ArgumentParser(description="Manage SERP Analysis Tool")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    subparsers.add_parser('run', help='Run the SERP scraper')
    subparsers.add_parser('dashboard', help='Start the visualization dashboard')
    subparsers.add_parser('setup', help='Install all dependencies')
    
    args = parser.parse_args()
    
    if not check_requirements():
        sys.exit(1)

    if args.command == 'run':
        run_scraper()
    elif args.command == 'dashboard':
        start_dashboard()
    elif args.command == 'setup':
        setup_project()
    else:
        # If no arguments provided, show interactive menu
        show_menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye!")

