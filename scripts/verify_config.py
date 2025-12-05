import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import Config

print(f"SUMMARY_REPORT_CHAT_ID: {Config.get_summary_report_chat_id()}")
print(f"SEND_SUMMARY_TO_CHAT: {Config.SEND_SUMMARY_TO_CHAT}")
