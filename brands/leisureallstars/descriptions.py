"""Japanese product copy for EPOKHE styles new to the leisureallstars store.

Thirteen styles in the SOH260818 drop -- six eyewear, all seven headwear -- have
no sibling colourway already on the store to inherit a description from. These
were adapted from EPOKHE's own product pages into the two house formats the
store already uses: eyewear gets the bilingual Frame/Lens layout of the existing
EPOKHE products, headwear the simpler intro-plus-Material shape of the AFENDS
cap.

Keyed by the sheet's STYLE value; lookup is case- and whitespace-insensitive.
A style with a live sibling is deliberately absent, because
:meth:`EpokheClient.description_source` prefers the live product so colourways
of one style cannot drift apart.

Every specification here comes from the brand's own page; nothing was invented.
Worth a native read-through before these go live.
"""

#: Source pages, for whoever revises these next.
SOURCES = {
    "DOME": "https://epokhe.co/collections/sunglasses/products/dome-black-polished-black",
    "VOID": "https://epokhe.co/collections/sunglasses/products/void-black-polished-black",
    "PANO": "https://epokhe.co/collections/sunglasses/products/pano-black-polished-amber",
    "REALM": "https://epokhe.co/collections/sunglasses/products/realm-black-polished-black-polarized",
    "JACUZZZI x JALEESSA VINCENT": "https://epokhe.co/collections/sunglasses/products/jacuzzi-x-jalessa-vincent-black-polished-black",
    "EMBER": "https://epokhe.co/collections/sunglasses/products/ember-black-polished-black",
    "CORE HAT": None,
    "ASHFALL CAP": None,
    "CAVE TRUCKER": None,
    "INFERNO CAP": None,
    "STELLAR CAP": None,
    "TUNDRA TRACKER CAP": None,
    "THOMAS TOWNEND ART SERIES HAT": None,
}

#: Which house format each style uses.
FORMATS = {
    "DOME": "eyewear",
    "VOID": "eyewear",
    "PANO": "eyewear",
    "REALM": "eyewear",
    "JACUZZZI x JALEESSA VINCENT": "eyewear",
    "EMBER": "eyewear",
    "CORE HAT": "headwear",
    "ASHFALL CAP": "headwear",
    "CAVE TRUCKER": "headwear",
    "INFERNO CAP": "headwear",
    "STELLAR CAP": "headwear",
    "TUNDRA TRACKER CAP": "headwear",
    "THOMAS TOWNEND ART SERIES HAT": "headwear",
}

