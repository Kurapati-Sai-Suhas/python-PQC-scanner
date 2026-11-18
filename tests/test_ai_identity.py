"""AI-review identity record (V8; guide v1.1 Sec. 6): the validator accepts only a complete, placeholder-free record
of a ChatGPT Temporary Chat session with every required isolation setting switched off. All values are test values."""
from __future__ import annotations

import copy
import json

import pytest

from pqscan.bench import review as R

GOOD = {
    "interface_or_api": "TEST interface",
    "model": "TEST-MODEL",
    "recorded_utc": "2026-11-16T09:00:00Z",
    "isolation": {"fresh_temporary_chat_per_batch": "yes", "custom_instructions": "off",
                  "memory_and_chat_history_reference": "off", "projects": "off", "connectors": "off",
                  "file_library": "off", "browsing_search": "off"},
}


def _write(tmp_path, obj, raw: str | None = None):
    p = tmp_path / "ident.json"
    p.write_text(raw if raw is not None else json.dumps(obj), encoding="utf-8")
    return p


def _rejected(tmp_path, obj, match: str):
    with pytest.raises(R.ReviewError, match=match):
        R.load_identity(_write(tmp_path, obj))


def test_complete_record_accepted_with_optional_fields(tmp_path):
    assert R.load_identity(_write(tmp_path, GOOD))["model"] == "TEST-MODEL"
    assert R.load_identity(_write(tmp_path, GOOD | {"app_version": "TEST 1.0", "notes": "test"}))["app_version"] == "TEST 1.0"
    upper = copy.deepcopy(GOOD)
    upper["isolation"]["projects"] = " OFF "
    assert R.load_identity(_write(tmp_path, upper))


def test_missing_file_refused(tmp_path):
    with pytest.raises(R.ReviewError, match="V8"):
        R.load_identity(tmp_path / "absent.json")


@pytest.mark.parametrize("key", R.IDENTITY_REQUIRED)
def test_each_required_key_missing_or_blank_refused(tmp_path, key):
    _rejected(tmp_path, {k: v for k, v in GOOD.items() if k != key}, f"{key} is missing")
    _rejected(tmp_path, GOOD | {key: "  "}, key)


@pytest.mark.parametrize("value", ["FILL: the model", "<model>", "TODO", "FILL"])
def test_placeholders_refused_anywhere(tmp_path, value):
    _rejected(tmp_path, GOOD | {"model": value}, "placeholder")
    iso = copy.deepcopy(GOOD)
    iso["isolation"]["connectors"] = "FILL: off"
    _rejected(tmp_path, iso, "placeholder")
    _rejected(tmp_path, GOOD | {"app_version": "FILL if shown"}, "placeholder")


def test_checklist_and_unfilled_templates_refused(tmp_path):
    checklist = {"interface_or_api": "<what you actually use>", "model": "<the model name>",
                 "recorded_utc": "<the current date and time in UTC>", "isolation": "<the settings you switched off>"}
    _rejected(tmp_path, checklist, "not acceptable")
    unfilled = {"interface_or_api": "FILL: x", "model": "FILL: y", "app_version": "FILL", "recorded_utc": "FILL",
                "isolation": {k: "FILL: off" for k in R.ISOLATION_YES + R.ISOLATION_OFF}, "notes": "FILL"}
    _rejected(tmp_path, unfilled, "placeholder")


@pytest.mark.parametrize("setting", R.ISOLATION_OFF)
def test_every_isolation_setting_must_be_off(tmp_path, setting):
    on = copy.deepcopy(GOOD)
    on["isolation"][setting] = "on"
    _rejected(tmp_path, on, f"{setting} must be 'off'")
    absent = copy.deepcopy(GOOD)
    del absent["isolation"][setting]
    _rejected(tmp_path, absent, f"{setting} is not recorded")


def test_fresh_temporary_chat_required(tmp_path):
    no = copy.deepcopy(GOOD)
    no["isolation"]["fresh_temporary_chat_per_batch"] = "no"
    _rejected(tmp_path, no, "must be 'yes'")


def test_isolation_must_be_the_settings_object(tmp_path):
    _rejected(tmp_path, GOOD | {"isolation": "temporary chat; memory off"}, "isolation must be an object")
    _rejected(tmp_path, GOOD | {"isolation": {}}, "is not recorded")
    extra = copy.deepcopy(GOOD)
    extra["isolation"]["memroy"] = "off"                                        # typo is not silently accepted
    _rejected(tmp_path, extra, "unknown keys")


def test_unknown_top_level_key_refused(tmp_path):
    _rejected(tmp_path, GOOD | {"api_key": "x"}, "unknown keys")


@pytest.mark.parametrize("utc", ["yesterday", "2026-11-18 09:00:00", "2026-11-18T09:00:00+05:30", "2999-01-01T00:00:00Z"])
def test_recorded_utc_must_be_a_past_utc_timestamp(tmp_path, utc):
    _rejected(tmp_path, GOOD | {"recorded_utc": utc}, "recorded_utc")


def test_non_object_and_invalid_json_refused_cleanly(tmp_path):
    with pytest.raises(R.ReviewError, match="JSON object"):
        R.load_identity(_write(tmp_path, None, raw="[1, 2]"))
    with pytest.raises(R.ReviewError, match="not valid"):
        R.load_identity(_write(tmp_path, None, raw="{not json"))


def test_prompt_refused_with_an_invalid_identity(tmp_path):
    with pytest.raises(R.ReviewError, match="not acceptable"):
        R.build_prompt([{"text": "PACKET"}], identity_path=_write(tmp_path, GOOD | {"model": "<model>"}))


def test_identity_sha256_is_line_ending_independent(tmp_path):
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    a.write_bytes(b'{\n "x": 1\n}\n')
    b.write_bytes(b'{\r\n "x": 1\r\n}\r\n')
    assert R.identity_sha256(a) == R.identity_sha256(b) and len(R.identity_sha256(a)) == 64
