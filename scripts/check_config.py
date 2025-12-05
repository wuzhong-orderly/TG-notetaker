import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.config import Config

print(f"ENABLE_AI_SUMMARY: {Config.ENABLE_AI_SUMMARY}")
print(f"AUTO_SUMMARY_TIME: {Config.AUTO_SUMMARY_TIME}")
print(f"AI_PROVIDER: {Config.AI_PROVIDER}")
print(f"MIN_MESSAGES_FOR_SUMMARY: {Config.MIN_MESSAGES_FOR_SUMMARY}")
