from typing import List, Dict
from .logger import logger

class PermissionChecker:
    # Permission risk levels and descriptions
    PERMISSION_RISKS = {
        'android.permission.READ_SMS': {'level': 'high', 'description': 'Can read SMS messages'},
        'android.permission.RECEIVE_SMS': {'level': 'high', 'description': 'Can receive SMS messages'},
        'android.permission.SEND_SMS': {'level': 'high', 'description': 'Can send SMS messages'},
        'android.permission.ACCESS_FINE_LOCATION': {'level': 'high', 'description': 'Precise location access'},
        'android.permission.ACCESS_COARSE_LOCATION': {'level': 'medium', 'description': 'Approximate location access'},
        'android.permission.READ_CONTACTS': {'level': 'high', 'description': 'Can read contacts'},
        'android.permission.WRITE_CONTACTS': {'level': 'high', 'description': 'Can modify contacts'},
        'android.permission.CAMERA': {'level': 'medium', 'description': 'Camera access'},
        'android.permission.RECORD_AUDIO': {'level': 'high', 'description': 'Microphone access'},
        'android.permission.READ_PHONE_STATE': {'level': 'medium', 'description': 'Phone state information'},
        'android.permission.CALL_PHONE': {'level': 'high', 'description': 'Can make phone calls'},
        'android.permission.READ_CALL_LOG': {'level': 'high', 'description': 'Can read call history'},
        'android.permission.WRITE_CALL_LOG': {'level': 'high', 'description': 'Can modify call history'},
        'android.permission.READ_EXTERNAL_STORAGE': {'level': 'medium', 'description': 'External storage read access'},
        'android.permission.WRITE_EXTERNAL_STORAGE': {'level': 'medium', 'description': 'External storage write access'},
        'android.permission.INTERNET': {'level': 'low', 'description': 'Network access'},
        'android.permission.WAKE_LOCK': {'level': 'low', 'description': 'Prevent device sleep'},
    }

    def analyze_permissions(self, permissions: List[Dict]) -> Dict:
        """Analyze permissions for security risks."""
        analysis = {
            'total_permissions': len(permissions),
            'dangerous_permissions': [],
            'normal_permissions': [],
            'signature_permissions': [],
            'risk_assessment': {},
            'overprivilege_score': 0
        }

        for perm in permissions:
            name = perm['name']
            level = perm.get('protection_level', 'normal')

            if level == 'dangerous':
                analysis['dangerous_permissions'].append(name)
            elif level == 'normal':
                analysis['normal_permissions'].append(name)
            else:
                analysis['signature_permissions'].append(name)

            # Risk assessment
            if name in self.PERMISSION_RISKS:
                risk_info = self.PERMISSION_RISKS[name]
                analysis['risk_assessment'][name] = risk_info
                if risk_info['level'] == 'high':
                    analysis['overprivilege_score'] += 3
                elif risk_info['level'] == 'medium':
                    analysis['overprivilege_score'] += 2
                else:
                    analysis['overprivilege_score'] += 1

        # Normalize overprivilege score
        analysis['overprivilege_score'] = min(analysis['overprivilege_score'], 10)

        logger.info(f"Permission analysis completed: {len(permissions)} permissions analyzed")
        return analysis

    def check_component_exposure(self, components: Dict) -> Dict:
        """Check for exposed components without proper protection."""
        issues = []

        for component_type, comp_list in components.items():
            for comp in comp_list:
                if comp.get('exported', False):
                    if not comp.get('permission'):
                        issues.append({
                            'type': 'exposed_component',
                            'component': comp['name'],
                            'component_type': component_type,
                            'severity': 'high',
                            'description': f"{component_type} {comp['name']} is exported without permission protection"
                        })

        return {'component_issues': issues, 'total_issues': len(issues)}

    def assess_security_flags(self, flags: Dict) -> Dict:
        """Assess security flags for potential issues."""
        issues = []

        if flags.get('debuggable', False):
            issues.append({
                'type': 'debuggable_enabled',
                'severity': 'critical',
                'description': 'App is debuggable, allowing code injection and data theft'
            })

        if flags.get('allow_backup', True):
            issues.append({
                'type': 'backup_enabled',
                'severity': 'medium',
                'description': 'App data can be backed up, potentially exposing sensitive data'
            })

        if flags.get('uses_cleartext_traffic', False):
            issues.append({
                'type': 'cleartext_traffic',
                'severity': 'high',
                'description': 'App allows unencrypted HTTP traffic'
            })

        return {'security_issues': issues, 'total_issues': len(issues)}