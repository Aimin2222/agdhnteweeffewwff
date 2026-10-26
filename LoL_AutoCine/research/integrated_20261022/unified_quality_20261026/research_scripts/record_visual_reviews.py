from common import *
pair_notes=[
(3,'金の太陽・四角枠は共通。接続部と角装飾の差は小さく、同族グループ表示が適切。'),
(2,'同じ赤黒テーマだが中央紋章と枠突起が明確に異なる。意味のある形状差。'),
(3,'太陽・四角枠は共通、発光と青い接続線の追加。グループ内差として表示。'),
(3,'青銀の枠構成はほぼ共通。中央のV形・X/発光位置差をグループ内に整理。'),
(2,'同じ枠でも中央の環と縦長機械紋章が異なる。色だけの差ではない。'),
(3,'青銀枠は共通。中央形状の小差をグループ内比較で見せる。'),
(3,'金の四角枠と橙色中央紋章。中央の十字・弓の細部差は同族でまとめる候補。'),
(2,'海賊の交差刀と錨・水しぶき。地域記号が異なり意味のある差。'),
(2,'金の太陽/四角枠と氷/円枠。輪郭hash同点でも同一デザインではない。No004原本制約は別保留。'),
(2,'金の太陽と紫の三角ネオンで色・形・構成が異なる。No004原本制約は別保留。'),
(2,'赤黒の刃と氷青の角形枠は明確に異なる。原本が違うため同一視しない。'),
(2,'炎と星の翼は色/中央記号/装飾が異なる。同じ円枠構造だけでは重複にしない。'),
(2,'緑葉と白青の刃/翼が異なる。輪郭のみの誤検出例。'),
(2,'紫の三角と金青の翼/Xは異なる。No004の形状忠実性は未確定。'),
(2,'weak/strongは色だけでなく枝と枠突起に差。strongが単に高輝度とは限らない。'),
(2,'星形・軌道の形と青/金の比率が異なる。強度ラベルだけで統合しない。'),
(2,'渦と尖った星・暗粒子に差。中央形状の異なる選択肢。'),
(2,'羽と外周軌道の差が見える。白金は明背景で細部が弱い。'),
(2,'中央の赤黒紋章と火花が異なる。意味のある差だが同族表示も併用可能。'),
(2,'炎の中央紋章と外周張り出しが異なる。名前だけで同一視しない。'),
(2,'pixel Xと大きい星/外周星に明確な差。過剰演出は別品質審査。'),
(2,'蝙蝠状の中央と月/煙の中央。形状として意味のある差。'),
(2,'氷のXと円形の陶器紋章・粒子。中央構成が異なる。'),
(2,'紫青テーマは共通だが中央菱形と三角/目状形状が異なる。スキン忠実性までは未判定。')]
queue=load(O/'A1_similarity/SELECTED_PAIR_REVIEW_QUEUE.json');out=[]
for i,(x,(cat,note)) in enumerate(zip(queue,pair_notes),1):out.append({'pair_number':i,'a':x['a'],'b':x['b'],'classification':cat,'observation':note,'image':x['comparison'],'AI_visual_status':'REVIEW','human_approval':False})
save('A1_similarity/AI_PAIR_REVIEWS.json',{'count':24,'scope':'AI review of full ornaments scaled over two backgrounds; not full native pixels, filled portraits or temporal compatibility','items':out,'remaining_prior_pair_visual_NOT_RUN':1464-sum(any(y['a']==x['a'] and y['b']==x['b'] for x in load(O/'A1_similarity/PAIR_METRICS_1464.json')['pairs']) for y in out)})
p2texts=['緑枝と金枠は両背景で識別。候補穴マスクは顔中心を大きく隠さない。','青ネオンは両背景で見える。穴マスクの丸い境界は低解像度抽出のため原寸確認が必要。','角切り四角穴に収まり、顔が外側へ飛び出さない。細い金は明背景で弱め。','中央の発光が強い。左右の穴は顔を覆わず、主に外周が発光する。','四角枠と顔の位置は改善候補として自然。中央ネオンが高密度。','青紫のXが非常に明るい。顔は識別可能。暗粒子は暗背景で弱い。','中央の惑星・軌道が高密度。金の細線は明背景で弱め。顔穴は収まる。','中央赤黒刃と鎖が密集。黒い線は暗背景で弱い。四角穴の候補は顔を隠さない。','羽と冠が大きく、明背景で淡い羽が弱い。顔は左右の穴に収まる。','淡い水色/ピンクは明背景で弱い。四角穴に顔が収まる。','金の細線は明背景で弱め。四角マスクは顔の横ずれを抑える。','白い中央Xが大きく高輝度。顔の識別は保たれる。','扇と色つきの装飾が左右アイコンへ近接。顔の中心は隠れていない。','青赤破片は左右へ広い。顔穴は収まるが3段/実HUDの確認が必要。','キャンディと葉の差は明暗で識別。顔は円穴に収まる。','暗赤のしぶきは暗背景で弱い。四角穴に顔が収まる。','クリームの雲と金の細部が明背景で弱い。顔は識別可能。','中央のカボチャ・王冠・翼が高密度。穴の顔は識別可能。','赤黒の布は暗背景で弱い。装飾が下へ大きく張り出し、stack確認が必要。','白い雪は明背景で弱め。中央のベルと顔は識別可能。','角枠に円弧の切欠きがあり、円アイコン固定ではなく穴マスクが必要。候補は顔を収める。','角切り四角穴を埋める候補。氷の細部は明背景で弱め。','青い泡は明背景で弱い。顔穴と中心は自然だが境界は原寸確認待ち。','淡い青紫の花は明背景で弱め。円穴に顔が収まる。']
q=load(O/'A2_quality/P2_VISUAL_QUEUE.json');r=[]
for i,(x,note) in enumerate(zip(q,p2texts),1):r.append(dict(x,AI_new_visual_review='REVIEW',observation=note,scope='new P2 static AI review; source and mask-based research fill, no author verification or all-time test'))
save('A2_quality/P2_AI_IMAGE_REVIEWS.json',{'items':r,'new_count':24,'inherited_P0_P1_review_count':140,'cumulative_distinct_asset_AI_review_count':164,'remaining_P2_new_visual_count':523,'formal_changes':0})
# Classifications are suggestions; user-rejected items are never reopened as recommendations.
draft=load(O/'A1_similarity/ASSET_CLASSIFICATION_DRAFT.json');mapping={}
for x in out:
 for key in [x['a'],x['b']]:mapping.setdefault(key,[]).append(x)
labels={1:'優先的に残したい',2:'意味のあるバリエーションとして残したい',3:'似ているためグループ表示が適切',4:'デザインの作り直しを検討',5:'ユーザーに採否確認が必要'}
for x in draft:
 if x['user_rejected']:x.update(classification_label='ユーザー不採用・再推奨禁止',decision_pending=False);continue
 if x['kind']=='frame' and x['id'] in mapping:
  cats=[y['classification'] for y in mapping[x['id']]];cat=3 if all(c==3 for c in cats) else 2
  if x['id'].startswith('004/'):cat=5
  x.update(classification=cat,classification_label=labels[cat],AI_new_visual_review='REVIEW',evidence=[y['image'] for y in mapping[x['id']]])
save('A1_similarity/ASSET_CLASSIFICATION_RESEARCH.json',{'items':draft,'complete_human_selection':False,'not_inspected_remain_category5':True,'category4_not_forced_without_evidence':True,'delete_merge_approval_changes':0})
