"""Run inside a separate Slicer instance using --python-script. Saves actual views."""
import json, traceback
from pathlib import Path
import numpy as np
import slicer, vtk, qt
root=Path(r'<LOCAL_WORKSPACE>\breast-mri-evals')
run=Path((root/'latest_run.txt').read_text())

def review():
    try:
        source=next((run/'input').glob('*.nii.gz'))
        v=slicer.util.loadVolume(str(source))
        seg=slicer.mrmlScene.AddNewNodeByClass('vtkMRMLSegmentationNode','EVAL_0003_ASTRA_DRAFT')
        seg.CreateDefaultDisplayNodes(); seg.SetReferenceImageGeometryParameterFromVolumeNode(v)
        arrays=np.load(run/'segments.npz')
        matrix=vtk.vtkMatrix4x4();v.GetIJKToRASMatrix(matrix)
        # Original NIfTI direction is reflected relative to Slicer's normalized K.
        # Load scalar masks via Slicer and use segment import to honor physical geometry.
        label=slicer.util.loadLabelVolume((run/'prediction.txt').read_text())
        slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(label,seg)
        ids=[seg.GetSegmentation().GetNthSegmentID(i) for i in range(2)]
        for sid,name,color in zip(ids,['breast_region','nipple'],[(0,1,0),(1,0,0)]):
            seg.GetSegmentation().GetSegment(sid).SetName(name)
            seg.GetSegmentation().GetSegment(sid).SetColor(*color)
        # Restore breast overlap where nipple lies inside original breast, using physical mapping.
        import SimpleITK as sitk
        ref=sitk.ReadImage(str(source))
        bm=sitk.GetImageFromArray(arrays['breast'].transpose(2,1,0).astype('uint8'));bm.CopyInformation(ref)
        sitk.WriteImage(bm,str(run/'breast_overlap.nii.gz'))
        bv=slicer.util.loadLabelVolume(str(run/'breast_overlap.nii.gz'))
        temp=slicer.mrmlScene.AddNewNodeByClass('vtkMRMLSegmentationNode')
        slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(bv,temp)
        ba=slicer.util.arrayFromSegmentBinaryLabelmap(temp,temp.GetSegmentation().GetNthSegmentID(0),v)
        slicer.util.updateSegmentBinaryLabelmapFromArray(ba,seg,ids[0],v)
        slicer.mrmlScene.RemoveNode(temp);slicer.mrmlScene.RemoveNode(bv);slicer.mrmlScene.RemoveNode(label)
        slicer.util.selectModule('SegmentEditor')
        editor=slicer.modules.segmenteditor.widgetRepresentation().self().editor
        editor.setSegmentationNode(seg);editor.setSourceVolumeNode(v)
        editor.mrmlSegmentEditorNode().SetOverwriteMode(slicer.vtkMRMLSegmentEditorNode.OverwriteNone)
        editor.setCurrentSegmentID(ids[0]);editor.setActiveEffectByName('')
        display=seg.GetDisplayNode();display.SetVisibility(True);display.SetVisibility2D(True)
        display.SetOpacity2DFill(.08);display.SetOpacity2DOutline(1)
        slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpYellowSliceView)
        slicer.util.setSliceViewerLayers(background=v)
        sw=slicer.app.layoutManager().sliceWidget('Yellow');sn=sw.mrmlSliceNode()
        sn.SetOrientationToSagittal();sn.RotateToVolumePlane(v)
        slicer.util.resetSliceViews()
        # Source original affine, LPS->RAS; original k indices explicitly mapped to world.
        origin=np.array(ref.GetOrigin()); direction=np.array(ref.GetDirection()).reshape(3,3); spacing=np.array(ref.GetSpacing())
        out=run/'slicer_review';out.mkdir(exist_ok=True)
        for k in range(ref.GetSize()[2]):
            lps=origin+direction @ (np.array([95.5,95.5,k])*spacing)
            ras=lps*np.array([-1,-1,1])
            sn.JumpSliceByCentering(*ras)
            for overlay in [False,True]:
                display.SetVisibility(overlay)
                slicer.app.processEvents();slicer.util.forceRenderAllViews();slicer.app.processEvents()
                sw.sliceView().grab().save(str(out/f'k{k:02d}_{"overlay" if overlay else "source"}.png'))
        display.SetVisibility(True)
        slicer.util.saveNode(seg,str(run/'QIN-BREAST-01-0003_ASTRA.seg.nrrd'))
        (run/'slicer_capture_status.json').write_text(json.dumps({'captured_native_k':list(range(20)),'reviewed':False,'slicer_version':slicer.app.applicationVersion,'source_node':v.GetID(),'draft_node':seg.GetID(),'overwrite_mode':editor.mrmlSegmentEditorNode().GetOverwriteMode()}))
    except Exception:
        (run/'slicer_error.txt').write_text(traceback.format_exc())
qt.QTimer.singleShot(3000,review)
