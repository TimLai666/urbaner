import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Arc, Wedge, Ellipse, Rectangle
import numpy as np
import matplotlib
matplotlib.rcParams['font.family'] = ['Microsoft YaHei', 'sans-serif']
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

# ─── Icon drawing functions ───────────────────────────────────

def ib(cx, cy, r=0.32, bg=LBLUE):
    """Background circle for icon"""
    ax.add_patch(Circle((cx, cy), r, color=bg, zorder=4))

def ic_people(cx, cy, r=0.32, c='white', lw=1.5):
    """Two person silhouettes"""
    for dx in [-0.26*r, 0.26*r]:
        ax.add_patch(Circle((cx+dx, cy+0.32*r), 0.19*r, color=c, zorder=6))
        ax.add_patch(Arc((cx+dx, cy-0.08*r), 0.44*r, 0.40*r,
                         theta1=0, theta2=180, color=c, lw=lw, zorder=6))

def ic_bar(cx, cy, r=0.32, c='white', lw=2.5):
    """Bar chart (3 bars)"""
    for i, h in enumerate([0.50, 0.82, 0.42]):
        x = cx + (i-1)*0.42*r
        y0 = cy - 0.42*r
        ax.plot([x, x], [y0, y0+h*r], color=c, lw=lw*1.7,
                solid_capstyle='butt', zorder=6)
    ax.plot([cx-0.65*r, cx+0.65*r], [cy-0.42*r]*2, color=c, lw=lw*0.8, zorder=6)

def ic_db(cx, cy, r=0.32, c='white', lw=1.5):
    """Database / cylinder (3 ellipses + sides)"""
    spacing = 0.30*r
    for k, dy in enumerate([spacing, 0.0, -spacing]):
        filled = (k == 0)
        ax.add_patch(Ellipse((cx, cy+dy), 1.18*r, 0.30*r,
                             fill=filled,
                             facecolor=c if filled else 'none',
                             edgecolor=c, lw=lw, zorder=6))
    ax.plot([cx-0.59*r, cx-0.59*r], [cy-spacing, cy+spacing], color=c, lw=lw, zorder=6)
    ax.plot([cx+0.59*r, cx+0.59*r], [cy-spacing, cy+spacing], color=c, lw=lw, zorder=6)

def ic_gear(cx, cy, r=0.32, c='white', lw=1.5):
    """Gear / settings icon"""
    ax.add_patch(Circle((cx, cy), 0.43*r, fill=False, edgecolor=c, lw=lw, zorder=6))
    ax.add_patch(Circle((cx, cy), 0.19*r, color=c, zorder=6))
    for angle in range(0, 360, 45):
        rd = np.radians(angle)
        ax.add_patch(Circle((cx+np.cos(rd)*0.70*r, cy+np.sin(rd)*0.70*r),
                            0.13*r, color=c, zorder=6))

def ic_pie(cx, cy, r=0.32, c='white', lw=1.5):
    """Pie chart with one filled wedge"""
    ax.add_patch(Circle((cx, cy), 0.72*r, fill=False, edgecolor=c, lw=lw, zorder=6))
    ax.add_patch(Wedge((cx, cy), 0.72*r, 65, 168, fc=c, ec=c, lw=0.5, zorder=6))
    for angle in [65, 168, 305]:
        rd = np.radians(angle)
        ax.plot([cx, cx+np.cos(rd)*0.72*r], [cy, cy+np.sin(rd)*0.72*r],
                color=c, lw=lw, zorder=6)

def ic_check(cx, cy, r=0.32, c='white', lw=2.5):
    """Checkmark"""
    ax.plot([cx-0.55*r, cx-0.08*r, cx+0.55*r],
            [cy+0.02*r, cy-0.42*r, cy+0.46*r],
            color=c, lw=lw, solid_capstyle='round', solid_joinstyle='round', zorder=6)

