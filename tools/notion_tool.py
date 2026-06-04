import requests


class NotionTool:
    BASE_URL = "https://api.notion.com/v1"

    def __init__(self, config):
        self.config = config
        self.headers = {
            "Authorization": f"Bearer {config.NOTION_API_KEY}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        }

    # ── Episodes ───────────────────────────────────────────────────────────────

    def create_episode(self, data: dict) -> str:
        """Create a new episode page in Notion and return its page ID."""
        payload = {
            "parent": {"database_id": self.config.NOTION_EPISODES_DB},
            "properties": {
                "Title": {"title": [{"text": {"content": data["title"]}}]},
                "Status": {"select": {"name": data.get("status", "💡 Idea")}},
                "Script": {
                    "rich_text": [
                        {"text": {"content": data.get("script", "")[:2000]}}
                    ]
                },
            },
        }
        response = requests.post(
            f"{self.BASE_URL}/pages", headers=self.headers, json=payload
        )
        response.raise_for_status()
        return response.json().get("id", "")

    def create_episode_idea(self, idea: dict) -> str:
        return self.create_episode({
            "title": idea.get("title", "Untitled Idea"),
            "status": "💡 Idea",
        })

    def get_episode(self, episode_id: str) -> dict:
        response = requests.get(
            f"{self.BASE_URL}/pages/{episode_id}", headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def update_episode(self, episode_id: str, data: dict) -> dict:
        properties = {}
        if "status" in data:
            properties["Status"] = {"select": {"name": data["status"]}}
        if "title" in data:
            properties["Title"] = {
                "title": [{"text": {"content": data["title"]}}]
            }

        response = requests.patch(
            f"{self.BASE_URL}/pages/{episode_id}",
            headers=self.headers,
            json={"properties": properties},
        )
        response.raise_for_status()
        return response.json()

    # ── Guests ─────────────────────────────────────────────────────────────────

    def check_guest_responses(self) -> dict:
        response = requests.post(
            f"{self.BASE_URL}/databases/{self.config.NOTION_GUESTS_DB}/query",
            headers=self.headers,
        )
        response.raise_for_status()
        return response.json()

    def update_guest_status(self, guest: dict) -> dict:
        """Update a guest record's status. Override with specific logic as needed."""
        page_id = guest.get("id", "")
        if not page_id:
            return {}
        return self.update_episode(page_id, {"status": "✅ Confirmed"})

    # ── Reports ────────────────────────────────────────────────────────────────

    def create_report(self, report: dict) -> str:
        """Save a weekly analytics report to Notion (uses Episodes DB by default)."""
        return self.create_episode({
            "title": f"Weekly Report — {report.get('week', 'Latest')}",
            "status": "📊 Report",
            "script": str(report),
        })
