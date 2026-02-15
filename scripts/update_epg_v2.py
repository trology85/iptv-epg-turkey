#!/usr/bin/env python3
"""
IPTV EPG Turkey - ID Mapping ile EPG Güncelleme
M3U playlist'teki tvg-id değerlerine göre EPG kanallarını yeniden eşleştirir
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import sys
import re

# M3U tvg-id → EPG channel id eşleştirme tablosu
ID_MAPPING = {
    # Ulusal Kanallar
    "TRT1.tr": "TRT 1.tr",
    "ATV.tr": "ATV.tr",
    "KanalD.tr": "Kanal D.tr",
    "NOWTV.tr": "NOW.tr",
    "ShowTV.tr": "Show TV.tr",
    "BeyazTV.tr": "Beyaz TV.tr",
    "Kanal7.tr": "Kanal 7.tr",
    "TV8.tr": "TV 8.tr",
    "StarTV.tr": "Star TV.tr",
    "360TV.tr": "360.tr",
    "TV100.tr": "TV 100.tr",
    "TYTTurk.tr": "TYT Türk.tr",
    
    # Haber Kanalları
    "TRTHaber.tr": "TRT Haber.tr",
    "AHaber.tr": "a Haber.tr",
    "CNNTurk.tr": "CNN Turk.tr",
    "TGRTHaber.tr": "TGRT Haber.tr",
    "HaberturkTV.tr": "Haberturk.tr",
    "HaberGlobal.tr": "Haber Global.tr",
    "UlkeTV.tr": "Ulke TV.tr",
    "HalkTV.tr": "Halk TV.tr",
    "NTV.tr": "NTV.tr",
    "24TV.tr": "24.tr",
    "SozcuTV.tr": "Sozcu TV.tr",
    "EkolTV.tr": "Ekol TV.tr",
    "TVNET.tr": "TVNET.tr",
    "Tele1.tr": "TELE 1.tr",
    "AkitTV.tr": "Akit TV.tr",
    "BenguturkTV.tr": "Benguturk TV.tr",
    "UlusalKanal.tr": "Ulusal Kanal.tr",
    "TV5.tr": "TV 5.tr",
    "FlashHaberTV.tr": "Flash Haber.tr",
    "LiderHaber.tr": "Lider Haber.tr",
    "NeoHaber.tr": "Neo Haber.tr",
    
    # Yurt Dışı
    "TRTTurk.tr": "TRT Turk.tr",
    "TRTAvaz.tr": "TRT Avaz.tr",
    "ATVAvrupa.tr": "ATV Avrupa.tr",
    "EuroD.tr": "Euro D.tr",
    "TGRTEU.tr": "TGRT EU.tr",
    "ShowTurk.tr": "Show Turk.tr",
    "Kanal7Avrupa.tr": "Kanal 7 Avrupa.tr",
    "KanalAvrupa.tr": "Kanal Avrupa.tr",
    
    # Ekonomi
    "APara.tr": "A Para.tr",
    "BloombergHT.tr": "Bloomberg HT.tr",
    "Ekoturk.tr": "Ekoturk.tr",
    "CNBCE.tr": "CNBC-E.tr",
    
    # Spor
    "TRTSpor.tr": "TRT Spor.tr",
    "TRTSporYildiz.tr": "TRT Spor Yildiz.tr",
    "ASpor.tr": "A Spor.tr",
    "SportsTV.tr": "Sports TV.tr",
    "TivibuSpor1.tr": "Tivibu Spor 1.tr",
    "TivibuSpor2.tr": "Tivibu Spor 2.tr",
    "TivibuSpor3.tr": "Tivibu Spor 3.tr",
    "TivibuSpor4.tr": "Tivibu Spor 4.tr",
    "SSpor.tr": "S Sport.tr",
    "SSpor2.tr": "S Sport 2.tr",
    "FBTV.tr": "FB TV.tr",
    "GSTV.tr": "GS TV.tr",
    "TJKTV.tr": "TJK TV.tr",
    "TAY.tr": "TAY TV.tr",
    "EkolSports.tr": "Ekol Sports.tr",
    "HTSpor.tr": "HT Spor.tr",
    
    # Belgesel & Yaşam
    "TRTBelgesel.tr": "TRT Belgesel.tr",
    "TRTWorld.tr": "TRT World.tr",
    "DMAX.tr": "DMAX.tr",
    "TLC.tr": "TLC.tr",
    "DSTV.tr": "DSTV.tr",
    "TRT2.tr": "TRT 2.tr",
    "TV85.tr": "TV8.5.tr",
    "NationalGeographic.tr": "National Geographic.tr",
    "NatGeoWild.tr": "Nat Geo Wild.tr",
    "BBCEarth.tr": "BBC Earth.tr",
    "HistoryChannel.tr": "History Channel.tr",
    
    # Çocuk
    "TRTCocuk.tr": "TRT Cocuk.tr",
    "MinikaGo.tr": "Minika Go.tr",
    "MinikaCocuk.tr": "Minika Cocuk.tr",
    "CartoonNetwork.tr": "Cartoon Network.tr",
    "Nickelodeon.tr": "Nickelodeon.tr",
    "DisneyChannel.tr": "Disney Channel.tr",
    "TRT3.tr": "TRT 3.tr",
    "ZarokTV.tr": "Zarok TV.tr",
    "CizgiFilmTV.tr": "Cizgi Film TV.tr",
    "CocuklaraOzelTV.tr": "Cocuklara Ozel TV.tr",
    
    # Müzik
    "TRTMuzik.tr": "TRT Muzik.tr",
    "Number1TV.tr": "Number One TV.tr",
    "Number1Turk.tr": "Number 1 Turk.tr",
    "Number1Damar.tr": "Number 1 Damar.tr",
    "PowerTV.tr": "Power TV.tr",
    "PowerTurkTV.tr": "PowerTurk TV.tr",
    "DreamTurk.tr": "Dream Turk.tr",
    "MuzikTV.tr": "Muzik TV.tr",
    
    # Dizi & Sinema
    "DiziTV.tr": "Dizi TV.tr",
    "DiziMax.tr": "Dizi Max.tr",
    "ShowMax.tr": "Show Max.tr",
    "A2TV.tr": "a2.tr",
}

def fetch_epg_from_source(url):
    """EPG kaynağından veri çeker"""
    try:
        print(f"📡 EPG verisi çekiliyor: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"❌ Hata: {e}")
        return None

def remap_channel_ids(root):
    """EPG'deki kanal ID'lerini M3U tvg-id'leriyle eşleştirir"""
    print("🔄 Kanal ID'leri eşleştiriliyor...")
    
    # Ters mapping oluştur (EPG ID → M3U ID)
    reverse_mapping = {v: k for k, v in ID_MAPPING.items()}
    
    mapped_count = 0
    unmapped_channels = []
    
    # Kanalları yeniden eşleştir
    for channel in root.findall('channel'):
        old_id = channel.get('id', '')
        
        if old_id in reverse_mapping:
            new_id = reverse_mapping[old_id]
            channel.set('id', new_id)
            mapped_count += 1
        else:
            unmapped_channels.append(old_id)
    
    # Programları yeniden eşleştir
    for programme in root.findall('programme'):
        old_channel = programme.get('channel', '')
        
        if old_channel in reverse_mapping:
            new_channel = reverse_mapping[old_channel]
            programme.set('channel', new_channel)
    
    print(f"✅ {mapped_count} kanal eşleştirildi")
    
    if unmapped_channels:
        print(f"⚠️  {len(unmapped_channels)} kanal eşleşmedi (ilk 10):")
        for ch in unmapped_channels[:10]:
            print(f"   - {ch}")
    
    return root

