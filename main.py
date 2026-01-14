import subprocess
import sys
import time
import threading
import queue
from collections import deque
import shutil
import argparse

# Rich imports
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.table import Table
from rich import box
from rich.align import Align
from rich.style import Style

# Windows-specific imports for keyboard handling
if sys.platform == 'win32':
    import msvcrt
else:
    # Simple fallback for non-Windows (though user is on Windows)
    import select
    import tty
    import termios

class ServiceManager:
    """Manages checker and server processes with a TUI interface using Rich"""
    
    def __init__(self):
        # Process management
        self.checker_process = None
        self.server_process = None
        self.checker_running = False
        self.server_running = False
        
        # Output buffers - store last N lines
        self.checker_output = deque(maxlen=100)
        self.server_output = deque(maxlen=100)
        
        # UI state
        self.selected_service = 0  # 0 = checker, 1 = server
        self.running = True
        self.paused_for_input = False
        
        # Checker stats
        self.checker_stats = {
            'checked': 0,
            'valid': 0,
            'rate': 0.0
        }
        
        # Input handling
        self.checker_input_queue = queue.Queue()
        self.server_input_queue = queue.Queue()
        self.checker_needs_input = False
        self.current_input_prompt = ""
        
        # Rich Console
        self.console = Console()
        
    def get_key(self):
        """Get a single keypress (Windows only)"""
        if sys.platform == 'win32':
            if not msvcrt.kbhit():
                return None
                
            key = msvcrt.getch()
            
            # Handle arrow keys
            if key == b'\xe0' or key == b'\x00':
                key = msvcrt.getch()
                if key == b'K':  # Left
                    return 'LEFT'
                elif key == b'M':  # Right
                    return 'RIGHT'
            
            # Handle regular keys
            if key == b'\r':
                return 'ENTER'
            try:
                return key.decode('utf-8').lower()
            except:
                return None
        return None
    
    def start_checker(self):
        """Start the checker process"""
        if self.checker_running:
            return
        
        try:
            self.checker_process = subprocess.Popen(
                [sys.executable, '-u', 'checker.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            self.checker_running = True
            self.checker_output.clear()
            self.checker_stats = {'checked': 0, 'valid': 0, 'rate': 0.0}
            
            # Start threads
            threading.Thread(target=self._read_checker_output, daemon=True).start()
            threading.Thread(target=self._handle_checker_input, daemon=True).start()
            
        except Exception as e:
            self.checker_output.append(f"[red][ERROR] Failed to start checker: {e}[/red]")
    
    def start_server(self):
        """Start the server process"""
        if self.server_running:
            return
        
        try:
            self.server_process = subprocess.Popen(
                [sys.executable, '-u', 'server.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            self.server_running = True
            self.server_output.clear()
            
            threading.Thread(target=self._read_server_output, daemon=True).start()
            threading.Thread(target=self._handle_server_input, daemon=True).start()
            
        except Exception as e:
            self.server_output.append(f"[red][ERROR] Failed to start server: {e}[/red]")
    
    def stop_checker(self):
        """Stop the checker process"""
        if self.checker_running and self.checker_process:
            try:
                self.checker_process.terminate()
                self.checker_process.wait(timeout=3)
            except:
                self.checker_process.kill()
            
            self.checker_running = False
            self.checker_needs_input = False
            self.checker_stats = {'checked': 0, 'valid': 0, 'rate': 0.0}
    
    def stop_server(self):
        """Stop the server process"""
        if self.server_running and self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=3)
            except:
                self.server_process.kill()
            
            self.server_running = False
    
    def restart_checker(self):
        """Restart the checker"""
        self.stop_checker()
        time.sleep(0.5)
        self.start_checker()
    
    def restart_server(self):
        """Restart the server"""
        self.stop_server()
        time.sleep(0.5)
        self.start_server()
    
    def _read_checker_output(self):
        """Read checker output in background thread"""
        try:
            for line in iter(self.checker_process.stdout.readline, ''):
                if not line:
                    break
                
                line = line.rstrip()
                
                # Skip empty lines
                if not line.strip():
                    continue
                
                # Avoid duplicate consecutive lines
                if self.checker_output and self.checker_output[-1] == line:
                    continue
                    
                self.checker_output.append(line)
                
                # Detect input prompts
                if 'Enter choice' in line or 'Enter number' in line:
                    self.checker_needs_input = True
                    self.current_input_prompt = line
                
                # Parse stats
                if 'Progress:' in line:
                    try:
                        parts = line.split('|')
                        for part in parts:
                            if 'Progress:' in part:
                                nums = part.split(':')[1].strip().split('/')
                                self.checker_stats['checked'] = int(nums[0])
                            elif 'Valid:' in part:
                                self.checker_stats['valid'] = int(part.split(':')[1].strip())
                            elif 'Rate:' in part:
                                rate = part.split(':')[1].strip().replace('/s', '')
                                self.checker_stats['rate'] = float(rate)
                    except:
                        pass
        except:
            pass
    
    def _read_server_output(self):
        """Read server output in background thread"""
        try:
            for line in iter(self.server_process.stdout.readline, ''):
                if not line:
                    break
                
                line = line.rstrip()
                
                # Skip empty lines
                if not line.strip():
                    continue
                
                # Avoid duplicate consecutive lines
                if self.server_output and self.server_output[-1] == line:
                    continue
                    
                self.server_output.append(line)
        except:
            pass
    
    def _handle_checker_input(self):
        """Handle sending input to checker process"""
        while self.checker_running and self.checker_process:
            try:
                if not self.checker_input_queue.empty():
                    user_input = self.checker_input_queue.get()
                    if self.checker_process and self.checker_process.stdin:
                        self.checker_process.stdin.write(user_input + '\n')
                        self.checker_process.stdin.flush()
                        self.checker_needs_input = False
                        self.current_input_prompt = ""
                time.sleep(0.1)
            except:
                break

    def _handle_server_input(self):
        """Handle sending input to server process"""
        while self.server_running and self.server_process:
            try:
                if not self.server_input_queue.empty():
                    user_input = self.server_input_queue.get()
                    if self.server_process and self.server_process.stdin:
                        self.server_process.stdin.write(user_input + '\n')
                        self.server_process.stdin.flush()
                time.sleep(0.1)
            except:
                break
    
    def get_text_input(self, prompt):
        """Get text input from user"""
        self.paused_for_input = True
        # We need to stop the Live display to get input
        return None # Signal to main loop to handle input
    
    def make_layout(self) -> Layout:
        layout = Layout()
        layout.split(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=6)
        )
        layout["main"].split_row(
            Layout(name="checker"),
            Layout(name="server")
        )
        return layout

    def generate_header(self) -> Panel:
        grid = Table.grid(expand=True)
        grid.add_column(justify="center", ratio=1)
        grid.add_row("[bold white]MULTI-SITE ACCOUNT CHECKER - SERVICE MANAGER[/bold white]")
        return Panel(grid, style="on blue", box=box.DOUBLE)

    def generate_checker_panel(self) -> Panel:
        content = "\n".join(list(self.checker_output)[-50:]) # Show last 50 lines
        
        border_style = "blue" if self.selected_service == 0 else "white"
        title = "[bold blue]CHECKER OUTPUT[/bold blue]" if self.selected_service == 0 else "CHECKER OUTPUT"
        
        if self.checker_needs_input:
            title += " [bold yellow](INPUT REQUIRED)[/bold yellow]"
            
        return Panel(
            Text.from_ansi(content),
            title=title,
            border_style=border_style,
            box=box.ROUNDED
        )

    def generate_server_panel(self) -> Panel:
        content = "\n".join(list(self.server_output)[-50:])
        
        border_style = "blue" if self.selected_service == 1 else "white"
        title = "[bold blue]SERVER OUTPUT[/bold blue]" if self.selected_service == 1 else "SERVER OUTPUT"
        
        return Panel(
            Text.from_ansi(content),
            title=title,
            border_style=border_style,
            box=box.ROUNDED
        )

    def generate_footer(self) -> Panel:
        # Status Line
        checker_status = "[bold green]● RUNNING[/bold green]" if self.checker_running else "[bold red]○ STOPPED[/bold red]"
        server_status = "[bold green]● RUNNING[/bold green]" if self.server_running else "[bold red]○ STOPPED[/bold red]"
        
        status_text = f"Checker: {checker_status}   Server: {server_status}"
        
        # Stats Line
        if self.checker_running:
            stats_text = f"Checked: [cyan]{self.checker_stats['checked']}[/cyan] | Valid: [green]{self.checker_stats['valid']}[/green] | Rate: [yellow]{self.checker_stats['rate']:.1f}/s[/yellow]"
        else:
            stats_text = "Waiting for checker..."

        # Controls Line
        controls = "[cyan]←/→[/cyan] Select | [green]S[/green] Start | [yellow]X[/yellow] Stop | [magenta]R[/magenta] Restart | [blue]I[/blue] Input | [red]Q[/red] Quit"
        
        grid = Table.grid(expand=True)
        grid.add_column(ratio=1)
        grid.add_row(status_text)
        grid.add_row(stats_text)
        grid.add_row(controls)
        
        return Panel(grid, title="Status & Controls", border_style="white", box=box.ROUNDED)

    def run(self):
        """Main loop"""
        self.start_server()
        
        layout = self.make_layout()
        
        with Live(layout, refresh_per_second=10, screen=True) as live:
            while self.running:
                # Update Layout
                layout["header"].update(self.generate_header())
                layout["main"]["checker"].update(self.generate_checker_panel())
                layout["main"]["server"].update(self.generate_server_panel())
                layout["footer"].update(self.generate_footer())
                
                # Check process status
                if self.checker_running and self.checker_process and self.checker_process.poll() is not None:
                    self.checker_running = False
                    self.checker_needs_input = False
                
                if self.server_running and self.server_process and self.server_process.poll() is not None:
                    self.server_running = False
                
                # Handle Input
                key = self.get_key()
                if key:
                    if key == 'LEFT':
                        self.selected_service = 0
                    elif key == 'RIGHT':
                        self.selected_service = 1
                    elif key == 's':
                        if self.selected_service == 0:
                            self.start_checker()
                        else:
                            self.start_server()
                    elif key == 'x':
                        if self.selected_service == 0:
                            self.stop_checker()
                        else:
                            self.stop_server()
                    elif key == 'r':
                        if self.selected_service == 0:
                            self.restart_checker()
                        else:
                            self.restart_server()
                    elif key == 'i':
                        # Allow input for either service if it's running
                        target_running = (self.selected_service == 0 and self.checker_running) or \
                                       (self.selected_service == 1 and self.server_running)
                        
                        if target_running:
                            # Pause Live to get input
                            live.stop()
                            try:
                                service_name = "CHECKER" if self.selected_service == 0 else "SERVER"
                                print(f"\n[bold cyan]{service_name} INPUT REQUIRED[/bold cyan]")
                                if self.selected_service == 0 and self.current_input_prompt:
                                    print(f"[yellow]{self.current_input_prompt}[/yellow]")
                                
                                user_input = input("➜ ")
                                
                                if self.selected_service == 0:
                                    self.checker_input_queue.put(user_input)
                                else:
                                    self.server_input_queue.put(user_input)
                            finally:
                                live.start()
                    elif key in '0123456789':
                        if self.selected_service == 0 and self.checker_needs_input:
                            self.checker_input_queue.put(key)
                    elif key == 'q':
                        self.running = False
                
                time.sleep(0.05)
        
        # Cleanup
        self.stop_checker()
        self.stop_server()
        print("Services stopped. Goodbye!")

def main():
    parser = argparse.ArgumentParser(description='Multi-Site Account Checker')
    parser.add_argument('mode', nargs='?', default='tui', 
                       choices=['tui', 'checker', 'server'],
                       help='Mode to run: tui (default), checker, or server')
    
    args = parser.parse_args()
    
    if args.mode == 'checker':
        # Run checker directly
        print("[*] Starting checker in CLI mode...")
        try:
            import checker
            import asyncio
            asyncio.run(checker.main())
        except KeyboardInterrupt:
            print("\n[*] Checker stopped by user")
        except Exception as e:
            print(f"[!] Error running checker: {e}")
            
    elif args.mode == 'server':
        # Run server as subprocess
        print("[*] Starting server in CLI mode...")
        try:
            subprocess.run([sys.executable, 'server.py'])
        except KeyboardInterrupt:
            print("\n[*] Server stopped by user")
        except Exception as e:
            print(f"[!] Error running server: {e}")
            
    else:  # tui mode (default)
        try:
            manager = ServiceManager()
            manager.run()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
