#!/usr/bin/env python3
import requests
import os
import sys
import argparse
import re
import json

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

def create_batch_issues(owner, repo, batch_file, token):
    """Create multiple issues from a JSON batch file"""
    try:
        with open(batch_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: Batch file '{batch_file}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in batch file: {e}")
        sys.exit(1)
    
    if 'issues' not in data:
        print("❌ Error: Batch file must contain an 'issues' array")
        sys.exit(1)
    
    issues = data['issues']
    total_issues = len(issues)
    
    if total_issues == 0:
        print("❌ No issues found in batch file")
        sys.exit(1)
    
    print(f"🚀 Creating {total_issues} issues in {owner}/{repo}")
    print("=" * 50)
    
    successful = 0
    failed = 0
    
    for i, issue in enumerate(issues, 1):
        try:
            # Validate required fields
            if 'title' not in issue or 'description' not in issue:
                print(f"❌ Issue {i}: Missing title or description")
                failed += 1
                continue
            
            title = issue['title']
            description = issue['description']
            
            print(f"📝 Creating issue {i}/{total_issues}: {title[:50]}...")
            
            # Create the issue
            url = f"https://api.github.com/repos/{owner}/{repo}/issues"
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json"
            }
            data = {
                "title": title,
                "body": description
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 201:
                issue_data = response.json()
                print(f"✅ Issue #{issue_data['number']}: {title}")
                print(f"   🔗 {issue_data['html_url']}")
                successful += 1
            else:
                print(f"❌ Failed to create issue: {response.status_code}")
                print(f"   Error: {response.json().get('message', 'Unknown error')}")
                failed += 1
            
            # Small delay to avoid rate limiting
            import time
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ Issue {i}: Error - {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"🎉 Batch creation complete!")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {total_issues}")

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
    
    # Ask about batch mode
    print("\n📋 Choose creation mode:")
    print("   1. Single issue (standard)")
    print("   2. Batch issues from JSON file")
    
    while True:
        mode_choice = input("Choose mode (1 or 2): ").strip()
        if mode_choice in ['1', '2']:
            break
        print("❌ Please enter 1 or 2")
    
    if mode_choice == '2':
        # Batch mode
        batch_file = None
        while not batch_file:
            print("\n📁 Batch file options:")
            print("   1. Type file path or partial name")
            print("   2. Browse current directory")
            print("   3. List .json files in current directory")
            print("   4. Search for files by name")
            
            file_choice = input("Choose option (1-4): ").strip()
            
            if file_choice == '1':
                user_input = input("📁 Enter file path or partial filename: ").strip()
                if not user_input:
                    continue
                
                # Check if it's an exact path first
                if os.path.exists(user_input):
                    batch_file = user_input
                else:
                    # Try to find files matching the partial name
                    try:
                        all_files = [f for f in os.listdir('.') if os.path.isfile(f)]
                        matching_files = [f for f in all_files if user_input.lower() in f.lower()]
                        
                        if not matching_files:
                            print(f"❌ No files found matching '{user_input}'")
                            continue
                        elif len(matching_files) == 1:
                            batch_file = matching_files[0]
                            print(f"✅ Found: {batch_file}")
                        else:
                            print(f"\n� Found {len(matching_files)} files matching '{user_input}':")
                            for i, file in enumerate(matching_files, 1):
                                print(f"   {i}. {file}")
                            
                            try:
                                choice = int(input(f"\nChoose file (1-{len(matching_files)}) or 0 to try again: ").strip())
                                if choice == 0:
                                    continue
                                elif 1 <= choice <= len(matching_files):
                                    batch_file = matching_files[choice - 1]
                                else:
                                    print("❌ Invalid choice")
                                    continue
                            except ValueError:
                                print("❌ Please enter a valid number")
                                continue
                    except Exception as e:
                        print(f"❌ Error searching files: {e}")
                        continue
                        
            elif file_choice == '2':
                print("\n📂 Files in current directory:")
                try:
                    files = [f for f in os.listdir('.') if os.path.isfile(f)]
                    if files:
                        for i, file in enumerate(files, 1):
                            print(f"   {i}. {file}")
                        
                        try:
                            choice = int(input(f"\nChoose file (1-{len(files)}) or 0 to cancel: ").strip())
                            if choice == 0:
                                continue
                            elif 1 <= choice <= len(files):
                                batch_file = files[choice - 1]
                            else:
                                print("❌ Invalid choice")
                                continue
                        except ValueError:
                            print("❌ Please enter a valid number")
                            continue
                    else:
                        print("❌ No files found in current directory")
                        continue
                except Exception as e:
                    print(f"❌ Error listing files: {e}")
                    continue
                    
            elif file_choice == '3':
                print("\n📄 JSON files in current directory:")
                try:
                    json_files = [f for f in os.listdir('.') if f.endswith('.json')]
                    if json_files:
                        for i, file in enumerate(json_files, 1):
                            print(f"   {i}. {file}")
                        
                        try:
                            choice = int(input(f"\nChoose JSON file (1-{len(json_files)}) or 0 to cancel: ").strip())
                            if choice == 0:
                                continue
                            elif 1 <= choice <= len(json_files):
                                batch_file = json_files[choice - 1]
                            else:
                                print("❌ Invalid choice")
                                continue
                        except ValueError:
                            print("❌ Please enter a valid number")
                            continue
                    else:
                        print("❌ No JSON files found in current directory")
                        continue
                except Exception as e:
                    print(f"❌ Error listing JSON files: {e}")
                    continue
                    
            elif file_choice == '4':
                search_term = input("🔍 Enter search term for filename: ").strip()
                if not search_term:
                    continue
                    
                try:
                    all_files = [f for f in os.listdir('.') if os.path.isfile(f)]
                    matching_files = [f for f in all_files if search_term.lower() in f.lower()]
                    
                    if not matching_files:
                        print(f"❌ No files found containing '{search_term}'")
                        continue
                    else:
                        print(f"\n🔍 Found {len(matching_files)} files containing '{search_term}':")
                        for i, file in enumerate(matching_files, 1):
                            print(f"   {i}. {file}")
                        
                        try:
                            choice = int(input(f"\nChoose file (1-{len(matching_files)}) or 0 to search again: ").strip())
                            if choice == 0:
                                continue
                            elif 1 <= choice <= len(matching_files):
                                batch_file = matching_files[choice - 1]
                            else:
                                print("❌ Invalid choice")
                                continue
                        except ValueError:
                            print("❌ Please enter a valid number")
                            continue
                except Exception as e:
                    print(f"❌ Error searching files: {e}")
                    continue
            else:
                print("❌ Please enter 1, 2, 3, or 4")
                continue
        
        # At this point, batch_file should contain a valid file path
        if batch_file and os.path.exists(batch_file):
            # Get token for batch mode
            token = os.environ.get("GITHUB_TOKEN")
            if token:
                print("🔑 Using GitHub token from environment variable")
            else:
                print("🔑 GitHub token not found in environment variables")
                print("💡 You can either:")
                print("   1. Set it: export GITHUB_TOKEN='your_token'")
                print("   2. Enter it below (just for this session)")
                token = input("🔑 Enter GitHub token (or press Ctrl+C to exit): ").strip()
                if not token:
                    print("❌ GitHub token is required for batch operations")
                    sys.exit(1)            # Confirm batch operation
            try:
                with open(batch_file, 'r') as f:
                    data = json.load(f)
                issue_count = len(data.get('issues', []))
                print(f"\n📊 Found {issue_count} issues in '{batch_file}'")
                confirm = input(f"✅ Create {issue_count} issues in {owner}/{repo}? (y/N): ").strip().lower()
                if confirm in ['y', 'yes']:
                    create_batch_issues(owner, repo, batch_file, token)
                    return
                else:
                    print("❌ Batch creation cancelled")
                    return
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"❌ Error reading batch file: {e}")
                sys.exit(1)
        else:
            print(f"❌ File '{batch_file}' not found")
            sys.exit(1)
    
    # Continue with single issue mode
    
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
  
  Batch Mode:
    ./create_issue.py "github.com/user/repo" --batch issues.json
    ./create_issue.py "user/repo" -b batch-issues.json --token YOUR_TOKEN
  
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
    parser.add_argument("--batch", "-b", 
                       help="Create multiple issues from JSON file (requires repo_url)")
    
    args = parser.parse_args()
    
    # Handle batch mode
    if args.batch:
        if not args.repo_url:
            print("❌ Error: Repository URL is required for batch mode")
            print("Usage: ./create_issue.py <repo_url> --batch <file.json>")
            sys.exit(1)
        
        # Get token
        token = args.token or os.environ.get("GITHUB_TOKEN")
        if not token:
            print("🔑 GitHub token not found")
            print("💡 You can either:")
            print("   1. Use: ./create_issue.py ... --token 'your_token'")
            print("   2. Set: export GITHUB_TOKEN='your_token'")
            print("   3. Enter it below (just for this session)")
            token = input("🔑 Enter GitHub token (or press Ctrl+C to exit): ").strip()
            if not token:
                print("❌ Error: GitHub token is required for batch operations.")
                sys.exit(1)
        
        try:
            owner, repo = parse_github_url(args.repo_url)
            create_batch_issues(owner, repo, args.batch, token)
            return
        except ValueError as e:
            print(f"❌ Error: {e}")
            print("💡 Expected formats:")
            print("   - https://github.com/owner/repo")
            print("   - github.com/owner/repo")
            print("   - owner/repo")
            sys.exit(1)
    
    # Force interactive mode if --interactive flag is used or missing arguments
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
