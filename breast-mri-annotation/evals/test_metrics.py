import tempfile
import unittest
from pathlib import Path
from evaluate import np,nib,compare,dice,centroid,decode

class MetricsTests(unittest.TestCase):
    def test_dice_partial_and_empty(self):
        a=np.array([1,1,0],bool);b=np.array([0,1,1],bool)
        self.assertEqual(dice(a,b),.5)
        self.assertEqual(dice(a,np.zeros(3,bool)),0)
        self.assertIsNone(dice(np.zeros(3,bool),np.zeros(3,bool)))

    def test_oblique_anisotropic_centroid(self):
        a=np.zeros((4,4,4),bool);a[1,2,3]=True
        affine=np.array([[0,-3,0,10],[2,0,0,-20],[0,0,5,30],[0,0,0,1]])
        np.testing.assert_allclose(centroid(a,affine),[4,-18,45])

    def test_full_comparison_shift_and_mismatch(self):
        with tempfile.TemporaryDirectory() as t:
            a=np.zeros((5,5,5),np.uint8);a[1,1,1]=2
            b=np.zeros_like(a);b[2,1,1]=2
            affine=np.diag([2.,3.,4.,1.])
            def save(data,path,aff):
                im=nib.Nifti1Image(data,aff);im.header.set_xyzt_units('mm');nib.save(im,path)
            p=Path(t)/'p.nii.gz';g=Path(t)/'g.nii.gz'
            save(a,p,affine);save(b,g,affine)
            r=compare(p,g)
            self.assertEqual(r['nipple_centroid_distance_mm'],2)
            self.assertEqual(r['nipple_dice'],0)
            save(a,g,affine)
            self.assertEqual(compare(p,g)['nipple_dice'],1)
            affine[0,3]=1;save(a,g,affine)
            with self.assertRaises(ValueError): compare(p,g)

    def test_overlap_components(self):
        a=np.zeros((3,3,3,1,2),np.uint8);a[1,1,1,0,:]=1
        b,n=decode(nib.Nifti1Image(a,np.eye(4)),'components')
        self.assertEqual(np.count_nonzero(b&n),1)
        with self.assertRaises(ValueError):decode(nib.Nifti1Image(a,np.eye(4)))

    def test_reversed_grid_extra_slice_is_background(self):
        from scipy.ndimage import affine_transform
        a=np.zeros((3,3,2),np.uint8);a[1,1,0]=1;a[1,1,1]=2
        mapped=affine_transform(a,np.diag([1,1,-1]),offset=[0,0,1],output_shape=(3,3,3),order=0,mode='grid-constant',cval=0,prefilter=False)
        np.testing.assert_array_equal(mapped[:,:,:2],a[:,:,::-1])
        self.assertFalse(mapped[:,:,2].any())

if __name__=='__main__':unittest.main()
