from jira import JIRA
from rich.console import Console

from jql_utils import JQLPrompt, load_config

config = load_config()
console = Console(color_system="truecolor")
jira = JIRA(server=config["server"], basic_auth=(config["username"], config["token"]))
jql_prompt = JQLPrompt(jira)

issues = jql_prompt.prompt()

console.print("[ℹ] Getting more issues... 🚀", style="#A3BE8C bold")

more_issues = jql_prompt.multi_prompt()

if issues or more_issues:
    console.print("[ℹ] Saving logs... 🚀", style="#A3BE8C bold")
    jql_prompt.save_log()

console.print("Exiting... 🚀", style="bold green")