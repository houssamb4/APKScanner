import os
import subprocess
import tempfile
import re
from typing import TYPE_CHECKING
from ..core.config import settings
from ..utils.logger import logger

if TYPE_CHECKING:
    from androguard.core.apk import APK

# Try to import androguard, but make it optional
try:
    from androguard.core.apk import APK as AndroidAPK
    from androguard.core.dex import DEX
    ANDROGUARD_AVAILABLE = True
except ImportError:
    ANDROGUARD_AVAILABLE = False
    logger.warning("Androguard not installed. Some analysis features will be limited.")
    AndroidAPK = None  # type: ignore

class Decompiler:
    def __init__(self):
        self.apktool_path = settings.apktool_path

    def decompile_with_apktool(self, apk_path: str) -> str:
        """Decompile APK using apktool and return the output directory."""
        output_dir = apk_path.replace('.apk', '_decompiled')
        try:
            cmd = [self.apktool_path, 'd', '-f', '-o', output_dir, apk_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                logger.error(f"Apktool decompilation failed: {result.stderr}")
                raise Exception(f"Apktool error: {result.stderr}")
            logger.info(f"APK decompiled to {output_dir}")
            return output_dir
        except subprocess.TimeoutExpired:
            logger.error("Apktool decompilation timed out")
            raise Exception("Decompilation timed out")
        except FileNotFoundError:
            logger.error("Apktool not found. Please install apktool.")
            raise Exception("Apktool not installed")

    def analyze_with_androguard(self, apk_path: str) -> dict:
        """Analyze APK using Androguard and return analysis data."""
        if not ANDROGUARD_AVAILABLE:
            logger.warning("Androguard not available - returning minimal analysis")
            return {
                'package_name': 'unknown',
                'version_code': 'unknown',
                'version_name': 'unknown',
                'min_sdk': 'unknown',
                'target_sdk': 'unknown',
                'permissions': [],
                'activities': [],
                'services': [],
                'receivers': [],
                'providers': [],
                'intent_filters': {},
                'manifest_xml': '<manifest></manifest>',
            }
        
        try:
            apk = AndroidAPK(apk_path)
            analysis = {
                'package_name': apk.get_package(),
                'version_code': apk.get_androidversion_code(),
                'version_name': apk.get_androidversion_name(),
                'min_sdk': apk.get_min_sdk_version(),
                'target_sdk': apk.get_target_sdk_version(),
                'permissions': apk.get_permissions(),
                'activities': apk.get_activities(),
                'services': apk.get_services(),
                'receivers': apk.get_receivers(),
                'providers': apk.get_providers(),
                'intent_filters': self._extract_intent_filters(apk),
                'manifest_xml': apk.get_android_manifest_axml().get_xml(),
            }
            logger.info(f"Androguard analysis completed for {apk_path}")
            return analysis
        except Exception as e:
            logger.error(f"Androguard analysis failed: {e}")
            raise

    def _extract_intent_filters(self, apk: "APK") -> dict:
        """Extract intent filters from the APK."""
        filters = {}
        try:
            manifest = apk.get_android_manifest_axml()
            for activity in manifest.get_elements("activity"):
                name = activity.get_attribute("name")
                if name:
                    filters[name] = []
                    for intent_filter in activity.get_elements("intent-filter"):
                        filter_data = {}
                        for action in intent_filter.get_elements("action"):
                            filter_data['action'] = action.get_attribute("name")
                        for category in intent_filter.get_elements("category"):
                            filter_data['category'] = category.get_attribute("name")
                        for data in intent_filter.get_elements("data"):
                            filter_data['data'] = {
                                'scheme': data.get_attribute("scheme"),
                                'host': data.get_attribute("host"),
                                'path': data.get_attribute("path"),
                            }
                        if filter_data:
                            filters[name].append(filter_data)
        except Exception as e:
            logger.warning(f"Failed to extract intent filters: {e}")
        return filters

    def extract_endpoints(self, decompiled_dir: str) -> list:
        """Extract URLs and endpoints from decompiled code."""
        endpoints = []
        try:
            # This is a simplified extraction - in practice, you'd need more sophisticated analysis
            for root, dirs, files in os.walk(decompiled_dir):
                for file in files:
                    if file.endswith('.smali'):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            # Simple regex for URLs - in production, use proper parsing
                            import re
                            urls = re.findall(r'https?://[^\s\'"]+', content)
                            for url in urls:
                                endpoints.append({'url': url, 'type': 'hardcoded'})
        except Exception as e:
            logger.error(f"Failed to extract endpoints: {e}")
        return endpoints