from typing import Dict, List
from sqlalchemy.orm import Session
from .decompiler import Decompiler
from .manifest_parser import ManifestParser
from .permission_checker import PermissionChecker
from .file_handler import save_uploaded_apk, cleanup_temp_files
from ..database import crud, models
from .logger import logger

class APKAnalyzer:
    def __init__(self):
        self.decompiler = Decompiler()
        self.manifest_parser = ManifestParser()
        self.permission_checker = PermissionChecker()

    async def analyze_apk(self, uploaded_file, db: Session) -> Dict:
        """Main APK analysis function."""
        apk_path = None
        try:
            # Save uploaded file
            apk_path = save_uploaded_apk(uploaded_file)

            # Decompile and analyze
            logger.info(f"Starting analysis of {uploaded_file.filename}")

            # Androguard analysis
            androguard_data = self.decompiler.analyze_with_androguard(apk_path)

            # Parse manifest
            manifest_analysis = self.manifest_parser.parse_manifest(androguard_data['manifest_xml'])

            # Permission analysis
            permission_analysis = self.permission_checker.analyze_permissions(manifest_analysis['permissions'])

            # Component analysis
            component_analysis = self.permission_checker.check_component_exposure(manifest_analysis['components'])

            # Security flags analysis
            security_analysis = self.permission_checker.assess_security_flags(manifest_analysis['security_flags'])

            # Decompile with apktool for deeper analysis
            decompiled_dir = self.decompiler.decompile_with_apktool(apk_path)

            # Extract endpoints
            endpoints = self.decompiler.extract_endpoints(decompiled_dir)

            # Store in database
            apk_record = self._store_analysis_results(db, uploaded_file.filename, manifest_analysis,
                                                    permission_analysis, component_analysis, security_analysis, endpoints)

            # Prepare response
            result = {
                'apk_id': apk_record.id,
                'package_name': manifest_analysis['package'],
                'version_code': manifest_analysis['version_code'],
                'version_name': manifest_analysis['version_name'],
                'permissions': permission_analysis,
                'components': component_analysis,
                'security_flags': security_analysis,
                'endpoints': endpoints,
                'overall_risk_score': self._calculate_risk_score(permission_analysis, component_analysis, security_analysis)
            }

            logger.info(f"Analysis completed for {uploaded_file.filename}")
            return result

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise
        finally:
            if apk_path:
                cleanup_temp_files(apk_path)

    def _store_analysis_results(self, db: Session, filename: str, manifest: Dict,
                              permissions: Dict, components: Dict, security: Dict, endpoints: List) -> models.APK:
        """Store analysis results in database."""
        # Create APK record
        apk_data = {
            'filename': filename,
            'package_name': manifest['package'],
            'version_code': manifest['version_code'],
            'version_name': manifest['version_name'],
            'min_sdk': manifest.get('min_sdk'),
            'target_sdk': manifest.get('target_sdk'),
            'debuggable': manifest['security_flags'].get('debuggable', False),
            'allow_backup': manifest['security_flags'].get('allow_backup', True),
            'uses_cleartext_traffic': manifest['security_flags'].get('uses_cleartext_traffic', False),
            'network_security_config': manifest['security_flags'].get('network_security_config', '')
        }
        apk = crud.create_apk(db, apk_data)

        # Store permissions
        for perm in manifest['permissions']:
            perm_record = crud.get_permission_by_name(db, perm['name'])
            if not perm_record:
                perm_record = crud.create_permission(db, perm)
            apk.permissions.append(perm_record)

        # Store components
        for comp_type, comp_list in manifest['components'].items():
            for comp in comp_list:
                comp_data = {
                    'type': comp_type,
                    'name': comp['name'],
                    'exported': comp.get('exported', False),
                    'permission': comp.get('permission', ''),
                    'intent_filters': str(comp.get('intent_filters', {}))
                }
                component = crud.create_component(db, comp_data)
                apk.components.append(component)

        # Store endpoints
        for endpoint in endpoints:
            endpoint_data = {
                'url': endpoint['url'],
                'type': endpoint['type'],
                'apk_id': apk.id
            }
            crud.create_endpoint(db, endpoint_data)

        db.commit()
        return apk

    def _calculate_risk_score(self, permissions: Dict, components: Dict, security: Dict) -> int:
        """Calculate overall risk score (0-10)."""
        score = 0

        # Permission risk
        score += min(permissions.get('overprivilege_score', 0), 4)

        # Component exposure
        score += min(components.get('total_issues', 0) * 2, 3)

        # Security flags
        score += min(security.get('total_issues', 0) * 2, 3)

        return min(score, 10)