import re
from typing import Any, Dict, List, Callable, Awaitable, Optional
from emailmanagement.debounce import IncomingEvent

EMAIL_REGEX = re.compile(r"<([^>]+)>|(\S+@\S+)")

class InboxPoller:
    """
    Boundary layer that standardizes raw webhooks and payloads
    from Gmail/Slack into IncomingEvents.
    """
    
    def __init__(
        self,
        slack_fetcher: Optional[Callable[[], Awaitable[List[Dict[str, Any]]]]] = None,
        gmail_fetcher: Optional[Callable[[], Awaitable[List[Dict[str, Any]]]]] = None,
    ):
        self.slack_fetcher = slack_fetcher
        self.gmail_fetcher = gmail_fetcher

    async def poll(self) -> List[IncomingEvent]:
        events = []
        if self.slack_fetcher:
            try:
                raw_slack = await self.slack_fetcher()
                for payload in raw_slack:
                    event = self.parse_slack_event(payload)
                    if event:
                        events.append(event)
            except Exception as e:
                print(f"[InboxPoller] Slack poll failed: {e}")

        if self.gmail_fetcher:
            try:
                raw_gmail = await self.gmail_fetcher()
                for payload in raw_gmail:
                    event = self.parse_gmail_event(payload)
                    if event:
                        events.append(event)
            except Exception as e:
                print(f"[InboxPoller] Gmail poll failed: {e}")
        return events
    
    def parse_slack_event(self, payload: Dict[str, Any]) -> Optional[IncomingEvent]:
        """
        Parse a typical Slack `message` event payload.
        """
        try:
            # Extract fields based on Slack payload structure
            event_id = payload.get("client_msg_id") or payload.get("ts")
            contact_id = payload.get("user", "unknown_user")
            content = payload.get("text", "")
            
            # Convert timestamp strings like "1711283456.123400" to float
            ts_str = payload.get("ts", "0.0")
            try:
                timestamp = float(ts_str)
            except ValueError:
                timestamp = 0.0
                
            headers = {
                "source": "slack",
                "channel": payload.get("channel", "unknown"),
                "team": payload.get("team", "unknown")
            }
            
            return IncomingEvent(
                id=event_id,
                contact_id=contact_id,
                content=content,
                timestamp=timestamp,
                headers=headers
            )
        except Exception as e:
            print(f"[InboxPoller] Failed to parse Slack event: {e}")
            return None

    def parse_gmail_event(self, payload: Dict[str, Any]) -> Optional[IncomingEvent]:
        """
        Parse a typical Gmail message payload (from users.messages.get).
        """
        try:
            event_id = payload.get("id", "unknown_id")
            content = payload.get("snippet", "")
            
            # Convert internalDate from ms string to sec float
            date_str = payload.get("internalDate", "0")
            try:
                timestamp = float(date_str) / 1000.0
            except ValueError:
                timestamp = 0.0
                
            # Extract headers from payload dict
            msg_headers = payload.get("payload", {}).get("headers", [])
            
            from_email = "unknown_sender"
            subject = ""
            for h in msg_headers:
                name = h.get("name", "").lower()
                val = h.get("value", "")
                if name == "from":
                    # Robust extraction using regex
                    match = EMAIL_REGEX.search(val)
                    if match:
                        from_email = match.group(1) or match.group(2)
                    else:
                        from_email = val.strip()
                elif name == "subject":
                    subject = val
                    
            headers = {
                "source": "gmail",
                "subject": subject,
                "threadId": payload.get("threadId", "unknown")
            }
            
            return IncomingEvent(
                id=event_id,
                contact_id=from_email,
                content=content,
                timestamp=timestamp,
                headers=headers
            )
        except Exception as e:
            print(f"[InboxPoller] Failed to parse Gmail event: {e}")
            return None
