import xml.etree.ElementTree as ET
from typing import Dict, List
from .logger import logger

class ManifestParser:
    # Dangerous permissions that require special attention
    DANGEROUS_PERMISSIONS = {
        'android.permission.READ_SMS',
        'android.permission.RECEIVE_SMS',
        'android.permission.SEND_SMS',
        'android.permission.ACCESS_FINE_LOCATION',
        'android.permission.ACCESS_COARSE_LOCATION',
        'android.permission.READ_CONTACTS',
        'android.permission.WRITE_CONTACTS',
        'android.permission.CAMERA',
        'android.permission.RECORD_AUDIO',
        'android.permission.READ_PHONE_STATE',
        'android.permission.CALL_PHONE',
        'android.permission.READ_CALL_LOG',
        'android.permission.WRITE_CALL_LOG',
        'android.permission.READ_EXTERNAL_STORAGE',
        'android.permission.WRITE_EXTERNAL_STORAGE',
    }

    def parse_manifest(self, manifest_xml: str) -> Dict:
        """Parse AndroidManifest.xml and extract security information."""
        try:
            root = ET.fromstring(manifest_xml)
            analysis = {
                'package': root.get('package'),
                'version_code': root.get('{http://schemas.android.com/apk/res/android}versionCode'),
                'version_name': root.get('{http://schemas.android.com/apk/res/android}versionName'),
                'permissions': self._extract_permissions(root),
                'components': self._extract_components(root),
                'security_flags': self._extract_security_flags(root),
            }
            logger.info("Manifest parsed successfully")
            return analysis
        except ET.ParseError as e:
            logger.error(f"Failed to parse manifest XML: {e}")
            raise

    def _extract_permissions(self, root: ET.Element) -> List[Dict]:
        """Extract permissions from manifest."""
        permissions = []
        for perm in root.findall('uses-permission'):
            name = perm.get('{http://schemas.android.com/apk/res/android}name')
            if name:
                permissions.append({
                    'name': name,
                    'protection_level': self._get_permission_level(name),
                    'is_dangerous': name in self.DANGEROUS_PERMISSIONS
                })
        return permissions

    def _extract_components(self, root: ET.Element) -> Dict:
        """Extract components (activities, services, receivers, providers)."""
        components = {
            'activities': [],
            'services': [],
            'receivers': [],
            'providers': []
        }

        # Activities
        for activity in root.findall('.//activity'):
            components['activities'].append(self._parse_component(activity, 'activity'))

        # Services
        for service in root.findall('.//service'):
            components['services'].append(self._parse_component(service, 'service'))

        # Receivers
        for receiver in root.findall('.//receiver'):
            components['receivers'].append(self._parse_component(receiver, 'receiver'))

        # Providers
        for provider in root.findall('.//provider'):
            components['providers'].append(self._parse_component(provider, 'provider'))

        return components

    def _parse_component(self, element: ET.Element, component_type: str) -> Dict:
        """Parse a component element."""
        android_ns = '{http://schemas.android.com/apk/res/android}'
        return {
            'name': element.get(f'{android_ns}name'),
            'exported': element.get(f'{android_ns}exported') == 'true',
            'permission': element.get(f'{android_ns}permission'),
            'type': component_type
        }

    def _extract_security_flags(self, root: ET.Element) -> Dict:
        """Extract security-related flags from manifest."""
        android_ns = '{http://schemas.android.com/apk/res/android}'
        application = root.find('application')

        if application is None:
            return {}

        flags = {
            'debuggable': application.get(f'{android_ns}debuggable') == 'true',
            'allow_backup': application.get(f'{android_ns}allowBackup') != 'false',  # Default is true
            'uses_cleartext_traffic': self._check_cleartext_traffic(root),
            'network_security_config': self._get_network_security_config(application, android_ns)
        }
        return flags

    def _check_cleartext_traffic(self, root: ET.Element) -> bool:
        """Check if app allows cleartext traffic."""
        for uses_cleartext in root.findall('.//usesCleartextTraffic'):
            if uses_cleartext.text == 'true':
                return True
        return False

    def _get_network_security_config(self, application: ET.Element, android_ns: str) -> str:
        """Get network security config reference."""
        return application.get(f'{android_ns}networkSecurityConfig', '')

    def _get_permission_level(self, permission_name: str) -> str:
        """Determine permission protection level."""
        if permission_name in self.DANGEROUS_PERMISSIONS:
            return 'dangerous'
        elif permission_name.startswith('android.permission.') or permission_name.startswith('com.android.'):
            return 'normal'
        else:
            return 'signature'  # Custom permissions