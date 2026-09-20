"""
tests/test_memory.py
Day 39 — tests for memory.py.

Run with:
    pytest tests/test_memory.py -v

Note: test_summarize_thread makes a real API call to Groq.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.memory import get_thread_context, summarize_thread


def test_get_thread_context_returns_messages_in_order():
    context = get_thread_context("thread_1")
    assert len(context) == 3
    assert context[0]["body"].lower().startswith("can we meet friday")
    assert "monday" in context[-1]["body"].lower()


def test_get_thread_context_nonexistent_thread_returns_empty():
    context = get_thread_context("nonexistent_thread")
    assert context == []


def test_summarize_thread_captures_latest_change():
    """
    The core Day 39 test case: the summary should reflect the LATEST
    request (Monday), not the original one (Friday).
    """
    summary = summarize_thread("thread_1")
    assert "monday" in summary.lower()


def test_summarize_thread_empty_for_nonexistent_thread():
    summary = summarize_thread("nonexistent_thread")
    assert "no prior thread history" in summary.lower()
