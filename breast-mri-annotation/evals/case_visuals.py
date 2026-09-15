"""Compact, reproducible visual comparisons of frozen annotations."""
from pathlib import Path
import html
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


def select_slices(pred_union, human_union, pred_nipple, human_nipple):
    """Show greatest union disagreement and peak-area nipple slices; fill duplicates."""
    counts = np.count_nonzero(pred_union ^ human_union, axis=(0, 1))
    selected = [int(np.argmax(counts))]
    for mask in (pred_nipple, human_nipple):
        if mask.any():
            k = int(np.argmax(np.count_nonzero(mask, axis=(0, 1))))
            if k not in selected:
                selected.append(k)
    foreground = np.count_nonzero(pred_union | human_union, axis=(0, 1))
    candidates = sorted(range(len(counts)), key=lambda k: (-int(counts[k]), -int(foreground[k]), k))
    while len(selected) < min(3, len(counts)):
        remaining = [k for k in candidates if k not in selected]
        separated = [k for k in remaining if foreground[k] and min(abs(k-j) for j in selected) >= 3]
        selected.append((separated or remaining)[0])
    return sorted(selected)


def render_comparison(source, pred_union, human_union, pred_nipple, human_nipple, output, case):
    masks = [np.asarray(m, dtype=bool) for m in (pred_union, human_union, pred_nipple, human_nipple)]
    indices = select_slices(*masks)
    colors = ['lime', 'cyan', '#ff4040', 'orange']
    labels = ['Astra breast', 'Human breast', 'Astra nipple', 'Human nipple']
    fig, axes = plt.subplots(1, len(indices), figsize=(5*len(indices), 5.6), squeeze=False, facecolor='#111820')
    vmin, vmax = np.percentile(source, [1, 99.8])
    for ax, k in zip(axes.flat, indices):
        ax.imshow(source[:, :, k].T, cmap='gray', origin='upper', vmin=vmin, vmax=vmax)
        for mask, color in zip(masks, colors):
            if mask[:, :, k].any():
                ax.contour(mask[:, :, k].T, levels=[.5], colors=[color], linewidths=1.2)
        ax.set_title(f'Slice {k} (0-based)', color='white', fontsize=12)
        ax.axis('off')
    fig.suptitle(f'{case} | Human vs Astra', color='white', fontsize=17)
    fig.legend([Line2D([0], [0], color=c, lw=2) for c in colors], labels,
               loc='lower center', ncol=4, frameon=False, labelcolor='white', fontsize=11)
    fig.tight_layout(rect=(0, .07, 1, .93))
    fig.savefig(Path(output)/'comparison.png', dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)
    return indices


def write_case_report(output, case):
    output = Path(output)
    (output/'report.md').write_text(f'# {case}: human vs Astra\n\n![Human and Astra contours on three selected MRI slices](comparison.png)\n', encoding='utf-8')
    title = html.escape(case)
    (output/'report.html').write_text(
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>{title}: human vs Astra</title><style>body{{font:16px system-ui;background:#111820;color:white;margin:24px}}'
        'main{max-width:1600px;margin:auto}img{width:100%;height:auto}</style>'
        f'<main><h1>{title}: human vs Astra</h1><img src="comparison.png" alt="Human and Astra contours on three selected MRI slices"></main></html>',
        encoding='utf-8')
