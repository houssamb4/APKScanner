#!/usr/bin/env python3
"""Test the APKScanner microservice with the test APK."""

import requests
import time
import sys

def test_apk_analysis():
    """Test the APK analysis endpoint."""
    url = "http://localhost:8001/api/v1/analyze"
    apk_path = "temp/F-Droid-test.apk"  # Use the F-Droid APK
    
    print("Testing APKScanner microservice with FULL Androguard power...")
    print(f"Endpoint: {url}")
    print(f"APK file: {apk_path}")
    print("-" * 50)
    
    try:
        # Give the server a moment to start
        time.sleep(2)
        
        # Test if server is running
        try:
            health_check = requests.get("http://localhost:8001/docs")
            print("✓ Server is running")
        except requests.exceptions.ConnectionError:
            print("✗ Server is not running. Please start it first.")
            print("  Run: python -m uvicorn main:app --host 0.0.0.0 --port 8001")
            return False
        
        # Open and send the APK file
        with open(apk_path, 'rb') as f:
            files = {'file': ('test.apk', f, 'application/vnd.android.package-archive')}
            print(f"\nSending APK file for analysis...")
            
            response = requests.post(url, files=files, timeout=300)
            
        print(f"Status Code: {response.status_code}")
        print("-" * 50)
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Analysis completed successfully!")
            print("\n=== Analysis Results ===")
            
            # Display key information
            if 'package_name' in result:
                print(f"Package Name: {result['package_name']}")
            if 'version_name' in result:
                print(f"Version: {result['version_name']}")
            if 'version_code' in result:
                print(f"Version Code: {result['version_code']}")
            
            # Display permissions
            if 'permissions' in result:
                perms = result['permissions']
                print(f"\nPermissions: {len(perms)} found")
                if isinstance(perms, dict):
                    for perm_type, perm_list in perms.items():
                        if perm_list:
                            print(f"  {perm_type}: {len(perm_list)}")
                            for p in perm_list[:3]:  # Show first 3
                                print(f"    - {p}")
            
            # Display components
            if 'components' in result:
                comps = result['components']
                print(f"\nComponents:")
                if isinstance(comps, dict):
                    for comp_type, comp_list in comps.items():
                        if comp_list:
                            print(f"  {comp_type}: {len(comp_list)}")
            
            # Display security flags
            if 'security_flags' in result:
                flags = result['security_flags']
                print(f"\nSecurity Flags:")
                if isinstance(flags, dict):
                    for key, value in flags.items():
                        print(f"  {key}: {value}")
            
            # Display risk score
            if 'overall_risk_score' in result:
                print(f"\nOverall Risk Score: {result['overall_risk_score']}/10")
            
            # Display endpoints
            if 'endpoints' in result:
                endpoints = result['endpoints']
                print(f"\nEndpoints Found: {len(endpoints)}")
                for endpoint in endpoints[:5]:  # Show first 5
                    print(f"  - {endpoint}")
            
            # === NEW: Display Security Analysis Results ===
            if 'security_analysis' in result:
                sec = result['security_analysis']
                print(f"\n{'='*50}")
                print("SECURITY ANALYSIS RESULTS (Java Source Code)")
                print(f"{'='*50}")
                print(f"Files Analyzed: {sec.get('total_files_analyzed', 0)}")
                print(f"Risk Level: {sec.get('risk_level', 'UNKNOWN')}")
                print(f"\nAPI Keys/Secrets Found: {sec.get('api_keys_found', 0)}")
                print(f"Crypto Issues Found: {sec.get('crypto_issues_found', 0)}")
                print(f"Insecure Patterns Found: {sec.get('insecure_patterns_found', 0)}")
                
                # Show sample findings
                if sec.get('api_keys_found', 0) > 0:
                    print("\n⚠️  API KEYS/SECRETS DETECTED:")
                    for finding in sec['findings']['api_keys'][:5]:
                        print(f"  [{finding['severity']}] {finding['type']} in {finding['file']}:{finding['line']}")
                
                if sec.get('crypto_issues_found', 0) > 0:
                    print("\n⚠️  CRYPTO ISSUES DETECTED:")
                    for finding in sec['findings']['crypto_issues'][:5]:
                        print(f"  [{finding['severity']}] {finding['type']}: {finding['match']}")
                
                if sec.get('insecure_patterns_found', 0) > 0:
                    print("\n⚠️  INSECURE PATTERNS DETECTED:")
                    for finding in sec['findings']['insecure_patterns'][:5]:
                        print(f"  [{finding['severity']}] {finding['type']} in {finding['file']}:{finding['line']}")
            
            # === NEW: Display Crypto Usage ===
            if 'crypto_usage' in result:
                crypto = result['crypto_usage']
                print(f"\n{'='*50}")
                print("CRYPTOGRAPHY USAGE ANALYSIS")
                print(f"{'='*50}")
                if crypto.get('cipher_algorithms'):
                    print(f"Cipher Algorithms: {', '.join(crypto['cipher_algorithms'])}")
                if crypto.get('message_digest_algorithms'):
                    print(f"Hash Algorithms: {', '.join(crypto['message_digest_algorithms'])}")
                if crypto.get('key_generators'):
                    print(f"Key Generators: {', '.join(crypto['key_generators'])}")
                if crypto.get('ssl_contexts'):
                    print(f"SSL/TLS Contexts: {', '.join(crypto['ssl_contexts'])}")
            
            # Display Java source directory
            if 'java_source_dir' in result:
                print(f"\n✅ Java Source Code: {result['java_source_dir']}")
            
            print("\n" + "=" * 50)
            print("Full JSON Response:")
            import json
            print(json.dumps(result, indent=2))
            
            return True
        else:
            print(f"✗ Analysis failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except FileNotFoundError:
        print(f"✗ APK file not found: {apk_path}")
        return False
    except requests.exceptions.Timeout:
        print("✗ Request timed out")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_apk_analysis()
    sys.exit(0 if success else 1)
