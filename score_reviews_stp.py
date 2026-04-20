"""
Review Scoring Script for B001K85BN2, B001K85BNC, B008KEJ1LM
Uses keyword-based salience detection + star-rating quality proxy.
Outputs: review_scoring_table.csv, product_quality_scorecard.csv
"""
import re
import json
import pandas as pd
from pathlib import Path

# ── Output directory ──────────────────────────────────────────────────────────
OUT_DIR = Path("output/stp_B001K85BN2_B001K85BNC_B008KEJ1LM")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Attribute catalog ─────────────────────────────────────────────────────────
catalog = pd.read_csv("attribute_catalog.csv")
ATTR_KEYS = catalog["attribute_key"].tolist()

# ── Keyword map: attribute_key → {en: [...], ja: [...], neg_en: [...], neg_ja: [...]} ──
# neg_* keywords suggest the attribute is being mentioned negatively (lowers quality)
KEYWORDS = {
    # ── Power Source ──────────────────────────────────────────────────────────
    "power_source_type": {
        "en": ["rechargeable","usb","battery","aa battery","aaa battery","cordless","batteries"],
        "ja": ["充電","電池","usb","単三","単四","コードレス","バッテリー"],
    },
    "rechargeable_design": {
        "en": ["rechargeable","recharge","usb charge","charging","charge"],
        "ja": ["充電式","充電できる","usb充電","充電","リチャージ"],
        "neg_en": ["not rechargeable","no usb","battery only","requires batteries"],
        "neg_ja": ["充電できない","電池のみ","充電不可"],
    },
    "usb_c_charging": {
        "en": ["usb-c","usb c","type-c","type c","usb type c"],
        "ja": ["usb-c","usbc","タイプc","type-c"],
    },
    "charging_dock_base": {
        "en": ["charging dock","charging base","dock","charging stand"],
        "ja": ["充電台","充電スタンド","ドック","充電クレードル"],
        "neg_en": ["no charging dock","no base","doesn't have a dock"],
        "neg_ja": ["充電台なし"],
    },
    "battery_type_aa": {
        "en": ["aa battery","aa batteries","double a","single a","2aa","uses aa"],
        "ja": ["単三","aa電池","単三電池","単三形"],
    },
    "battery_type_aaa": {
        "en": ["aaa battery","aaa batteries","triple a","uses aaa"],
        "ja": ["単四","aaa電池","単四電池","単四形"],
    },
    "battery_included": {
        "en": ["battery included","batteries included","comes with battery","includes battery","battery is included"],
        "ja": ["電池付属","電池同梱","電池が付いて","電池が含まれ","電池入り"],
        "neg_en": ["no battery","battery not included","batteries not included"],
        "neg_ja": ["電池なし","電池は別","電池が付いていない"],
    },
    "battery_life_duration": {
        "en": ["battery life","charge life","runtime","lasts","last long","holds charge","hours of","run time"],
        "ja": ["電池持ち","充電持ち","長持ち","使用時間","連続使用","持続時間","持ち時間"],
        "neg_en": ["short battery","dies quickly","doesn't last","poor battery life"],
        "neg_ja": ["電池がすぐ","持ちが悪い","すぐ切れ","短い"],
    },
    "wall_plug_included": {
        "en": ["wall plug","adapter","charger included","power adapter","ac adapter"],
        "ja": ["アダプター","充電器","コンセント","電源アダプタ"],
        "neg_en": ["no wall plug","no adapter","plug not included"],
        "neg_ja": ["アダプターなし"],
    },
    # ── Motor & Blade ─────────────────────────────────────────────────────────
    "motor_origin": {
        "en": ["japanese motor","japan motor","motor origin","made in japan"],
        "ja": ["日本製モーター","日本のモーター","国産モーター"],
    },
    "blade_material_japanese_steel": {
        "en": ["japanese steel","high-carbon","carbon steel","japanese blade","japan blade","stainless steel blade"],
        "ja": ["日本製刃","高炭素鋼","ステンレス刃","日本製の刃","鋼鉄刃"],
    },
    "blade_sharpness": {
        "en": ["sharp","dull","cutting","sharpness","blade","razor sharp","cuts well","well-sharpened"],
        "ja": ["切れ味","鋭い","鈍い","よく切れ","切れない","切れ味良","切れ味悪"],
        "neg_en": ["dull","not sharp","doesn't cut","poor cutting","won't cut"],
        "neg_ja": ["切れない","鈍い","切れ味が悪","うまく切れない"],
    },
    "blade_hair_pulling": {
        "en": ["pull","snag","tug","pulling","snagging","yanking","catch","catches hair"],
        "ja": ["引っ張る","挟む","痛い","毛を引く","引っかかる","痛み","不快"],
        "neg_en": ["pull","snag","painful","yanking"],
        "neg_ja": ["引っ張る","痛い","挟む","引っかかる"],
    },
    "motor_power_rpm": {
        "en": ["motor","power","speed","strong","weak","rpm","torque","powerful","motor speed"],
        "ja": ["モーター","パワー","力","速度","強い","弱い","スピード","馬力"],
        "neg_en": ["weak motor","slow","lacks power","underpowered"],
        "neg_ja": ["モーターが弱い","パワー不足","遅い"],
    },
    "blade_width": {
        "en": ["blade width","wide blade","narrow blade","blade size","0.8 inch","inch blade"],
        "ja": ["刃幅","刃の幅","ワイド","ナロー"],
    },
    "blade_replaceable": {
        "en": ["replaceable blade","replace blade","replacement blade","new blade","extra blade"],
        "ja": ["替え刃","刃の交換","交換刃","替え刃付"],
    },
    "ceramic_blade": {
        "en": ["ceramic blade","ceramic","heat reduction"],
        "ja": ["セラミック刃","セラミック","熱を軽減"],
    },
    "cutting_precision": {
        "en": ["precision","precise","accurate","detail","clean line","clean cut","exact","accurate cut"],
        "ja": ["精度","正確","精密","ライン","きれいに切れ","精確"],
        "neg_en": ["imprecise","not precise","uneven","messy"],
        "neg_ja": ["精度が低い","ばらつき","不均一"],
    },
    "foil_shaver_head": {
        "en": ["foil shaver","foil head","foil attachment","shaver head"],
        "ja": ["網刃","フォイル","フォイルシェーバー","シェーバーヘッド"],
    },
    # ── Waterproof ────────────────────────────────────────────────────────────
    "waterproof_rating_ipx8": {
        "en": ["ipx8","waterproof","water resistant","ip rating","ipx"],
        "ja": ["ipx8","防水","防水等級","防滴","ipx"],
        "neg_en": ["not waterproof","water damage","broke after water"],
        "neg_ja": ["防水ではない","水で壊れ"],
    },
    "shower_use_safe": {
        "en": ["shower","wet use","use in shower","shower safe","bath"],
        "ja": ["シャワー","お風呂","濡れた","シャワー中","入浴"],
        "neg_en": ["can't use in shower","not shower safe"],
        "neg_ja": ["シャワーで使えない"],
    },
    "rinse_under_tap": {
        "en": ["rinse","wash","tap water","running water","clean under water","washable"],
        "ja": ["水洗い","洗える","流せる","水で洗","すすぎ","洗浄"],
    },
    "wet_dry_dual_use": {
        "en": ["wet and dry","wet/dry","dry and wet","dual use","wet or dry"],
        "ja": ["乾湿両用","水でも","濡れた状態","乾いた状態でも"],
    },
    # ── Functions ─────────────────────────────────────────────────────────────
    "num_grooming_functions": {
        "en": ["in-1","functions","grooming","multi","versatile","all-in-one","multiple functions"],
        "ja": ["機能","多機能","オールインワン","一台で","複数の用途"],
    },
    "beard_trimming_function": {
        "en": ["beard","beard trimmer","beard trimming","facial hair","beard trim"],
        "ja": ["ひげ","髭","ヒゲ","あごひげ","口ひげ","ひげ剃り","ひげ整え"],
        "neg_en": ["doesn't trim beard","bad for beard","poor beard"],
        "neg_ja": ["髭が切れない","ひげに向かない"],
    },
    "nose_hair_trimming_function": {
        "en": ["nose hair","nostril","nasal","nose trimmer"],
        "ja": ["鼻毛","鼻","鼻のムダ毛"],
        "neg_en": ["too large for nose","doesn't fit nose","bad nose trimmer"],
        "neg_ja": ["鼻毛に向かない","鼻毛が切れない"],
    },
    "ear_hair_trimming_function": {
        "en": ["ear hair","ear trimmer","ear"],
        "ja": ["耳毛","耳","耳のムダ毛"],
    },
    "eyebrow_trimming_function": {
        "en": ["eyebrow","brow","eyebrow trimmer","eyebrow shaping"],
        "ja": ["眉毛","まゆ毛","まゆ","眉"],
    },
    "mustache_trimming_function": {
        "en": ["mustache","mustache trimmer","lip hair","upper lip"],
        "ja": ["口髭","口ひげ","マスタッシュ","上唇"],
    },
    "sideburn_trimming_function": {
        "en": ["sideburn","sideburns","side","temple"],
        "ja": ["もみあげ","サイドバーン"],
    },
    "chest_body_hair_function": {
        "en": ["body hair","chest hair","body groomer","body trimmer"],
        "ja": ["体毛","胸毛","体のムダ毛","ボディトリマー"],
    },
    "peach_fuzz_removal": {
        "en": ["peach fuzz","fine hair","facial fuzz","soft hair","light hair"],
        "ja": ["産毛","うぶ毛","細い毛","柔らかい毛"],
    },
    "pet_grooming_function": {
        "en": ["pet","cat","dog","animal","puppy","kitten"],
        "ja": ["ペット","猫","犬","動物","ペット用"],
    },
    "haircutting_head_function": {
        "en": ["head hair","scalp","hair cutting","haircut"],
        "ja": ["頭髪","頭","頭の毛","散髪","理髪"],
    },
    # ── Adjustability ─────────────────────────────────────────────────────────
    "adjustable_comb_settings": {
        "en": ["adjustable","comb","length settings","guide comb","adjustment","length adjustment","settings"],
        "ja": ["調節","長さ調節","アタッチメント","コーム","ガイド","調整","長さ"],
        "neg_en": ["not adjustable","no adjustment","fixed length"],
        "neg_ja": ["調節できない","固定","長さが変えられない"],
    },
    "min_cut_length_mm": {
        "en": ["minimum length","0.5mm","1mm","2mm","shortest","minimum cut","3mm minimum"],
        "ja": ["最短","最小","3ミリ","最短3","最短長さ"],
        "neg_en": ["minimum too long","can't cut short enough"],
        "neg_ja": ["最短が長い","3ミリでは長い","短くならない"],
    },
    "max_cut_length_mm": {
        "en": ["maximum length","14mm","longest","6mm","maximum cut"],
        "ja": ["最長","最大","最大長さ"],
    },
    "guide_comb_variety": {
        "en": ["combs","attachments","guide comb","4 combs","3 combs","multiple combs","comb attachments"],
        "ja": ["ガイドコーム","アタッチメント","コームの種類","複数のコーム"],
    },
    "stepless_adjustment": {
        "en": ["stepless","continuous adjustment","dial","infinite adjustment","smooth adjustment"],
        "ja": ["無段階","ダイヤル式","連続調整","なめらかな調整"],
    },
    "speed_settings": {
        "en": ["speed","high speed","low speed","speed setting","2 speeds","multiple speeds"],
        "ja": ["速度","スピード","高速","低速","2段階","速度切替"],
        "neg_en": ["one speed","single speed","no speed control"],
        "neg_ja": ["1段階のみ","速度調節なし"],
    },
    # ── Design ────────────────────────────────────────────────────────────────
    "pen_shaped_design": {
        "en": ["pen-shaped","pen shape","slim","pen-like","pen type"],
        "ja": ["ペン型","ペン形","スリム","ペン状"],
    },
    "product_weight_g": {
        "en": ["weight","grams","lightweight","light weight","heavy","13 grams","50 grams"],
        "ja": ["重さ","重量","軽い","重い","グラム","軽量"],
    },
    "grip_ergonomics": {
        "en": ["grip","ergonomic","comfortable","hold","handle","easy to hold","comfortable grip"],
        "ja": ["グリップ","握り","持ちやすい","エルゴノミック","手にフィット","握りやすい"],
        "neg_en": ["hard to hold","uncomfortable","bad grip","slippery grip"],
        "neg_ja": ["握りにくい","不快","滑りやすい","持ちにくい"],
    },
    "handle_slipperiness": {
        "en": ["slippery","slip","non-slip","grippy","wet hands","slips"],
        "ja": ["滑り","滑りにくい","滑る","ノンスリップ","ズレ"],
        "neg_en": ["slippery","slips","hard to hold when wet"],
        "neg_ja": ["滑る","ズレる"],
    },
    "compact_size": {
        "en": ["compact","small","portable","pocket","tiny","miniature","palm-sized"],
        "ja": ["コンパクト","小さい","小型","ポケット","携帯","ミニ"],
    },
    "color_style_aesthetics": {
        "en": ["color","style","look","aesthetic","design","appearance","stylish","beautiful","looks great"],
        "ja": ["デザイン","カラー","見た目","おしゃれ","外観","カッコいい","かっこいい"],
        "neg_en": ["ugly","boring design","plain","bad looking"],
        "neg_ja": ["デザインが悪い","地味","ダサい"],
    },
    "protective_cap_cover": {
        "en": ["cap","cover","protective cap","blade cover","protective cover","lid"],
        "ja": ["キャップ","カバー","保護キャップ","刃カバー","保護カバー"],
        "neg_en": ["no cap","no cover","missing cap"],
        "neg_ja": ["キャップなし","カバーなし"],
    },
    "dust_proof_cover": {
        "en": ["dust-proof","dust cover","dust protection"],
        "ja": ["防塵カバー","防塵","ほこり防止"],
    },
    "blade_head_storage_base": {
        "en": ["storage base","base","organize","head storage","storing blades"],
        "ja": ["収納","ベース","収納台","刃の収納"],
    },
    "lightweight_design": {
        "en": ["lightweight","light","featherlight","not heavy","very light"],
        "ja": ["軽い","軽量","軽さ","重くない"],
        "neg_en": ["heavy","too heavy","weighs a lot"],
        "neg_ja": ["重い","重たい"],
    },
    "product_dimensions_size": {
        "en": ["dimensions","size","length","width","cm","inches","14 x","mm size"],
        "ja": ["サイズ","寸法","大きさ","cm","センチ","mm","長さ","幅"],
    },
    "battery_cover_ease": {
        "en": ["battery cover","battery compartment","battery door","open battery"],
        "ja": ["電池カバー","電池蓋","電池ケース","電池の入れ方"],
    },
    # ── Portability ───────────────────────────────────────────────────────────
    "travel_suitability": {
        "en": ["travel","portable","trip","journey","on the go","carry-on","business trip","luggage"],
        "ja": ["旅行","持ち運び","携帯","トラベル","出張","旅"],
    },
    "carrying_case_pouch": {
        "en": ["case","pouch","bag","carrying case","travel bag","storage bag","zipper pouch"],
        "ja": ["ケース","ポーチ","バッグ","収納袋","携帯ケース"],
        "neg_en": ["no case","no pouch","missing case","wish it had a case"],
        "neg_ja": ["ケースなし","ポーチなし","袋がない"],
    },
    "storage_box_tray": {
        "en": ["storage box","tray","organize","box","case","compartment"],
        "ja": ["収納ケース","ボックス","トレー","収納ボックス","整理"],
    },
    "cordless_during_use": {
        "en": ["cordless","wireless","no cord","cord-free","without cord","no cable"],
        "ja": ["コードレス","コードなし","無線","ワイヤレス","コードが邪魔","充電式"],
    },
    # ── Accessories ───────────────────────────────────────────────────────────
    "total_attachments_count": {
        "en": ["attachments","pieces","set","accessories","6 piece","4 piece","heads","heads included"],
        "ja": ["アタッチメント","付属品","セット","アクセサリー","刃の種類","頭数"],
    },
    "cleaning_brush_included": {
        "en": ["cleaning brush","brush included","cleaning tool","brush"],
        "ja": ["クリーニングブラシ","お掃除ブラシ","掃除ブラシ","ブラシ付属","ブラシ"],
    },
    "maintenance_oil_included": {
        "en": ["oil","maintenance oil","lubricant","oiling","oil included"],
        "ja": ["オイル","潤滑油","メンテナンスオイル","油"],
        "neg_en": ["needs oil","must oil","oiling required"],
        "neg_ja": ["油が必要","面倒なオイル"],
    },
    "spare_blade_included": {
        "en": ["spare blade","extra blade","replacement blade","2 blades","blades included"],
        "ja": ["替え刃","予備刃","替刃","刃が付属"],
    },
    "instruction_manual_quality": {
        "en": ["instructions","manual","directions","user guide","easy to understand","clear instructions"],
        "ja": ["説明書","マニュアル","取扱説明書","説明が","わかりやすい","使い方"],
        "neg_en": ["confusing instructions","bad manual","unclear","no instructions"],
        "neg_ja": ["説明書がわかりにくい","マニュアルが不親切","説明が不足"],
    },
    "eyebrow_comb_attachment": {
        "en": ["eyebrow comb","eyebrow attachment","eyebrow guide","brow comb"],
        "ja": ["眉毛用コーム","眉コーム","眉毛アタッチメント"],
    },
    "grooming_kit_completeness": {
        "en": ["complete","kit","all-in-one","everything included","full kit","comprehensive","complete set"],
        "ja": ["揃っている","キット","完備","全部","一式","すべて揃"],
        "neg_en": ["incomplete","missing","lacks","not complete"],
        "neg_ja": ["物足りない","不完全","足りない"],
    },
    # ── Safety ────────────────────────────────────────────────────────────────
    "rounded_blade_tip": {
        "en": ["rounded tip","safety tip","round tip","safety blade","rounded blade"],
        "ja": ["丸い先端","安全","丸い刃","安全刃"],
    },
    "painless_operation": {
        "en": ["painless","no pain","comfortable","doesn't hurt","pain-free","gentle"],
        "ja": ["痛くない","無痛","快適","痛みなし","優しい","刺激なし"],
        "neg_en": ["painful","hurts","irritating","pain","scratches"],
        "neg_ja": ["痛い","不快","肌荒れ","かゆい"],
    },
    "skin_friendly_blade": {
        "en": ["skin-friendly","no irritation","gentle on skin","skin safe","doesn't scratch","sensitive skin"],
        "ja": ["肌に優しい","肌荒れしない","低刺激","敏感肌","肌に優しく"],
        "neg_en": ["irritates skin","scratches","skin irritation","redness","rash"],
        "neg_ja": ["肌荒れ","赤くなる","刺激","かゆみ","ヒリヒリ"],
    },
    "low_noise_operation": {
        "en": ["quiet","noise","silent","low noise","noise level","whisper","not noisy","doesn't make noise"],
        "ja": ["静か","音","騒音","静音","うるさくない","静かに","音が小さい"],
        "neg_en": ["noisy","loud","too loud","makes noise","disturbing"],
        "neg_ja": ["うるさい","音が大きい","騒音","音がする"],
    },
    "low_vibration_design": {
        "en": ["vibration","vibrate","no vibration","low vibration","barely vibrates"],
        "ja": ["振動","バイブレーション","振動が少ない","振動なし"],
        "neg_en": ["vibrates a lot","strong vibration","shaking"],
        "neg_ja": ["振動が強い","ブルブル","揺れる"],
    },
    # ── Build Quality ─────────────────────────────────────────────────────────
    "build_quality_perception": {
        "en": ["quality","build quality","sturdy","solid","well built","feels premium","durable","cheap","flimsy","feels cheap"],
        "ja": ["品質","作り","頑丈","しっかり","安っぽい","丈夫","チープ","質感"],
        "neg_en": ["cheap","flimsy","feels cheap","poor quality","low quality","fragile"],
        "neg_ja": ["安っぽい","チープ","品質が悪い","脆い","壊れやすい"],
    },
    "product_longevity": {
        "en": ["last","durability","broke","stopped working","weeks","months","years","long-lasting","lifespan"],
        "ja": ["耐久性","長持ち","壊れ","寿命","持つ","長年","何年も","すぐ壊れ"],
        "neg_en": ["broke","stopped working","failed","broken","short lifespan","died","only lasted"],
        "neg_ja": ["すぐ壊れた","壊れた","故障","短命","すぐ使えなくなった"],
    },
    "plastic_material_quality": {
        "en": ["plastic","material","feel","body material","plastic quality","feels plastic"],
        "ja": ["プラスチック","素材","材質","質感","プラスチック感"],
        "neg_en": ["cheap plastic","bad plastic","feels plastic-y","hollow"],
        "neg_ja": ["安いプラスチック","プラスチック感が強い","チープな素材"],
    },
    "motor_durability": {
        "en": ["motor","broke","failed","stopped working","motor failure","motor died"],
        "ja": ["モーター","故障","壊れ","モーターが","止まった"],
        "neg_en": ["motor broke","motor failed","motor stopped","motor died"],
        "neg_ja": ["モーターが壊れ","モーターが故障","モーターが止まった"],
    },
    "attachment_fitment": {
        "en": ["attachment","fit","attach","click","snap","fits","loose","hard to attach"],
        "ja": ["アタッチメント","取り付け","外れる","はまり","はずれ","取れ"],
        "neg_en": ["loose","hard to attach","doesn't click","falls off","loose fit"],
        "neg_ja": ["外れやすい","取り付けが難しい","ゆるい","はずれ","ガタ"],
    },
    # ── Ease of Use ───────────────────────────────────────────────────────────
    "ease_of_use_overall": {
        "en": ["easy","simple","intuitive","user-friendly","easy to use","straightforward","no learning curve"],
        "ja": ["使いやすい","簡単","直感的","操作性","使い勝手","わかりやすい"],
        "neg_en": ["hard to use","complicated","confusing","difficult","learning curve"],
        "neg_ja": ["使いにくい","複雑","難しい","操作が難しい"],
    },
    "ease_of_cleaning": {
        "en": ["easy to clean","clean","easy cleaning","maintenance","wash","rinse","hygienic"],
        "ja": ["掃除しやすい","手入れが簡単","洗浄","清潔","メンテナンスが簡単"],
        "neg_en": ["hard to clean","difficult to clean","hard to maintain"],
        "neg_ja": ["掃除しにくい","手入れが大変","洗いにくい"],
    },
    "head_change_ease": {
        "en": ["change head","swap head","switch head","change attachment","easy to swap","head change"],
        "ja": ["刃の交換","ヘッド交換","付け替え","アタッチメント交換","着脱"],
        "neg_en": ["hard to change","difficult to swap","head won't come off","stuck"],
        "neg_ja": ["交換しにくい","外れない","付け替えが大変"],
    },
    "on_off_switch_design": {
        "en": ["switch","on/off","power button","on off","power switch","toggle","turn on","turn off"],
        "ja": ["スイッチ","電源ボタン","オンオフ","電源スイッチ","切り替え"],
        "neg_en": ["confusing switch","hard to turn on","switch doesn't work"],
        "neg_ja": ["スイッチが使いにくい","電源ボタンが","操作しにくい"],
    },
    "initial_setup_ease": {
        "en": ["out of box","ready to use","setup","first use","unbox","works right away","immediately"],
        "ja": ["開封","すぐ使える","初期設定","すぐに使える","到着してすぐ"],
    },
    "maintenance_requirement": {
        "en": ["maintenance","oiling","oil","care","need to oil","maintain"],
        "ja": ["メンテナンス","お手入れ","オイルが必要","手入れ","油を差す"],
        "neg_en": ["requires maintenance","need to oil frequently","high maintenance"],
        "neg_ja": ["メンテナンスが面倒","油が必要","手入れが面倒"],
    },
    "quick_touch_up_design": {
        "en": ["quick","touch-up","daily","fast","quick trim","daily use","convenient"],
        "ja": ["手軽","素早い","毎日","日常","サッと","手軽に","毎日使える"],
    },
    "grooming_angle_control": {
        "en": ["angle","control","attack angle","precision","maneuver","easy to angle"],
        "ja": ["角度","コントロール","操作性","当て方","使い角度"],
    },
    # ── Gifting ───────────────────────────────────────────────────────────────
    "gift_packaging_quality": {
        "en": ["gift","packaging","box","present","wrap","giftable","gift box","holiday","birthday"],
        "ja": ["ギフト","プレゼント","包装","贈り物","箱","ラッピング","贈答"],
        "neg_en": ["bad packaging","damaged box","poor packaging"],
        "neg_ja": ["包装が悪い","箱が傷んだ","プレゼントに向かない"],
    },
    "gift_suitability_men": {
        "en": ["gift for","husband","boyfriend","father","dad","men","man","male","father's day","christmas gift"],
        "ja": ["男性へのプレゼント","旦那","彼氏","父","お父さん","男性","男"],
    },
    "gift_suitability_women": {
        "en": ["gift for women","wife","girlfriend","mother","mom","female","woman"],
        "ja": ["女性へのプレゼント","奥さん","彼女","母","女性","女"],
    },
    "box_presentation": {
        "en": ["box","packaging","presentation","well packaged","nicely packaged","looks professional"],
        "ja": ["パッケージ","箱","見栄え","きれいな箱","しっかりした箱"],
        "neg_en": ["bad box","plain packaging","poor presentation"],
        "neg_ja": ["箱が悪い","パッケージが地味"],
    },
    # ── Price & Value ─────────────────────────────────────────────────────────
    "price_value_ratio": {
        "en": ["price","value","worth","money","budget","cost","affordable","cheap","expensive","price point","great value"],
        "ja": ["コスパ","価格","値段","お得","割安","安い","高い","コストパフォーマンス","値段の割に"],
        "neg_en": ["overpriced","not worth","expensive","waste of money","poor value"],
        "neg_ja": ["高すぎる","コスパが悪い","お得じゃない","値段が高い"],
    },
    "budget_tier_positioning": {
        "en": ["budget","premium","mid-range","cheap","affordable","price tier","entry level"],
        "ja": ["価格帯","安価","プレミアム","エントリー","ミドル"],
    },
    "competitor_brand_comparison": {
        "en": ["philips","panasonic","norelco","braun","wahl","compared to","better than","vs","versus"],
        "ja": ["フィリップス","パナソニック","ブラウン","他社","比べ","他のメーカー","比較"],
    },
    # ── Target User ───────────────────────────────────────────────────────────
    "primary_user_gender": {
        "en": ["men","women","male","female","for men","for women","designed for","gender"],
        "ja": ["男性","女性","男性向け","女性向け","男女"],
    },
    "unisex_suitability": {
        "en": ["unisex","both men and women","men and women","gender neutral","for everyone"],
        "ja": ["男女兼用","両用","誰でも","男女問わず"],
    },
    "beginner_friendliness": {
        "en": ["beginner","first time","first trimmer","never used","new to","easy for beginners"],
        "ja": ["初心者","初めて","初めて使う","初めてのトリマー","入門"],
    },
    "couple_shared_use": {
        "en": ["partner","couple","share","wife","husband","together","both use","sharing"],
        "ja": ["パートナー","夫婦","カップル","共用","二人で使う","シェア"],
    },
    "professional_home_positioning": {
        "en": ["professional","barber","salon","home use","professional grade","like a pro"],
        "ja": ["プロ","家庭用","業務用","サロン","プロ仕様"],
    },
    # ── Blade Specs ───────────────────────────────────────────────────────────
    "blade_small_head_size": {
        "en": ["small head","precision head","small blade","tiny blade","narrow head","1cm blade"],
        "ja": ["小さい刃","精密","小さな刃先","ヘッドが小さい"],
    },
    "rotary_blade_type": {
        "en": ["rotary","360","rotating blade","spinning","rotary head"],
        "ja": ["ロータリー","回転式","360度","回転"],
    },
    "integrated_length_dial": {
        "en": ["dial","integrated adjustment","without comb","built-in adjustment","adjustable without"],
        "ja": ["ダイヤル","内蔵","コームなし","ダイヤル調節"],
    },
    "narrow_cutter_head": {
        "en": ["narrow head","thin head","narrow cutter","precision cutter","fine cutter"],
        "ja": ["細い","ナロー","細い刃","精密カッター"],
    },
    "attachment_nose_head_size_fit": {
        "en": ["nose trimmer","nostril","too large","fits in nose","nose head size"],
        "ja": ["鼻毛刃","鼻の穴","大きすぎ","鼻に入る","鼻のサイズ"],
        "neg_en": ["too large for nose","doesn't fit","too big for nostril"],
        "neg_ja": ["鼻に入らない","大きすぎる","鼻の穴に入らない"],
    },
    # ── Brand & Trust ─────────────────────────────────────────────────────────
    "product_listing_accuracy": {
        "en": ["as advertised","accurate","description","as expected","what i expected","matches description"],
        "ja": ["説明通り","商品説明","写真通り","思った通り","期待通り"],
        "neg_en": ["not as described","different from description","misleading","false advertising"],
        "neg_ja": ["説明と違う","写真と違う","誇大広告","期待と違う"],
    },
    "brand_trust_loyalty": {
        "en": ["brand","trust","urbaner","again","repeat","loyal","recommend brand","love this brand"],
        "ja": ["ブランド","信頼","また買う","リピート","ファン","おすすめ"],
    },
    "repeat_purchase_intent": {
        "en": ["buy again","repurchase","would buy again","already bought","purchased again","recommended"],
        "ja": ["また買う","リピート","再購入","また使いたい","次も買う"],
    },
    "product_perceived_premium": {
        "en": ["premium","high-end","quality feel","feels expensive","surprised by quality","exceeded expectations"],
        "ja": ["高品質","プレミアム","高級感","期待以上","驚いた","よりいい"],
        "neg_en": ["cheap feeling","feels low quality","doesn't feel premium"],
        "neg_ja": ["安っぽい","チープ感","高級感がない"],
    },
    # ── Sensory Experience ────────────────────────────────────────────────────
    "cut_smoothness": {
        "en": ["smooth","glide","clean cut","smooth cut","seamless","flows","butter"],
        "ja": ["滑らか","スムーズ","なめらか","スムーズに切れ","滑るように"],
        "neg_en": ["rough","scratchy","snagging","rough cut","jagged"],
        "neg_ja": ["荒い","ガタガタ","引っかかる","滑らかでない"],
    },
    "operation_vibration_feel": {
        "en": ["vibration","vibrate","shake","rumble","buzz"],
        "ja": ["振動","ブルブル","震える","バイブ"],
        "neg_en": ["heavy vibration","strong vibration","vibrates too much","shakes a lot"],
        "neg_ja": ["振動が強い","ブルブルする","振れが大きい"],
    },
    "thick_hair_handling": {
        "en": ["thick hair","coarse hair","strong beard","handles thick","tough hair","thick"],
        "ja": ["太い髭","硬い毛","太い毛","剛毛","太い"],
        "neg_en": ["struggles with thick","can't handle thick","jams on thick","poor with coarse"],
        "neg_ja": ["太い毛に弱い","詰まる","パワー不足","太い毛が切れない"],
    },
    "trimming_evenness": {
        "en": ["even","uniform","consistent","uniform cut","even trim","balanced","evenly"],
        "ja": ["均一","ムラ","均等","一定","揃った"],
        "neg_en": ["uneven","patchy","not uniform","uneven cut"],
        "neg_ja": ["ムラがある","不均一","揃わない","ばらつき"],
    },
    # ── Hair Capability ───────────────────────────────────────────────────────
    "grey_hair_handling": {
        "en": ["grey hair","gray hair","white hair","silver hair"],
        "ja": ["白髪","グレーの毛","白い毛"],
    },
    "close_shave_capability": {
        "en": ["close shave","skin close","close to skin","smooth skin","shave close","zero gap"],
        "ja": ["深剃り","肌ぎりぎり","近い","スキンクロース"],
        "neg_en": ["not close enough","leaves stubble","can't shave close"],
        "neg_ja": ["深剃りできない","浅い","肌に近づかない"],
    },
    "fine_hair_precision": {
        "en": ["fine hair","thin hair","soft hair","light hair","delicate hair"],
        "ja": ["細い毛","薄い毛","産毛","柔らかい毛"],
        "neg_en": ["misses fine hair","can't catch fine","doesn't get fine"],
        "neg_ja": ["細い毛が切れない","産毛が切れない","取れない"],
    },
    # ── Social Context ────────────────────────────────────────────────────────
    "social_gifting_context": {
        "en": ["gift","bought for","husband","father","boyfriend","present","gave as","received as gift"],
        "ja": ["プレゼント","贈り物","旦那","父","彼氏","贈った","もらった"],
    },
    "shareable_between_partners": {
        "en": ["partner","share","couple","wife uses","husband uses","we both","both of us"],
        "ja": ["パートナー","共用","夫婦で","カップルで","二人で","シェア"],
    },
    # ── Eco & Sustainability ──────────────────────────────────────────────────
    "battery_independence": {
        "en": ["rechargeable","eco","no batteries","save batteries","environmentally","battery-free"],
        "ja": ["充電式","電池不要","エコ","環境","乾電池不要"],
    },
    # ── Functions (composite) ─────────────────────────────────────────────────
    "multi_use_versatility_score": {
        "en": ["versatile","all-in-one","multiple uses","many uses","does it all","everything","multipurpose"],
        "ja": ["多用途","オールインワン","万能","何でも","一台で","多目的"],
    },
}

