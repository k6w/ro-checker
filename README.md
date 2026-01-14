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

### 1. Prepare your Combo File
The checker supports advanced combo formats often found in logs. See the [Input Format](#-input-format) section below.

### 2. Run the Application
Start the main service manager:
```bash
python main.py
```

### 3. Control via TUI
The Terminal User Interface allows you to:
- **Start/Stop Services**: Toggle the Checker and Web Server independently.
- **Monitor Output**: View live logs from both services side-by-side.
- **Input Management**: Send commands directly to the running checker process.

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
├── main.py           # Central TUI service manager
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

## ⚠️ Disclaimer

This tool is developed for **educational purposes and security testing only**. The author is not responsible for any misuse of this software. Ensure you have authorization before testing any accounts.

## Author

[k6w](https://github.com/k6w)