def ic_doc(cx, cy, r=0.32, c='white', lw=1.5):
    """Document / list icon"""
    ax.add_patch(Rectangle((cx-0.52*r, cy-0.65*r), 1.04*r, 1.30*r,
                            fill=False, edgecolor=c, lw=lw, zorder=6))
    for dy in [0.30*r, 0.0, -0.30*r]:
        ax.add_patch(Circle((cx-0.38*r, cy+dy), 0.07*r, color=c, zorder=6))
        ax.plot([cx-0.24*r, cx+0.35*r], [cy+dy]*2, color=c, lw=lw*0.9, zorder=6)

def ic_monitor(cx, cy, r=0.32, c='white', lw=1.5):
    """Monitor / dashboard icon"""
    ax.add_patch(Rectangle((cx-0.65*r, cy-0.05*r), 1.30*r, 0.82*r,
                            fill=False, edgecolor=c, lw=lw, zorder=6))
    ax.plot([cx, cx], [cy-0.05*r, cy-0.45*r], color=c, lw=lw, zorder=6)
    ax.plot([cx-0.38*r, cx+0.38*r], [cy-0.45*r]*2, color=c, lw=lw, zorder=6)
    xs = [cx-0.48*r, cx-0.18*r, cx+0.12*r, cx+0.48*r]
    ys = [cy+0.22*r, cy+0.52*r, cy+0.32*r, cy+0.62*r]
    ax.plot(xs, ys, color=c, lw=lw*0.8, zorder=6)

def ic_target(cx, cy, r=0.32, c='white', lw=1.5):
    """Bullseye / target icon"""
    for mult in [0.28, 0.52, 0.76]:
        ax.add_patch(Circle((cx, cy), mult*r,
                            fill=(mult == 0.28),
                            facecolor=c if mult == 0.28 else 'none',
                            edgecolor=c, lw=lw, zorder=6))

def icon(fn, cx, cy, r=0.32, bg=LBLUE):
    ib(cx, cy, r, bg)
    fn(cx, cy, r)

# ─── Layout helpers ────────────────────────────────────────────

def rbox(x, y, w, h, fc=BOX, ec='#2855B5', lw=1.5, rad=0.3, ls='-', zo=2):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
        boxstyle=f'round,pad=0,rounding_size={rad}',
        facecolor=fc, edgecolor=ec, linewidth=lw, linestyle=ls, zorder=zo))

def txt(x, y, s, fs=12, fw='normal', c=WHITE, ha='left', va='center', zo=5):
    ax.text(x, y, s, ha=ha, va=va, fontsize=fs, fontweight=fw, color=c, zorder=zo)

def h_arr(x1, y, x2, c='white', lw=2.5):
    ax.annotate('', xy=(x2, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle='->', color=c, lw=lw, mutation_scale=22), zorder=8)

def v_arr(x, y1, y2, c='white', lw=2.5):
    ax.annotate('', xy=(x, y2), xytext=(x, y1),
                arrowprops=dict(arrowstyle='->', color=c, lw=lw, mutation_scale=22), zorder=8)

def d_arr(x, y1, y2, c=GRAY, lw=1.8):
    ax.plot([x, x], [y1, y2+0.12], color=c, lw=lw, ls='--', zorder=6)
    ax.annotate('', xy=(x, y2), xytext=(x, y2+0.12),
                arrowprops=dict(arrowstyle='->', color=c, lw=lw, mutation_scale=14), zorder=8)

# ─── TITLE ─────────────────────────────────────────────────────
txt(W/2, 12.3, 'M  M  R  流  程  圖', fs=40, fw='bold', ha='center')

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# INPUT COLUMN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IX, IY, IW, IH = 0.3, 0.45, 5.5, 10.9
rbox(IX, IY, IW, IH, fc='#0D1D38', ec=RED, lw=2.5, ls='--')
txt(IX+IW/2, 0.18, 'I N P U T', fs=11, fw='bold', c=LIGHT, ha='center')