# ── Positive / Negative sentiment word lists ──────────────────────────────────
POS_EN = ["great","good","excellent","love","nice","perfect","amazing","fantastic","wonderful",
          "sharp","clean","easy","smooth","solid","reliable","quality","highly recommend",
          "highly recommended","recommend","satisfied","happy","pleased","impressed","awesome",
          "works well","works great","works perfectly","best","outstanding","superb","lightweight"]
NEG_EN = ["bad","poor","weak","dull","hard","difficult","broke","broken","fails","complaint",
          "disappointed","terrible","horrible","awful","worst","cheap","flimsy","useless",
          "waste","stopped working","doesn't work","not working","failed","issues","problem",
          "unfortunately","would not","would not recommend","not recommend","avoid","return"]
POS_JA = ["良い","いい","素晴らしい","使いやすい","便利","満足","気に入","おすすめ","好き",
          "よく切れ","きれい","しっかり","快適","丈夫","安心","優秀","最高","よかった",
          "コスパ良","コスパが良","値段の割","価格の割","リピ","またリピ","感動","喜んで"]
NEG_JA = ["悪い","ダメ","壊れ","残念","不満","問題","困","切れない","うるさい","痛","壊","故障",
          "返品","がっかり","最悪","お勧めできない","おすすめできない","使えない","購入しなければよかった"]


