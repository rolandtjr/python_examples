"""
Jira Field Utilities for CLI-based Issue Updates.

This module provides a clean abstraction for working with Jira issue fields
in a CLI or automation context. It hides the complexity of Jira's API field
IDs (e.g. "customfield_10302") and automatically formats values according
to the field's type, allowing developers to reference fields by friendly
names instead of raw Jira IDs.

Key Components:
    - FieldType: Enum describing how each Jira field type (e.g. single select,
      multi select, user picker) must be structured for API updates.
    - JiraFields: Developer-friendly enum for referencing Jira fields by
      logical names (e.g. RELEASE_TRAIN) instead of raw custom field IDs.
    - JiraFieldInfo: Dataclass tying together a Jira field's API ID and its
      FieldType, along with an appropriate formatter.
    - FIELD_REGISTRY: The single source of truth mapping JiraFields to their
      JiraFieldInfo, used to build correctly formatted update payloads.
    - UpdateFields: A builder class for collecting field changes and generating
      a payload dictionary ready to pass into jira.issue.update(fields=...).

Usage Example:
    >>> update_fields = UpdateFields()
    >>> update_fields.add_field(JiraFields.RELEASE_TRAIN, "Beta Train")
    >>> update_fields.add_field(JiraFields.REPORTER, "jdoe")
    >>> jira.issue("AETHER-1").update(fields=update_fields.as_dict())

Notes:
    - Currently defaults to Jira Server/DC formatting for user fields
      ({"name": ...}). Jira Cloud users can easily switch to {"accountId": ...}
      by swapping the formatter for FieldType.USER.
    - FIELD_REGISTRY is the single source of truth for all Jira field mappings.
      To add new fields (e.g. cascading select or date fields), simply register
      them here with their appropriate type and formatter.

This design centralizes all field formatting rules and mappings, making Jira
updates cleaner, safer, and easier to maintain.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable

from jira import Issue
from jira.resources import CustomFieldOption, User


class DeploymentRequirements(Enum):
    """Checklist of deployment requirements for the Jira 'Deployment Requirements' multi-select field."""
    CODE_REVIEW_COMPLETED = "Code Review Completed"
    UNIT_TESTS_PASSED = "Unit Tests Passed"
    QA_SIGN_OFF = "QA Sign-off"
    DOCUMENTATION_UPDATED = "Documentation Updated"
    SECURITY_SCAN_APPROVED = "Security Scan Approved"
    CHANGE_MANAGEMENT_TICKET_LINKED = "Change Management Ticket Linked"


class ReleaseTrain(Enum):
    """Valid release train options for the Jira 'Release Train' single-select field."""
    ALPHA_TRAIN = "Alpha Train"
    BETA_TRAIN = "Beta Train"
    GAMMA_TRAIN = "Gamma Train"
    STABLE_TRAIN = "Stable Train"

    def __str__(self):
        return self.value


class FieldType(Enum):
    """
    Enumeration of supported Jira field types used by UpdateFields.

    Each value represents how data for that field type should be structured
    when sent to the Jira API. The value is paired with a formatter function
    in FIELD_FORMATTERS to handle the conversion.

    Members:
        TEXT: A simple text or raw value (string, number, etc.) sent as-is.
        SINGLE_SELECT: A single-choice select list, formatted as {"value": "..."}.
        MULTI_SELECT: A multi-choice select list, formatted as [{"value": "..."}, ...].
        USER: A user picker field, typically formatted as {"name": "..."} on Server/DC,
              or {"accountId": "..."} on Jira Cloud.
        GROUP: A group picker field, formatted as {"name": "..."}.
        DATE: A date field, expected in ISO-8601 string format (e.g., "2025-07-26").
        LABELS: A label field, sent as a list of strings.
    """
    TEXT = "text"
    SINGLE_SELECT = "single_select"
    MULTI_SELECT = "multi_select"
    USER = "user"
    GROUP = "group"
    DATE = "date"
    LABELS = "labels"

def single_select_formatter(value: Any):
    if isinstance(value, Enum):
        return {"value": value.value}
    return {"value": value}

def multi_select_formatter(values: Any):
    if all(isinstance(v, Enum) for v in values):
        return [{"value": v.value} for v in values]
    return [{"value": value} for value in (values if isinstance(values, list) else [values])]

def user_formatter(value: Any):
    return {"name": value}

def labels_formatter(value: Any):
    return value if isinstance(value, list) else [value]


FIELD_FORMATTERS = {
    FieldType.TEXT: lambda v: v,
    FieldType.SINGLE_SELECT: single_select_formatter,
    FieldType.MULTI_SELECT: multi_select_formatter,
    FieldType.USER: user_formatter,
    FieldType.GROUP: user_formatter,   # same shape as USER on Server/DC
    FieldType.DATE: lambda v: v,       # could later enforce ISO 8601
    FieldType.LABELS: labels_formatter,
}


def get_single_select_formatter(value: CustomFieldOption) -> str:
    if not isinstance(value, CustomFieldOption):
        raise ValueError(f"Expected CustomFieldOption, got {type(value)}")
    return value.value


def get_multi_select_formatter(values: list[CustomFieldOption]) -> list[str]:
    if not isinstance(values, list):
        raise ValueError(f"Expected list of CustomFieldOption, got {type(values)}")
    if not all(isinstance(v, CustomFieldOption) for v in values):
        raise ValueError("All items in the list must be CustomFieldOption instances")
    return [get_single_select_formatter(v) for v in values]


def get_user_formatter(user: User) -> dict:
    if not isinstance(user, User):
        raise ValueError(f"Expected User, got {type(user)}")
    return user.name


GET_FIELD_FORMATTERS = {
    FieldType.TEXT: lambda v: v,
    FieldType.SINGLE_SELECT: get_single_select_formatter,
    FieldType.MULTI_SELECT: get_multi_select_formatter,
    FieldType.USER: get_user_formatter,
    FieldType.LABELS: lambda v: v,
}


class JiraFields(Enum):
    """
    Enumeration of high-level Jira field names used in the CLI.

    This enum provides developer-friendly identifiers for Jira fields,
    hiding Jira's internal custom field IDs (e.g. "customfield_10302").

    Members:
        REPORTER: The user who created or is assigned responsibility for the issue.
        RELEASE_TRAIN: A single-select custom field for specifying the release train.
        DEPLOYMENT_REQUIREMENTS: A multi-select custom field for deployment prerequisites.

    Notes:
        JiraFields values are mapped to Jira API field IDs and types
        through the FIELD_REGISTRY, which is the single source of truth
        for how each field is formatted and sent to Jira.
    """
    REPORTER = "reporter"
    RELEASE_TRAIN = "release_train"
    DEPLOYMENT_REQUIREMENTS = "deployment_requirements"

    def __str__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other
        return super().__eq__(other)

    def __hash__(self):
        return hash((self.name, self.value))


@dataclass
class JiraFieldInfo:
    """
    Metadata container for a Jira field.

    Each JiraFieldInfo instance holds the information needed to
    correctly serialize a Jira field for API updates.

    Attributes:
        field_id (str): The Jira API identifier for the field
            (e.g. "customfield_10302" or "reporter").
        field_type (FieldType): The type of field, which determines
            how its value should be formatted.

    Properties:
        formatter (Callable[[Any], Any]): Returns the correct formatter
            function for the field_type, so values are automatically
            wrapped or structured as required by the Jira API.

    Usage:
        >>> FIELD_REGISTRY[JiraFields.RELEASE_TRAIN].formatter("Beta Train")
        {"value": "Beta Train"}
    """
    field_id: str
    field_type: FieldType

    @property
    def formatter(self) -> Callable[[Any], Any]:
        return FIELD_FORMATTERS[self.field_type]

    @property
    def get_field_formatter(self) -> Callable[[Any], Any]:
        return GET_FIELD_FORMATTERS[self.field_type]


FIELD_REGISTRY = {
    JiraFields.RELEASE_TRAIN: JiraFieldInfo(
        field_id="customfield_10302",
        field_type=FieldType.SINGLE_SELECT,
    ),
    JiraFields.DEPLOYMENT_REQUIREMENTS: JiraFieldInfo(
        field_id="customfield_10300",
        field_type=FieldType.MULTI_SELECT,
    ),
    JiraFields.REPORTER: JiraFieldInfo(
        field_id="reporter",
        field_type=FieldType.USER,
    ),
}


def get_field(issue: Issue, name: JiraFields) -> JiraFieldInfo:
    """
    Retrieve a field from a Jira issue and format it according to FieldType.

    Args:
        issue (Issue): Jira issue instance (from jira-python).
        name (JiraFields): Logical Jira field enum member.

    Returns:
        Any: The formatted field data (e.g. str, list, dict) appropriate to the type.

    Raises:
        ValueError: If the field name is not a valid JiraFields enum member
        AttributeError: If the issue does not have the field
    """
    if not isinstance(name, JiraFields):
        raise ValueError(f"Expected JiraFields enum, got {type(name)}")
    try:
        info = FIELD_REGISTRY[name]
    except KeyError:
        raise ValueError(f"Field {name} is not registered in FIELD_REGISTRY")
    try:
        data = getattr(issue.fields, info.field_id)
    except AttributeError:
        raise ValueError(f"Issue does not have field {name} ({FIELD_REGISTRY[name].field_id})")
    return info.get_field_formatter(data)


class UpdateFields:
    """
    Builder class for constructing Jira issue field update payloads.

    This class uses FIELD_REGISTRY to look up how each JiraFields
    enum member should be formatted and which Jira API field ID
    it maps to. The resulting dictionary can be passed directly
    to Jira's issue.update() method.

    Attributes:
        fields (dict[str, Any]): A dictionary mapping Jira API field IDs
            to their correctly formatted values.

    Methods:
        add_field(name: JiraFields, value: Any):
            Adds a field to the update payload. Automatically applies
            the correct formatter based on the field's FieldType.

        as_dict() -> dict:
            Returns the completed payload as a dictionary suitable
            for passing to jira.issue.update(fields=...).

    Example:
        >>> update_fields = UpdateFields()
        >>> update_fields.add_field(JiraFields.RELEASE_TRAIN, "Beta Train")
        >>> update_fields.add_field(JiraFields.REPORTER, "jdoe")
        >>> jira.issue("AETHER-1").update(fields=update_fields.as_dict())
    """
    def __init__(self):
        self.fields = {}

    def add_field(self, name: JiraFields, value: Any):
        if not isinstance(name, JiraFields):
            raise ValueError(f"Expected JiraFields enum, got {type(name)}")
        info: JiraFieldInfo = FIELD_REGISTRY[name]
        self.fields[info.field_id] = info.formatter(value)

    def as_dict(self):
        return self.fields