# S1: 行銷問題
S1Y, S1H = 8.0, 2.95
rbox(IX+0.18, S1Y, IW-0.36, S1H, fc='#0F2248', ec='#1A3D7A')
icon(ic_people, IX+0.70, S1Y+S1H-0.43)
txt(IX+1.18, S1Y+S1H-0.43, '行銷問題', fs=15, fw='bold')
for i, b in enumerate(['美日雙市場區隔', '鎖定目標客群', '競品定位分析', '消費者屬性偏好預測']):
    txt(IX+0.60, S1Y+S1H-1.05-i*0.56, f'• {b}', fs=11, c=LIGHT)

# S2: 統計模型
S2Y, S2H = 4.85, 2.95
rbox(IX+0.18, S2Y, IW-0.36, S2H, fc='#0F2248', ec='#1A3D7A')
icon(ic_bar, IX+0.70, S2Y+S2H-0.43)
txt(IX+1.18, S2Y+S2H-0.43, '統計模型', fs=15, fw='bold')
for i, b in enumerate(['Review-Mining STP', 'Logistic Conjoint', 'Hedonic Pricing / MNL']):
    txt(IX+0.60, S2Y+S2H-1.05-i*0.65, f'• {b}', fs=11, c=LIGHT)

# S3: 資料來源
S3Y, S3H = 0.60, 4.05
rbox(IX+0.18, S3Y, IW-0.36, S3H, fc='#0F2248', ec='#1A3D7A')
icon(ic_db, IX+0.70, S3Y+S3H-0.43)
txt(IX+1.18, S3Y+S3H-0.43, '資料來源', fs=15, fw='bold')
for i, b in enumerate(['Amazon US/JP 評論 11,523 則',
                        '88 個 URBANER SKU × 114 屬性評分',
                        '9 類別競品銷售資料',
                        '社群媒體洞察資料']):
    txt(IX+0.60, S3Y+S3H-1.05-i*0.65, f'• {b}', fs=10.5, c=LIGHT)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Arrow: INPUT → PROCESS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PX = 6.3
h_arr(IX+IW, 6.0, PX)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PROCESS COLUMN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PW = 7.8
txt(PX+PW/2, 0.18, 'P R O C E S S', fs=11, fw='bold', c=LIGHT, ha='center')

# PB1: Review-Mining STP 模型
PB1Y, PB1H = 9.5, 1.8
rbox(PX, PB1Y, PW, PB1H)
icon(ic_gear, PX+0.60, PB1Y+PB1H/2)
txt(PX+1.20, PB1Y+PB1H/2, 'Review-Mining STP 模型', fs=14, fw='bold')

# Arrow PB1 → PB2
v_arr(PX+PW/2, PB1Y, PB1Y-0.50)
txt(PX+PW/2+0.15, PB1Y-0.25, '建立模型', fs=10, c=GRAY)

# PB2: 聯合分析方法
PB2Y, PB2H = 4.4, 4.6
rbox(PX, PB2Y, PW, PB2H)
icon(ic_pie, PX+0.60, PB2Y+PB2H-0.42)
txt(PX+1.20, PB2Y+PB2H-0.42, '聯合分析方法', fs=14, fw='bold')
for i, b in enumerate(['WTP 願付價格分析',
                        '最適產品組合模擬',
                        '市場份額預測（MNL Share-of-Pref）',
                        '族群偏好區隔分析',
                        '定價敏感度分析']):
    txt(PX+0.55, PB2Y+PB2H-1.05-i*0.62, f'• {b}', fs=11, c=LIGHT)

# Arrow PB2 → PB3
v_arr(PX+PW/2, PB2Y, PB2Y-0.45)

