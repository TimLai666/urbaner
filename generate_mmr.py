import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle
import matplotlib
matplotlib.rcParams['font.family'] = ['Microsoft YaHei', 'SimHei', 'sans-serif']
matplotlib.rcParams['axes.unicode_minus'] = False

BG    = '#0C1B35'
BOX   = '#0F2248'
WHITE = '#FFFFFF'
LIGHT = '#B8C4D4'
GRAY  = '#6A7888'
RED   = '#C5392E'
BLUE  = '#1A52A5'
LBLUE = '#2060C0'

W, H = 22, 13
fig = plt.figure(figsize=(W, H))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W); ax.set_ylim(0, H)
ax.axis('off')
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

def rbox(x, y, w, h, fc=BOX, ec='#2855B5', lw=1.5, rad=0.3, ls='-', zo=2):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f'round,pad=0,rounding_size={rad}',
        facecolor=fc, edgecolor=ec, linewidth=lw, linestyle=ls, zorder=zo))

def icon_c(cx, cy, char, r=0.32, bg=LBLUE, fg=WHITE, fs=13):
    ax.add_patch(Circle((cx, cy), r, color=bg, zorder=4))
    ax.text(cx, cy, char, ha='center', va='center',
            fontsize=fs, fontweight='bold', color=fg, zorder=5)

def txt(x, y, s, fs=12, fw='normal', c=WHITE, ha='left', va='center', zo=5):
    ax.text(x, y, s, ha=ha, va=va, fontsize=fs, fontweight=fw, color=c, zorder=zo)

def h_arr(x1, y, x2, c='white', lw=2.5):
    ax.annotate('', xy=(x2, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle='->', color=c, lw=lw, mutation_scale=22), zorder=8)

def v_arr(x, y1, y2, c='white', lw=2.5):
    ax.annotate('', xy=(x, y2), xytext=(x, y1),
                arrowprops=dict(arrowstyle='->', color=c, lw=lw, mutation_scale=22), zorder=8)

def d_line_arr(x, y1, y2, c=GRAY, lw=1.8):
    ax.plot([x, x], [y1, y2 + 0.12], color=c, lw=lw, ls='--', zorder=6)
    ax.annotate('', xy=(x, y2), xytext=(x, y2 + 0.12),
                arrowprops=dict(arrowstyle='->', color=c, lw=lw, mutation_scale=14), zorder=8)

# ── TITLE
txt(W/2, 12.3, 'M  M  R  流  程  圖', fs=40, fw='bold', ha='center')

# ━━ INPUT COLUMN ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IX, IY, IW, IH = 0.3, 0.45, 5.5, 10.9
rbox(IX, IY, IW, IH, fc='#0D1D38', ec=RED, lw=2.5, ls='--')
txt(IX + IW/2, 0.18, 'I N P U T', fs=11, fw='bold', c=LIGHT, ha='center')

# S1: 行銷問題
S1Y, S1H = 8.0, 2.95
rbox(IX+0.18, S1Y, IW-0.36, S1H, fc='#0F2248', ec='#1A3D7A')
icon_c(IX+0.70, S1Y+S1H-0.43, '問', bg=BLUE)
txt(IX+1.18, S1Y+S1H-0.43, '行銷問題', fs=15, fw='bold')
for i, b in enumerate(['美日雙市場區隔', '鎖定目標客群', '競品定位分析', '消費者屬性偏好預測']):
    txt(IX+0.60, S1Y+S1H-1.05-i*0.56, f'• {b}', fs=11, c=LIGHT)

# S2: 統計模型
S2Y, S2H = 4.85, 2.95
rbox(IX+0.18, S2Y, IW-0.36, S2H, fc='#0F2248', ec='#1A3D7A')
icon_c(IX+0.70, S2Y+S2H-0.43, '統', bg=BLUE)
txt(IX+1.18, S2Y+S2H-0.43, '統計模型', fs=15, fw='bold')
for i, b in enumerate(['Review-Mining STP', 'Logistic Conjoint', 'Hedonic Pricing / MNL']):
    txt(IX+0.60, S2Y+S2H-1.05-i*0.65, f'• {b}', fs=11, c=LIGHT)

# S3: 資料來源
S3Y, S3H = 0.60, 4.05
rbox(IX+0.18, S3Y, IW-0.36, S3H, fc='#0F2248', ec='#1A3D7A')
icon_c(IX+0.70, S3Y+S3H-0.43, '資', bg=BLUE)
txt(IX+1.18, S3Y+S3H-0.43, '資料來源', fs=15, fw='bold')
for i, b in enumerate(['Amazon US/JP 評論 11,523 則',
                        '88 個 URBANER SKU × 114 屬性評分',
                        '9 類別競品銷售資料',
                        '社群媒體洞察資料']):
    txt(IX+0.60, S3Y+S3H-1.05-i*0.65, f'• {b}', fs=10.5, c=LIGHT)

