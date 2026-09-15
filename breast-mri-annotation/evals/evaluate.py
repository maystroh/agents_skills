"""Strict same-grid segmentation metrics. Coordinates use NIfTI RAS millimetres."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent / '.deps'))
import nibabel as nib
import numpy as np

def sha256(path):
    with open(path, 'rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def decode(image, encoding='scalar'):
    data = np.asanyarray(image.dataobj)
    if not np.isfinite(data).all():
        raise ValueError('Nonfinite mask values')
    if encoding == 'scalar':
        if data.ndim != 3 or not np.isin(data, [0, 1, 2]).all():
            raise ValueError('Expected 3D scalar labels 0=background, 1=breast, 2=nipple')
        return data == 1, data == 2
    if data.ndim == 5 and data.shape[3] == 1:
        data = data[:, :, :, 0, :]
    if data.ndim != 4 or data.shape[-1] != 2 or not np.isin(data, [0, 1]).all():
        raise ValueError('Expected binary components with explicit breast,nipple order')
    return data[..., 0].astype(bool), data[..., 1].astype(bool)

def dice(a, b):
    denominator = int(a.sum()) + int(b.sum())
    return float(2 * np.count_nonzero(a & b) / denominator) if denominator else None

def centroid(mask, affine):
    if not mask.any():
        return None
    return nib.affines.apply_affine(affine, np.argwhere(mask).mean(axis=0)).tolist()

def compare(prediction, reference, pred_encoding='scalar', ref_encoding='scalar'):
    p, g = nib.load(prediction), nib.load(reference)
    if p.header.get_xyzt_units()[0] != 'mm' or g.header.get_xyzt_units()[0] != 'mm':
        raise ValueError('Spatial units must explicitly be mm')
    if p.shape[:3] != g.shape[:3] or not np.allclose(p.affine, g.affine, atol=1e-4, rtol=0):
        raise ValueError('Geometry mismatch; explicitly resample with nearest neighbour before scoring')
    pb, pn = decode(p, pred_encoding)
    gb, gn = decode(g, ref_encoding)
    pc, gc = centroid(pn, p.affine), centroid(gn, g.affine)
    # Scalar export loses overlap: compare exclusive breast consistently for both encodings.
    return {
        'breast_dice_exclusive': dice(pb & ~pn, gb & ~gn),
        'breast_nipple_union_dice': dice(pb | pn, gb | gn),
        'nipple_dice': dice(pn, gn),
        'nipple_centroid_prediction_ras_mm': pc,
        'nipple_centroid_reference_ras_mm': gc,
        'nipple_centroid_distance_mm': float(np.linalg.norm(np.array(pc)-gc)) if pc is not None and gc is not None else None,
        'nipple_status': 'present_both' if pc is not None and gc is not None else 'missing_prediction' if pc is None and gc is not None else 'missing_reference' if gc is None and pc is not None else 'both_empty',
        'prediction_voxels': {'breast_exclusive': int((pb & ~pn).sum()), 'nipple': int(pn.sum())},
        'reference_voxels': {'breast_exclusive': int((gb & ~gn).sum()), 'nipple': int(gn.sum())},
        'prediction': str(Path(prediction).resolve()), 'reference': str(Path(reference).resolve()),
        'prediction_sha256': sha256(prediction), 'reference_sha256': sha256(reference),
        'prediction_encoding': pred_encoding, 'reference_encoding': ref_encoding,
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prediction', required=True)
    parser.add_argument('--reference', required=True)
    parser.add_argument('--prediction-encoding', choices=['scalar','components'], default='scalar')
    parser.add_argument('--reference-encoding', choices=['scalar','components'], default='scalar')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    result = compare(args.prediction, args.reference, args.prediction_encoding, args.reference_encoding)
    Path(args.output).write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps(result, indent=2))
