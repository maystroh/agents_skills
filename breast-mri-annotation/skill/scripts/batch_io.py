"""NIfTI batch inventory and verified labelmap export; no segmentation model."""
import argparse
import datetime as dt
import json
from pathlib import Path
import re

def source_stem(path):
    name = Path(path).name
    if name.lower().endswith('.nii.gz'):
        return name[:-7]
    if name.lower().endswith('.nii'):
        return name[:-4]
    raise ValueError('Expected .nii or .nii.gz')

def inventory(folder):
    folder = Path(folder)
    if not folder.is_dir():
        raise ValueError('Input folder does not exist')
    rows = []
    for path in sorted(folder.iterdir()):
        if not path.is_file() or not path.name.lower().endswith(('.nii', '.nii.gz')):
            continue
        stem = source_stem(path)
        if re.search(r'(^|[_\-.])(mask|seg|segmentation|label|labels)([_\-.]|$)', stem, re.I):
            continue
        rows.append({'source': str(path.resolve()), 'stem': stem, 'status': 'pending'})
    return rows

def output_path(source, folder=None, timestamp=None):
    stamp = timestamp or dt.datetime.now().astimezone().strftime('%Y%m%d_%H%M%S')
    dt.datetime.strptime(stamp, '%Y%m%d_%H%M%S')
    return Path(folder or Path(source).parent) / f'{source_stem(source)}_mask_astra_{stamp}.nii.gz'

def export_mask(source, breast, nipple, destination):
    """Arrays must already be in the original source's KJI grid."""
    import numpy as np
    import SimpleITK as sitk
    source, destination = Path(source), Path(destination)
    if destination.exists():
        raise FileExistsError(destination)
    ref = sitk.ReadImage(str(source))
    if ref.GetDimension() != 3 or ref.GetNumberOfComponentsPerPixel() != 1:
        raise ValueError('Expected a scalar 3D source; choose timepoint/components explicitly')
    shape = tuple(reversed(ref.GetSize()))
    if breast.shape != shape or nipple.shape != shape:
        raise ValueError(f'Masks must match original source KJI shape {shape}')
    if not np.isin(breast, [0, 1]).all() or not np.isin(nipple, [0, 1]).all():
        raise ValueError('Expected binary masks')
    labels = np.zeros(shape, dtype=np.uint8)
    labels[breast != 0] = 1
    labels[nipple != 0] = 2
    image = sitk.GetImageFromArray(labels)
    image.CopyInformation(ref)
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Reserve the name exclusively, avoiding silent replacement of an export.
    with destination.open('xb'):
        pass
    sitk.WriteImage(image, str(destination), True)
    saved = sitk.ReadImage(str(destination))
    if not np.array_equal(sitk.GetArrayFromImage(saved), labels):
        raise RuntimeError('Export voxel verification failed')
    for getter in ('GetOrigin', 'GetSpacing', 'GetDirection'):
        if not np.allclose(getattr(saved, getter)(), getattr(ref, getter)(), atol=1e-5, rtol=1e-6):
            raise RuntimeError('Export geometry verification failed: ' + getter)
    return {'path': str(destination.resolve()), 'verified': True,
            'labelVoxels': {str(i): int((labels == i).sum()) for i in (0, 1, 2)}}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    inv = sub.add_parser('inventory'); inv.add_argument('folder')
    args = parser.parse_args()
    print(json.dumps(inventory(args.folder), indent=2))