# PB3: 模型驗證（標題移至頂端，補上 bullet points）
PB3Y, PB3H = 0.55, 3.4
rbox(PX, PB3Y, PW, PB3H)
icon(ic_check, PX+0.60, PB3Y+PB3H-0.43)
txt(PX+1.20, PB3Y+PB3H-0.43, '模型驗證', fs=14, fw='bold')
for i, b in enumerate(['Logistic 模型顯著性驗證（p<0.05）',
                        'ANOVA 屬性重要性排序確認',
                        'Conjoint 預測效度與內部效度',
                        'MNL 市場份額模擬校準']):
    txt(PX+0.55, PB3Y+PB3H-1.05-i*0.62, f'• {b}', fs=11, c=LIGHT)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# OUTPUT COLUMN（加高框體，補入 bullet points）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OX = PX + PW + 0.75   # = 14.85
OW = 6.2
OB_H = 2.0            # 統一框高（足夠放 3 條 bullet）
txt(OX+OW/2, 0.18, 'O U T P U T', fs=11, fw='bold', c=LIGHT, ha='center')

# OB1: 行銷劇本
OB1Y = 9.3
rbox(OX, OB1Y, OW, OB_H)
icon(ic_doc, OX+0.55, OB1Y+OB_H-0.42, r=0.30)
txt(OX+1.10, OB1Y+OB_H-0.42, '行銷劇本', fs=14, fw='bold')
for i, b in enumerate(['US：Gift-Ready × 7-in-1 套組策略',
                        'JP：精度・耐久・規格数値化策略',
                        '12 個月行銷檔期規劃']):
    txt(OX+0.45, OB1Y+OB_H-1.02-i*0.46, f'• {b}', fs=10.5, c=LIGHT)
h_arr(PX+PW, OB1Y+OB_H/2, OX)
d_arr(OX+OW/2, OB1Y, OB1Y-0.72)
txt(OX+OW/2, OB1Y-0.92, '11項即戰行銷動作', fs=10, c=LIGHT, ha='center')

# OB2: 雙市場戰略儀表板
OB2Y = 5.9
rbox(OX, OB2Y, OW, OB_H)
icon(ic_monitor, OX+0.55, OB2Y+OB_H-0.42, r=0.30)
txt(OX+1.10, OB2Y+OB_H-0.42, '雙市場戰略儀表板', fs=13, fw='bold')
for i, b in enumerate(['STP 族群分析視覺化',
                        'Conjoint 偏好互動圖表',
                        '競品市場份額對比']):
    txt(OX+0.45, OB2Y+OB_H-1.02-i*0.46, f'• {b}', fs=10.5, c=LIGHT)
h_arr(PX+PW, OB2Y+OB_H/2, OX)
d_arr(OX+OW/2, OB2Y, OB2Y-0.72)
txt(OX+OW/2, OB2Y-0.92, '視覺化分析平台', fs=10, c=LIGHT, ha='center')

# OB3: 產品優化建議
OB3Y = 2.0
rbox(OX, OB3Y, OW, OB_H)
icon(ic_target, OX+0.55, OB3Y+OB_H-0.42, r=0.30)
txt(OX+1.10, OB3Y+OB_H-0.42, '產品優化建議', fs=14, fw='bold')
for i, b in enumerate(['Hero SKU 差異化配置方向',
                        '新 SKU 規格共識（IPX7+ / ≥7件）',
                        '定價帶建議（US $60–120）']):
    txt(OX+0.45, OB3Y+OB_H-1.02-i*0.46, f'• {b}', fs=10.5, c=LIGHT)
h_arr(PX+PW, OB3Y+OB_H/2, OX)
d_arr(OX+OW/2, OB3Y, OB3Y-0.72)
txt(OX+OW/2, OB3Y-0.92, 'Hero SKU 配置方向', fs=10, c=LIGHT, ha='center')

# ─── Save ──────────────────────────────────────────────────────
plt.savefig('output/mmr_flowchart.png', dpi=180, bbox_inches='tight', facecolor=BG)
plt.close()
print('Done: output/mmr_flowchart.png')
