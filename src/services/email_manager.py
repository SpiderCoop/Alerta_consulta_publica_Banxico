"""
Description:   Instance of email object to be able to send emails from the defined account
Author:        David Jiménez Cooper - SpiderCoop
Date:          2026-08-28
"""

from email_automation import EmailManager

from src.config import CUENTA, PASSWORD

email = EmailManager(CUENTA, PASSWORD)
