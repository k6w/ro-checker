import re
from typing import List, Dict, Optional
from abc import ABC, abstractmethod


class ComboParser(ABC):
    """Base class for combo file parsers"""

    @abstractmethod
    def can_parse(self, content: str) -> bool:
        """Check if this parser can handle the given content"""
        pass

    @abstractmethod
    def parse(self, content: str) -> List[Dict[str, str]]:
        """Parse the content and return list of combo dicts with 'login', 'password', 'original_login'"""
        pass


class ResultFormatParser(ComboParser):
    """Parser for the original Result format"""

    def can_parse(self, content: str) -> bool:
        return bool(re.search(r'Result \d+:', content))

    def parse(self, content: str) -> List[Dict[str, str]]:
        combos = []
        pattern = r'Result \d+:.*?Login:\s*(.+?)\s*Password:\s*(.+?)\s*URL:'
        matches = re.findall(pattern, content, re.DOTALL)

        for login, password in matches:
            login = login.strip()
            password = password.strip()

            # Skip invalid entries
            if not login or not password or len(login) < 3 or len(password) < 3:
                continue

            combos.append({
                'login': login,
                'password': password,
                'original_login': login
            })

        return combos


class OsintcatFormatParser(ComboParser):
    """Parser for OSINTCAT format with DOMAIN/EMAIL/PASS blocks"""

    def can_parse(self, content: str) -> bool:
        return bool(re.search(r'==================\s*DOMAIN:', content))

    def parse(self, content: str) -> List[Dict[str, str]]:
        combos = []
        # Split by the separator blocks
        blocks = re.split(r'={18,}', content)

        for block in blocks:
            block = block.strip()
            if not block:
                continue

            # Extract fields
            domain_match = re.search(r'DOMAIN:\s*(.+)', block)
            email_match = re.search(r'EMAIL:\s*(.+)', block)
            pass_match = re.search(r'PASS:\s*(.+)', block)

            if email_match and pass_match:
                email = email_match.group(1).strip()
                password = pass_match.group(1).strip()

                # Handle special case for OSINTCAT format where phone might be split
                # If EMAIL is just "+40" or similar prefix, and PASS contains colon-separated numbers
                if email in ['+40', '+39', '40', '39'] and ':' in password:
                    # Split password by last colon to separate phone extension from actual password
                    pass_parts = password.rsplit(':', 1)
                    if len(pass_parts) == 2 and pass_parts[0].replace(':', '').isdigit():
                        # Combine email prefix with phone numbers, use last part as password
                        login = email + pass_parts[0].replace(':', '')
                        password = pass_parts[1]
                    else:
                        login = email
                else:
                    login = email

                # Skip invalid entries
                if not login or not password or len(login) < 3 or len(password) < 3:
                    continue

                combos.append({
                    'login': login,
                    'password': password,
                    'original_login': login,
                    'domain': domain_match.group(1).strip() if domain_match else ''
                })

        return combos


class SimpleColonFormatParser(ComboParser):
    """Parser for simple login:password format"""

    def can_parse(self, content: str) -> bool:
        # Check if content has lines with colon but not the other formats
        lines = content.split('\n')
        colon_lines = [line for line in lines if ':' in line and not line.startswith(('DOMAIN:', 'EMAIL:', 'PASS:', 'Login:', 'Password:', 'URL:', 'Result '))]
        return len(colon_lines) > 0 and len(colon_lines) / len(lines) > 0.5

    def parse(self, content: str) -> List[Dict[str, str]]:
        combos = []
        lines = content.split('\n')

        for line in lines:
            line = line.strip()
            if ':' not in line:
                continue

            parts = line.split(':', 1)
            if len(parts) == 2:
                login, password = parts
                login = login.strip()
                password = password.strip()

                if login and password and len(login) >= 3 and len(password) >= 3:
                    combos.append({
                        'login': login,
                        'password': password,
                        'original_login': login
                    })

        return combos


# List of all available parsers in order of preference
PARSERS = [
    ResultFormatParser(),
    OsintcatFormatParser(),
    SimpleColonFormatParser(),
]


def parse_combo_file(content: str) -> List[Dict[str, str]]:
    """Parse combo file content using the appropriate parser"""
    for parser in PARSERS:
        if parser.can_parse(content):
            return parser.parse(content)

    # If no parser matches, try all and combine results
    all_combos = []
    for parser in PARSERS:
        try:
            combos = parser.parse(content)
            all_combos.extend(combos)
        except:
            continue

    return all_combos