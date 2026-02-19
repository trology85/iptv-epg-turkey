import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import gzip
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_data(day_offset=0):
    """Belirlenen gün ofsetine göre veri çekmeyi dener."""
    target_date = datetime.now() - timedelta(days=day_offset)
    day_str = target_date.strftime("%d").lstrip('0')
    url = f"https://www.turksatkablo.com.tr/userFiles/epg/{day_str}.json"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        print(f"📡 Deneniyor: {url}")
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        if response.status_code == 200:
            return response.json(), target_date
        return None, None
    except:
        return None, None

def create_xmltv():
    # Önce bugünü, olmazsa dünü dene
    data, actual_date = fetch_data(0)
    if not data:
        print("⚠️ Bugünün verisi bulunamadı, dünün verisi deneniyor...")
        data, actual_date = fetch_data(1)

    if not data:
        print("❌ Hiçbir veri kaynağına ulaşılamadı!")
        return

    root = ET.Element("tv")
    root.set("generator-info-name", "Turksat Scraper")

    for channel in data.get('k', []):
        chan_name = channel.get('n', 'Unknown')
        chan_id = chan_name.replace(" ", ".")
        
        chan_elem = ET.SubElement(root, "channel", id=chan_id)
        ET.SubElement(chan_elem, "display-name").text = chan_name

        for prog in channel.get('p', []):
            # JSON'daki saatleri XMLTV formatına çevir
            start_time = prog.get('c', '').replace(":", "") + "00 +0300"
            end_time = prog.get('d', '').replace(":", "") + "00 +0300"
            date_prefix = actual_date.strftime('%Y%m%d')
            
            prog_elem = ET.SubElement(root, "programme", 
                                     start=f"{date_prefix}{start_time}",
                                     stop=f"{date_prefix}{end_time}",
                                     channel=chan_id)
            ET.SubElement(prog_elem, "title").text = prog.get('b', 'No Title')

    # Dosya işlemleri
    os.makedirs("epg", exist_ok=True)
    tree = ET.ElementTree(root)
    xml_file = "epg/turksat_epg.xml"
    gz_file = "epg/turksat_epg.xml.gz"

    tree.write(xml_file, encoding="utf-8", xml_declaration=True)
    with open(xml_file, 'rb') as f_in:
        with gzip.open(gz_file, 'wb') as f_out:
            f_out.writelines(f_in)
    
    print(f"✅ İşlem tamamlandı: {gz_file}")

if __name__ == "__main__":
    create_xmltv()
