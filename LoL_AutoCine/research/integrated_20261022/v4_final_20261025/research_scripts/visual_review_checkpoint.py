from lab_common import *
from datetime import datetime
static=sorted((O/'fx_composition').glob('*.jpg'))
colors=['桃青ネオン交差','桃金星粒','桃花弁','細い金線','金火花','赤青斬線','金線','多色ピクセル大X','橙赤火花大X','橙紫小交差','赤黒小交差','赤白尖塔X','青金星','紫金渦','紫黒棘','白金羽','橙青龍斬','緑金葉','淡桃蝶花','赤黒多線','橙水平斬','橙炎柱','桃紫星','青橙金属交差','金橙大X','暗赤橙交差','淡青水粒','青水飛沫','青白陶片','青桃ネオン','金雲交差','多色軌道','青シアン線','金赤斬線','淡青氷晶']
save('FX_STATIC_VISUAL_LOG_V4.json',{'reviewed_sheets':35,'scope':'全35比較シートをoriginal detail表示で目視。各タイルは256x144縮小、全解像度動画審査ではない。','items':[{'file':p.relative_to(O).as_posix(),'visual_observation':c,'common_observation':'左右の顔は識別可能。四角/八角/横長は円形fallback配置で穴との不一致あり。3段の発光は縦に重なり得る。人工minimap/HUDとの重なりあり。Flash診断行で白washと彩度低下。','decision':'REVIEW_REQUIRED','actual_LoL_pass':False} for p,c in zip(static,colors)]})
bg=load(O/'FRAME_BACKGROUND_EXECUTION_V4.json')
for a in bg['cases']:
 if int(Path(a['sheet']).stem)<=66:
  a['visual_review']='VIEWED_384PX_THREE_BACKGROUNDS'
  a['note']='killer左Yasuo/victim右Jinxを確認。穴と円形fallbackの一致は保証しない。人工HUD/HP線との重なりを可視化。実LoL配置審査は未実行。'
save('FRAME_BACKGROUND_EXECUTION_V4.json',bg)
pixel=load(O/'NATIVE_PIXEL_LEDGER_V4.json');native=load(O/'NATIVE_VISUAL_LOG_V4.json')['viewed']
for a in pixel['items']:
 a['native_visual_state']='VIEWED_ORIGINAL_DETAIL_FULL_PNG' if a['id'] in native else 'NOT_RUN'
 a['visual_note']=native.get(a['id'],{}).get('note','')
save('NATIVE_PIXEL_LEDGER_V4.json',pixel)
