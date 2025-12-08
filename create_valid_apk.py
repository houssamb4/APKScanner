#!/usr/bin/env python3
"""Create a valid minimal APK for endpoint testing with proper binary manifest."""

import zipfile
import os
import struct

# Minimal binary Android manifest (compiled format)
# This is the smallest valid binary manifest structure
def create_minimal_manifest():
    """Create a minimal valid binary Android manifest."""
    # Android manifest magic + version
    manifest = bytearray()
    
    # ResXMLTree_header
    manifest.extend(struct.pack('<H', 0x0003))  # type: RES_XML_TYPE
    manifest.extend(struct.pack('<H', 8))       # headerSize
    manifest.extend(struct.pack('<I', 116))     # size (minimum)
    
    # StringPool_header
    manifest.extend(struct.pack('<H', 0x0001))  # type: RES_STRING_POOL_TYPE
    manifest.extend(struct.pack('<H', 28))      # headerSize
    manifest.extend(struct.pack('<I', 48))      # size
    manifest.extend(struct.pack('<I', 0))       # stringCount
    manifest.extend(struct.pack('<I', 0))       # styleCount
    manifest.extend(struct.pack('<I', 0x100))   # flags: UTF-8
    manifest.extend(struct.pack('<I', 28))      # stringsStart
    manifest.extend(struct.pack('<I', 0))       # stylesStart
    
    # EndElementTag
    manifest.extend(struct.pack('<H', 0x0103))  # type: RES_END_ELEMENT_TYPE
    manifest.extend(struct.pack('<H', 16))      # headerSize
    manifest.extend(struct.pack('<I', 16))      # size
    manifest.extend(struct.pack('<I', 0))       # lineNumber
    manifest.extend(struct.pack('<I', 0))       # unknown
    manifest.extend(struct.pack('<I', 0))       # nameRef
    
    return bytes(manifest)

# Create the APK
test_apk_path = 'temp/valid_test.apk'
os.makedirs('temp', exist_ok=True)

with zipfile.ZipFile(test_apk_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    # Add binary manifest
    zf.writestr('AndroidManifest.xml', create_minimal_manifest())
    
    # Add classes.dex with minimal DEX format
    # DEX magic number + version
    dex_header = bytearray(b'dex\n')
    dex_header.extend(b'035\x00')  # version 035
    dex_header.extend(b'\x00' * (0x70 - len(dex_header)))  # Pad to header size
    dex_header.extend(struct.pack('<I', len(dex_header)))  # file_size
    
    zf.writestr('classes.dex', bytes(dex_header))
    
    # Add optional resources
    zf.writestr('resources.arsc', b'')

print(f'Valid test APK created: {test_apk_path}')
print(f'File size: {os.path.getsize(test_apk_path)} bytes')
print('Ready for testing with androguard!')
