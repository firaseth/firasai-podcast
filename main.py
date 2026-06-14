import schedule
import time
import os
import threading
import sys
import argparse
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

    # ── Fail-Safe Scheduled Wrappers ───────────────────────────────────────────

    def safe_run_weekly_workflow(self):
        try:
            self.run_weekly_workflow()
        except Exception as e:
            print(f"❌ Error in weekly workflow: {e}")

    def safe_check_responses(self):
        try:
            self.check_responses()
        except Exception as e:
            print(f"❌ Error checking guest responses: {e}")

    def safe_schedule_weekly_newsletter(self):
        try:
            self.marketer.schedule_weekly_newsletter()
            print("✅ Weekly newsletter scheduling completed successfully.")
        except Exception as e:
            print(f"❌ Error scheduling weekly newsletter: {e}")

    def safe_generate_weekly_report(self):
        try:
            report = self.analyst.generate_weekly_report()
            self.notion.create_report(report)
            print("✅ Weekly report generated and saved to Notion.")
        except Exception as e:
            print(f"❌ Error generating weekly report: {e}")

    # ── Scheduler ─────────────────────────────────────────────────────────────

    def start(self):
        """Start the agent with all scheduled tasks."""
        print("🤖 FirasAi Agent started — press Ctrl+C to stop")

        # Start health check server for cloud deployment
        threading.Thread(target=start_health_check_server, daemon=True).start()

        schedule.every().monday.at("09:00").do(self.safe_run_weekly_workflow)
        schedule.every().day.at("10:00").do(self.safe_check_responses)
        schedule.every().friday.at("17:00").do(
            self.safe_schedule_weekly_newsletter
        )
        schedule.every().sunday.at("20:00").do(
            self.safe_generate_weekly_report
        )

        while True:
            try:
                schedule.run_pending()
            except Exception as e:
                print(f"⚠️ Scheduler warning (will retry): {e}")
            time.sleep(60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🎙️ FirasAi - Autonomous AI Podcast Agent")
    parser.add_argument(
        "--scheduler",
        action="store_true",
        help="Start the background scheduler (default behavior if no arguments provided)"
    )
    parser.add_argument(
        "--create-episode",
        type=str,
        nargs="?",
        const="",
        help="Trigger the full episode creation pipeline on-demand. Optionally pass a specific topic."
    )
    parser.add_argument(
        "--weekly-workflow",
        action="store_true",
        help="Run the weekly workflow on-demand (generate ideas, weekly report, newsletter)"
    )
    parser.add_argument(
        "--check-responses",
        action="store_true",
        help="Check Notion for guest outreach responses on-demand"
    )

    args = parser.parse_args()

    agent = FirasAiAgent()

    # If no arguments are provided, or --scheduler is explicitly set, start scheduler
    if len(sys.argv) == 1 or args.scheduler:
        agent.start()
    else:
        if args.create_episode is not None:
            topic = args.create_episode if args.create_episode != "" else None
            try:
                agent.create_episode(topic=topic)
            except Exception as e:
                print(f"❌ Error during manual episode creation: {e}")
        
        if args.weekly_workflow:
            try:
                agent.run_weekly_workflow()
            except Exception as e:
                print(f"❌ Error during manual weekly workflow: {e}")
                
        if args.check_responses:
            try:
                agent.check_responses()
            except Exception as e:
                print(f"❌ Error during manual guest response check: {e}")