def parse_and_filter_epg(xml_content, days=7):
    """EPG'yi parse eder ve tarih filtreleme yapar"""
    try:
        root = ET.fromstring(xml_content)
        
        # Geçmiş 3 gün ve gelecek 7 gün
        now = datetime.now()
        start_date_limit = now - timedelta(days=3)
        end_date_limit = now + timedelta(days=days)
        
        # Programme öğelerini filtrele
        programmes = root.findall('programme')
        filtered_count = 0
        
        for prog in programmes[:]:
            start_str = prog.get('start', '')
            if start_str:
                try:
                    start_date = datetime.strptime(start_str[:14], '%Y%m%d%H%M%S')
                    
                    if start_date < start_date_limit or start_date > end_date_limit:
                        root.remove(prog)
                        filtered_count += 1
                except:
                    pass
        
        print(f"✅ {len(programmes) - filtered_count} program kaldı, {filtered_count} program filtrelendi")
        print(f"📅 Tarih aralığı: {start_date_limit.strftime('%Y-%m-%d')} - {end_date_limit.strftime('%Y-%m-%d')}")
        return ET.tostring(root, encoding='unicode')
        
    except Exception as e:
        print(f"❌ Parse hatası: {e}")
        return None

def merge_epg_sources(sources):
    """Birden fazla EPG kaynağını birleştirir"""
    print("🔄 EPG kaynakları birleştiriliyor...")
    
    merged_root = None
    
    for idx, source_url in enumerate(sources):
        xml_content = fetch_epg_from_source(source_url)
        if not xml_content:
            continue
            
        try:
            root = ET.fromstring(xml_content)
            
            if merged_root is None:
                merged_root = root
                print(f"  ✓ Kaynak {idx+1}: Temel olarak alındı")
            else:
                for channel in root.findall('channel'):
                    merged_root.append(channel)
                
                for programme in root.findall('programme'):
                    merged_root.append(programme)
                    
                print(f"  ✓ Kaynak {idx+1}: Birleştirildi")
                
        except Exception as e:
            print(f"  ✗ Kaynak {idx+1}: Hata - {e}")
            continue
    
    return merged_root

