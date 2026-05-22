import json
import os
import time
from multiprocessing import Process, Queue

from cinnamon_panel_anchor import cli
from cinnamon_panel_anchor.locking import CommandLock, LockRefused, lock_path
from cinnamon_panel_anchor.logging import MAX_RECORDS, log_path, write_log


def _write_log_worker(state_home, index, queue):
    os.environ["XDG_STATE_HOME"] = state_home
    try:
        write_log(
            level="info",
            component="worker",
            event="concurrent",
            outcome="ok",
            message=str(index),
            context={"index": index},
        )
        queue.put(("ok", index))
    except Exception as exc:
        queue.put(("error", str(exc)))


def _hold_lock_worker(runtime_dir, queue):
    os.environ["XDG_RUNTIME_DIR"] = runtime_dir
    try:
        with CommandLock("capture"):
            queue.put("locked")
            time.sleep(0.5)
    except Exception as exc:
        queue.put(f"error:{exc}")


def _try_lock_worker(runtime_dir, queue):
    os.environ["XDG_RUNTIME_DIR"] = runtime_dir
    try:
        with CommandLock("restore"):
            queue.put("acquired")
    except LockRefused:
        queue.put("refused")
    except Exception as exc:
        queue.put(f"error:{exc}")


def test_jsonl_logging_schema_and_retention(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))

    for index in range(MAX_RECORDS + 5):
        write_log(
            level="info",
            component="test",
            event="retention",
            command="status",
            outcome="ok",
            message=str(index),
            context={"index": index},
        )

    lines = log_path().read_text(encoding="utf-8").splitlines()
    assert len(lines) == MAX_RECORDS
    first = json.loads(lines[0])
    last = json.loads(lines[-1])
    assert first["context"]["index"] == 5
    assert last["version"] == "0.2.1"
    assert {"timestamp", "level", "component", "event", "version", "command", "action", "outcome", "message", "context", "exception"} <= set(last)


def test_lock_refusal_returns_code_3_json(monkeypatch, tmp_path, capsys):
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(runtime))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    with CommandLock("capture"):
        code = cli.main(["capture", "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert code == 3
    assert payload["ok"] is False
    assert payload["severity"] == "warning"
    assert payload["error_details"]["type"] == "LockRefused"


def test_stale_lock_is_recovered(monkeypatch, tmp_path):
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(runtime))
    lock_path().write_text(json.dumps({"pid": 999999, "command": "capture", "timestamp": 0}), encoding="utf-8")

    with CommandLock("capture"):
        data = json.loads(lock_path().read_text(encoding="utf-8"))
        assert data["command"] == "capture"

    assert lock_path().exists()


def test_command_lock_serializes_contenders_after_stale_metadata(monkeypatch, tmp_path):
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(runtime))
    lock_path().write_text(json.dumps({"pid": 999999, "command": "old", "timestamp": 0}), encoding="utf-8")

    with CommandLock("capture"):
        code = cli.main(["capture", "--json"])

    assert code == 3


def test_command_lock_refuses_concurrent_process(monkeypatch, tmp_path):
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(runtime))
    queue = Queue()
    holder = Process(target=_hold_lock_worker, args=(str(runtime), queue))
    holder.start()
    assert queue.get(timeout=2) == "locked"

    contender = Process(target=_try_lock_worker, args=(str(runtime), queue))
    contender.start()
    assert queue.get(timeout=2) == "refused"

    contender.join(2)
    holder.join(2)
    assert contender.exitcode == 0
    assert holder.exitcode == 0


def test_log_event_json_writes_applet_event(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))

    code = cli.main([
        "log-event",
        "--json",
        "--event",
        "unit-test",
        "--action",
        "click",
        "--outcome",
        "ok",
        "--context",
        "{\"source\":\"test\"}",
    ])
    payload = json.loads(capsys.readouterr().out)
    record = json.loads(log_path().read_text(encoding="utf-8").splitlines()[0])

    assert code == 0
    assert payload["ok"] is True
    assert record["component"] == "applet"
    assert record["event"] == "unit-test"
    assert record["context"]["source"] == "test"


def test_concurrent_log_writes_preserve_valid_jsonl(monkeypatch, tmp_path):
    state_home = str(tmp_path / "state")
    monkeypatch.setenv("XDG_STATE_HOME", state_home)
    queue = Queue()
    processes = [Process(target=_write_log_worker, args=(state_home, index, queue)) for index in range(20)]

    for process in processes:
        process.start()
    for process in processes:
        process.join(10)

    results = [queue.get(timeout=1) for _ in processes]
    assert all(status == "ok" for status, _ in results)
    lines = log_path().read_text(encoding="utf-8").splitlines()
    records = [json.loads(line) for line in lines]
    indexes = sorted(record["context"]["index"] for record in records if record["event"] == "concurrent")
    assert indexes == list(range(20))
