import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import gzip
import os

def create_xmltv():
    # Günün dosyasını belirle
    today_day = datetime.now().strftime("%d").lstrip('0')
    url = f"https://www.turksatkablo.com.tr/userFiles/epg/{today_day}.json"
    
    response = requests.get(url, verify=False)
    data = response.json()

    # XML Yapısını Oluştur
    root = ET.Element("tv")
    root.set("generator-info-name", "Turksat Scraper")

    for channel in data.get('k', []):
        chan_id = channel.get('n').replace(" ", ".")
        # Kanal tanımı
        chan_elem = ET.SubElement(root, "channel", id=chan_id)
        ET.SubElement(chan_elem, "display-name").text = channel.get('n')

        # Programlar
        for prog in channel.get('p', []):
            start_time = prog.get('c').replace(":", "") + "00 +0300" # Örn: 090000 +0300
            end_time = prog.get('d').replace(":", "") + "00 +0300"
            
            prog_elem = ET.SubElement(root, "programme", 
                                     start=f"{datetime.now().strftime('%Y%m%d')}{start_time}",
                                     stop=f"{datetime.now().strftime('%Y%m%d')}{end_time}",
                                     channel=chan_id)
            ET.SubElement(prog_elem, "title").text = prog.get('b')

    # XML'i kaydet ve sıkıştır
    tree = ET.ElementTree(root)
    # scraper.py içindeki dosya yolları:
xml_file = "epg/turksat_epg.xml"
gz_file = "epg/turksat_epg.xml.gz"

# Kaydetme kısmında bu değişkenleri kullan:
tree.write(xml_file, encoding="utf-8", xml_declaration=True)
with open(xml_file, 'rb') as f_in:
    with gzip.open(gz_file, 'wb') as f_out:
        f_out.writelines(f_in)
    
    print("✅ xml.gz dosyası oluşturuldu.")

if __name__ == "__main__":
    create_xmltv()
