"""Type definitions."""
from typing import TypedDict


class PageConfig(TypedDict):
    """page sub-configuration type definition"""

    label: str
    urls: "list[str]"
    channels: "list[str | int]"


class GroupConfig(TypedDict):
    """group sub-configuraiton type definition"""

    base_url: str
    approval_group_chatid: "int | None"
    pages: "dict[str, PageConfig]"


class Config(TypedDict):
    """config_map type definition"""

    token: str
    dev_group_chatid: int
    log_group_chatid: int
    logfile_reset_interval_minutes: int
    update_interval: int
    max_messages_length: int
    max_length_footer: str
    max_connection_tries: int
    notices_groups: "dict[str, GroupConfig]"


class NoticeData(TypedDict):
    "notice data type definition"

    pending_notices: "list[str]"
    scraped_links: "list[str]"