def save_epg(root, output_path):
    """EPG'yi dosyaya kaydeder"""
    try:
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        tree = ET.ElementTree(root)
        with open(output_path, 'wb') as f:
            f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
            tree.write(f, encoding='utf-8', xml_declaration=False)
        
        print(f"✅ EPG kaydedildi: {output_path}")
        return True
    except Exception as e:
        print(f"❌ Kaydetme hatası: {e}")
        return False

def main():
    print("=" * 60)
    print("🇹🇷 IPTV EPG Turkey - ID Mapping ile Güncelleme")
    print("=" * 60)
    print(f"⏰ Zaman: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # EPG Kaynakları
    sources = [
        "https://raw.githubusercontent.com/globetvapp/epg/main/Turkey/turkey1.xml",
        "https://raw.githubusercontent.com/globetvapp/epg/main/Turkey/turkey2.xml",
        "https://raw.githubusercontent.com/globetvapp/epg/main/Turkey/turkey3.xml",
        "https://raw.githubusercontent.com/globetvapp/epg/main/Turkey/turkey4.xml",
    ]
    
    # EPG'leri birleştir
    merged_root = merge_epg_sources(sources)
    
    if merged_root is None:
        print("❌ EPG birleştirilemedi!")
        sys.exit(1)
    
    # ÖNCE Filtreleme (kanal ID'leri değişmeden)
    xml_str = ET.tostring(merged_root, encoding='unicode')
    filtered_xml = parse_and_filter_epg(xml_str, days=7)
    
    if not filtered_xml:
        print("❌ EPG filtrelemesi başarısız!")
        sys.exit(1)
    
    # SONRA Kanal ID'lerini yeniden eşleştir
    merged_root = ET.fromstring(filtered_xml)
    merged_root = remap_channel_ids(merged_root)
    
    # Kaydet
    output_path = "epg/epg_turkey.xml"
    
    if save_epg(merged_root, output_path):
        channels = len(merged_root.findall('channel'))
        programmes = len(merged_root.findall('programme'))
        
        print()
        print("=" * 60)
        print("📊 İstatistikler:")
        print(f"   Kanal sayısı: {channels}")
        print(f"   Program sayısı: {programmes}")
        print(f"   Eşleştirilen kanal: {len(ID_MAPPING)}")
        print("=" * 60)
        print("✅ Güncelleme tamamlandı!")
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
