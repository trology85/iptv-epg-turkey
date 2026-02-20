import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import gzip
import os
import urllib3

# Güvenlik uyarılarını kapat
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_data(day_offset=0):
    # GitHub UTC kullandığı için Türkiye saatine (+3) göre hesaplıyoruz
    # Gece 00:00 - 03:00 arası dünün verisine takılmaması için önemli
    target_date = datetime.utcnow() + timedelta(hours=3) - timedelta(days=day_offset)
    
    # URL'deki gün formatı (Örn: 20)
    day_str = target_date.strftime("%d").lstrip('0')
    
    # Türksat'ın her gün değişen JSON adresi
    url = f"https://www.turksatkablo.com.tr/userUpload/EPG/{day_str}.json"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.turksatkablo.com.tr/yayin-akisi.aspx'
    }
    
    try:
        print(f"📡 Deneniyor: {url}")
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        if response.status_code == 200:
            return response.json(), target_date
        else:
            print(f"⚠️ Sunucu yanıtı: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
        return None, None

def create_xmltv():
    data = None
    actual_date = None
    
    # Gece geçişlerinde veya güncelleme gecikmelerinde boş kalmasın diye son 3 günü dene
    for offset in range(3):
        data, actual_date = fetch_data(offset)
        if data and 'k' in data:
            print(f"✅ Veri başarıyla çekildi ({actual_date.strftime('%d/%m/%Y')})")
            break

    if not data or 'k' not in data:
        print("❌ Geçerli EPG verisine ulaşılamadı!")
        return

    root = ET.Element("tv")
    root.set("generator-info-name", "Turksat Scraper Pro")

    for channel in data.get('k', []):
        chan_name = channel.get('n', 'Unknown')
        # Uygulama ID uyumu için boşlukları nokta yap (Kanal D -> Kanal.D)
        chan_id = chan_name.replace(" ", ".")
        
        chan_elem = ET.SubElement(root, "channel", id=chan_id)
        ET.SubElement(chan_elem, "display-name").text = chan_name

        for prog in channel.get('p', []):
            # Saat formatını XMLTV standartına getir
            start_time = prog.get('c', '').replace(":", "") + "00 +0300"
            end_time = prog.get('d', '').replace(":", "") + "00 +0300"
            date_prefix = actual_date.strftime('%Y%m%d')
            
            prog_elem = ET.SubElement(root, "programme", 
                                     start=f"{date_prefix}{start_time}",
                                     stop=f"{date_prefix}{end_time}",
                                     channel=chan_id)
            ET.SubElement(prog_elem, "title", lang="tr").text = prog.get('b', 'No Title')

    # Dosya kaydetme işlemleri
    os.makedirs("epg", exist_ok=True)
    tree = ET.ElementTree(root)
    xml_file = "epg/turksat_epg.xml"
    gz_file = "epg/turksat_epg.xml.gz"

    tree.write(xml_file, encoding="utf-8", xml_declaration=True)
    with open(xml_file, 'rb') as f_in:
        with gzip.open(gz_file, 'wb') as f_out:
            f_out.writelines(f_in)
    
    print(f"🚀 Türksat EPG Dosyası hazır: {gz_file}")

if __name__ == "__main__":
    create_xmltv()
