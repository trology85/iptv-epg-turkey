import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import gzip
import os
import urllib3

# SSL uyarılarını kapat
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def create_xmltv():
    # 1. Günün dosyasını belirle (Örn: 19.json)
    today_day = datetime.now().strftime("%d").lstrip('0')
    url = f"https://www.turksatkablo.com.tr/userFiles/epg/{today_day}.json"
    
    print(f"📡 Veri çekiliyor: {url}")
    
    try:
        response = requests.get(url, verify=False, timeout=15)
        response.raise_for_status()
        data = response.json()

        # XML Kök Dizini
        root = ET.Element("tv")
        root.set("generator-info-name", "Turksat Scraper")

        for channel in data.get('k', []):
            chan_name = channel.get('n', 'Unknown')
            chan_id = chan_name.replace(" ", ".")
            
            # Kanal tanımı
            chan_elem = ET.SubElement(root, "channel", id=chan_id)
            ET.SubElement(chan_elem, "display-name").text = chan_name

            # Programlar
            for prog in channel.get('p', []):
                # Saat formatını düzenle (HHMMSS +0300)
                start_time = prog.get('c', '').replace(":", "") + "00 +0300"
                end_time = prog.get('d', '').replace(":", "") + "00 +0300"
                date_str = datetime.now().strftime('%Y%m%d')
                
                prog_elem = ET.SubElement(root, "programme", 
                                         start=f"{date_str}{start_time}",
                                         stop=f"{date_str}{end_time}",
                                         channel=chan_id)
                ET.SubElement(prog_elem, "title").text = prog.get('b', 'No Title')

        # XML Ağacını Oluştur (Hata buradaydı, 'tree' tanımlanmalı)
        tree = ET.ElementTree(root)
        
        # Klasör kontrolü (epg klasörü yoksa oluştur)
        os.makedirs("epg", exist_ok=True)
        
        xml_file = "epg/turksat_epg.xml"
        gz_file = "epg/turksat_epg.xml.gz"

        # XML dosyasına yaz
        tree.write(xml_file, encoding="utf-8", xml_declaration=True)
        print(f"✅ XML oluşturuldu: {xml_file}")

        # Gzip ile sıkıştır
        with open(xml_file, 'rb') as f_in:
            with gzip.open(gz_file, 'wb') as f_out:
                f_out.writelines(f_in)
        
        print(f"✅ GZ oluşturuldu: {gz_file}")

    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
        raise # GitHub Actions'ın hatayı görmesi için

if __name__ == "__main__":
    create_xmltv()
