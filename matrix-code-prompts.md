# POD Tシャツ用 画像生成プロンプト集 — Matrix Code / 日本モチーフ シリーズ

参照画像(緑のASCII/半角カタカナ文字で構成された顔、マトリックス風コードレイン)を技法のベースに、
日本的モチーフ(京都の街並み・日本庭園・サイバーパンク浮世絵・能面・鳥居)へ展開した5案。

共通技法：モノスペースのASCII文字＋半角カタカナで濃淡を作り、像を構成する「コードレイン・ポートレート」技法。
緑の燐光(phosphor green)、黒背景、CRT走査線、グロー。前シリーズ(design-concepts.md / image-prompts.md)との
視覚的連続性のため、各案に金継ぎ風の金のひび割れを一本通している。

---

## 1. 京都の街並み

```
Digital matrix code-rain portrait technique for a streetwear t-shirt graphic: a narrow Kyoto Gion backstreet at dusk, wooden machiya facades, hanging lanterns, and a distant five-story pagoda silhouette, the entire scene constructed from dense monospace ASCII and half-width katakana characters of varying size and brightness, forming light and shadow like a mosaic. Luminous phosphor green on pure black background, faint CRT scanline texture, soft glow bloom around denser character clusters. One thin hairline crack of warm gold light bleeds diagonally across the composition like a kintsugi seam merging with a circuit trace. Centered vertical composition, isolated on black background, flat print-ready graphic, transparent background acceptable for DTG, 4500x5400px, no legible text, no photorealism.
```
**Negative:** `photo, 3d render, readable text, watermark, blurry, low contrast`

---

## 2. 日本庭園(枯山水)

```
Digital matrix code-rain portrait technique for a streetwear t-shirt graphic: a minimalist karesansui zen rock garden — raked gravel spirals, three moss-covered stones, and a single pine bough — entirely constructed from dense monospace ASCII and half-width katakana characters of varying size and brightness, forming light and shadow like a mosaic. Luminous phosphor green on pure black background, faint CRT scanline texture, glow bloom concentrated along the raked gravel lines to suggest motion. A single thin gold kintsugi-crack of light runs through one stone, splitting it without fully breaking the composition. Centered square composition, isolated on black background, flat print-ready graphic, transparent background, DTG print-ready, 4500x5400px, no legible text, no photorealism.
```
**Negative:** `photo, 3d render, readable text, watermark, cluttered, oversaturated`

---

## 3. サイバーパンク浮世絵(神奈川沖浪裏)

```
Digital matrix code-rain portrait technique for a streetwear t-shirt graphic: a reinterpretation of Hokusai's Great Wave off Kanagawa, the cresting wave and distant Mount Fuji entirely constructed from dense monospace ASCII and half-width katakana characters of varying size and brightness, forming light and shadow like a mosaic. Luminous phosphor green on pure black background, faint CRT scanline texture, the wave's foam rendered as brighter clustered characters cascading downward like digital rain. A thin gold kintsugi-crack of light cuts across the wave's curl. Bold ukiyo-e woodblock framing and composition preserved, centered, isolated on black background, flat print-ready graphic, transparent background, DTG print-ready, 4500x5400px, no legible text, no photorealism.
```
**Negative:** `photo, 3d render, readable text, watermark, realistic ocean photo`

---

## 4. 能面(般若)— 「素顔と仮面」

```
Digital matrix code-rain portrait technique for a streetwear t-shirt graphic, closely echoing a code-rendered face: a traditional Japanese Noh mask (hannya style), entirely constructed from dense monospace ASCII and half-width katakana characters of varying size and brightness, forming light and shadow like a mosaic, with the mask's carved eye and mouth openings rendered as pure black negative space. Luminous phosphor green on pure black background, faint CRT scanline texture, soft glow bloom along the mask's brow ridge and horns. A single thin gold kintsugi-crack of light runs down one side of the mask like a hairline fracture across porcelain. Centered symmetrical composition, isolated on black background, flat print-ready graphic, transparent background, DTG print-ready, 4500x5400px, no legible text, no photorealism.
```
**Negative:** `photo, 3d render, readable text, watermark, asymmetrical distortion`

---

## 5. 伏見稲荷・鳥居のトンネル

```
Digital matrix code-rain portrait technique for a streetwear t-shirt graphic: a receding tunnel of vermillion torii gates (Fushimi Inari style), viewed in one-point perspective toward a distant point of light, entirely constructed from dense monospace ASCII and half-width katakana characters of varying size and brightness, forming light and shadow like a mosaic. Luminous phosphor green on pure black background, faint CRT scanline texture, the vanishing point rendered as a cluster of brighter, larger characters suggesting a portal. A single thin gold kintsugi-crack of light runs along the ground line beneath the gates. Centered one-point-perspective composition, isolated on black background, flat print-ready graphic, transparent background, DTG print-ready, 4500x5400px, no legible text, no photorealism.
```
**Negative:** `photo, 3d render, readable text, watermark, symmetrical torii row without depth`

---

## 補足メモ

- 色は緑がデフォルト。アンバーや白(旧型ターミナル風)にする場合は `phosphor green` を `phosphor amber` 等に差し替える
- 「金継ぎのひび」は前シリーズとの視覚的連続性のための共通糸。単体使用時は削っても成立する
- Midjourneyの場合、末尾に `--ar 4:5 --style raw --stylize 100` を付けると砂嵐感を保ちつつ印刷用コントラストが出やすい
