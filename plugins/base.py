from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import aiohttp

class WebsitePlugin(ABC):
    """Base class for website checker plugins"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Website name"""
        pass
    
    @property
    @abstractmethod
    def display_name(self) -> str:
        """Display name for UI"""
        pass
    
    @abstractmethod
    async def check_account(self, session: aiohttp.ClientSession, login: str, password: str, original_login: str) -> Optional[Dict]:
        """
        Check account credentials and return account data if valid
        Returns None if invalid
        """
        pass
    
    @abstractmethod
    def parse_combo_line(self, login: str, password: str) -> Dict[str, str]:
        """
        Parse and normalize login credentials
        Returns dict with 'login', 'password', 'original_login'
        """
        pass
    
    @abstractmethod
    def format_account_display(self, account: Dict) -> str:
        """Format account data for console display"""
        pass
    
    @abstractmethod
    def get_balance_key(self) -> str:
        """Get the key name for balance/points in account data"""
        pass