def detect_language(text: str) -> str:
    """Detect if review is Japanese or English."""
    if not isinstance(text, str):
        return "en"
    ja_chars = sum(1 for c in text if '\u3040' <= c <= '\u30ff' or '\u4e00' <= c <= '\u9fff')
    return "ja" if ja_chars > 5 else "en"


def score_salience(text: str, attr_key: str, lang: str) -> int:
    """Return salience score 0-7 for an attribute in a review."""
    if not isinstance(text, str) or not text.strip():
        return 0

    kw_dict = KEYWORDS.get(attr_key, {})
    kw_list = kw_dict.get(lang, [])
    if not kw_list:
        kw_list = kw_dict.get("en", [])

    if not kw_list:
        return 0

    text_lower = text.lower()
    matches = sum(1 for kw in kw_list if kw.lower() in text_lower)

    if matches == 0:
        return 0

    text_len = len(text)

    if matches >= 4:
        return 7
    elif matches == 3:
        return 6
    elif matches == 2:
        return 5 if text_len > 200 else 4
    else:  # matches == 1
        if text_len < 80:
            return 2
        elif text_len < 300:
            return 3
        else:
            return 4


def score_quality_from_review(text: str, attr_key: str, star: int, lang: str) -> float | None:
    """Return per-review quality contribution (star-adjusted, 0-10) or None if absent."""
    sal = score_salience(text, attr_key, lang)
    if sal == 0:
        return None

    kw_dict = KEYWORDS.get(attr_key, {})
    neg_kws = kw_dict.get(f"neg_{lang}", kw_dict.get("neg_en", []))

    text_lower = text.lower()
    neg_hits = sum(1 for kw in neg_kws if kw.lower() in text_lower)

    # Base from star rating
    star_base = {5: 9.0, 4: 7.5, 3: 5.5, 2: 3.0, 1: 1.5}.get(int(star) if not pd.isna(star) else 3, 5.5)

    # Adjust for attribute-specific negative signals
    if neg_hits > 0:
        star_base = max(1.0, star_base - (neg_hits * 1.5))

    # Further adjust for general positive/negative sentiment
    pos_list = POS_JA if lang == "ja" else POS_EN
    neg_list = NEG_JA if lang == "ja" else NEG_EN
    pos_count = sum(1 for w in pos_list if w in text_lower)
    neg_count = sum(1 for w in neg_list if w in text_lower)
    sentiment_delta = (pos_count - neg_count) * 0.3

    return max(0.0, min(10.0, star_base + sentiment_delta))


# ── Load reviews ──────────────────────────────────────────────────────────────
TARGETS = {
    "B001K85BN2": "Panasonic ER-GB42",   # placeholder — will be read from file
    "B001K85BNC": "Panasonic ER-GB62",
    "B008KEJ1LM": "Conair GMT175CS",
}
BRAND_MAP = {
    "B001K85BN2": "Panasonic",
    "B001K85BNC": "Panasonic",
    "B008KEJ1LM": "Conair",
}

all_reviews = []
for asin in ["B001K85BN2", "B001K85BNC", "B008KEJ1LM"]:
    path = f"rawdata_Urbaner/amazon_reviews/001_Beard_Mustache_Trimmers/{asin}.xlsx"
    df = pd.read_excel(path)
    df["asin"] = asin
    all_reviews.append(df)

raw = pd.concat(all_reviews, ignore_index=True)

# Normalise column names
raw = raw.rename(columns={
    "ASIN": "asin_orig",
    "标题": "title",
    "内容": "review_text",
    "星级": "rating",
    "型号": "model",
    "评论人": "reviewer",
    "所属国家": "country",
    "评论时间": "review_date",
})
# Use our asin column
raw["product"] = raw["asin"]
raw["brand"] = raw["asin"].map(BRAND_MAP)
raw["review_id"] = raw.index.map(lambda i: f"R{i+1:05d}")
raw["unit_id"] = raw["review_id"]

