import unittest
from batch_metrics import np,map_array,region_stats,summarize

class BatchMetricTests(unittest.TestCase):
    def test_reversed_affine_and_outside_coverage(self):
        a=np.zeros((3,3,2),np.uint8);a[1,1,:]=[1,2]
        ref=np.eye(4);ref[2,2]=-1;ref[2,3]=1
        out,_=map_array(a,np.eye(4),(3,3,3),ref)
        np.testing.assert_array_equal(out[1,1,:],[2,1,0])
        ref[0,3]=100
        out,_=map_array(a,np.eye(4),(3,3,3),ref)
        self.assertFalse(out.any())

    def test_physical_surface_and_empty(self):
        a=np.zeros((5,5,5),bool);b=a.copy();a[1,1,1]=1;b[2,1,1]=1
        r=region_stats(a,b,np.diag([3,2,5,1]))
        self.assertEqual(r['hd95_mm'],3)
        self.assertEqual(r['average_symmetric_surface_distance_mm'],3)
        self.assertEqual(r['centroid_distance_mm'],3)
        r=region_stats(a,np.zeros_like(a),np.eye(4))
        self.assertEqual(r['dice'],0);self.assertIsNone(r['centroid_distance_mm'])
        self.assertIsNone(r['hd95_mm'])

    def test_macro_differs_from_pooled(self):
        rows=[]
        for n,present in [(1,False),(9,True)]:
            a=np.ones((n,1,1),bool);b=a.copy() if present else np.zeros_like(a)
            stats=region_stats(a,b,np.eye(4),False)
            scope={k:stats for k in ['breast_exclusive','nipple','breast_nipple_union']}
            rows.append({'case':str(n),'full_reference_grid':scope,'common_field_of_view':scope,'nipple_localization':{'distance_mm':None}})
        total=summarize(rows)['metrics']['full_reference_grid']['breast_exclusive']
        self.assertEqual(total['mean_dice'],.5)
        self.assertAlmostEqual(total['pooled_voxel_dice'],18/19)

if __name__=='__main__':unittest.main()
