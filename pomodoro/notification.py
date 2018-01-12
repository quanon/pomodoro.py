import os


def notify(message):
  title = 'pomodoro.py'
  os.system(f"osascript -e 'display notification" +
            f" \"{message}\" with title \"{title}\"'")
