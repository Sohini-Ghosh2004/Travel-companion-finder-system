#!/usr/bin/python3

'''

'''


import requests
import mysql.connector
from os import getenv
from time import sleep
from dotenv import load_dotenv

load_dotenv()

class POIService:
    def __init__(self):
        self.radius = 10000  # meters
        self.limit = 150

    def _get_connection(self, retries = 5):
        host = getenv("DB_HOST")
        user = getenv("DB_USER")
        password = getenv("DB_PASSWD")
        database = getenv("DB")

        for attempt in range(1, retries + 1):
            try:
                conn = mysql.connector.connect(host = host, user = user, password = password, database = database)
                return conn
            except Exception as e:
                sleep(5)
        raise Exception("Cannot connect to Database after several retries")

    
    def _is_close(self, lat1, lon1, lat2, lon2, threshold = 0.001):
        return abs(lat1 - lat2) < threshold and abs(lon1 - lon2) < threshold

    
    def fetch_external_pois(self, lat, lon):

        def safe_get(url, params):
            try:
                res = requests.get(url, params=params, timeout=10)
                if res.status_code != 200:
                    return []
                return res.json()
            except:
                return []

        common_params = {
            "lat": lat,
            "lon": lon,
            "radius": self.radius,
            "limit": self.limit,
            "apikey": getenv("OPENTRIPMAP_KEY"),
            "format": "json"
        }

        # API 1: radius
        radius_data = safe_get(
            "https://api.opentripmap.com/0.1/en/places/radius",
            common_params
        )

        # API 2: autosuggest
        autosuggest_data = safe_get(
            "https://api.opentripmap.com/0.1/en/places/autosuggest",
            {**common_params, "name": "tourist"}
        )

        # merge + uniq by xid
        unique = {}

        for el in (radius_data or []) + (autosuggest_data or []):
            if not isinstance(el, dict):
                continue

            xid = el.get("xid")
            point = el.get("point", {})
            name = el.get("name")

            if not xid or not name:
                continue

            lat = point.get("lat")
            lon = point.get("lon")

            if lat is None or lon is None:
                continue

            if xid not in unique:
                unique[xid] = {
                    "name": name,
                    "lat": lat,
                    "lon": lon,
                    "category": el.get("kinds", ""),
                    "external_id": xid
                }

        return list(unique.values())[:self.limit]

    
    def upsert_pois(self, pois):
        conn = self._get_connection()
        cursor = conn.cursor()
        poi_ids = []
        
        for poi in pois:
            try:
                cursor.execute("""
                    INSERT INTO poi (poi_name, latitude, longitude, category, external_id)
                    VALUES (%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE poi_id=LAST_INSERT_ID(poi_id)
                """, (
                    poi["name"],
                    poi["lat"],
                    poi["lon"],
                    poi["category"],
                    poi["external_id"]
                ))
                poi_ids.append(cursor.lastrowid)
            
            except Exception as e:
                continue
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return poi_ids

    
    def get_or_create_pois(self, lat, lon):
        pois = self.fetch_external_pois(lat, lon)
        
        if not pois:
            return []
        
        return self.upsert_pois(pois)