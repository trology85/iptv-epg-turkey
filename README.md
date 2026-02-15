# 🇹🇷 IPTV EPG Turkey

**Türk TV kanalları için ücretsiz EPG (Elektronik Program Rehberi) verisi**

Her gün otomatik olarak güncellenen, 7 günlük program rehberi.

---

## 📺 Desteklenen Kanallar

### Ulusal Kanallar
- **TRT Kanalları** (TRT1, TRT Haber, TRT Spor, vb.)
- **Ana Yayıncılar:** NOW, Kanal D, Star, ATV, Show TV, TV8, Kanal 7, Beyaz TV
- **Haber:** NTV, CNN Türk, Habertürk, Halk TV, Bloomberg HT, 360, Tele1
- **Eğlence:** A2, TV 8.5, TV2, TLC, Euro D, Show Max, Show Türk, Tivi 6
- **Spor:** Bein Sports (1-5), Bein Sports Haber, A Spor, Spor Smart, TiviBu Spor, HT Spor
- **Belgesel/Sinema:** DMAX, CNBC-E, BBC Earth, Discovery kanalları, TiviBu Sinema
- **Dizi/Film:** Movie Türk, Movie Classic, Dizi Premium, Dizi Smart Max

### Yabancı Kanallar
- **Almanya:** RTL, RTL Zwei, Pro7, Nitro HD, VOX HD, Sat1 Gold, ZDF HD
- **Fransa:** M6 HD, RTL 9
- **Yunanistan:** ERT 1-2-3, Alpha HD, Skai HD, Ant1 HD, Mega HD, Star HD, Mak TV HD

---

## 🚀 Kullanım

### Android (IPTV Player)

EPG URL'sini uygulamanıza ekleyin:

```
https://raw.githubusercontent.com/KULLANICI_ADINIZ/iptv-epg-turkey/main/epg/epg_turkey.xml
```

**Kotlin/Java Kod Örneği:**

```kotlin
val epgUrl = "https://raw.githubusercontent.com/KULLANICI_ADINIZ/iptv-epg-turkey/main/epg/epg_turkey.xml"

// EPG'yi indir ve parse et
lifecycleScope.launch {
    val epgData = withContext(Dispatchers.IO) {
        URL(epgUrl).readText()
    }
    // XML parse et ve kullan
}
```

### ExoPlayer ile EPG Entegrasyonu

```kotlin
// 1. EPG verilerini çek
suspend fun fetchEpg(): String = withContext(Dispatchers.IO) {
    URL(EPG_URL).readText()
}

// 2. Parse et (XmlPullParser veya kütüphane kullan)
fun parseEpg(xmlString: String): List<Programme> {
    // XMLTV formatını parse et
    // <programme start="..." stop="..." channel="...">
}

// 3. Aktif programı göster
fun getCurrentProgramme(channelId: String): Programme? {
    val now = System.currentTimeMillis()
    return epgList.find { 
        it.channelId == channelId && 
        it.startTime <= now && 
        it.endTime >= now 
    }
}
```

---

## 🔄 Güncelleme

EPG her gün **saat 03:00 UTC** (Türkiye saati 06:00) otomatik güncellenir.

Manuel güncelleme için:
1. GitHub repo'nuza gidin
2. **Actions** sekmesine tıklayın
3. **Update EPG Daily** workflow'unu seçin
4. **Run workflow** butonuna basın

---

## 📊 EPG Formatı (XMLTV)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<tv>
  <channel id="trt1">
    <display-name>TRT 1</display-name>
    <icon src="logo_url"/>
  </channel>
  
  <programme start="20260215180000 +0300" stop="20260215190000 +0300" channel="trt1">
    <title lang="tr">Ana Haber</title>
    <desc lang="tr">Günün önemli olayları...</desc>
    <category lang="tr">Haber</category>
  </programme>
</tv>
```

---

## 🛠️ Kurulum (Kendi Repo'nuz İçin)

### 1. Fork/Clone
```bash
git clone https://github.com/KULLANICI_ADINIZ/iptv-epg-turkey.git
cd iptv-epg-turkey
```

### 2. İlk Güncelleme
```bash
cd scripts
pip install requests
python update_epg.py
```

### 3. GitHub'a Push
```bash
git add .
git commit -m "İlk EPG verisi"
git push
```

### 4. GitHub Actions Aktif
- Repo'nuza gidin → **Settings** → **Actions** → **General**
- **Allow all actions** seçin
- Workflow otomatik çalışmaya başlayacak

---

## 📝 Notlar

- EPG verisi 7 gün (geçmiş 1 gün + gelecek 6 gün) içerir
- Veri kaynağı: [Globetvapp EPG](https://github.com/globetvapp/epg)
- Format: XMLTV standardı
- Kodlama: UTF-8
- Timezone: +0300 (Türkiye)

---

## 🤝 Katkıda Bulunma

Eksik kanal veya hata bildirimi için **Issues** açabilirsiniz.

---

## 📄 Lisans

Bu proje GPL-3.0 lisansı altında sunulmaktadır.

EPG verisi [Globetvapp](https://github.com/globetvapp/epg) projesinden sağlanmaktadır.

---

## ⭐ Destek

Projeyi beğendiyseniz yıldız vermeyi unutmayın! 🌟

**Son güncelleme:** $(date +'%Y-%m-%d')