# ━━ ARROW: INPUT → PROCESS ━━━━━━━━━━━━━━━━━━━━
PX = 6.3
h_arr(IX+IW, 6.0, PX)

# ━━ PROCESS COLUMN ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PW = 7.8
txt(PX+PW/2, 0.18, 'P R O C E S S', fs=11, fw='bold', c=LIGHT, ha='center')

# PB1: Review-Mining STP 模型
PB1Y, PB1H = 9.5, 1.8
rbox(PX, PB1Y, PW, PB1H)
icon_c(PX+0.60, PB1Y+PB1H/2, '型', bg=LBLUE)
txt(PX+1.20, PB1Y+PB1H/2, 'Review-Mining STP 模型', fs=14, fw='bold')

# Arrow PB1→PB2
v_arr(PX+PW/2, PB1Y, PB1Y-0.5)
txt(PX+PW/2+0.15, PB1Y-0.25, '建立模型', fs=10, c=GRAY)

# PB2: 聯合分析方法
PB2Y, PB2H = 4.4, 4.6
rbox(PX, PB2Y, PW, PB2H)
icon_c(PX+0.60, PB2Y+PB2H-0.42, '析', bg=LBLUE)
txt(PX+1.20, PB2Y+PB2H-0.42, '聯合分析方法', fs=14, fw='bold')
for i, b in enumerate(['WTP 願付價格分析',
                        '最適產品組合模擬',
                        '市場份額預測（MNL Share-of-Pref）',
                        '族群偏好區隔分析',
                        '定價敏感度分析']):
    txt(PX+0.55, PB2Y+PB2H-1.05-i*0.62, f'• {b}', fs=11, c=LIGHT)

# Arrow PB2→PB3
v_arr(PX+PW/2, PB2Y, PB2Y-0.45)

# PB3: 模型驗證
PB3Y, PB3H = 0.55, 3.4
rbox(PX, PB3Y, PW, PB3H)
icon_c(PX+0.60, PB3Y+PB3H/2, '驗', bg=LBLUE)
txt(PX+1.20, PB3Y+PB3H/2, '模型驗證', fs=14, fw='bold')

# ━━ OUTPUT COLUMN ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OX = PX + PW + 0.75
OW = 6.2
txt(OX+OW/2, 0.18, 'O U T P U T', fs=11, fw='bold', c=LIGHT, ha='center')

# OB1: 行銷劇本
OB1Y, OB1H = 9.8, 1.5
rbox(OX, OB1Y, OW, OB1H)
icon_c(OX+0.55, OB1Y+OB1H/2, '劇', bg=LBLUE, r=0.30)
txt(OX+1.10, OB1Y+OB1H/2, '行銷劇本', fs=14, fw='bold')
h_arr(PX+PW, OB1Y+OB1H/2, OX)
d_line_arr(OX+OW/2, OB1Y, OB1Y-0.78)
txt(OX+OW/2, OB1Y-0.95, '11項即戰行銷動作', fs=10, c=LIGHT, ha='center')

# OB2: 雙市場戰略儀表板
OB2Y, OB2H = 6.5, 1.5
rbox(OX, OB2Y, OW, OB2H)
icon_c(OX+0.55, OB2Y+OB2H/2, '表', bg=LBLUE, r=0.30)
txt(OX+1.10, OB2Y+OB2H/2, '雙市場戰略儀表板', fs=13, fw='bold')
h_arr(PX+PW, OB2Y+OB2H/2, OX)
d_line_arr(OX+OW/2, OB2Y, OB2Y-0.78)
txt(OX+OW/2, OB2Y-0.95, '視覺化分析平台', fs=10, c=LIGHT, ha='center')

# OB3: 產品優化建議
OB3Y, OB3H = 2.2, 1.5
rbox(OX, OB3Y, OW, OB3H)
icon_c(OX+0.55, OB3Y+OB3H/2, '優', bg=LBLUE, r=0.30)
txt(OX+1.10, OB3Y+OB3H/2, '產品優化建議', fs=14, fw='bold')
h_arr(PX+PW, OB3Y+OB3H/2, OX)
d_line_arr(OX+OW/2, OB3Y, OB3Y-0.78)
txt(OX+OW/2, OB3Y-0.95, 'Hero SKU 配置方向', fs=10, c=LIGHT, ha='center')

plt.savefig('output/mmr_flowchart.png', dpi=180, bbox_inches='tight', facecolor=BG)
plt.close()
print('Done: output/mmr_flowchart.png')
