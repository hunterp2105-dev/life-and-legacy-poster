import requests
import time

BASE_URL = "https://backend.blotato.com/v2"


class BlotatoClient:
    def __init__(self, api_key: str):
        self.headers = {
            "blotato-api-key": api_key,
            "Content-Type": "application/json",
        }

    def create_visual(self, template_id: str, prompt: str, title: str = "") -> str:
        payload = {
            "templateId": template_id,
            "prompt": prompt,
            "inputs": {},
            "title": title,
            "useBrandKit": True,
        }
        resp = requests.post(f"{BASE_URL}/videos/from-templates", json=payload, headers=self.headers)
        resp.raise_for_status()
        return resp.json()["item"]["id"]

    def poll_visual(self, creation_id: str, max_wait: int = 360, interval: int = 6) -> dict:
        elapsed = 0
        while elapsed < max_wait:
            time.sleep(interval)
            elapsed += interval
            resp = requests.get(f"{BASE_URL}/videos/creations/{creation_id}", headers=self.headers)
            resp.raise_for_status()
            item = resp.json()["item"]
            status = item["status"]
            if status == "done":
                url = (item.get("imageUrls") or [None])[0] or item.get("mediaUrl")
                return {"status": "done", "url": url}
            if status == "creation-from-template-failed":
                return {"status": "failed", "url": None}
        return {"status": "timeout", "url": None}

    def upload_media(self, url: str) -> str:
        resp = requests.post(f"{BASE_URL}/media", json={"url": url}, headers=self.headers)
        resp.raise_for_status()
        return resp.json()["url"]

    def publish_post(self, account_id: str, platform: str, text: str,
                     media_url: str, scheduled_time: str = None) -> str:
        if platform == "tiktok":
            target = {
                "targetType": "tiktok",
                "privacyLevel": "PUBLIC_TO_EVERYONE",
                "disabledComments": False,
                "disabledDuet": False,
                "disabledStitch": False,
                "isBrandedContent": False,
                "isYourBrand": False,
                "isAiGenerated": True,
                "autoAddMusic": True,
            }
        else:
            target = {"targetType": platform}

        payload = {
            "post": {
                "accountId": account_id,
                "content": {"text": text, "mediaUrls": [media_url], "platform": platform},
                "target": target,
            }
        }
        if scheduled_time:
            payload["scheduledTime"] = scheduled_time

        resp = requests.post(f"{BASE_URL}/posts", json=payload, headers=self.headers)
        resp.raise_for_status()
        return resp.json()["postSubmissionId"]

    def check_connection(self) -> bool:
        try:
            resp = requests.get(f"{BASE_URL}/videos/templates", headers=self.headers, timeout=5)
            return resp.status_code == 200
        except Exception:
            return False
