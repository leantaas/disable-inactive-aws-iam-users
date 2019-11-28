import json
import requests


def message(color, pretext, title, message, webhook):
    payload = {
        "attachments": [
            {
                "color": color,
                "pretext": pretext,
                "title": title,
                "text": message,
                "footer": "DEVOPS MADE EASY ALERTS"
            }
        ]
    }
    requests.post(webhook,
                  json.dumps(payload),
                  headers={'content-type': 'application/json'})