_RAW = {
    "DOME": """<meta charset="UTF-8">
<p data-mce-fragment="1"> </p>
<p>1995年の夏の空気をまとう、スリムなシルエット。</p>
<p>クリーンな4ベース構造から立ち上がる DOME は、顔に沿うように低く収まり、無駄を削ぎ落とした精緻なラインを描きます。テンプルに配された6ピンヒンジは、EPOKHE のデザインシグネチャーのひとつ。素材には、強度と軽さ、そして仕上がりの美しさから選ばれた植物由来のプレミアムバイオアセテートを採用しています。</p>
<p>生産は少量ずつ。ひとつひとつ、手作業で仕上げています。</p>
<p data-mce-fragment="1"> </p>
<p data-mce-fragment="1"><strong>Frame / フレーム</strong></p>
<p><span>Slimline 4-Base Frame / スリムライン 4ベースカーブフレーム</span><span><br> </span><span>6-Pin Hinge Detail / 6ピンヒンジ ディテール</span><span><br> </span><span>Rolled Faceting / ロールドファセット（丸みを帯びた面取り加工）</span><span><br> </span><span>Premium Bio-Acetate / プレミアム バイオアセテート（植物由来素材）</span><span><br> </span><span>Hand-Finished Construction / ハンドフィニッシュによる仕上げ</span><span><br> </span><span>Precision detailing & small-batch craftsmanship / 精密なディテーリングとスモールバッチのクラフトマンシップ</span><span><br> </span><span>Lens 58mm / Bridge 18mm / Temple 140mm / レンズ 58mm ／ ブリッジ 18mm ／ テンプル 140mm</span></p>
<p data-mce-fragment="1"><br></p>
<p data-mce-fragment="1"><strong data-mce-fragment="1">Lens / レンズ</strong></p>
<p><span>CR39 Lens / CR39レンズ</span><span><br> </span><span>100% UV protection / 100% UVプロテクション</span><span><br> </span><span>Scratch Resistant / スクラッチレジスタント（傷がつきにくい仕様）</span><span><br> </span><span>RX / Prescription Compatible / 度付きレンズへの交換に対応</span></p>""",
    "VOID": """<meta charset="UTF-8">
<p data-mce-fragment="1"> </p>
<p>90年代レイヴの黎明から、00年代初頭のサーフ・ヒステリアの渦中へ。</p>
<p>ハンドクラフトのフラットブロウがハードエッジな要素を束ね、"ブルータリスト"と呼ぶべき佇まいを描き出す VOID 。計算されたコンターベベリングが、その輪郭に静かな陰影を与えます。</p>
<p>顔まわりを覆うオーバーサイズフィットで、快適な掛け心地を追求。最高品質のバイオアセテートをハンドシェイプし、7バレルヒンジと固定式3ピンディテールで組み上げた堅牢なジオメトリック構造に。フロントは2ベースカーブのセミフラットシェイプ。時代を超えて立ち続ける、モノリシックなフレームです。</p>
<p data-mce-fragment="1"> </p>
<p data-mce-fragment="1"><strong>Frame / フレーム</strong></p>
<p><span>Handshape Bio-acetate produced from natural cellulose / 天然セルロース由来のバイオアセテートをハンドシェイプ</span><span><br> </span><span>Custom Temple Detailing / カスタム テンプルディテール</span><span><br> </span><span>7-Barrel 3-pin hinge / 7バレル 3ピンヒンジ</span><span><br> </span><span>2 base curvature frame (Semi-flat) / 2ベースカーブフレーム（セミフラット）</span></p>
<p data-mce-fragment="1"><br></p>
<p data-mce-fragment="1"><strong data-mce-fragment="1">Lens / レンズ</strong></p>
<p><span>CR39 Black Lens / CR39 ブラックレンズ</span><span><br> </span><span>100% UV protection / 100% UVカット</span><span><br> </span><span>Scratch Resistant / 耐スクラッチ仕様</span><span><br> </span><span>All EPOKHE frames are RX compatible / EPOKHEの全フレームが度付きレンズに対応</span></p>
<p data-mce-fragment="1"><br></p>
<p data-mce-fragment="1"><strong data-mce-fragment="1">Size / サイズ</strong></p>
<p><span>Lens: 52mm / レンズ幅 52mm</span><span><br> </span><span>Bridge: 20mm / ブリッジ幅 20mm</span><span><br> </span><span>Temple: 145mm / テンプル長 145mm</span></p>""",
    "PANO": """<meta charset="UTF-8">
<p data-mce-fragment="1"> </p>
<p>デコの建築美をまとう、オーバーサイズのアビエイター -</p>
<p>EPOKHE のデザインを大胆な領域へと押し広げる、オーバーサイズのアセテート アビエイター、PANO 。アーカイブに眠るシルエットの数々を掘り起こし、デコ期の建築が持つ構築的な強さに着想を得た一本。大きめの顔立ちに映え、強い主張を求める人のために生まれました。</p>
<p>ベストセラー Mono のクリーンなジオメトリを受け継ぎながら、プロポーションはより大胆に、ディテールはより精緻に。彫刻的なシングル ブロウバーが鋭くモダンなラインを描き、堅牢な5バレル ピンヒンジが、EPOKHE が積み重ねてきた耐久性とクラフトマンシップを裏づけます。存在感と精度が拮抗する、外の世界へ踏み出す人のためのアイウェア。</p>
<p>プレミアム バイオアセテートを手作業で仕上げた、スモールバッチのクラフトマンシップ。CR39 レンズは紫外線を100%カットします。<br> レンズ幅 55mm / ブリッジ 18mm / テンプル 145mm 。</p>
<p data-mce-fragment="1"> </p>
<p data-mce-fragment="1"><strong>Frame / フレーム</strong></p>
<p><span>Premium Bio-Acetate / プレミアム バイオアセテート</span><span><br> </span><span>Hand-Finished Construction / ハンドフィニッシュ コンストラクション</span><span><br> </span><span>Precision detailing & small-batch craftsmanship / 精緻なディテーリングとスモールバッチ クラフトマンシップ</span><span><br> </span><span>Modern evolution of classic aviator shape / クラシックなアビエイター シェイプのモダンな進化形</span><span><br> </span><span>5-barrel Hinge / 5バレル ヒンジ</span></p>
<p data-mce-fragment="1"><br></p>
<p data-mce-fragment="1"><strong data-mce-fragment="1">Lens / レンズ</strong></p>
<p><span>CR39 Lens / CR39レンズ</span><span><br> </span><span>100% UV protection / 紫外線を100%カット</span><span><br> </span><span>Scratch Resistant / 傷がつきにくい仕様</span><span><br> </span><span>RX / Prescription Compatible / 度付き（オプティカル）レンズに対応</span></p>""",
    "REALM": """<meta charset="UTF-8">
<p data-mce-fragment="1"> </p>
<p>スピードのために彫り上げられた、8ベースのラップフォルム。</p>
<p>コンセプトから削り出したような 8ベースのラップフレームが、デザインとパフォーマンスを一体に融合させた REALM。大胆に、そして深くベベルを効かせたシルエットが、ラップアラウンド アイウェアのあり方を描き直します。</p>
<p>顔のラインに沿って包み込むフォルムは、比類のないカバレッジと保護性能をもたらし、あらゆるシーンで揺るがないフィット感を約束します。EPOKHE を象徴するプレミアム バイオアセテートから生まれた REALM は、革新とスタイル、そしてサステナビリティへの揺るぎない姿勢を映し出す一本です。</p>
<p data-mce-fragment="1"> </p>
<p data-mce-fragment="1"><strong>Frame / フレーム</strong></p>
<p><span>Handshape acetate produced from natural cellulose / 天然セルロース由来のハンドシェイプアセテート</span><span><br> </span><span>Custom Temple Detailing / カスタム テンプル ディテーリング</span><span><br> </span><span>7-barrel hinge / 7バレル ヒンジ</span><span><br> </span><span>8 Base Wrap / 8ベースカーブフレーム (ラップ)</span><span><br> </span><span>Lens: 58mm / レンズ幅 58mm</span><span><br> </span><span>Bridge: 21mm / ブリッジ幅 21mm</span><span><br> </span><span>Temple: 120mm / テンプル長 120mm</span></p>
<p data-mce-fragment="1"><br></p>
<p data-mce-fragment="1"><strong data-mce-fragment="1">Lens / レンズ</strong></p>
<p><span>Polarized CR39 Lens / 偏光 CR39レンズ</span><span><br> </span><span>100% UV protection / 100% UVプロテクション</span><span><br> </span><span>Scratch Resistant / スクラッチレジスタント（傷が付きにくい仕様）</span><span><br> </span><span>RX / Prescription Compatible / 度付きレンズ対応</span></p>""",
    "JACUZZZI x JALEESSA VINCENT": """<meta charset="UTF-8">
<p data-mce-fragment="1"> </p>
<p>ハイグロスのエネルギーを、2000年代初頭のグラマーに沈めて。</p>
<p>Jaleesa Vincent とともにデザインされた、EPOKHE の新作フレーム JACUZZI。鮮烈な青い水のなかへ解き放たれたようなハイグロスの輝きが、2000年代初頭のグラマラスな空気を呼び起こします。ファッションを起点にした精緻な設計は、遊び心とシャープさを併せ持ち、力強く華やか。大胆で、時代の先を示すような、意図して遊び心を効かせた一本です。</p>
<p>サステナブルな耐久性を備えたプレミアム バイオアセテートを使用し、軽やかなかけ心地とハンドフィニッシュによる精緻なディテールを両立させました。<br> レンズ幅60mm、ブリッジ18mm、テンプル130mm。</p>
<p data-mce-fragment="1"> </p>
<p data-mce-fragment="1"><strong>Frame / フレーム</strong></p>
<p><span>Handshape acetate produced from natural cellulose / 天然セルロース由来のハンドシェイプアセテート</span><span><br> </span><span>Custom Temple Detailing / オリジナルのテンプルディテール</span><span><br> </span><span>5-barrel hinge / 5バレルヒンジ</span></p>
<p data-mce-fragment="1"><br></p>
<p data-mce-fragment="1"><strong data-mce-fragment="1">Lens / レンズ</strong></p>
<p><span>CR39 Black Lens / CR39 ブラックレンズ</span><span><br> </span><span>100% UV protection / 100% UVカット</span><span><br> </span><span>Scratch Resistant / 傷が付きにくい仕様</span><span><br> </span><span>All EPOKHE frames are RX compatible / EPOKHE のフレームはすべて度付きレンズに対応</span></p>""",
    "EMBER": """<meta charset="UTF-8">
<p data-mce-fragment="1"> </p>
<p>大きさと、やわらかさ。その狭間に生まれる緊張感。</p>
<p>EPOKHE の新しいフレーム EMBER は、スケールとソフトネスのせめぎ合いを探ったモデル。大胆なプロポーションを描きながら、丸みを帯びたベベルドラインが顔の輪郭に自然と寄り添います。ラージフィットでありながら、佇まいはあくまで控えめ。</p>
<p>素材にはプレミアムなバイオアセテートを採用し、彫刻的でありながら削ぎ落とされた表情を生み出しました。厚みを持たせ、先へ向かうほど細くテーパードするテンプルを支えるのは、7バレル デュアル3ピン ヒンジ。EPOKHE がアーカイブから受け継いできたエンジニアリングを進化させ、堅牢性と洗練された重量バランスをともに高めています。</p>
<p>普遍的な幾何学と、現代的な流れ。控えめなデザインが、雄弁に語りかけます。</p>
<p data-mce-fragment="1"> </p>
<p data-mce-fragment="1"><strong>Frame / フレーム</strong></p>
<p><span>Crafted from biodegradable, plant-based acetate / 生分解性の植物由来アセテート</span><span><br> </span><span>Large-fitting silhouette with rolled bevelled edges / 丸みを帯びたベベルドエッジのラージフィットシルエット</span><span><br> </span><span>7-Barrel Dual 3-Pin Hinge / 7バレル デュアル3ピン ヒンジ</span><span><br> </span><span>2 base curvature frame (Semi-flat) / 2ベースカーブフレーム（セミフラット）</span></p>
<p data-mce-fragment="1"><br></p>
<p data-mce-fragment="1"><strong data-mce-fragment="1">Lens / レンズ</strong></p>
<p><span>CR39 Lens / CR39 レンズ</span><span><br> </span><span>Scratch-Resistant / 傷がつきにくい仕様</span><span><br> </span><span>100% UVA & UVB protection / 100% UVA・UVB プロテクション</span></p>""",
    "CORE HAT": """<p data-mce-fragment="1"><b style="font-size: 0.875rem;">丈夫なコットンツイルで仕立てた、装飾を削ぎ落としたベーシックなキャップ。コントラストカラーのステッチが、シンプルな表情にさりげない表情を添えます。あらかじめカーブをつけたプリカーブドブリムと、スナップバック仕様の後ろ留め。しっかりと収まりながら、心地よくかぶれる一頂です。ワンサイズで、幅広い方にお使いいただけます。</b></p>
<p data-mce-fragment="1"> </p>
<p><b>Material</b></p>
<p data-mce-fragment="1"><span>Cotton Twill</span><br></p>
<p><b>Details</b></p>
<p data-mce-fragment="1"><span>Pre-curved brim</span><br><span>Snapback closure</span><br><span>Contrast stitching</span><br><span>One size fits most</span><br></p>""",
    "ASHFALL CAP": """<p data-mce-fragment="1"><b style="font-size: 0.875rem;">ウォッシュをかけたコットンツイルで仕立てたダッドキャップ。オーバーサイズのEpokheスクリプト刺繍を、両脇のスター刺繍が引き立てます。ブリムとパネルに効かせたコントラストステッチが、リラックスしたシルエットに程よい表情を加えます。</b></p>
<p data-mce-fragment="1"> </p>
<p><b>Material</b></p>
<p data-mce-fragment="1"><span>100% Woven Cotton</span><br></p>
<p data-mce-fragment="1"> </p>
<p><b>Details</b></p>
<p data-mce-fragment="1"><span>Washed cotton twill</span><br><span>Relaxed dad fit</span><br><span>Oversized Epokhe script embroidery flanked by embroidered stars</span><br><span>Contrast stitching across the brim and panels</span><br></p>""",
    "CAVE TRUCKER": """<p data-mce-fragment="1"><b style="font-size: 0.875rem;">EPOKHE のトラッカーキャップ。コットンツイルのボディにメッシュバックを合わせ、フロントパネルには "Eternal World" の文字をオーバル型のバッジで一文字ずつ配置しました。全体にあしらったコントラストステッチが、シンプルなつくりにさりげない表情を添えています。</b></p>
<p data-mce-fragment="1"> </p>
<p><b>Material</b></p>
<p data-mce-fragment="1"><span>100% Woven Cotton</span><br></p>
<p><b>Details</b></p>
<p data-mce-fragment="1"><span>Cotton twill body</span><br><span>Mesh back</span><br><span>"Eternal World" oval-badged lettering across front panel</span><br><span>Contrast stitching throughout</span><br></p>""",
    "INFERNO CAP": """<p data-mce-fragment="1"><b style="font-size: 0.875rem;">フレイムモチーフの刺繍を大胆にあしらったコットンキャップ。フロントパネルにはオーバルロゴを刺繍し、全体に効かせたコントラストステッチが表情に奥行きを添えます。ウォッシュ加工を施した生地の落ち着いた色味に、プリカーブドバイザーとスナップバックを合わせ、頭になじむかぶり心地に仕上げました。</b></p>
<p data-mce-fragment="1"> </p>
<p><b>Material</b></p>
<p data-mce-fragment="1"><span>100% Woven Cotton</span><br></p>
<p><b>Details</b></p>
<p data-mce-fragment="1"><span>Embroidered oval logo at front panel</span><br><span>Contrast stitch detailing throughout</span><br><span>Pre-curved brim</span><br><span>Snapback closure</span><br><span>One size fits most</span><br></p>""",
    "STELLAR CAP": """<p data-mce-fragment="1"><b style="font-size: 0.875rem;">ウォッシュ加工を施した、肩の力の抜けた表情のキャップ。芯のあるブリムがかたちをしっかりと保ち、顔まわりの輪郭を引き締めます。アジャスタブル仕様のワンサイズで、頭まわりに合わせて調整できます。</b></p>
<p data-mce-fragment="1"> </p>
<p><b>Details</b></p>
<p data-mce-fragment="1"><span>Washed finish</span><br><span>Structured brim</span><br><span>Adjustable fit</span><br><span>One size fits most</span><br></p>""",
    "TUNDRA TRACKER CAP": """<p data-mce-fragment="1"><b style="font-size: 0.875rem;">コットンツイルに、色味を揃えたメッシュのバックパネルを合わせたトラッカーキャップ。フロント中央に据えたオーバルロゴバッジが目を引き、ブリムとパネルに走るコントラストステッチが表情を引き締めます。余計な装飾を省いたつくりのなかに、EPOKHEらしい素っ気なさがにじむ一点。</b></p>
<p data-mce-fragment="1"> </p>
<p><b>Material</b></p>
<p data-mce-fragment="1"><span>100% Woven Cotton</span><br></p>
<p data-mce-fragment="1"> </p>
<p><b>Details</b></p>
<p data-mce-fragment="1"><span>Trucker cap with tonal mesh back panels</span><br><span>Oval logo badge at centre front</span><br><span>Contrast stitching across the brim and panels</span><br></p>""",
    "THOMAS TOWNEND ART SERIES HAT": """<p data-mce-fragment="1"><b style="font-size: 0.875rem;">オーストラリアのタトゥーアーティスト Thomas Townend とのアートシリーズ。大胆な 'Trad Style' のタトゥーワークで知られる彼のインシグニアをあしらった限定キャップです。コットン100%の6パネル構造に、コントラストステッチと刺繍アイレットをあしらいました。ウォッシュ加工と上質なトリムで仕上げた、スナップバックで調整できるリラックスフィット。</b></p>
<p data-mce-fragment="1"> </p>
<p><b>Material</b></p>
<p data-mce-fragment="1"><span>100% Cotton</span><br></p>
<p><b>Details</b></p>
<p data-mce-fragment="1"><span>6-Panel Design</span><br><span>Contrast Stitching</span><br><span>Embroidered Eyelets</span><br><span>Adjustable Snapback Closure</span><br><span>Washed Treatment & Premium Trims</span><br><span>Relaxed Fit</span><br></p>""",
}


def _normalise(style):
    """Collapse whitespace and case so 'JACUZZZI x JALEESSA VINCENT' matches."""
    return " ".join(str(style).split()).upper()


#: Style -> description HTML, keyed on the normalised style name.
DESCRIPTIONS = {_normalise(style): body for style, body in _RAW.items()}


def description_html(style):
    """Copy for ``style``, or None when it must come from a live sibling."""
    return DESCRIPTIONS.get(_normalise(style))
