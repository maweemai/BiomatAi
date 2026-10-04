"""Protects a shared Groq key: daily cap, cooldown, parallel-run limit, result cache.
Edit the numbers below to fit your free quota."""
import datetime
import json
import threading
import time

import streamlit as st

DAILY_CAP = 60          # total runs per day for ALL visitors using the shared key
SESSION_MAX_RUNS = 5    # runs per visitor session
COOLDOWN_SEC = 45       # wait between runs of the same visitor
MAX_PARALLEL = 2        # runs allowed at the same time
CACHE_SIZE = 50         # saved results (identical requests cost 0 tokens)


@st.cache_resource
def _shared():
    return {"lock": threading.Lock(), "day": None, "count": 0,
            "gate": threading.Semaphore(MAX_PARALLEL), "cache": {}}


def runs_left_today() -> int:
    s, today = _shared(), datetime.date.today()
    with s["lock"]:
        if s["day"] != today:
            s["day"], s["count"] = today, 0
        return max(0, DAILY_CAP - s["count"])


def check_shared_limits():
    """Return a message if this run must be refused, otherwise None."""
    ss = st.session_state
    if ss.get("runs_done", 0) >= SESSION_MAX_RUNS:
        return (f"You used your {SESSION_MAX_RUNS} free runs for this visit. "
                "Reload later, or paste your own free Groq key in the sidebar for more.")
    wait = COOLDOWN_SEC - (time.time() - ss.get("last_run", 0))
    if wait > 0:
        return f"Please wait {int(wait) + 1} seconds before the next run."
    if runs_left_today() <= 0:
        return ("Today's shared free quota is used up. Try again tomorrow, "
                "or paste your own free Groq key in the sidebar.")
    return None


def register_run():
    runs_left_today()  # makes sure the day counter is current
    s = _shared()
    with s["lock"]:
        s["count"] += 1
    st.session_state["runs_done"] = st.session_state.get("runs_done", 0) + 1
    st.session_state["last_run"] = time.time()


def try_acquire() -> bool:
    return _shared()["gate"].acquire(blocking=False)


def release():
    _shared()["gate"].release()


def cache_key(inputs: dict, use_search: bool, use_critic: bool) -> str:
    return json.dumps([inputs, use_search, use_critic], sort_keys=True)


def cache_get(key):
    s = _shared()
    with s["lock"]:
        return s["cache"].get(key)


def cache_put(key, value):
    s = _shared()
    with s["lock"]:
        s["cache"][key] = value
        while len(s["cache"]) > CACHE_SIZE:
            s["cache"].pop(next(iter(s["cache"])))
