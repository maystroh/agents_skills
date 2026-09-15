from pathlib import Path
from evaluate import np
from PIL import Image,ImageDraw
run=Path((Path(__file__).parent/'latest_run.txt').read_text())
for mode in ['source','overlay']:
    for start in range(0,20,5):
        canvas=Image.new('RGB',(2000,440))
        draw=ImageDraw.Draw(canvas)
        for n,k in enumerate(range(start,start+5)):
            im=Image.open(run/'slicer_review'/f'k{k:02d}_{mode}.png').convert('RGB')
            w,h=im.size
            im=im.crop(((w-h)//2,0,(w+h)//2,h));im.thumbnail((400,400))
            canvas.paste(im,(n*400,30));draw.text((n*400+10,8),f'Slicer native k={k} {mode}',fill='white')
        canvas.save(run/'slicer_review'/f'sheet_{mode}_{start}.png')
