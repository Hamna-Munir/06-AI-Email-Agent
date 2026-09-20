"""
tests/test_tools.py
Day 38 — tests for tools.py.

Run with:
    pytest tests/test_tools.py -v
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.tools import search_emails, get_email, create_draft, search_contacts, get_calendar_availability, execute_tool


def test_search_emails_finds_match():
    results = search_emails("meeting")
    assert len(results) > 0
    assert any("meeting" in r["subject"].lower() or "meeting" in r["body"].lower() for r in results)


def test_search_emails_no_match_returns_empty_list():
    results = search_emails("xyznonexistentterm")
    assert results == []


def test_get_email_valid_id():
    email = get_email("email_1")
    assert email["subject"] == "Meeting request"


def test_get_email_invalid_id_returns_error_not_exception():
    result = get_email("nonexistent_id")
    assert isinstance(result, str)
    assert "error" in result.lower()


def test_create_draft():
    draft = create_draft("client@example.com", "Re: Meeting", "Sure, let's meet.")
    assert draft["status"] == "draft"
    assert draft["to"] == "client@example.com"


def test_search_contacts_found():
    contact = search_contacts("Alex")
    assert contact["email"] == "client@example.com"


def test_search_contacts_not_found():
    result = search_contacts("nonexistent person")
    assert isinstance(result, str)
    assert "no contact" in result.lower()


def test_get_calendar_availability_returns_slots():
    slots = get_calendar_availability()
    assert isinstance(slots, list)
    assert len(slots) > 0


def test_execute_tool_valid_call():
    result = execute_tool("get_email", {"email_id": "email_1"})
    assert result["subject"] == "Meeting request"


def test_execute_tool_unknown_tool():
    result = execute_tool("nonexistent_tool", {})
    assert "unknown tool" in result.lower()


def test_execute_tool_bad_arguments_does_not_crash():
    result = execute_tool("get_email", {})  # missing required email_id
    assert isinstance(result, str)
    assert "error" in result.lower()
