#!/usr/bin/env python3
import requests
import os
import sys
import argparse
import re

def parse_github_url(url):
    """Parse GitHub URL to extract owner and repo"""
    # Remove trailing slash if present
    url = url.rstrip('/')
    
    # Match GitHub URL patterns
    patterns = [
        r'https?://github\.com/([^/]+)/([^/]+)',  # https://github.com/owner/repo
        r'github\.com/([^/]+)/([^/]+)',           # github.com/owner/repo
        r'([^/]+)/([^/]+)'                        # owner/repo
    ]
    
    for pattern in patterns:
        match = re.match(pattern, url)
        if match:
            return match.group(1), match.group(2)
    
    raise ValueError(f"Invalid GitHub URL format: {url}")

def create_issue(owner, repo, title, body, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    data = {
        "title": title,
        "body": body
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        issue_data = response.json()
        print("✅ Issue created successfully!")
        print(f"📄 Title: {issue_data['title']}")
        print(f"🔗 URL: {issue_data['html_url']}")
        print(f"📝 Issue #{issue_data['number']}")
    else:
        print("❌ Failed to create issue:", response.status_code)
        print(response.json())
        sys.exit(1)

def interactive_wizard():
    """Interactive wizard for creating GitHub issues"""
    print("🚀 GitHub Issue Creator - Interactive Mode")
    print("=" * 45)
    
    # Get repository URL
    while True:
        repo_url = input("📂 Enter GitHub repository URL: ").strip()
        if repo_url:
            try:
                owner, repo = parse_github_url(repo_url)
                print(f"✅ Repository: {owner}/{repo}")
                break
            except ValueError as e:
                print(f"❌ {e}")
                print("💡 Try formats like: https://github.com/owner/repo or owner/repo")
        else:
            print("❌ Repository URL cannot be empty")
    
    # Get issue title
    while True:
        title = input("📝 Enter issue title: ").strip()
        if title:
            break
        print("❌ Title cannot be empty")
    
    # Get issue body
    print("📄 Enter issue description:")
    print("    💡 Type your description on one line (you can use \\n for line breaks)")
    print("    💡 Or press Enter to open your default editor for multi-line input")
    print()
    
    choice = input("Choose: (t)ype here, (e)ditor, or just start typing: ").strip().lower()
    
    if choice == 'e' or choice == 'editor':
        # Detect available editors
        import tempfile
        import subprocess
        
        editors = [
            ('nano', 'Nano (beginner-friendly terminal editor)'),
            ('vim', 'Vim (advanced terminal editor)'),
            ('vi', 'Vi (basic terminal editor)'),
            ('code --wait', 'VS Code (if installed)'),
            ('open -W -a TextEdit', 'TextEdit (macOS default)')
        ]
        
        available_editors = []
        for editor_cmd, description in editors:
            try:
                # Test if editor is available
                test_cmd = editor_cmd.split()[0]
                subprocess.run(['which', test_cmd], capture_output=True, check=True)
                available_editors.append((editor_cmd, description))
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        if not available_editors:
            print("❌ No suitable editors found. Please type description directly:")
            body = input("Description: ").strip()
        else:
            print("📝 Available editors:")
            for i, (cmd, desc) in enumerate(available_editors, 1):
                print(f"   {i}. {desc}")
            print()
            
            while True:
                try:
                    choice_num = input(f"Choose editor (1-{len(available_editors)}): ").strip()
                    editor_index = int(choice_num) - 1
                    if 0 <= editor_index < len(available_editors):
                        chosen_editor = available_editors[editor_index][0]
                        break
                    else:
                        print(f"❌ Please enter a number between 1 and {len(available_editors)}")
                except ValueError:
                    print("❌ Please enter a valid number")
            
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as tmp_file:
                tmp_file.write("# Enter your issue description below (delete this line)\n")
                tmp_file.flush()
                
                try:
                    print(f"🚀 Opening {available_editors[editor_index][1]}...")
                    subprocess.run(chosen_editor.split() + [tmp_file.name], check=True)
                    
                    # Read the content back
                    with open(tmp_file.name, 'r') as f:
                        body = f.read()
                    # Remove the comment line if it's still there
                    lines = body.split('\n')
                    if lines and lines[0].startswith('# Enter your issue description'):
                        lines = lines[1:]
                    body = '\n'.join(lines).strip()
                    
                except subprocess.CalledProcessError:
                    print("❌ Editor failed. Please type description directly:")
                    body = input("Description: ").strip()
                finally:
                    os.unlink(tmp_file.name)
    else:
        # Single line input with \n support
        if choice and choice != 't' and choice != 'type':
            # They started typing, use that as the input
            body = choice
        else:
            body = input("Description: ").strip()
        
        # Replace \n with actual newlines
        body = body.replace('\\n', '\n')
    
    if not body:
        body = input("📄 Description cannot be empty, enter something: ").strip()
        if not body:
            print("❌ Description is required")
            sys.exit(1)
    
    # Get token
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        print("🔑 Using GitHub token from environment variable")
    else:
        print("🔑 GitHub token not found in GITHUB_TOKEN environment variable")
        print("💡 You can either:")
        print("   1. Set it: export GITHUB_TOKEN='your_token'")
        print("   2. Enter it below (just for this session)")
        token = input("🔑 Enter GitHub token (or press Ctrl+C to exit): ").strip()
        if not token:
            print("❌ GitHub token is required")
            sys.exit(1)
    
    # Confirm before creating
    print("\n" + "=" * 45)
    print("📋 Issue Summary:")
    print(f"Repository: {owner}/{repo}")
    print(f"Title: {title}")
    print(f"Description: {body[:100]}{'...' if len(body) > 100 else ''}")
    print("=" * 45)
    
    confirm = input("✅ Create this issue? (y/N): ").strip().lower()
    if confirm in ['y', 'yes']:
        create_issue(owner, repo, title, body, token)
    else:
        print("❌ Issue creation cancelled")

def main():
    # Check if running in interactive mode (no arguments provided)
    if len(sys.argv) == 1:
        interactive_wizard()
        return
    
    # Command-line mode
    parser = argparse.ArgumentParser(
        description="🚀 GitHub Issue Creator - Create issues easily!",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
💡 Usage Examples:
  
  Interactive Mode (easiest):
    ./create_issue.py                    # Launches step-by-step wizard
    ./create_issue.py -i                 # Force interactive mode
  
  Command Line Mode:
    ./create_issue.py "github.com/user/repo" "Bug: App crashes" "The app crashes on startup"
    ./create_issue.py "https://github.com/microsoft/vscode" "Feature request" "Add dark mode"
  
  With custom token:
    ./create_issue.py "user/repo" "Title" "Description" --token YOUR_TOKEN

🔑 GitHub Token:
  Set environment variable: export GITHUB_TOKEN="your_token_here"
  Or use --token flag for one-time use
  
✨ Pro tip: Just run './create_issue.py' for the friendly wizard!
        """
    )
    
    parser.add_argument("repo_url", nargs='?', 
                       help="GitHub repository URL (https://github.com/owner/repo, github.com/owner/repo, or owner/repo)")
    parser.add_argument("title", nargs='?', 
                       help="Issue title")
    parser.add_argument("body", nargs='?', 
                       help="Issue description/body")
    parser.add_argument("--token", 
                       help="GitHub personal access token (or set GITHUB_TOKEN environment variable)")
    parser.add_argument("--interactive", "-i", action="store_true", 
                       help="Launch interactive wizard mode")
    
    args = parser.parse_args()
    
    # Force interactive mode if --interactive flag is used
    if args.interactive or not all([args.repo_url, args.title, args.body]):
        interactive_wizard()
        return
    
    # Get token from argument or environment variable
    token = args.token or os.environ.get("GITHUB_TOKEN")
    if token and not args.token:
        print("🔑 Using GitHub token from environment variable")
    
    if not token:
        print("🔑 GitHub token not found")
        print("💡 You can either:")
        print("   1. Use: ./create_issue.py ... --token 'your_token'")
        print("   2. Set: export GITHUB_TOKEN='your_token'")
        print("   3. Enter it below (just for this session)")
        token = input("🔑 Enter GitHub token (or press Ctrl+C to exit): ").strip()
        if not token:
            print("❌ Error: GitHub token is required to create issues.")
            sys.exit(1)
    
    try:
        owner, repo = parse_github_url(args.repo_url)
        print(f"📂 Repository: {owner}/{repo}")
        create_issue(owner, repo, args.title, args.body, token)
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("💡 Expected formats:")
        print("   - https://github.com/owner/repo")
        print("   - github.com/owner/repo")
        print("   - owner/repo")
        sys.exit(1)

if __name__ == "__main__":
    main()