# Fill missing review_text
raw["review_text"] = raw["review_text"].fillna("").astype(str)
raw["combined_text"] = raw["title"].fillna("").astype(str) + " " + raw["review_text"]
raw["lang"] = raw["combined_text"].apply(detect_language)
raw["rating"] = pd.to_numeric(raw["rating"], errors="coerce").fillna(3)

print(f"Loaded {len(raw)} reviews across {raw['product'].nunique()} products")
print(raw.groupby("product")["review_id"].count())

# ── Score every review × attribute ───────────────────────────────────────────
print("Scoring reviews... (this may take a minute)")
scoring_rows = []

for _, row in raw.iterrows():
    text = row["combined_text"]
    lang = row["lang"]
    star = row["rating"]

    score_row = {
        "review_id": row["review_id"],
        "unit_id": row["unit_id"],
        "brand": row["brand"],
        "product": row["product"],
        "review_text": row["review_text"],
        "rating": star,
        "lang": lang,
        "country": row.get("country", ""),
        "review_date": row.get("review_date", ""),
    }

    for attr_key in ATTR_KEYS:
        sal = score_salience(text, attr_key, lang)
        score_row[f"{attr_key}_salience"] = sal

    scoring_rows.append(score_row)

scoring_df = pd.DataFrame(scoring_rows)
scoring_df.to_csv(OUT_DIR / "review_scoring_table.csv", index=False, encoding="utf-8-sig")
print(f"Saved review_scoring_table.csv ({len(scoring_df)} rows)")

