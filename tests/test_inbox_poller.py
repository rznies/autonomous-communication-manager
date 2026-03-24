import pytest
from emailmanagement.inbox_poller import InboxPoller
from emailmanagement.debounce import IncomingEvent

def test_parse_slack_message_event():
    # Example raw Slack message payload
    raw_slack_event = {
        "client_msg_id": "9b1dbce-9d2a-4bc8-8c5e-b830d1c44e91",
        "type": "message",
        "text": "Hey, are we still on for the meeting?",
        "user": "U12345678",
        "ts": "1711283456.123400",
        "team": "T12345678",
        "channel": "C12345678"
    }
    
    poller = InboxPoller()
    event = poller.parse_slack_event(raw_slack_event)
    
    assert isinstance(event, IncomingEvent)
    assert event.id == "9b1dbce-9d2a-4bc8-8c5e-b830d1c44e91"
    assert event.contact_id == "U12345678"
    assert event.content == "Hey, are we still on for the meeting?"
    assert event.timestamp == 1711283456.123400
    assert event.headers == {
        "source": "slack",
        "channel": "C12345678",
        "team": "T12345678"
    }

def test_parse_gmail_message_event():
    # Example raw Gmail message payload from users.messages.get
    raw_gmail_event = {
        "id": "18e6b9c9f8a7e6d5",
        "threadId": "18e6b9c9f8a7e6d5",
        "snippet": "Hi, let me know if you are free tomorrow.",
        "internalDate": "1711284000000",
        "payload": {
            "headers": [
                {"name": "From", "value": "Alice Smith <alice@example.com>"},
                {"name": "To", "value": "bob@startup.com"},
                {"name": "Subject", "value": "Meeting tomorrow?"}
            ]
        }
    }
    
    poller = InboxPoller()
    event = poller.parse_gmail_event(raw_gmail_event)
    
    assert isinstance(event, IncomingEvent)
    assert event.id == "18e6b9c9f8a7e6d5"
    assert event.contact_id == "alice@example.com"
    assert event.content == "Hi, let me know if you are free tomorrow."
    assert event.timestamp == 1711284000.0  # Converted from ms
    assert event.headers == {
        "source": "gmail",
        "subject": "Meeting tomorrow?",
        "threadId": "18e6b9c9f8a7e6d5"
    }

def test_parse_malformed_slack_event():
    poller = InboxPoller()
    # Missing all major fields
    event = poller.parse_slack_event({})
    
    assert event.id is None
    assert event.contact_id == "unknown_user"
    assert event.content == ""
    assert event.timestamp == 0.0

def test_parse_malformed_gmail_event():
    poller = InboxPoller()
    # Missing headers, internalDate, id
    event = poller.parse_gmail_event({})
    
    assert event.id == "unknown_id"
    assert event.contact_id == "unknown_sender"
    assert event.content == ""
    assert event.timestamp == 0.0
