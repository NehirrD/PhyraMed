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

## Prompt ince ayarı (v2)

Sprint 1 serbest metin yerine yapılandırılmış format istenir:

```
Bitki (TR): zencefil
Bitki (EN): ginger
Güven: yüksek
Kısa not: ...
```

Bu format parse edilebilirliği artırır; Sprint 3'te backend'e entegre edilebilir.

### Qwen thinking modu

`qwen/qwen3.6-27b` varsayılan olarak dahili "thinking" blokları üretebilir. `groq_client.vision_completion()` içinde `reasoning_effort: none` ile kapatılır. Eski yanıtlarda thinking içeriği `extract_model_text()` ile ayıklanır.

Değerlendirme, önce `Bitki (TR):` satırına bakarak tam eşleşme sayar; yalnızca not/metin içinde geçen alias'lar kısmi eşleşme sayılır.

## Sonraki adımlar

- [ ] Backend'den gelen kullanıcı fotoğraflarıyla veri setini büyüt
- [ ] 10+ görselde %80+ strict accuracy hedefi
- [ ] Düşük güven durumunda "emin değilim" fallback
