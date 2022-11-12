"""Constant strings"""
from .types import NoticeData


START_TEXT = (
    "Benvenuto! Questo bot è stato realizzato dagli studenti di Informatica"
    "al fine di supportare gli studenti dell'Università di Catania!"
    "Per scoprire cosa puoi fare usa /help"
)
CLEAR_LOGFILE_TEXT = "Logfile has been cleared"

DEFAULT_NOTICES_DATA: NoticeData = {
    "pending_notices": [],
    "scraped_links": [],
}
