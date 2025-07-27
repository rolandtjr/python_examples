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
created_date = get_field(tick, jf.CREATED)
updated_date = get_field(tick, jf.UPDATED)
status = get_field(tick, jf.STATUS)
issuetype = get_field(tick, jf.ISSUETYPE)
project = get_field(tick, jf.PROJECT)
priority = get_field(tick, jf.PRIORITY)
print(f"{created_date=}", type(created_date))
print(f"{updated_date=}", type(updated_date))
print(f"{reporter=}", type(reporter))
print(f"{deployment_requirements=}", type(deployment_requirements))
print(f"{status=}", type(status))
print(f"{issuetype=}", type(issuetype))
print(f"{project=}", type(project))
print(f"{priority=}", type(priority))


update_fields = UpdateFields()
update_fields.add_field(jf.RELEASE_TRAIN, rt.GAMMA_TRAIN)
update_fields.add_field(
    jf.DEPLOYMENT_REQUIREMENTS, [dr.CODE_REVIEW_COMPLETED, dr.QA_SIGN_OFF]
)

tick.update(fields=update_fields.as_dict())

for name, value in tick.raw["fields"].items():
    console.print(f"[bold green]{name}[/bold green]: {value}")
