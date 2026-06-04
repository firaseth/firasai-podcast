import schedule
import time
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from config import Config
from agents.planner import PlannerAgent
from agents.researcher import ResearcherAgent
from agents.scriptwriter import ScriptwriterAgent
from agents.editor import EditorAgent
from agents.marketer import MarketerAgent
from agents.analyst import AnalystAgent
from tools.notion_tool import NotionTool
from tools.audio_tool import AudioTool


class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status": "healthy", "agent": "FirasAi"}')


def start_health_check_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    print(f"🏥 Health check server listening on port {port}")
    server.serve_forever()



class FirasAiAgent:
    def __init__(self):
        self.config = Config()
        self.planner = PlannerAgent(self.config)
        self.researcher = ResearcherAgent(self.config)
        self.scriptwriter = ScriptwriterAgent(self.config)
        self.editor = EditorAgent(self.config)
        self.marketer = MarketerAgent(self.config)
        self.analyst = AnalystAgent(self.config)
        self.notion = NotionTool(self.config)
        self.audio = AudioTool(self.config)
        print("🎙️ FirasAi Agent initialized")

    # ── Core pipeline ──────────────────────────────────────────────────────────

    def create_episode(self, topic: str | None = None) -> str:
        """Full episode creation pipeline: topic → research → script → Notion."""
        print("🎙️ Starting FirasAi episode creation...")

        if not topic:
            topic_dict = self.planner.suggest_topic()
            topic = topic_dict.get("title") or topic_dict.get("topic") or str(topic_dict)
            print(f"💡 Suggested topic: {topic}")

        research = self.researcher.research_topic(topic)
        print("🔍 Research complete")

        script = self.scriptwriter.write_script(topic, research)
        print(f"📝 Script written: {script['word_count']} words")

        episode_id = self.notion.create_episode({
            "title": script["title"],
            "status": "Scripted",
            "script": script["content"],
            "research": research,
            "show_notes": script["show_notes"],
        })
        print(f"💾 Saved to Notion: {episode_id}")
        return episode_id

    # ── Scheduled workflows ────────────────────────────────────────────────────

    def run_weekly_workflow(self):
        """Automated weekly tasks: generate ideas, build report, queue newsletter."""
        print("📅 Running FirasAi weekly workflow...")

        ideas = self.planner.generate_weekly_ideas(count=5)
        for idea in ideas.get("ideas", []):
            self.notion.create_episode_idea(idea)

        report = self.analyst.generate_weekly_report()
        self.notion.create_report(report)

        self.marketer.schedule_weekly_newsletter()
        print("✅ Weekly workflow complete")

    def check_responses(self):
        """Check Notion for guest outreach responses and update statuses."""
        print("📧 Checking guest responses...")
        responses = self.notion.check_guest_responses()
        for response in responses.get("results", []):
            self.notion.update_guest_status(response)

    # ── Scheduler ─────────────────────────────────────────────────────────────

    def start(self):
        """Start the agent with all scheduled tasks."""
        print("🤖 FirasAi Agent started — press Ctrl+C to stop")

        # Start health check server for cloud deployment
        threading.Thread(target=start_health_check_server, daemon=True).start()

        schedule.every().monday.at("09:00").do(self.run_weekly_workflow)
        schedule.every().day.at("10:00").do(self.check_responses)
        schedule.every().friday.at("17:00").do(
            self.marketer.schedule_weekly_newsletter
        )
        schedule.every().sunday.at("20:00").do(
            self.analyst.generate_weekly_report
        )

        while True:
            schedule.run_pending()
            time.sleep(60)


if __name__ == "__main__":
    agent = FirasAiAgent()
    agent.start()
