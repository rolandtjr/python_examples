from jira import JIRA
from rich.console import Console

from fields import JiraFields as jf
from fields import DeploymentRequirements as dr
from fields import ReleaseTrain as rt
from fields import UpdateFields, get_field
from jql_utils import load_config


config = load_config()
console = Console(color_system="truecolor")
jira = JIRA(server=config["server"], basic_auth=(config["username"], config["token"]))


tick = jira.issue("AETHER-1")

deployment_requirements = get_field(tick, jf.DEPLOYMENT_REQUIREMENTS)
reporter = get_field(tick, jf.REPORTER)

update_fields = UpdateFields()
update_fields.add_field(jf.RELEASE_TRAIN, rt.GAMMA_TRAIN)
update_fields.add_field(
    jf.DEPLOYMENT_REQUIREMENTS, [dr.CODE_REVIEW_COMPLETED, dr.QA_SIGN_OFF]
)

tick.update(fields=update_fields.as_dict())

for name, value in tick.raw["fields"].items():
    console.print(f"[bold green]{name}[/bold green]: {value}")
