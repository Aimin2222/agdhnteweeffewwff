"""Bounded, single-layer QA ZIPs; stream large videos and preserve originals."""
from pathlib import Path
import json
import zipfile

DEFAULT_MAX_BYTES = 500_000_000
SAFETY_BYTES = 25_000_000
CHUNK_BYTES = 420_000_000
READ_BYTES = 1024 * 1024


def split_test_results(folder, *, max_bytes=DEFAULT_MAX_BYTES, log=lambda _m: None,
                       report_update=None):
    """Plan archives before updating results.json, so every ZIP has final data.

    Oversized inputs are streamed into numbered parts with a restoration note.
    Repeat exports use new names, and original videos/reports remain on disk.
    """
    folder = Path(folder).resolve()
    max_bytes = int(max_bytes)
    if not 1_000_000 < max_bytes <= DEFAULT_MAX_BYTES:
        raise ValueError('max_bytes must be greater than 1MB and at most 500MB')
    limit = max_bytes - min(SAFETY_BYTES, max_bytes // 12)
    chunk_size = min(CHUNK_BYTES, limit - 8192)
    items = []; restoration = []
    extensions = {'.mp4', '.json', '.txt', '.md', '.csv', '.jpg', '.png'}
    for path in sorted(folder.rglob('*')):
        if path.is_symlink() or not path.is_file() or path.suffix.lower() not in extensions:
            continue
        if not path.resolve().is_relative_to(folder):
            continue
        name = path.relative_to(folder).as_posix(); size = path.stat().st_size
        if size + 4096 <= limit:
            # Leave headroom for archive names appended to final results.json.
            reserve = min(250_000, limit // 8) if name == 'results.json' else 0
            items.append((path, name, 0, size, reserve))
        else:
            count = (size + chunk_size - 1) // chunk_size
            for index in range(count):
                offset = index * chunk_size
                items.append((path, f'{name}.part{index+1:03d}', offset, min(chunk_size, size-offset), 0))
            restoration.append({'original': name, 'bytes': size, 'parts': count,
                                'instruction': 'Restore by binary concatenation in numeric part order.'})
    if restoration:
        note = json.dumps(restoration, ensure_ascii=False, indent=2).encode('utf-8')
        items.append((note, 'RESTORE_OVERSIZED_FILES.txt', 0, len(note), 0))
    if not items:
        if report_update: report_update([])
        return []
    bins = []; current = []; used = 0
    for item in items:
        cost = item[3] + item[4] + 4096 + len(item[1].encode('utf-8'))
        if cost > limit:
            raise ValueError('QA report or archive entry exceeds the size limit')
        if current and used + cost > limit:
            bins.append(current); current = []; used = 0
        current.append(item); used += cost
    if current: bins.append(current)
    generation = 0
    while True:
        stem = folder.name if generation == 0 else f'{folder.name}_export{generation+1:02d}'
        outputs = [folder / f'{stem}_part{index+1:03d}.zip' for index in range(len(bins))]
        if not any(p.exists() for p in outputs): break
        generation += 1
    if report_update:
        report_update(outputs)
    for target, entries in zip(outputs, bins):
        created = False
        try:
            with zipfile.ZipFile(target, 'x', compression=zipfile.ZIP_STORED, allowZip64=True) as archive:
                created = True
                for path, name, offset, size, reserve in entries:
                    if isinstance(path, bytes):
                        archive.writestr(name, path)
                        continue
                    if name == 'results.json' and report_update:
                        actual = path.stat().st_size
                        if actual > size + reserve:
                            raise ValueError('Updated QA report exceeds reserved space')
                        size = actual
                    with path.open('rb') as source, archive.open(name, 'w', force_zip64=True) as dest:
                        source.seek(offset); remaining = size
                        while remaining:
                            data = source.read(min(READ_BYTES, remaining))
                            if not data: raise OSError('QA input changed during export')
                            dest.write(data); remaining -= len(data)
            if target.stat().st_size > max_bytes:
                raise RuntimeError('Produced QA archive exceeds the maximum size')
            with zipfile.ZipFile(target) as archive:
                if archive.testzip() is not None:
                    raise RuntimeError('QA archive CRC failed')
            log(f'QA ZIP完成: {target.name} / {target.stat().st_size/1_000_000:.1f}MB')
        except Exception:
            if created: target.unlink(missing_ok=True)
            raise
    return outputs
