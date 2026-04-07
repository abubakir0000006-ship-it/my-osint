import subprocess
import json
from fastapi import FastAPI, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import exifread
from geopy.geocoders import Nominatim

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/phone")
def phone_lookup(number: str = Query(..., description="+998xxxxxxxxx")):
    cmd = f"phoneinfoga scan -n {number} --json"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    try:
        data = json.loads(result.stdout)
    except:
        return {"error": "Не удалось распарсить", "raw": result.stdout, "number": number}
    
    accounts = {}
    if "results" in data and "googlesearch" in data["results"]:
        for item in data["results"]["googlesearch"].get("social_media", []):
            url = item.get("url", "")
            domain = url.split("//")[-1].split("/")[0].replace("www.", "")
            accounts[domain] = url
    return {"number": number, "accounts": accounts}

@app.post("/api/phish/create")
def create_phish():
    import random, string
    link = f"https://tg-premium-free.loca.lt?uid={''.join(random.choices(string.ascii_letters, k=8))}"
    return {"link": link}

@app.post("/api/image")
async def extract_gps(file: UploadFile = File(...)):
    contents = await file.read()
    with open("/tmp/upload.jpg", "wb") as f:
        f.write(contents)
    with open("/tmp/upload.jpg", "rb") as f:
        tags = exifread.process_file(f)
    lat = lon = None
    if "GPS GPSLatitude" in tags and "GPS GPSLongitude" in tags:
        lat = tags["GPS GPSLatitude"].values
        lon = tags["GPS GPSLongitude"].values
        lat = float(lat[0]) + float(lat[1])/60 + float(lat[2])/3600
        lon = float(lon[0]) + float(lon[1])/60 + float(lon[2])/3600
        if tags.get("GPS GPSLatitudeRef") and str(tags["GPS GPSLatitudeRef"]) == "S":
            lat = -lat
        if tags.get("GPS GPSLongitudeRef") and str(tags["GPS GPSLongitudeRef"]) == "W":
            lon = -lon
        return {"lat": lat, "lon": lon, "address": get_address(lat, lon)}
    return {"error": "No GPS data"}

def get_address(lat, lon):
    geolocator = Nominatim(user_agent="osint_tool")
    location = geolocator.reverse(f"{lat}, {lon}")
    return location.address if location else "Не найдено"
