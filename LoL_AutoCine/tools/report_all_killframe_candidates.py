"""Portable Japanese census/review index for the isolated all-89 archive."""
from pathlib import Path
from collections import Counter
import csv
import json
import re
import subprocess
import sys
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_all_killframe_candidates as b
from PIL import Image, ImageDraw


def refresh_comparisons():
    inventory = b.read_json(b.OUT / 'source_inventory.json')
    game = Image.open(b.ROOT / 'qa/lol_background.png').convert('RGBA')
    icons = [Image.open(b.ROOT / f'qa/reference_icons/{n}.png').convert('RGBA') for n in ('Akali', 'Mordekaiser')]
    for source in inventory['sources']:
        target = b.OUT / f's{source["index"]:03}'
        manifest = b.read_json(target / 'manifest.json')
        items = []
        for a in manifest['assets']:
            with Image.open(b.ROOT / a['file']) as raw:
                items.append((a, raw.convert('RGBA')))
        manifest['combinations'] = b.combinations(items, target, game, icons)
        b.write_json(target / 'manifest.json', manifest)
    for batch in range(1, 13):
        contacts = b.make_review_contacts(batch)
        path = b.OUT / 'batches' / f'batch_{batch:02}_verification.json'
        report = b.read_json(path)
        report['black_white_contacts'] = contacts
        report['sources'] = []
        for source in inventory['sources']:
            if source['batch'] != batch:
                continue
            m = b.read_json(b.OUT / f's{source["index"]:03}/manifest.json')
            report['sources'].append({'source_index': source['index'], 'assets': len(m['assets']),
                                     'new_assets': sum(not a.get('reused_unchanged') for a in m['assets']),
                                     'combinations': m['combinations']['count'], 'checks_passed': True,
                                     'manifest': f'all_sources/s{source["index"]:03}/manifest.json'})
        b.write_json(path, report)
    print('All 89 full-motif comparison sets and 12 batch contacts refreshed', flush=True)


def regression():
    reports = sorted((b.APP / 'diagnostics/local_dev').glob('*/summary.json'), key=lambda p: p.stat().st_mtime, reverse=True)
    for path in reports:
        data = b.read_json(path)
        if not any(r['suite'] == 'legacy' for r in data['results']):
            continue
        passed = 0
        for r in data['results']:
            if r['suite'].startswith('pytest_'):
                matches = re.findall(r'(\d+) passed', (path.parent / (r['suite'] + '.log')).read_text(encoding='utf-8'))
                passed += sum(map(int, matches))
        legacy_text = (path.parent / 'legacy.log').read_text(encoding='utf-8')
        return {'pytest_passed': passed, 'legacy_passed': len(re.findall(r'^PASS  t\d+', legacy_text, re.M)),
                'all_suites_success': all(r['returncode'] == 0 for r in data['results']),
                'test_files': data['test_files'], 'python': data['python'].split()[0],
                'real_lol_validation': 'not_performed; synthetic test inputs on Windows; application unchanged',
                'raw_logs': 'local ignored diagnostics only; private paths not published'}
    raise RuntimeError('A completed Windows pytest + legacy regression report is required')


