# 🚀 GitHub Issue Creator

> A handy script to quickly open issues on any GitHub repo, right from your terminal.

[![License: MIT](https://img.shields.io/badge/Licens## 🐛 Troubleshooting

<details>
<summary><strong>Common Issues & Solutions</strong></summary>

| Issue                           | Solution                                                     |
| ------------------------------- | ------------------------------------------------------------ |
| **"GitHub token not found"**    | Set `export GITHUB_TOKEN="your_token"` or use `--token` flag |
| **"Permission denied"**         | Run `chmod +x create_issue.py`                               |
| **"requests module not found"** | Install with `pip install requests`                          |
| **"404 error"**                 | Check repository name and token permissions                  |

</details>ttps://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)

## ✨ Features

- 🧙‍♂️ **Interactive wizard** - Step-by-step guidance for beginners
- ⚡ **Command-line mode** - Lightning-fast issue creation
- 📝 **Multiple input methods** - Type inline, use `\n`, or open your favorite editor
- 🎨 **Editor detection** - Automatically finds and lets you choose from available editors
- 🔒 **Secure token handling** - Multiple authentication methods
- 🌐 **Flexible URL parsing** - Works with any GitHub URL format

---

## 🚀 Quick Start

<details>
<summary><strong>📋 Prerequisites</strong></summary>

- Python 3.6 or higher
- `requests` library
- A GitHub personal access token

</details>

### 1. Setup

```bash
# Make it executable
chmod +x create_issue.py

# Install dependencies
pip install requests

# Set up your GitHub token
export GITHUB_TOKEN="your_github_token_here"
```

### 2. Run

```bash
./create_issue.py
```

That's it! The interactive wizard will guide you through the rest. 🎉

---

## 📖 Usage

<table>
<tr>
<td width="50%">

### 🧙‍♂️ Interactive Mode

_Perfect for beginners_

```bash
./create_issue.py
```

The script will guide you step-by-step through:

- Repository selection
- Issue title
- Description (with editor options)
- Confirmation before creation

</td>
<td width="50%">

### ⚡ Command Line Mode

_For power users_

```bash
./create_issue.py "repo_url" "title" "description"
```

Quick one-liner for experienced users who know exactly what they want to create.

</td>
</tr>
</table>

### 💡 Examples

<details>
<summary><strong>Click to see usage examples</strong></summary>

```bash
# Basic usage - interactive mode
./create_issue.py

# Command line with full URL
./create_issue.py "https://github.com/microsoft/vscode" "Bug: App crashes" "The app crashes on startup"

# Short format
./create_issue.py "microsoft/vscode" "Feature request" "Add dark mode"

# With custom token
./create_issue.py "user/repo" "Bug report" "Description" --token "your_token"

# Force interactive mode
./create_issue.py --interactive
```

</details>

---

### Supported URL Formats

- `https://github.com/owner/repo`
- `github.com/owner/repo`
- `owner/repo`

---

## 🔑 Token Handling

The script looks for your GitHub token in this order:

1. The `--token` flag
2. The `GITHUB_TOKEN` environment variable
3. If neither is set, you’ll be prompted for it

---

## 🛠️ More Options

### Need Help?

```bash
./create_issue.py --help
```

---

## 📝 Writing Your Issue

When using interactive mode, you have multiple options for entering your description:

1. **Quick typing:** Type directly (use `\n` for line breaks)
2. **Start immediately:** Just start typing when prompted
3. **Full editor:** Choose `e` to pick from available editors:
   - Nano (beginner-friendly)
   - Vim (advanced users)
   - VS Code (if installed)
   - TextEdit (macOS)

The script will detect which editors you have installed and let you choose.

---

## 🎯 Tips

- **New to this?** Just run `./create_issue.py` - it will guide you step by step
- **Want it fast?** Supply everything on the command line
- **Writing something long?** Use the editor option (`e`) for multi-line issues
- **For convenience:** Add `GITHUB_TOKEN` to your shell profile

---

## 🐛 Troubleshooting

**GitHub token not found?**

- Make sure you’ve exported `GITHUB_TOKEN`
- Or pass it with `--token`
- If all else fails, the script will ask for it

**Permission denied?**

- Run: `chmod +x create_issue.py`

**Missing the requests library?**

- Install it with: `pip install requests`

**Getting a 404 error?**

- Double-check the repository name and your permissions
- Make sure your token has access

## 🤝 Contributing

Found a bug? Have a feature idea?

- 🐛 [Report issues](../../issues)
- 💡 [Suggest features](../../issues)
- 🔧 [Submit pull requests](../../pulls)

---

## 📄 License

MIT License — feel free to use, share, and modify!

---

<div align="center">

**Made with ❤️ for developers who love efficiency**

⭐ Star this repo if it helped you! ⭐

</div>