# ── Build product quality scorecard ──────────────────────────────────────────
print("Computing product quality scorecard...")
quality_rows = []

for asin, grp in raw.groupby("asin"):
    q_row = {
        "product": asin,
        "brand": BRAND_MAP[asin],
        "n_reviews": len(grp),
    }

    for attr_key in ATTR_KEYS:
        quality_vals = []
        for _, row in grp.iterrows():
            text = row["combined_text"]
            lang = row["lang"]
            star = row["rating"]
            q = score_quality_from_review(text, attr_key, star, lang)
            if q is not None:
                quality_vals.append(q)

        if quality_vals:
            q_score = sum(quality_vals) / len(quality_vals)
        else:
            # Attribute not mentioned: use overall product rating as neutral proxy
            avg_star = grp["rating"].mean()
            q_score = {5: 9.0, 4: 7.5, 3: 5.5, 2: 3.0, 1: 1.5}.get(round(avg_star), 5.5)
            # Apply mild shrinkage toward neutral when unmentioned
            q_score = 0.5 * q_score + 0.5 * 5.5

        q_row[f"{attr_key}_quality"] = round(q_score, 2)

    quality_rows.append(q_row)

quality_df = pd.DataFrame(quality_rows)
quality_df.to_csv(OUT_DIR / "product_quality_scorecard.csv", index=False, encoding="utf-8-sig")
print(f"Saved product_quality_scorecard.csv")

# ── Copy attribute catalog ────────────────────────────────────────────────────
import shutil
shutil.copy("attribute_catalog.csv", OUT_DIR / "attribute_catalog.csv")
print("Copied attribute_catalog.csv")

# ── Print summary stats ───────────────────────────────────────────────────────
sal_cols = [c for c in scoring_df.columns if c.endswith("_salience")]
mentioned = scoring_df[sal_cols].gt(0).sum().sum()
total_cells = len(scoring_df) * len(sal_cols)
print(f"\nSalience coverage: {mentioned}/{total_cells} cells ({mentioned/total_cells*100:.1f}%) with salience > 0")

for asin in ["B001K85BN2", "B001K85BNC", "B008KEJ1LM"]:
    subset = scoring_df[scoring_df["product"] == asin]
    avg_sal = subset[sal_cols].values.mean()
    avg_rating = subset["rating"].mean()
    print(f"{asin}: {len(subset)} reviews | avg_rating={avg_rating:.2f} | avg_salience={avg_sal:.3f}")

print("\nDone. Artifacts written to:", OUT_DIR)
