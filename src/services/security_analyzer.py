"""
Security Analysis Module for detecting:
- Hardcoded API keys and secrets
- Weak/insecure cryptography
- Sensitive data exposure
- Insecure patterns
"""

import re
import os
from typing import Dict, List, Set
from ..utils.logger import logger


class SecurityAnalyzer:
    """Analyzes decompiled Java code for security vulnerabilities."""
    
    # Patterns for detecting API keys and secrets
    API_KEY_PATTERNS = {
        'aws_access_key': r'AKIA[0-9A-Z]{16}',
        'aws_secret_key': r'aws(.{0,20})?[\'\"][0-9a-zA-Z\/+]{40}[\'\"]',
        'google_api_key': r'AIza[0-9A-Za-z\-_]{35}',
        'google_oauth': r'[0-9]+-[0-9A-Za-z_]{32}\.apps\.googleusercontent\.com',
        'firebase': r'AAAA[A-Za-z0-9_-]{7}:[A-Za-z0-9_-]{140}',
        'generic_api_key': r'(?i)(api[_-]?key|apikey|api[_-]?secret)[\'\"\s:=]+[a-zA-Z0-9_\-]{20,}',
        'generic_secret': r'(?i)(secret|password|passwd|pwd|token)[\'\"\s:=]+[a-zA-Z0-9_\-!@#$%^&*]{8,}',
        'private_key': r'-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----',
        'slack_token': r'xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24,}',
        'stripe_key': r'(?i)sk_live_[0-9a-zA-Z]{24}',
        'square_token': r'sq0atp-[0-9A-Za-z\-_]{22}',
        'paypal_token': r'access_token\$production\$[0-9a-z]{16}\$[0-9a-f]{32}',
        'github_token': r'ghp_[0-9a-zA-Z]{36}',
        'heroku_api': r'[h|H][e|E][r|R][o|O][k|K][u|U].{0,30}[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}',
    }
    
    # Weak crypto algorithms
    WEAK_CRYPTO = {
        'md5': r'\bMD5\b|MessageDigest\.getInstance\([\'"]MD5[\'"]\)',
        'sha1': r'\bSHA-?1\b|MessageDigest\.getInstance\([\'"]SHA-?1[\'"]\)',
        'des': r'\bDES\b|Cipher\.getInstance\([\'"]DES',
        'rc4': r'\bRC4\b|Cipher\.getInstance\([\'"]RC4',
        'ecb_mode': r'Cipher\.getInstance\([\'"][^/]+/ECB',
        'no_padding': r'Cipher\.getInstance\([\'"][^/]+/[^/]+/NoPadding',
    }
    
    # Insecure patterns
    INSECURE_PATTERNS = {
        'sql_injection': r'(execSQL|rawQuery)\s*\([^?]*\+',
        'webview_js': r'setJavaScriptEnabled\s*\(\s*true\s*\)',
        'ssl_bypass': r'(X509TrustManager|HostnameVerifier|ALLOW_ALL_HOSTNAME_VERIFIER)',
        'world_readable': r'MODE_WORLD_READABLE|MODE_WORLD_WRITEABLE',
        'insecure_random': r'\bnew\s+Random\s*\(',
        'hardcoded_ip': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
        'log_sensitive': r'Log\.[dviwe]\s*\([^)]*(?:password|token|key|secret)',
    }
    
    def __init__(self):
        self.findings = {
            'api_keys': [],
            'crypto_issues': [],
            'insecure_patterns': [],
            'sensitive_data': [],
        }
    
    def analyze_java_sources(self, java_src_dir: str) -> Dict:
        """
        Analyze decompiled Java source code for security issues.
        
        Args:
            java_src_dir: Directory containing decompiled Java files
            
        Returns:
            Dictionary with security findings
        """
        logger.info(f"Starting security analysis on {java_src_dir}")
        
        file_count = 0
        
        try:
            for root, dirs, files in os.walk(java_src_dir):
                for file in files:
                    if file.endswith('.java'):
                        file_path = os.path.join(root, file)
                        self._analyze_file(file_path)
                        file_count += 1
                        
                        if file_count % 100 == 0:
                            logger.info(f"Analyzed {file_count} Java files...")
            
            logger.info(f"Security analysis completed: {file_count} files analyzed")
            
            # Prepare summary
            summary = {
                'total_files_analyzed': file_count,
                'api_keys_found': len(self.findings['api_keys']),
                'crypto_issues_found': len(self.findings['crypto_issues']),
                'insecure_patterns_found': len(self.findings['insecure_patterns']),
                'sensitive_data_found': len(self.findings['sensitive_data']),
                'findings': self.findings,
                'risk_level': self._calculate_risk_level()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Security analysis failed: {e}")
            raise
    
    def _analyze_file(self, file_path: str):
        """Analyze a single Java file for security issues."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                relative_path = file_path.split('_java_src')[-1]
                
                # Detect API keys and secrets
                self._detect_api_keys(content, relative_path)
                
                # Detect weak crypto
                self._detect_weak_crypto(content, relative_path)
                
                # Detect insecure patterns
                self._detect_insecure_patterns(content, relative_path)
                
        except Exception as e:
            logger.warning(f"Failed to analyze {file_path}: {e}")
    
    def _detect_api_keys(self, content: str, file_path: str):
        """Detect hardcoded API keys and secrets."""
        for key_type, pattern in self.API_KEY_PATTERNS.items():
            matches = re.finditer(pattern, content)
            for match in matches:
                # Get context (line number)
                line_num = content[:match.start()].count('\n') + 1
                
                finding = {
                    'type': key_type,
                    'file': file_path,
                    'line': line_num,
                    'match': match.group(0)[:50] + '...' if len(match.group(0)) > 50 else match.group(0),
                    'severity': 'CRITICAL'
                }
                self.findings['api_keys'].append(finding)
    
    def _detect_weak_crypto(self, content: str, file_path: str):
        """Detect weak or insecure cryptographic usage."""
        for crypto_type, pattern in self.WEAK_CRYPTO.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                
                finding = {
                    'type': crypto_type,
                    'file': file_path,
                    'line': line_num,
                    'match': match.group(0),
                    'severity': 'HIGH' if crypto_type in ['md5', 'sha1', 'des'] else 'MEDIUM'
                }
                self.findings['crypto_issues'].append(finding)
    
    def _detect_insecure_patterns(self, content: str, file_path: str):
        """Detect insecure coding patterns."""
        for pattern_type, pattern in self.INSECURE_PATTERNS.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                
                severity_map = {
                    'sql_injection': 'CRITICAL',
                    'ssl_bypass': 'CRITICAL',
                    'webview_js': 'HIGH',
                    'world_readable': 'HIGH',
                    'insecure_random': 'MEDIUM',
                    'log_sensitive': 'MEDIUM',
                    'hardcoded_ip': 'LOW',
                }
                
                finding = {
                    'type': pattern_type,
                    'file': file_path,
                    'line': line_num,
                    'match': match.group(0)[:100] + '...' if len(match.group(0)) > 100 else match.group(0),
                    'severity': severity_map.get(pattern_type, 'MEDIUM')
                }
                self.findings['insecure_patterns'].append(finding)
    
    def _calculate_risk_level(self) -> str:
        """Calculate overall risk level based on findings."""
        critical_count = sum(
            1 for finding in self.findings['api_keys'] + self.findings['insecure_patterns']
            if finding['severity'] == 'CRITICAL'
        )
        
        high_count = sum(
            1 for finding_list in self.findings.values()
            for finding in finding_list
            if finding['severity'] == 'HIGH'
        )
        
        if critical_count > 0:
            return 'CRITICAL'
        elif high_count > 5:
            return 'HIGH'
        elif high_count > 0:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def extract_strings_from_dex(self, apk_path: str) -> List[str]:
        """
        Extract all strings from DEX files for analysis.
        Useful for finding hardcoded URLs, keys, etc.
        """
        try:
            from androguard.misc import AnalyzeAPK
            
            apk, dex_list, analysis = AnalyzeAPK(apk_path)
            all_strings = set()
            
            for dex in dex_list:
                strings = dex.get_strings()
                all_strings.update(strings)
            
            logger.info(f"Extracted {len(all_strings)} unique strings from DEX files")
            return list(all_strings)
            
        except Exception as e:
            logger.error(f"Failed to extract strings: {e}")
            return []
    
    def find_crypto_usage(self, apk_path: str) -> Dict:
        """
        Analyze crypto usage in the APK using Androguard.
        Identifies which crypto algorithms and libraries are used.
        """
        try:
            from androguard.misc import AnalyzeAPK
            
            apk, dex_list, analysis = AnalyzeAPK(apk_path)
            
            crypto_usage = {
                'cipher_algorithms': set(),
                'message_digest_algorithms': set(),
                'key_generators': set(),
                'signature_algorithms': set(),
                'ssl_contexts': set(),
                'crypto_libraries': set(),
            }
            
            # Search for crypto API usage
            for dex in dex_list:
                for method in dex.get_methods():
                    try:
                        source = method.get_source()
                        
                        # Cipher usage
                        cipher_matches = re.findall(r'Cipher\.getInstance\([\'"]([^\'"]+)[\'"]', source)
                        crypto_usage['cipher_algorithms'].update(cipher_matches)
                        
                        # MessageDigest usage
                        digest_matches = re.findall(r'MessageDigest\.getInstance\([\'"]([^\'"]+)[\'"]', source)
                        crypto_usage['message_digest_algorithms'].update(digest_matches)
                        
                        # KeyGenerator usage
                        keygen_matches = re.findall(r'KeyGenerator\.getInstance\([\'"]([^\'"]+)[\'"]', source)
                        crypto_usage['key_generators'].update(keygen_matches)
                        
                        # Signature usage
                        sig_matches = re.findall(r'Signature\.getInstance\([\'"]([^\'"]+)[\'"]', source)
                        crypto_usage['signature_algorithms'].update(sig_matches)
                        
                        # SSL/TLS contexts
                        ssl_matches = re.findall(r'SSLContext\.getInstance\([\'"]([^\'"]+)[\'"]', source)
                        crypto_usage['ssl_contexts'].update(ssl_matches)
                        
                    except:
                        continue
            
            # Convert sets to lists for JSON serialization
            result = {k: list(v) for k, v in crypto_usage.items()}
            
            logger.info(f"Crypto analysis completed: {sum(len(v) for v in result.values())} crypto usages found")
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze crypto usage: {e}")
            return {}
