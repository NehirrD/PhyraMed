# Sprint 2 — Görsel Tanıma Değerlendirmesi

## Veri seti

`poc/dataset/image_labels.json` — etiketli bitki fotoğrafları:

| Dosya | Beklenen |
|-------|----------|
| ginger.jpg | zencefil |
| mint.jpg | nane |
| turmeric.jpg | zerdeçal |

Yeni fotoğraf eklemek için:
1. Görseli `poc/sample/` altına koy
2. `image_labels.json`'a `expected_tr`, `aliases` ekle

## Değerlendirme

```powershell
python poc/image_eval.py              # Sprint 1 prompt
python poc/image_eval.py --prompt-v2  # iyileştirilmiş prompt
```

## Metrikler

| Metrik | Açıklama |
|--------|----------|
| **strict_accuracy** | Tam eşleşme (Türkçe ad yanıtta geçiyor) |
| **lenient_accuracy** | Tam + kısmi eşleşme (alias eşleşmesi) |

Rapor: `poc/reports/image_eval_v1.json` veya `image_eval_v2.json`

## Prompt ince ayarı (v2 → v3)

Sprint 3'te v3 prompt eklendi — zerdeçal/zencefil ayırım kuralları ve düşük güven fallback:

```powershell
python poc/image_eval.py --prompt-v3
python poc/image_test.py poc/sample/turmeric.jpg --json
```

v3 kuralları:
- Zerdeçal: turuncu-sarı kesit rengi
- Zencefil: daha açık sarı kesit
- Emin değilse `Güven: düşük` + `Bitki (TR): Belirsiz`

Görsel tanıma sonrası ürün eşleştirme: `vision.identify_and_lookup()`

## Sonraki adımlar

- [x] 10+ görselde %80+ strict accuracy hedefi (v2: %80)
- [x] Düşük güven durumunda "emin değilim" fallback (v3)
- [ ] Backend'den gelen kullanıcı fotoğraflarıyla veri setini büyüt
- [ ] v3 prompt ile yeniden değerlendirme raporu (`image_eval_v3.json`)
