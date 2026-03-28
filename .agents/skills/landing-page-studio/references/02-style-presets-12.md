# Style Presets (A-L)

## A — Modern SaaS
- Tone: 清新、專業、明亮
- Palette: `#F8FAFC`, `#2563EB`, `#0F172A`
- Typography: 幾何無襯線 + 清晰內文
- Motion: 柔和淡入、hover tilt、light drift

## B — Quiet Luxury
- Tone: 低調奢華、深色、精緻
- Palette: `#0D0D12`, `#D4AF7A`, `#F3E7D3`
- Typography: Serif + Sans 混搭
- Motion: 逐字浮現、流光遮罩、cursor difference

## C — Tech Impact
- Tone: 前衛、高對比、科技感
- Palette: `#070B14`, `#00E5FF`, `#7C3AED`
- Typography: Condensed + Mono
- Motion: WebGL 粒子、magnetic CTA、beam border

## D — Vintage Artsy
- Tone: 溫暖、故事感、人文
- Palette: `#F5F0E8`, `#6E1F2B`, `#8D7B68`
- Typography: Old-style Serif + Humanist Sans
- Motion: 平滑滾動、film grain、濾鏡切換

## E — Editorial Bold
- Tone: 時尚雜誌、強對比排版
- Palette: `#F4F1EB`, `#111111`, `#D72638`
- Typography: Display Serif + Neutral Sans
- Motion: 大標遮罩 reveal、跨欄滑入

## F — Eco Organic
- Tone: 自然、永續、手感
- Palette: `#EEF3EA`, `#2F6F4F`, `#B08D57`
- Typography: Organic Sans + Soft Serif
- Motion: 葉片曲線浮動、柔和視差

## G — Playful Neo
- Tone: 活潑、創意、年輕
- Palette: `#FFF9E8`, `#FF5D5D`, `#3A86FF`
- Typography: Rounded Sans + Accent Display
- Motion: 彈跳 easing、彩塊動態轉場

## H — Minimal Brutalist
- Tone: 大膽、直接、實驗排版
- Palette: `#F2F2F2`, `#111111`, `#FF3B30`
- Typography: Mono + Heavy Grotesk
- Motion: 硬切換、step-like transitions

## I — Cyber Grid
- Tone: 網格、終端、數位戰術
- Palette: `#06090F`, `#39FF14`, `#8BE9FD`
- Typography: Mono Dominant
- Motion: scanline、grid pulse、glitch-lite

## J — Wellness Calm
- Tone: 放鬆、療癒、乾淨
- Palette: `#F7F5F2`, `#89A8A2`, `#334E68`
- Typography: Soft Sans + Elegant Serif
- Motion: 慢速淡入、柔和 blur/unblur

## K — Finance Authority
- Tone: 穩健、可信、權威
- Palette: `#0F172A`, `#1D4ED8`, `#E2E8F0`
- Typography: Corporate Sans + Metrics Mono
- Motion: 精準微動效、數字遞增

## L — Creator Neon
- Tone: 創作者經濟、霓虹、街頭數位
- Palette: `#0B0B15`, `#FF3D81`, `#00F5D4`
- Typography: Expressive Display + Crisp Sans
- Motion: glow trails、masked spotlight

## Custom Style Rule

當 `style_variant=custom`：

1. 抽取 `mood`, `material`, `contrast`, `energy`
2. 對映最接近的 A-L 作基底
3. 覆寫 token：`--bg`, `--text`, `--accent`, `--font-display`, `--font-body`
4. 不改變核心轉換區塊結構（避免為視覺犧牲可用性）
