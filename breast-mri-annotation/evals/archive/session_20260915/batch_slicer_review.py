"""Run in a separate Slicer instance. Only manipulates this script's created nodes."""
import json,traceback,hashlib
from pathlib import Path
from datetime import datetime
import numpy as np
import slicer,qt,SimpleITK as sitk
from PIL import Image,ImageDraw
root=Path(r'<LOCAL_WORKSPACE>\breast-mri-evals')
batch=Path((root/'latest_batch.txt').read_text())

def run_all():
    jobs=json.loads((batch/'batch.json').read_text())['cases']
    for job in jobs:
        run=Path(job['run']);m=json.loads((run/'manifest.json').read_text());created=[]
        try:
            def remember(node):created.append(node);return node
            v=remember(slicer.util.loadVolume(str(next((run/'input').glob('*.nii.gz')))))
            seg=remember(slicer.mrmlScene.AddNewNodeByClass('vtkMRMLSegmentationNode',m['case']+'_ASTRA_EVAL_DRAFT'))
            seg.CreateDefaultDisplayNodes();seg.SetReferenceImageGeometryParameterFromVolumeNode(v)
            slicer.util.selectModule('SegmentEditor')
            editor=slicer.modules.segmenteditor.widgetRepresentation().self().editor
            editor.setSegmentationNode(seg);editor.setSourceVolumeNode(v);editor.setActiveEffectByName('')
            editor.mrmlSegmentEditorNode().SetOverwriteMode(slicer.vtkMRMLSegmentEditorNode.OverwriteNone)
            expected=np.load(run/'segments.npz');ref=sitk.ReadImage(str(next((run/'input').glob('*.nii.gz'))))
            segment_ids=[]
            for name,color in [('breast_region',(0,1,0)),('nipple',(1,0,0))]:
                key='breast' if name=='breast_region' else 'nipple'
                sid=seg.GetSegmentation().AddEmptySegment(name,name,color);segment_ids.append(sid)
                mask=sitk.GetImageFromArray(expected[key].transpose(2,1,0).astype('uint8'));mask.CopyInformation(ref)
                file=run/(key+'_raw.nii.gz');sitk.WriteImage(mask,str(file))
                volume=slicer.util.loadLabelVolume(str(file))
                temp=slicer.mrmlScene.AddNewNodeByClass('vtkMRMLSegmentationNode')
                slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(volume,temp)
                array=slicer.util.arrayFromSegmentBinaryLabelmap(temp,temp.GetSegmentation().GetNthSegmentID(0),v).copy()
                slicer.util.updateSegmentBinaryLabelmapFromArray(array,seg,sid,v)
                assert np.array_equal(array,slicer.util.arrayFromSegmentBinaryLabelmap(seg,sid,v))
                slicer.mrmlScene.RemoveNode(temp);slicer.mrmlScene.RemoveNode(volume)
            editor.setCurrentSegmentID(segment_ids[0])
            display=seg.GetDisplayNode();display.SetVisibility(True);display.SetVisibility2D(True)
            for sid in segment_ids:display.SetSegmentVisibility(sid,True)
            display.SetOpacity2DFill(.08);display.SetOpacity2DOutline(1)
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpYellowSliceView)
            slicer.util.setSliceViewerLayers(background=v)
            sw=slicer.app.layoutManager().sliceWidget('Yellow');sn=sw.mrmlSliceNode()
            sn.SetOrientationToSagittal();sn.RotateToVolumePlane(v);slicer.util.resetSliceViews()
            origin=np.array(ref.GetOrigin());direction=np.array(ref.GetDirection()).reshape(3,3);spacing=np.array(ref.GetSpacing());size=np.array(ref.GetSize())
            out=run/'slicer_review';out.mkdir(exist_ok=True)
            for k in range(size[2]):
                ras=(origin+direction @ (np.array([(size[0]-1)/2,(size[1]-1)/2,k])*spacing))*[-1,-1,1]
                sn.JumpSliceByCentering(*ras)
                for mode in ['source','overlay']:
                    display.SetVisibility(mode=='overlay');slicer.app.processEvents();slicer.util.forceRenderAllViews();slicer.app.processEvents()
                    sw.sliceView().grab().save(str(out/f'k{k:02d}_{mode}.png'))
            display.SetVisibility(True)
            saved=run/(m['case']+'_ASTRA.seg.nrrd');slicer.util.saveNode(seg,str(saved))
            reloaded=slicer.util.loadSegmentation(str(saved))
            for n,sid in enumerate(segment_ids):
                assert np.array_equal(slicer.util.arrayFromSegmentBinaryLabelmap(seg,sid,v),slicer.util.arrayFromSegmentBinaryLabelmap(reloaded,reloaded.GetSegmentation().GetNthSegmentID(n),v))
            slicer.mrmlScene.RemoveNode(reloaded)
            for mode in ['source','overlay']:
                canvas=Image.new('RGB',(1600,1360));draw=ImageDraw.Draw(canvas)
                for k in range(size[2]):
                    image=Image.open(out/f'k{k:02d}_{mode}.png').convert('RGB');w,h=image.size
                    image=image.crop(((w-h)//2,0,(w+h)//2,h)).resize((320,320))
                    x=k%5*320;y=k//5*340;canvas.paste(image,(x,y+20));draw.text((x+5,y+3),f'{m["case"][-4:]} native k={k} {mode}',fill='white')
                canvas.save(out/f'{mode}_all.png')
            k=int(round(json.loads((run/'anchors.json').read_text())['nipple_ijk'][2]))
            canvas=Image.new('RGB',(1200,620));draw=ImageDraw.Draw(canvas)
            for n,mode in enumerate(['source','overlay']):
                image=Image.open(out/f'k{k:02d}_{mode}.png').convert('RGB');w,h=image.size
                image=image.crop(((w-h)//2,0,(w+h)//2,h)).resize((600,600))
                canvas.paste(image,(n*600,20));draw.text((n*600+5,3),f'{m["case"][-4:]} k={k} {mode}',fill='white')
            canvas.save(out/'nipple_closeup.png')
            (run/'slicer_capture_status.json').write_text(json.dumps({'captured_native_k':list(range(int(size[2]))),'reviewed':False,'prediction_sha256':hashlib.sha256(Path(m['prediction']).read_bytes()).hexdigest(),'slicer_version':slicer.app.applicationVersion,'source_node':v.GetID(),'draft_node':seg.GetID(),'allow_overlap_verified':editor.mrmlSegmentEditorNode().GetOverwriteMode()==slicer.vtkMRMLSegmentEditorNode.OverwriteNone,'working_segmentation_reload_verified':True,'created':datetime.now().astimezone().isoformat()}))
            print('CAPTURED',m['case'])
        except Exception:
            (run/'slicer_error.txt').write_text(traceback.format_exc())
        finally:
            for node in reversed(created):
                if slicer.mrmlScene.IsNodePresent(node):slicer.mrmlScene.RemoveNode(node)
    (batch/'slicer_batch_finished.txt').write_text(datetime.now().astimezone().isoformat())
qt.QTimer.singleShot(3000,run_all)