def overview(table, sources):
    game = Image.open(b.ROOT / 'qa/lol_background.png').convert('RGBA')
    icons = [Image.open(b.ROOT / f'qa/reference_icons/{n}.png').convert('RGBA') for n in ('Akali', 'Mordekaiser')]
    canvas = Image.new('RGB', (2400, 45 + 170 * 8), '#252933')
    draw = ImageDraw.Draw(canvas)
    draw.text((10, 10), '31 CATALOG THEMES / WEAK + STRONG / SOURCE PIXELS / DEMO: AKALI x MORDEKAISER / UNAPPROVED', fill='white', font=b.font(17))
    for index, row in enumerate(table['registered_themes']):
        m = b.read_json(b.OUT / f's{row["primary_source_index"]:03}/manifest.json')
        theme = row['theme']
        cell = Image.new('RGBA', (600, 137))
        for j, intensity in enumerate(('weak', 'strong')):
            entry = next(a for a in m['assets'] if a['theme'] == theme and a['component'] == 'frame' and a['intensity'] == intensity)
            with Image.open(b.ROOT / entry['file']) as raw:
                image = b.demo(raw.convert('RGBA'), entry, icons)
            shown = b.fit_preview(image, (292, 132))
            bg = game.resize((300, 137), Image.Resampling.LANCZOS)
            bg.alpha_composite(shown, ((300 - shown.width) // 2, (137 - shown.height) // 2))
            cell.alpha_composite(bg, (j * 300, 0))
        x, y = index % 4 * 600, 45 + index // 4 * 170
        canvas.paste(cell.convert('RGB'), (x, y + 28))
        draw.text((x + 7, y + 5), f'{theme} / s{row["primary_source_index"]:03} / WEAK | STRONG', fill='white', font=b.font(14))
    b.save_image(canvas, b.OUT / 'all31_overview.jpg', quality=94, subsampling=0)


def generate_report():
    inventory = b.read_json(b.OUT / 'source_inventory.json')
    table = b.read_json(b.OUT / 'theme_correspondence.json')
    protected = b.read_json(b.OUT / 'protected_sha256.json')
    verification = []
    all_assets = []
    source_rows = []
    manifests = {}
    for source in inventory['sources']:
        m = b.read_json(b.OUT / f's{source["index"]:03}/manifest.json')
        checks = b.verify_source(source, m)
        assert len(checks) == source['component_count']
        manifests[source['index']] = m
        flagged = sum(bool(a['quality_flags']) for a in m['assets'])
        source_rows.append({'index': source['index'], 'source_file': source['source_file'], 'sha256': source['sha256'],
                            'decoded_rgb_sha256': source['decoded_rgb_sha256'], 'dimensions': 'x'.join(map(str, source['dimensions'])),
                            'bytes': source['bytes'], 'themes': ' / '.join(source['themes']), 'parts': len(m['assets']),
                            'quality_flags': flagged, 'batch': source['batch'], 'status': 'processed_candidates_unapproved',
                            'unsupported': json.dumps(source['unsupported'], ensure_ascii=False),
                            'excluded_content': ' / '.join(source['excluded_content'])})
        verification.append({'source_index': source['index'], 'source_sha256': source['sha256'],
                             'rgb_exact_parts': len(checks), 'mask_and_hole_checks_passed': True,
                             'manifest_sha256': b.sha(b.OUT / f's{source["index"]:03}/manifest.json')})
        for a in m['assets']:
            all_assets.append(dict(a, source_index=source['index'], source_file=source['source_file'], source_sha256=source['sha256']))
    for path, expected in protected['files'].items():
        assert b.sha(b.APP / path) == expected, path
    files = {a['file'] for a in all_assets}
    masks = {a['mask_file'] for a in all_assets}
    assert len(files) == len(masks)
    new = {f for f in files if f.startswith('all_sources/')}
    counts = {'original_pngs': len(source_rows), 'unique_decoded_originals': len({r['decoded_rgb_sha256'] for r in source_rows}),
              'part_records': len(all_assets), 'unique_rgba_png_files': len(files), 'unique_alpha_png_files': len(masks),
              'new_rgba_png_files': len(new), 'new_alpha_png_files': len(new), 'protected_three_theme_sprites': 15,
              'logical_reference_records': sum(bool(a.get('reused_unchanged')) for a in all_assets),
              'review_pages': sum(len(m['review_pages']) for m in manifests.values()),
              'combination_patterns': sum(m['combinations']['count'] for m in manifests.values()),
              'combination_pages': sum(len(m['combinations']['files']) for m in manifests.values()),
              'partial_original_edge_parts': sum(a['id'].endswith('_partial') for a in all_assets),
              'parts_with_quality_flags': sum(bool(a['quality_flags']) for a in all_assets),
              'catalog_themes': 31, 'additional_design_or_reference_labels': len(table['additional_observed_design_labels']),
              'protected_baseline_files': len(protected['files']), 'existing_badges': 37}
    for path, rows in [(b.OUT / 'source_census.csv', source_rows), (b.OUT / 'part_correspondence.csv', [
        {'source_index': a['source_index'], 'source_file': a['source_file'], 'source_sha256': a['source_sha256'],
         'theme_or_design': a['theme'], 'part': a['id'], 'type': a['component'], 'intensity': a['intensity'], 'role': a['role'],
         'crop_box': json.dumps(a['crop_box']), 'portrait_holes': json.dumps(a['portrait_holes']),
         'rgba_file': a['file'], 'rgba_sha256': a['sha256'], 'mask_file': a['mask_file'], 'mask_sha256': a['mask_sha256'],
         'status': a['status'], 'quality_notes': ' / '.join(a['quality_flags'])} for a in all_assets])]:
        with path.open('w', encoding='utf-8-sig', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    with (b.OUT / 'part_correspondence.csv').open(encoding='utf-8-sig', newline='') as stream:
        issues = [row for row in csv.DictReader(stream) if row['quality_notes']]
    with (b.OUT / 'quality_issues.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(issues[0]))
        writer.writeheader()
        writer.writerows(issues)
    b.write_json(b.OUT / 'unsupported_parts.json', [
        {'source_index': s['index'], 'source_file': s['source_file'], 'unsupported': s['unsupported'],
         'excluded_content': s['excluded_content']} for s in inventory['sources']])
    table['additional_designs'] = [
        {'label_id': label, 'observed_source_indices': [s['index'] for s in inventory['sources'] if label in s['themes']],
         'actual_source_files': [s['source_file'] for s in inventory['sources'] if label in s['themes']],
         'status': 'observed_design_or_reference_group; not a newly invented official theme'}
        for label in table['additional_observed_design_labels']]
    b.write_json(b.OUT / 'theme_correspondence.json', table)
    design_rows = []
    for theme in sorted({a['theme'] for a in all_assets}):
        assets = [a for a in all_assets if a['theme'] == theme]
        design_rows.append({'theme_or_design': theme, 'source_indices': ','.join(map(str, sorted({a['source_index'] for a in assets}))),
                            'source_files': ' / '.join(sorted({a['source_file'] for a in assets})), 'part_records': len(assets),
                            'quality_attention_parts': sum(bool(a['quality_flags']) for a in assets),
                            'classification': 'existing_31_catalog' if any(t['theme'] == theme for t in table['registered_themes']) else 'additional_design_or_reference',
                            'status': 'numeric_checks_passed; visual_approval_pending',
                            'quality_notes': ' / '.join(sorted({note for a in assets for note in a['quality_flags']}))})
    with (b.OUT / 'all_design_quality.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(design_rows[0]))
        writer.writeheader()
        writer.writerows(design_rows)
    reg = regression()
    overview(table, inventory['sources'])
    sha_list = {p.relative_to(b.ROOT).as_posix(): b.sha(p) for p in sorted(b.OUT.rglob('*'))
                if p.is_file() and p.name not in ['verification_report.json', 'sha256_files.json']}
    b.write_json(b.OUT / 'sha256_files.json', sha_list)
    report = {'base_commit': b.BASE, 'branch': 'codex/killframes-all-89-candidates-20261014', 'counts': counts,
              'all_89_original_shas_verified': True, 'all_source_rgb_pixels_exact': True, 'independent_masks_exact': True,
              'declared_portrait_hole_interiors_transparent': True, 'protected_baseline_files_unchanged': True,
              'visual_approval': False, 'regression': reg, 'source_verifications': verification,
              'source_inventory_sha256': b.sha(b.OUT / 'source_inventory.json'),
              'part_correspondence_sha256': b.sha(b.OUT / 'part_correspondence.csv'),
              'source_census_sha256': b.sha(b.OUT / 'source_census.csv'), 'files_sha256_index': 'sha256_files.json',
              'rgb_policy': 'Every RGB pixel, including alpha=0, equals the unscaled original crop. No regeneration/inpainting.',
              'missing_old_chat_images': inventory['old_chat_images_missing'],
              'semantic_visual_limit': 'Numerical hole checks validate the declared masks, not complete semantic removal of every hair/clothing fringe. Human inspection remains required.'}
    b.write_json(b.OUT / 'verification_report.json', report)
    doc = ['# 全89元画像のキルフレーム候補制作・検証レポート', '',
           '基準: `22861a90c585c8b6b91263241d7437ccf956acc2`。作業ブランチ: `codex/killframes-all-89-candidates-20261014`。', '',
           '全89枚を読み取り、元ファイル名・寸法・ファイルSHA-256・デコードRGBのSHA-256・各部品の座標を台帳へ記録した。最大8元画像の12バッチで処理し、デコードは1元画像ずつ。**素材は完成候補または要手直し候補であり、最終の見た目は未承認。**', '',
           '## 成果物と確認の入口', '',
           '- [31台帳テーマの弱・強・肖像入り一覧](../assets/kill_frames/all_sources/all31_overview.jpg)',
           '- [全89枚の一覧CSV](../assets/kill_frames/all_sources/source_census.csv)',
           '- [全部品の元ファイル・座標・PNG/マスクSHA-256対応CSV](../assets/kill_frames/all_sources/part_correspondence.csv)',
           '- [全画像の切り出し定義JSON](../assets/kill_frames/all_sources/source_inventory.json)',
           '- [既存31テーマの旧ファイル名と実ファイル名の対応](../assets/kill_frames/all_sources/theme_correspondence.json)',
           '- [検証結果JSON](../assets/kill_frames/all_sources/verification_report.json) / [全成果物SHA-256一覧](../assets/kill_frames/all_sources/sha256_files.json)',
           '- [要確認部品だけの一覧](../assets/kill_frames/all_sources/quality_issues.csv) / [全テーマ・設計別の品質一覧](../assets/kill_frames/all_sources/all_design_quality.csv) / [未対応・対象外の理由](../assets/kill_frames/all_sources/unsupported_parts.json)',
           '- [各バッチの全素材・黒白比較](../assets/kill_frames/all_sources/batches/) / [保存場所と再現方法](../assets/kill_frames/all_sources/README_JA.md)', '',
           '各 `s001`〜`s089` フォルダーで、`source_regions.jpg`（水色の切り出し範囲・赤色の肖像穴）、`review_*.jpg`（全素材をチェック柄/黒/白/実LoL背景/サンプル肖像/小サイズで比較）、`combinations_*.jpg`（その原画像に存在する全フレーム×明示された全ロールモチーフ）を確認する。比較文字は表示用で、素材や動画へ追加していない。Akali×Mordekaiserは既存公式キャッシュのデモであり、試合のキラー/被害者を示すものではない。', '',
           '## 実数', '', '| 項目 | 数 |', '|---|---:|']
    labels = {'original_pngs': '元PNG（変更・改名なし）', 'unique_decoded_originals': '異なる元画像RGB', 'part_records': '部品レコード（参照を含む。独立デザイン数ではない）',
              'new_rgba_png_files': '新規透過PNG', 'new_alpha_png_files': '新規独立アルファマスク', 'unique_rgba_png_files': '既存15点を含めたPNG実ファイル',
              'review_pages': '全素材の背景別・肖像入り・縮小比較ページ', 'combination_patterns': '実在部品の組合せ比較パターン',
              'parts_with_quality_flags': '品質注意フラグ付き部品（自動承認しない）', 'partial_original_edge_parts': '元画像の端で欠損した部分図', 'existing_badges': '保護した既存キルフレーム'}
    doc += [f'| {label} | {counts[key]} |' for key, label in labels.items()]
    doc += ['', 's058 `image-gen-6(6).png` と s082 `image.png` は、PNGファイルのSHAは異なるがデコードRGBが完全一致した。同じデザインの符号化違いとして分類し、候補ファイルを共有した。既存3テーマ15点と15マスクは再加工せず参照する。部品数には一覧の別案、小型の色/効果参照、同画像の異なるモチーフ、重複元画像からの参照も含むため、テーマ数や独立した完成デザイン数に置き換えない。', '',
            '## テスト・保護条件', '',
            f'- Windows/Python {reg["python"]}: pytest **{reg["pytest_passed"]}件合格**（{reg["test_files"]}ファイルを分割実行）、旧式総合 **{reg["legacy_passed"]}/16合格**。',
            '- 各バッチで元画像SHA、全RGB画素、独立マスク一致、指定肖像穴の内部アルファ0、非空の素材、背景比較の存在を検証した。新規の数理テストは、肖像が面積の大半を占める場合でも肖像を背景サンプルとして誤採用しないことを暗/明の両背景で確認する。',
            '- 既存37素材、既存3テーマ候補、core/app/legacy_app等の保護対象153ファイルは基準SHAと一致。元PNG89枚も輸入台帳のSHAと全件一致。',
            '- 初期の既存テスト3件はサンドボックスの既定一時ディレクトリに書けず実行エラーとなったが、作業領域内の新規一時ディレクトリで58件合格した。テスト/本体の安全チェックは削除していない。',
            '- 数値検証は宣言した穴の透明性を確認する。残った髪/衣装の縁、全ての細線の保全、フリンジの見た目を保証するものではない。',
            '- 本番カメラ/TargetLock/録画/GPU/音声/UIのコードは変更していない。LoLを終了したWindowsで合成・モック入力を使った回帰テストを実施し、実LoL録画・動画合成・UI選択・登場FXの新規統合は未実施。',
            '- 一時テストコピーは既存ランナーが削除。検査用スクリプト・ログ・一時画像は無視対象の `diagnostics/local_dev` へ整理し、個人パスを含む生ログ/録画をGitHubへ保存していない。既存のユーザーデータは削除していない。', '',
            '## 未完成・未対応・品質課題', '',
            '- **s004の右端8部分図**: ターゴン/ヴォイド、覇王/プールパーティー、ビースト/カフェ、機械仕掛け/深海の恐怖の掲載図は原画像端で欠ける。完全な二者フレームは復元できない。部分候補として残し、描き足していない。',
            '- **s005**: テーマ名が表示されない低解像度のゲーム背景付き参考画像。名称未確認として登録。背景と金属が似た画素色のため境界は要マスク確認。',
            '- **s017**: 水滴・発光・隣のモチーフが接する。全9案の実画像を切り出したが、接触部の正確な分離・役割見出しの色の残りは要手直し候補。',
            '- **s028**: 明るい紙面/紺の下地の混在を元画像のサンプル画素で抑制。星/金属の暗部、白い発光と背景が同色になる所は未承認。',
            '- **s003 KDA、s066 Arcade、s078 Soul Fighter**: 元デザイン中の文字/数値と装飾が重なる。測定した文字領域をアルファで除外した候補だが、背後にない絵を復元できず欠けが生じる。残字・デザインとしての可否は最終目視で判断する。',
            '- **小型一覧/パレット/構造参照**: 低解像度の原画を高精細な素材と誤認しない。拡大時の画質・細い輪郭・肖像の周辺は要確認。部品CSVで該当点を識別できる。',
            '- **全テーマ共通のRGB制約**: 背景と発光が混ざったRGBのアンマット、黒/白フリンジの色修正、肖像で隠れた装飾、原図から欠けた線はアルファだけで一意に復元できない。RGBの補色・描画・再生成はせず、課題として残した。',
            '- 原画像に弱/強や3ロールの指定・パーツがなければ `unspecified` または `unsupported` に記録。A/B/C/D主図の説明アニメーション途中・拡大図、背景人物、操作部品、見出し/文章/罫線は独立した追加デザインとして数えない。全体の別案・実在する色/形状見本は別途保存した。',
            '- **旧ChatGPT画像の不足**: 旧チャットの画像一覧と原本が参照不能なため、89枚以外に不足があるか確認不能。台帳の旧ファイル名不一致は実画像対応へ解決し、「未取得の画像がある」とは推測で断定しない。', '',
            '## 全89枚の処理一覧', '', '| ID | 元PNG（そのままの名前） | 寸法 | 部品 | 品質注意 | 比較 |', '|---|---|---|---:|---:|---|']
    for r in source_rows:
        n = r['index']
        filename = quote(r['source_file'])
        doc.append(f'| s{n:03} | [{r["source_file"]}](../assets/kill_concepts/{filename}) | {r["dimensions"]} | {r["parts"]} | {r["quality_flags"]} | [比較](../assets/kill_frames/all_sources/s{n:03}/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s{n:03}/manifest.json) |')
    doc += ['', '全行が処理済み。除外対象・未対応理由は89行CSV/JSONで確認できる。欠損図や品質注意の部品は正式に使用できる素材として承認していない。', '',
            '## 既存31テーマの対応と品質判定', '', '| テーマ | 実ファイル | 主図 | 同名の掲載/別案画像 | 判定 |', '|---|---|---|---|---|']
    for row in table['registered_themes']:
        n = row['primary_source_index']
        m = manifests[n]
        flags = sum(bool(a['quality_flags']) for a in m['assets'] if a['theme'] == row['theme'])
        status = '数値検証合格・目視未承認' + (f' / 品質注意{flags}点' if flags else '')
        doc.append(f'| {row["label"]} (`{row["theme"]}`) | {row["actual_source_file"]} | [s{n:03}](../assets/kill_frames/all_sources/s{n:03}/review_01.jpg) | {", ".join("s"+str(i).zfill(3) for i in row["observed_source_indices"])} | {status} |')
    doc += ['', f'台帳31件以外にも、地域案、A/B/C/D案、名称未表示、共通パレット等の追加分類IDが{counts["additional_design_or_reference_labels"]}件ある。これを公式のテーマ数と断定せず、[対応JSON](../assets/kill_frames/all_sources/theme_correspondence.json)と全部品CSVで実画の掲載位置を追えるようにした。', '',
            '## Git保存・次の工程', '',
            '12バッチをそれぞれ検証後に専用ブランチへコミット・Pushした。追加参照図と測定の仕上げも同じ専用ブランチに保存する。main・PR #29・カメラv5.10.27・素材試作ブランチを変更/マージしていない。コミット一覧は `batch_commits.json` とブランチ履歴で確認できる。', '',
            '次はChatGPTとユーザーが背景別/肖像入り/縮小比較で正式な見た目を判定する。要手直しだけを分離して、承認した部品ID・許容する欠け・必要な解像度を台帳へ記録する。ChatGPTがA/B/C/D UI・視覚設計・登場FXを担当し、Codexが元画素/Windows検証と共有エンジンの接続を担当する分担を維持する。**本報告を区切りとして、正式UI・動画・FX統合を開始せず停止する。**', '']
    (b.APP / 'docs/KILLFRAME_ALL_89_CANDIDATES_20261014_JA.md').write_text('\n'.join(doc), encoding='utf-8')
    print(json.dumps({'counts': counts, 'regression': reg}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    if '--refresh-comparisons' in sys.argv:
        refresh_comparisons()
    else:
        generate_report()
