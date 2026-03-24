from typing import Any, Dict
from emailmanagement.debounce import IncomingEvent

class InboxPoller:
    """
    Boundary layer that standardizes raw webhooks and payloads
    from Gmail/Slack into IncomingEvents.
    """
    
    def parse_slack_event(self, payload: Dict[str, Any]) -> IncomingEvent:
        """
        Parse a typical Slack `message` event payload.
        """
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

    def parse_gmail_event(self, payload: Dict[str, Any]) -> IncomingEvent:
        """
        Parse a typical Gmail message payload (from users.messages.get).
        """
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
                # Basic extraction of email out of "Name <email@domain.com>"
                if "<" in val and ">" in val:
                    from_email = val.split("<")[1].split(">")[0].strip()
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
