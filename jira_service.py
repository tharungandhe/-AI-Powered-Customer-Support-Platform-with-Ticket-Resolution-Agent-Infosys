import os
import requests
from requests.auth import HTTPBasicAuth

class JiraService:
    def __init__(self):
        self.url = os.getenv("JIRA_URL")
        self.email = os.getenv("JIRA_EMAIL")
        self.api_token = os.getenv("JIRA_API_TOKEN")
        self.project_key = os.getenv("JIRA_PROJECT_KEY")

    def create_ticket(
        self,
        summary,
        description,
        priority="High"
    ):
        if not all([
            self.url,
            self.email,
            self.api_token,
            self.project_key
        ]):
            return {
                "success": False,
                "message": "Jira configuration not available"
            }

        if self.url == "https://your-domain.atlassian.net":
            import random
            return {
                "success": True,
                "ticket_id": f"{self.project_key}-{random.randint(1000, 9999)}",
                "message": "Jira ticket created successfully (Simulated)"
            }

        endpoint = f"{self.url}/rest/api/3/issue"

        payload = {
            "fields": {
                "project": {
                    "key": self.project_key
                },
                "summary": summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "text": description,
                                    "type": "text"
                                }
                            ]
                        }
                    ]
                },
                "issuetype": {
                    "name": "Task"
                },
                "priority": {
                    "name": priority
                }
            }
        }

        try:
            response = requests.post(
                endpoint,
                json=payload,
                auth=HTTPBasicAuth(
                    self.email,
                    self.api_token
                ),
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                timeout=20
            )

            if response.status_code in [200, 201]:
                data = response.json()
                return {
                    "success": True,
                    "ticket_id": data.get("key"),
                    "message": "Jira ticket created successfully"
                }

            return {
                "success": False,
                "message": response.text
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }
