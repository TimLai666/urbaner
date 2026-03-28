# Animation System and Fallbacks

## Required Animation Categories

至少覆蓋 4 類：

1. Hero 動畫
2. 區塊進場動畫
3. 互動動畫（CTA/卡片/游標）
4. 背景層動畫

## Recommended Libraries

- GSAP: 時序控制、ScrollTrigger 類效果
- Anime.js: 輕量數值補間、SVG 路徑動畫
- Three.js: WebGL 粒子/幾何（可選）
- CSS Native: fallback 與低功耗模式

## Fallback Matrix

| Scenario | WebGL Layer | Hero Motion | Scroll Motion | Interaction Motion |
| --- | --- | --- | --- | --- |
| High capability | Three.js enabled | SVG + shader-like overlay | Stagger + parallax | Magnetic + beam + tilt |
| Mid capability | Optional | SVG-only | Stagger only | Tilt + subtle glow |
| Low capability | Disabled | Static gradient + tiny float | Fade-in only | Color/opacity transitions |
| prefers-reduced-motion | Disabled | Static hero | No scroll animation | No magnetic/tilt |

## Detection Rules

1. `prefers-reduced-motion: reduce` -> 強制最小動態
2. 無 WebGL context -> 停用 Three.js
3. `animation_level=low` -> 停用高刺激動畫
4. 行動裝置 -> 預設降低粒子密度與陰影層數

## Animation Manifest Schema

```json
{
  "animation_manifest": [
    {
      "id": "hero_webgl_particles",
      "category": "hero",
      "library": "three",
      "target": "#hero-canvas",
      "trigger": "on-load",
      "fallback": "svg-gradient-drift"
    }
  ]
}
```

## Guardrails

- 不可讓動畫壓過主訊息可讀性
- 不可因動畫導致 CTA 可點擊區域不穩定
- 不可使用無 fallback 的關鍵視覺特效
