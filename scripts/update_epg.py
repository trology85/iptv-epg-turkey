#!/usr/bin/env python3
"""
IPTV EPG Turkey - EPG Güncelleme Scripti
Globetvapp'den Türk kanalları EPG verilerini çeker ve birleştirir
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import sys

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

def parse_and_filter_epg(xml_content, days=7):
    """EPG'yi parse eder ve 7 günlük veriyi filtreler"""
    try:
        root = ET.fromstring(xml_content)
        
        # Şu anki zaman ve 7 gün sonrası
        now = datetime.now()
        end_date = now + timedelta(days=days)
        
        # Programme öğelerini filtrele
        programmes = root.findall('programme')
        filtered_count = 0
        
        for prog in programmes[:]:  # Liste kopyası üzerinde iterate et
            start_str = prog.get('start', '')
            if start_str:
                # XMLTV formatı: 20260215040000 +0300
                try:
                    start_date = datetime.strptime(start_str[:14], '%Y%m%d%H%M%S')
                    
                    # 7 günden eski programları sil
                    if start_date < now - timedelta(days=1) or start_date > end_date:
                        root.remove(prog)
                        filtered_count += 1
                except:
                    pass
        
        print(f"✅ {len(programmes) - filtered_count} program, {filtered_count} eski program filtrelendi")
        return ET.tostring(root, encoding='unicode')
        
    except Exception as e:
        print(f"❌ Parse hatası: {e}")
        return None

def merge_epg_sources(sources):
    """Birden fazla EPG kaynağını birleştirir"""
    print("🔄 EPG kaynakları birleştiriliyor...")
    
    # İlk kaynağı al
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
                # Kanalları ve programları ekle
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
        # XML declaration ekle
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
    print("🇹🇷 IPTV EPG Turkey - Güncelleme Başlıyor")
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
    
    # 7 günlük filtrele
    xml_str = ET.tostring(merged_root, encoding='unicode')
    filtered_xml = parse_and_filter_epg(xml_str, days=7)
    
    if not filtered_xml:
        print("❌ EPG filtrelemesi başarısız!")
        sys.exit(1)
    
    # Kaydet
    output_path = "epg/epg_turkey.xml"
    merged_root_filtered = ET.fromstring(filtered_xml)
    
    if save_epg(merged_root_filtered, output_path):
        # İstatistikler
        channels = len(merged_root_filtered.findall('channel'))
        programmes = len(merged_root_filtered.findall('programme'))
        
        print()
        print("=" * 60)
        print("📊 İstatistikler:")
        print(f"   Kanal sayısı: {channels}")
        print(f"   Program sayısı: {programmes}")
        print("=" * 60)
        print("✅ Güncelleme tamamlandı!")
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
