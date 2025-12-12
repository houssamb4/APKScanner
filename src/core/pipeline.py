"""
APK Processing Pipeline Orchestrator.

Pipeline flow: Input APK → Validate → Extract → Decompile → Organize → Output
"""

from typing import Dict, Tuple
from sqlalchemy.orm import Session
from ..utils.logger import logger
from .validators import APKValidator
from ..services.apk_analyzer import APKAnalyzer
import os
import shutil
import uuid


class PipelineStage:
    """Represents a stage in the APK processing pipeline."""
    
    VALIDATE = "validate"
    EXTRACT = "extract"
    DECOMPILE = "decompile"
    ORGANIZE = "organize"
    OUTPUT = "output"
    
    ALL_STAGES = [VALIDATE, EXTRACT, DECOMPILE, ORGANIZE, OUTPUT]


class APKPipeline:
    """Orchestrates the complete APK analysis pipeline."""
    
    def __init__(self):
        self.validator = APKValidator()
        self.analyzer = APKAnalyzer()
        self.pipeline_log = []
    
    def process_apk(self, apk_file_path: str, db: Session) -> Tuple[bool, Dict]:
        """
        Process an APK through the complete pipeline.
        
        Args:
            apk_file_path: Path to the APK file
            db: Database session
            
        Returns:
            Tuple of (success, result_dict)
        """
        self.pipeline_log = []
        result = {
            'success': False,
            'stages': {},
            'data': None,
            'error': None
        }
        
        try:
            # Stage 1: Validate
            logger.info("[STAGE 1/5] VALIDATE")
            valid, error_msg = self._stage_validate(apk_file_path)
            result['stages']['validate'] = {
                'success': valid,
                'message': error_msg if not valid else 'APK file validation successful'
            }
            
            if not valid:
                result['error'] = error_msg
                logger.error(f"[ERROR] Validation failed: {error_msg}")
                return False, result
            
            logger.info("[OK] Validation passed")
            
            # Stage 2: Extract (Info extraction via androguard)
            logger.info("[STAGE 2/5] EXTRACT")
            extract_data, extract_error = self._stage_extract(apk_file_path)
            result['stages']['extract'] = {
                'success': extract_data is not None,
                'message': extract_error if extract_error else 'APK metadata extraction successful'
            }
            
            if extract_data is None:
                result['error'] = extract_error
                logger.error(f"[ERROR] Extraction failed: {extract_error}")
                return False, result
            
            logger.info("[OK] Extraction passed")
            
            # Stage 3: Decompile
            logger.info("[STAGE 3/5] DECOMPILE")
            decompile_result, decompile_error = self._stage_decompile(apk_file_path, extract_data)
            result['stages']['decompile'] = {
                'success': decompile_result is not None,
                'message': decompile_error if decompile_error else 'APK decompilation successful'
            }
            
            if decompile_result is None:
                result['error'] = decompile_error
                logger.error(f"[ERROR] Decompilation failed: {decompile_error}")
                return False, result
            
            logger.info("[OK] Decompilation passed")
            
            # Stage 4: Organize (Prepare structured analysis)
            logger.info("[STAGE 4/5] ORGANIZE")
            organized_data, organize_error = self._stage_organize(extract_data, decompile_result)
            result['stages']['organize'] = {
                'success': organized_data is not None,
                'message': organize_error if organize_error else 'Analysis organization successful'
            }
            
            if organized_data is None:
                result['error'] = organize_error
                logger.error(f"[ERROR] Organization failed: {organize_error}")
                return False, result
            
            logger.info("[OK] Organization passed")
            
            # Stage 5: Output (Store results)
            logger.info("[STAGE 5/5] OUTPUT")
            output_result, output_error = self._stage_output(organized_data, db)
            result['stages']['output'] = {
                'success': output_result is not None,
                'message': output_error if output_error else 'Results stored successfully'
            }
            
            if output_result is None:
                result['error'] = output_error
                logger.error(f"[ERROR] Output failed: {output_error}")
                return False, result
            
            logger.info("[OK] Output passed")
            
            # All stages completed
            result['success'] = True
            result['data'] = output_result
            logger.info("[OK] Pipeline completed successfully!")
            
            return True, result
            
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}")
            result['error'] = str(e)
            return False, result
    
    def _stage_validate(self, apk_file_path: str) -> Tuple[bool, str]:
        """
        Stage 1: Validate APK file format and structure.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Basic file validation
            valid, error = self.validator.validate_apk_file(apk_file_path)
            if not valid:
                return False, error
            
            # Structure validation
            valid, error = self.validator.validate_apk_structure(apk_file_path)
            if not valid:
                return False, error
            
            return True, ""
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def _stage_extract(self, apk_file_path: str) -> Tuple[Dict, str]:
        """
        Stage 2: Extract APK metadata using androguard.
        
        Returns:
            Tuple of (extracted_data, error_message)
        """
        try:
            extracted_data = self.analyzer.decompiler.analyze_with_androguard(apk_file_path)
            return extracted_data, ""
        except Exception as e:
            return None, f"Extraction error: {str(e)}"
    
    def _stage_decompile(self, apk_file_path: str, extracted_data: Dict) -> Tuple[Dict, str]:
        """
        Stage 3: Decompile APK using apktool and analyze code.
        
        Returns:
            Tuple of (decompile_data, error_message)
        """
        try:
            decompiled_dir = self.analyzer.decompiler.decompile_with_apktool(apk_file_path)
            
            # Generate random UID for decompiled folder
            decompile_uid = str(uuid.uuid4())
            parent_dir = os.path.dirname(decompiled_dir)
            uid_decompiled_dir = os.path.join(parent_dir, decompile_uid)
            
            # Rename decompiled directory to use the UID
            if os.path.exists(decompiled_dir) and decompiled_dir != uid_decompiled_dir:
                if os.path.exists(uid_decompiled_dir):
                    shutil.rmtree(uid_decompiled_dir)
                shutil.move(decompiled_dir, uid_decompiled_dir)
                logger.info(f"Renamed decompiled dir to {uid_decompiled_dir}")
            
            endpoints = self.analyzer.decompiler.extract_endpoints(uid_decompiled_dir)
            apk_filename = os.path.basename(apk_file_path)

            return {
                'decompiled_dir': uid_decompiled_dir,
                'decompile_uid': decompile_uid,
                'endpoints': endpoints,
                'apk_filename': apk_filename
            }, ""
        except Exception as e:
            return None, f"Decompilation error: {str(e)}"
    
    def _stage_organize(self, extract_data: Dict, decompile_data: Dict) -> Tuple[Dict, str]:
        """
        Stage 4: Organize analysis data into structured format.
        
        Returns:
            Tuple of (organized_data, error_message)
        """
        try:
            # Parse manifest
            manifest = self.analyzer.manifest_parser.parse_manifest(
                extract_data.get('manifest_xml', '')
            )
            
            # Analyze permissions
            permissions = self.analyzer.permission_checker.analyze_permissions(
                manifest.get('permissions', [])
            )
            
            # Check components
            components = self.analyzer.permission_checker.check_component_exposure(
                manifest.get('components', {})
            )
            
            # Assess security
            security = self.analyzer.permission_checker.assess_security_flags(
                manifest.get('security_flags', {})
            )
            
            organized_data = {
                'manifest': manifest,
                'permissions': permissions,
                'components': components,
                'security': security,
                'endpoints': decompile_data.get('endpoints', []),
                'extract_data': extract_data,
                'decompiled_dir': decompile_data.get('decompiled_dir'),
                'decompile_uid': decompile_data.get('decompile_uid'),
                'apk_filename': decompile_data.get('apk_filename')
            }
            
            return organized_data, ""
        except Exception as e:
            return None, f"Organization error: {str(e)}"
    
    def _stage_output(self, organized_data: Dict, db: Session) -> Tuple[Dict, str]:
        """
        Stage 5: Store results in database.
        
        Returns:
            Tuple of (output_result, error_message)
        """
        try:
            # Store in database
            from ..database import crud
            
            manifest = organized_data['manifest']
            endpoints = organized_data['endpoints']
            
            apk_data = {
                'filename': organized_data.get('apk_filename', 'analyzed_apk.apk'),
                'package_name': manifest.get('package', ''),
                'version_code': manifest.get('version_code', ''),
                'version_name': manifest.get('version_name', ''),
                'min_sdk': manifest.get('min_sdk'),
                'target_sdk': manifest.get('target_sdk'),
                'debuggable': manifest.get('security_flags', {}).get('debuggable', False),
                'allow_backup': manifest.get('security_flags', {}).get('allow_backup', True),
                'uses_cleartext_traffic': manifest.get('security_flags', {}).get('uses_cleartext_traffic', False),
                'network_security_config': manifest.get('security_flags', {}).get('network_security_config', '')
            }
            
            apk = crud.create_apk(db, apk_data)
            
            # Store permissions
            for perm in manifest.get('permissions', []):
                perm_record = crud.get_permission_by_name(db, perm['name'])
                if not perm_record:
                    # Filter out fields not in Permission model
                    perm_data = {
                        'name': perm['name'],
                        'protection_level': perm.get('protection_level', ''),
                        'description': perm.get('description', '')
                    }
                    perm_record = crud.create_permission(db, perm_data)
                apk.permissions.append(perm_record)
            
            # Store components
            for comp_type, comp_list in manifest.get('components', {}).items():
                for comp in comp_list:
                    comp_data = {
                        'type': comp_type,
                        'name': comp.get('name', ''),
                        'exported': comp.get('exported', False),
                        'permission': comp.get('permission', ''),
                        'intent_filters': str(comp.get('intent_filters', {}))
                    }
                    component = crud.create_component(db, comp_data)
                    apk.components.append(component)
            
            # Store endpoints
            for endpoint in endpoints:
                endpoint_data = {
                    'url': endpoint.get('url', ''),
                    'type': endpoint.get('type', 'unknown'),
                    'apk_id': apk.id
                }
                crud.create_endpoint(db, endpoint_data)
            
            db.commit()
            
            decompile_uid = organized_data.get('decompile_uid', 'unknown')

            result = {
                'apk_id': apk.id,
                'decompiled_folder': decompile_uid,
                'package_name': manifest.get('package', ''),
                'version_code': manifest.get('version_code', ''),
                'version_name': manifest.get('version_name', ''),
                'permissions': organized_data['permissions'],
                'components': organized_data['components'],
                'security_flags': organized_data['security'],
                'endpoints': endpoints,
                'overall_risk_score': self._calculate_risk_score(
                    organized_data['permissions'],
                    organized_data['components'],
                    organized_data['security']
                )
            }
            
            return result, ""
        except Exception as e:
            return None, f"Output error: {str(e)}"
    
    @staticmethod
    def _calculate_risk_score(permissions: Dict, components: Dict, security: Dict) -> int:
        """Calculate overall risk score (0-10)."""
        score = 0
        score += min(permissions.get('overprivilege_score', 0), 4)
        score += min(components.get('total_issues', 0) * 2, 3)
        score += min(security.get('total_issues', 0) * 2, 3)
        return min(score, 10)
