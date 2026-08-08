# POD Tシャツ用 画像生成プロンプト集(5案)

対応テーマ：統合失調症の母との断絶／負債／39年動けなかった時間／失敗の数々 ＋ それらを統合する再起の1枚。
design-concepts.md のコンセプト 03・04・05・07・09 に対応。

英語プロンプト。Midjourney / SDXL / DALL-E など主要な画像生成ツールにそのまま使える汎用形式。

---

## 1. 静寂のノイズ — 母との断絶(concept 03)

```
A minimalist Japanese sumi-e ink wash illustration for a streetwear t-shirt print, centered composition, isolated on a pure white background. A single faint human figure sits cross-legged, rendered only as a soft ink silhouette that dissolves into television static noise across the right half of the body. Thin concentric ripples of digital scanline glitch radiate outward in muted grey and pale vermillion, with subtle RGB chromatic aberration fringing at the noise edges. Faint torn washi-paper grain in the background. One small solid vermillion dot near the figure's mouth is the only sharp point of color, representing a voice that was never heard. 70% negative space. Flat graphic illustration, ink brushstroke style, wabi-sabi restraint, no text, no photorealism, transparent background, DTG print-ready, 4500x5400px.
```

**Negative:** `photo, 3d render, photorealistic, cluttered background, text, watermark, gradient mesh, neon saturation`

---

## 2. 金継ぎ負債 — 負債(concept 04)

```
Graphic illustration of a traditional Japanese ceramic bowl cross-section, shattered into angular fragments, rendered in bold black ink outline for streetwear apparel print, isolated on white background. The cracks are filled with thick metallic gold kintsugi seams, but partway along, the gold lines fracture into pixelated glitch blocks and RGB-split streaks in desaturated cyan and magenta. The bowl's silhouette leans slightly, as if under invisible weight. High-contrast black linework, flat vector shading, metallic gold as the only gradient element. Centered composition, transparent background, DTG print-ready, 4500x5400px, no text.
```

**Negative:** `photorealistic ceramic photo, 3d render, background scenery, drop shadow, text, watermark`

---

## 3. 39年の抜け殻 — 39年動けなかった時間(concept 05)

```
Detailed fine-line illustration of an empty cicada shell clinging to a thin branch, rendered in sumi-ink hatching for a streetwear t-shirt graphic, isolated on white background. The lower half of the shell is crisp and fully rendered; the upper half dissolves into scattered square glitch pixels drifting upward and to the right, fading toward transparency, as if the form is only now finally breaking free after decades. Muted sepia and dusty sage-green accents within the pixel fragments. Fine linework contrasted against blocky low-resolution pixel debris. Centered vertical composition with generous negative space above, suggesting ascension. Flat illustration, transparent background, DTG print-ready, 4500x5400px, no text, no photorealism.
```

**Negative:** `photo, 3d, colorful background, gradient sky, watermark, text`

---

## 4. 偽りの輝き — 失敗の数々(concept 07)

```
Bold streetwear graphic collage for a t-shirt print, isolated on white background. A fragmented barcode and torn QR-code pattern arranged vertically, interrupted by scattered dull gold-foil-textured glitch blocks and diagonal RGB-split streaks in desaturated magenta and cyan. Small torn paper receipt fragments with illegible printed numerals overlap like discarded flyers scattered across the composition. Overall impression: cheap shine that never holds together, a promise cracking apart mid-collapse. High-contrast flat vector illustration with one metallic gold spot-color layer, asymmetric centered composition, transparent background, DTG/screen-print-ready, 4500x5400px, no legible text, no photorealism.
```

**Negative:** `photo, real barcode scan, readable text, watermark, 3d render, soft gradient background`

---

## 5. 侘び寂び再起 — 統合と再生(concept 09、仕上げの1枚)

```
Minimalist Japanese ink illustration of broken pottery fragments suspended mid-air, slowly reassembling toward a central point, for a streetwear t-shirt graphic, isolated on white background. Each fragment carries a faint echo of the others in the series: one shard textured with faint scanline static, one seamed in cracked gold kintsugi lines, one etched with fine cicada-shell hatching, one carrying a torn barcode fragment — all unified by soft sumi-ink outlines and warm sepia fill. Trailing dust particles connect the fragments like a constellation converging into a single circular form echoing an enso, not yet closed. Restrained palette of ink black, warm sepia, and one gold accent. Centered composition, transparent background, DTG print-ready, 4500x5400px, no text, no photorealism, wabi-sabi minimalism meets glitch-core streetwear.
```

**Negative:** `photo, 3d, bright saturated colors, cluttered composition, text, watermark`

---

## 共通の技術メモ

- 背景は白 or 透過PNGで統一(印刷会社の入稿規定に合わせやすい)
- 解像度は4500×5400px目安(DTG印刷の実寸+余白を確保)
- Midjourneyの場合、末尾に `--ar 4:5 --style raw --stylize 50` を付けるとグラフィック然とした印刷向きの仕上がりになりやすい(過剰装飾を抑える)
- タグラインなどの英字コピーはAIに生成させず、別途ベクターソフトで配置する(AI生成テキストは文字化けしやすい)
