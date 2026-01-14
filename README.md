# ro-checker

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

A high-performance, modular multi-site account checker designed for speed and efficiency. It features a sophisticated TUI (Terminal User Interface) for management and a real-time Flask-based web dashboard for monitoring results.

## 🚀 Features

- **High-Performance Async Engine**: Built on `asyncio` and `aiohttp` to handle hundreds of concurrent connections efficiently.
- **Modular Plugin Architecture**: Easily extensible system supporting multiple target websites (currently includes Jerry's Pizza and Pizza Hut).
- **Advanced TUI Manager**: A beautiful, interactive terminal interface built with `rich` to manage checker and server processes simultaneously without leaving the console.
- **Real-Time Web Dashboard**: Flask-based web interface with WebSocket support for instant updates of successful hits as they happen.
- **Smart Data Management**: 
  - Automatic parsing of complex combo file formats.
  - Real-time sorting of hits by value (e.g., loyalty balance).
  - Dual output formats (JSON for machines, TXT for humans).
- **Live Statistics**: Real-time tracking of check rates (CPM), valid accounts, and total value found.

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/k6w/ro-checker.git
   cd ro-checker
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 💻 Usage

### Quick Start

1. **Prepare your combo file** (see [Input Format](#-input-format) below)
2. **Run the application** in your preferred mode

### Interface Options

ro-checker supports multiple interface modes for different use cases:

#### 🎨 **TUI Mode (Terminal User Interface) - Default**
The full-featured terminal interface for managing both checker and server simultaneously.

```bash
# Start TUI mode (default)
python main.py

# Or explicitly
python main.py tui
```

**TUI Features:**
- **Dual-Panel Display**: Monitor checker and server outputs side-by-side
- **Live Controls**: Start/stop services with keyboard shortcuts
- **Real-time Stats**: View checking progress, rates, and valid hits
- **Interactive Input**: Send commands to running processes
- **Service Management**: Control checker and web server independently

**TUI Controls:**
- `←/→` - Switch between checker/server panels
- `S` - Start selected service
- `X` - Stop selected service  
- `R` - Restart selected service
- `I` - Send input to selected service
- `Q` - Quit application

**TUI Layout:**
```
┌─ Service Manager ──────────────────┐  ┌─ Status & Controls ───────┐
│ Checker: ● RUNNING   Server: ○ STOPPED │  │ Status: Running           │
│                                     │  │ Valid: 12 | Rate: 45.2/s │
│ [Live checker output here...]      │  │ ←/→ Select | S Start | ... │
│                                     │  └───────────────────────────┘
└─────────────────────────────────────┘
```

#### 💻 **CLI Mode - Individual Components**
Run checker or server independently for automation, scripting, or when TUI isn't needed.

```bash
# Run only the checker
python main.py checker

# Run only the web server
python main.py server
```

**CLI Advantages:**
- **No TUI Dependencies**: Works in any terminal environment
- **Scripting Friendly**: Easy to integrate into automation workflows
- **Resource Efficient**: Only loads what you need
- **Background Compatible**: Can run in background processes
- **Stable**: No interactive UI to cause issues

**CLI Output:**
```bash
[*] Starting checker in CLI mode...
================================================================================
MULTI-SITE ACCOUNT CHECKER
================================================================================

[*] Select website to check:
  1. Jerry's Pizza
  2. Pizza Hut

Enter choice (1 or 2): 1
[+] Selected: Jerry's Pizza
[*] Please select the combo file...
[+] Selected file: combos.txt
[*] Parsing combo file...
[+] Found 1001 combos to check
[*] Starting Jerry's Pizza checker with 50 workers
[*] Total accounts to check: 1001

[✓] Valid: +40773960731 | Balance: 0 | Orders: 7 | Total: $846.82
Progress: 150/1001 | Valid: 12 | Rate: 45.2/s
```

### When to Use Each Mode

| Mode | Best For | Advantages | Disadvantages |
|------|----------|------------|---------------|
| **TUI** | Interactive management, monitoring multiple services | Live dual-panel view, real-time controls, comprehensive monitoring | Requires compatible terminal, can be resource-intensive |
| **CLI Checker** | Automation, scripting, headless operation | Lightweight, stable, scriptable, background-friendly | No live monitoring, manual service management |
| **CLI Server** | Dedicated web dashboard hosting | Isolated server operation, resource-efficient | No checker integration |

### 4. Web Dashboard
Access the dashboard at `http://localhost:5000` to view:
- Live table of valid accounts.
- Total value statistics.
- Real-time notifications of new hits.

## 📝 Input Format

The checker supports multiple combo file formats automatically. It detects the format and parses accordingly.

### Supported Formats

**1. Result Format (Original):**
```text
Result 1:
Source DB: combo_logs_29_08_2025
Login: +40 7** *** ***
Password: ******
URL: https://www.example.com/login
```

**2. OSINTCAT Format:**
```text
==================
DOMAIN: https://www.jerryspizza.ro/account/register
EMAIL: +40
PASS: 333:779:555:petrerobert1911
==================
```

**3. Simple Colon Format:**
```text
user@example.com:password123
+40712345678:secretpass
```

### Adding Custom Formats

To add support for new combo formats, edit `combo_parsers.py`:

1. Create a new class inheriting from `ComboParser`
2. Implement `can_parse()` to detect your format
3. Implement `parse()` to extract login/password
4. Add your parser to the `PARSERS` list

**Example:**
```python
class MyCustomFormatParser(ComboParser):
    def can_parse(self, content: str) -> bool:
        return 'MY_FORMAT_MARKER' in content
    
    def parse(self, content: str) -> List[Dict[str, str]]:
        # Your parsing logic here
        pass
```

## 📊 Example Output

The checker provides detailed feedback during operation.

**Console Output:**
```text
[*] Starting checker with 50 workers
[*] Total accounts to check: 976

[✓] Valid: use***@gmail.com | Balance: 15 | Orders: 8 | Total: $285.50
[✗] Invalid: +407*******
Progress: 150/976 | Valid: 12 | Rate: 45.2/s

[*] Checking complete!
[*] Time elapsed: 21.58s
[*] Average rate: 45.2 accounts/s
[*] Valid accounts: 87
[*] Invalid accounts: 889
```

**Saved Files:**
- `success_jerryspizza_1.json`: Full data dump sorted by balance.
- `success_jerryspizza_1.txt`: Human-readable summary.

## 🏗️ Project Structure

```
ro-checker/
├── main.py           # Main entry point with TUI and CLI modes
├── checker.py        # Core async checking engine
├── server.py         # Flask web server & WebSocket handler
├── combo_parsers.py  # Modular combo file format parsers
├── plugins/          # Site-specific modules
│   ├── base.py       # Abstract base class for plugins
│   ├── jerryspizza.py
│   └── pizzahut.py
├── templates/        # Web dashboard templates
├── example_combos.txt # Sample combo files in different formats
└── requirements.txt  # Python dependencies
```

**Main Components:**
- **`main.py`**: Entry point supporting both TUI and CLI modes
- **`checker.py`**: Async account validation engine with multi-threading
- **`server.py`**: Real-time web dashboard with WebSocket updates
- **`combo_parsers.py`**: Extensible parser system for multiple combo formats
- **`plugins/`**: Modular website-specific implementations

## ⚠️ Disclaimer

This tool is developed for **educational purposes and security testing only**. The author is not responsible for any misuse of this software. Ensure you have authorization before testing any accounts.

## Author

[k6w](https://github.com/k6w)
