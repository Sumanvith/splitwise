import json
import logging
import sys

from app.core.logging_config import JsonFormatter

from app.config import settings
from app.core.logging_config import setup_logging


def test_json_formatter_fields():
    record = logging.LogRecord(
        "app", logging.INFO, "f.py", 1, "hello", None, None)
    record.path = "/x"
    data = json.loads(JsonFormatter().format(record))
    assert data["message"] == "hello"
    assert data["level"] == "INFO"
    assert data["path"] == "/x"
    assert "timestamp" in data


def test_json_formatter_exception():
    try:
        raise ValueError("boom")
    except ValueError:
        record = logging.LogRecord(
            "app", logging.ERROR, "f.py", 1, "failed", None, sys.exc_info()
        )
    data = json.loads(JsonFormatter().format(record))
    assert "ValueError" in data["exception"]


def test_file_logging(tmp_path, monkeypatch):
    log_file = tmp_path / "logs" / "app.log"
    monkeypatch.setattr(settings, "log_file", str(log_file))
    root = logging.getLogger()
    old_handlers = root.handlers[:]
    try:
        setup_logging()
        logging.getLogger("app").info("hello file")
        for h in root.handlers:
            h.flush()
        assert "hello file" in log_file.read_text()
    finally:
        for h in root.handlers:
            if h not in old_handlers:
                h.close()
        root.handlers = old_handlers
