import yaml
from datetime import datetime
from typing import List, Dict, Any


class PMAgent:
    """
    The Project Manager Agent for Fulcrum.
    Orchestrates tasks, enforces quality, and reports progress.
    """

    def __init__(self, config_path: str = "project_config.yaml"):
        """
        Initializes the agent by loading the project's source of truth.
        """
        self.config_path = config_path
        self.config = self._load_config()
        print("PM Agent Initialized. State loaded from project_config.yaml.")

    def _load_config(self) -> dict:
        """Loads the YAML configuration file."""
        with open(self.config_path, "r") as f:
            return yaml.safe_load(f)

    def get_sprint_goal(self) -> str:
        """Retrieves the goal for the current sprint."""
        return self.config["current_sprint"]["goal"]

    def get_tasks_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Utility to filter tasks by their status."""
        all_tasks = self.config.get("current_sprint", {}).get("tasks", [])
        return [task for task in all_tasks if task.get("status") == status]

    def generate_daily_digest(self) -> str:
        """Generates the morning startup checklist and daily briefing."""

        sprint_goal = self.get_sprint_goal()
        in_progress_tasks = self.get_tasks_by_status("in_progress")
        todo_tasks = self.get_tasks_by_status("todo")

        # Simple prioritization: P0 tasks first, then P1, etc.
        recommended_focus = sorted(
            [t for t in todo_tasks if t["priority"] in ["P0", "P1"]],
            key=lambda x: x["priority"],
        )

        digest = f"""
🌅 **Good morning! Daily Update for {datetime.now().strftime('%Y-%m-%d')}**

**✅ 1. SYSTEMS CHECK & STARTUP:**
Before you begin, ensure your environment is running:
- **[ ] Backend DB:** `docker compose up -d`
- **[ ] Frontend Server:** `npm run dev` (in a separate 'frontend' terminal)

**🎯 2. TODAY'S SPRINT GOAL:**
{sprint_goal}

**🏃 3. RECOMMENDED FOCUS:**
"""
        if recommended_focus:
            for task in recommended_focus[:3]:  # Show top 3 priorities
                digest += f"- **[{task['id']}] {task['title']}** (Priority: {task['priority']})\n"
        else:
            digest += "- All high-priority tasks are in progress. Continue with current tasks.\n"

        digest += f"""
**📊 4. CURRENT STATUS:**
- **In Progress:** {len(in_progress_tasks)} tasks
- **Todo:** {len(todo_tasks)} tasks
"""
        return digest

    def generate_eod_summary(self) -> str:
        """Generates the end-of-day summary and shutdown checklist."""

        sprint_goal = self.get_sprint_goal()  # noqa: F841
        completed_tasks_today = []  # Placeholder # noqa: F841
        in_progress_tasks = self.get_tasks_by_status("in_progress")

        summary = f"""
📊 **End of Day Summary - {datetime.now().strftime('%Y-%m-%d')}**

**✅ 1. ACCOMPLISHMENTS (Manual Update for now):**
- Review today's completed tasks and update their status in `project_config.yaml` to 'done'.

**🏃 2. STILL IN PROGRESS:**
"""
        if in_progress_tasks:
            for task in in_progress_tasks:
                summary += f"- [{task['id']}] {task['title']}\n"
        else:
            summary += "- No tasks currently in progress.\n"

        summary += """
**🎯 3. TOMORROW'S PLAN:**
- Continue with the recommended focus from the morning briefing.

**🛑 4. SHUTDOWN CHECKLIST:**
To free up system resources, run these commands:
- **[ ] Stop Backend DB:** `docker compose down`
- **[ ] Stop Frontend Server:** `Ctrl+C` (in the npm terminal)
"""
        return summary


if __name__ == "__main__":
    agent = PMAgent()
    daily_report = agent.generate_daily_digest()
    print("\n--- PM AGENT DAILY DIGEST ---")
    print(daily_report)
    print("-----------------------------\n")
