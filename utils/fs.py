import os
import subprocess

def gdal_path():
    common_paths = [
        '',
        '/Library/Frameworks/GDAL.framework/Programs',
        '/usr/local/bin'
    ]

    for common_path in common_paths:
        try:
            subprocess.run([os.path.join(common_path, 'gdalbuildvrt'), '--version'])
            return common_path
        except FileNotFoundError as e:
            continue

    return None

