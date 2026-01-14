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
        lines = content.split('\n')
        result_lines = [line for line in lines if re.match(r'Result \d+:', line)]
        return len(result_lines) > 0

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
        blocks = re.split(r'={18,}', content)
        valid_blocks = 0
        for block in blocks:
            block = block.strip()
            if block and re.search(r'DOMAIN:', block) and re.search(r'EMAIL:', block) and re.search(r'PASS:', block):
                valid_blocks += 1
        return valid_blocks > 0

    def _is_phone_prefix(self, text: str) -> bool:
        """Check if text looks like a phone country code prefix"""
        text = text.strip()
        if re.match(r'^\+\d{1,4}$', text):
            return True
        if re.match(r'^\d{1,4}$', text):
            return True
        return False

    def parse(self, content: str) -> List[Dict[str, str]]:
        combos = []
        blocks = re.split(r'={18,}', content)

        for block in blocks:
            block = block.strip()
            if not block:
                continue

            domain_match = re.search(r'DOMAIN:\s*(.+)', block)
            email_match = re.search(r'EMAIL:\s*(.+)', block)
            pass_match = re.search(r'PASS:\s*(.+)', block)

            if email_match and pass_match:
                email = email_match.group(1).strip()
                password = pass_match.group(1).strip()

                if self._is_phone_prefix(email) and ':' in password:
                    pass_parts = password.rsplit(':', 1)
                    if len(pass_parts) == 2 and pass_parts[0].replace(':', '').isdigit():
                        login = email + pass_parts[0].replace(':', '')
                        password = pass_parts[1]
                    else:
                        login = email
                else:
                    login = email

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
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        if not lines:
            return False
        colon_lines = [line for line in lines if ':' in line and not any(line.startswith(prefix) for prefix in ('DOMAIN:', 'EMAIL:', 'PASS:', 'Login:', 'Password:', 'URL:', 'Result '))]
        return len(colon_lines) / len(lines) > 0.7

    def parse(self, content: str) -> List[Dict[str, str]]:
        combos = []
        lines = content.split('\n')

        for line in lines:
            line = line.strip()
            if ':' not in line:
                continue
            if any(line.startswith(prefix) for prefix in ('DOMAIN:', 'EMAIL:', 'PASS:', 'Login:', 'Password:', 'URL:', 'Result ')):
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
    """Parse combo file content using all applicable parsers"""
    all_combos = []
    for parser in PARSERS:
        try:
            combos = parser.parse(content)
            all_combos.extend(combos)
        except:
            continue
    return all_combos