import json, os, time
from pathlib import Path

import requests
from flask import Flask, jsonify, render_template, request

import rag
from dotenv import load_dotenv

load_dotenv()

BASE = Path(__file__).parent
app = Flask(__name__)
_cache, _hits = {}, {}
EMAILJS = {"service": os.getenv("EMAILJS_SERVICE_ID", ""), "template": os.getenv("EMAILJS_TEMPLATE_ID", ""),
          "key": os.getenv("EMAILJS_PUBLIC_KEY", "")}


def content():
    return json.loads((BASE / "content.json").read_text(encoding="utf-8"))


def cached(key, ttl, fn):
    """Tiny TTL cache. A failed fetch serves the last good value and retries in 5 minutes."""
    hit = _cache.get(key)
    if hit and time.time() - hit[0] < ttl:
        return hit[1]
    try:
        val, stamp = fn(), time.time()
    except Exception as exc:
        app.logger.warning("%s fetch failed: %s", key, exc)
        val, stamp = (hit[1] if hit else []), time.time() - ttl + 300
    _cache[key] = (stamp, val)
    return val


def github_repos(user):
    headers = {"Accept": "application/vnd.github+json"}
    if os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    r = requests.get(f"https://api.github.com/users/{user}/repos",
                     params={"per_page": 100, "sort": "pushed"}, headers=headers, timeout=6)
    r.raise_for_status()
    return [{"name": x["name"], "description": x["description"] or "", "language": x["language"],
             "url": x["html_url"], "pushed": (x["pushed_at"] or "")[:10]}
            for x in r.json() if not x["fork"] and not x["archived"]]


def docker_images(user):
    r = requests.get(f"https://hub.docker.com/v2/repositories/{user}/",
                     params={"page_size": 25, "ordering": "last_updated"}, timeout=6)
    r.raise_for_status()
    return [{"name": x["name"], "description": x.get("description") or "",
             "pulls": x.get("pull_count", 0), "url": f"https://hub.docker.com/r/{user}/{x['name']}",
             "updated": (x.get("last_updated") or "")[:10]} for x in r.json().get("results", [])]


def live_data(c):
    acc = c["accounts"]
    repos = cached("github", 3600, lambda: github_repos(acc["github"]))
    pinned = {p.get("repo") for p in c["projects"]}
    more = [r for r in repos if r["name"] not in pinned and r["description"]
            and r["name"].lower() != acc["github"].lower()][: c.get("more_limit", 8)]
    docker = cached("docker", 3600, lambda: docker_images(acc["docker"]))
    return more, docker


@app.route("/")
def home():
    print("EMAILJS CREDS:", EMAILJS)
    c = content()
    more, docker = live_data(c)
    by_repo = {x["repo"]: x for x in c["projects"]}
    used = {t for x in c["projects"] for t in x.get("areas", [])}
    return render_template("index.html", c=c, more=more, docker=docker, by_repo=by_repo, used=used,
                           year=time.localtime().tm_year, emailjs=EMAILJS)


@app.route("/api/projects")
def api_projects():
    c = content()
    more, docker = live_data(c)
    return jsonify(pinned=c["projects"], github=more, docker=docker)


def limited(ip, n=12, window=60):
    now = time.time()
    if len(_hits) > 5000:
        _hits.clear()
    recent = [t for t in _hits.get(ip, []) if now - t < window] + [now]
    _hits[ip] = recent
    return len(recent) > n


@app.post("/api/chat")
def api_chat():
    ip = (request.headers.get("X-Forwarded-For") or request.remote_addr or "").split(",")[0].strip()
    if limited(ip):
        return jsonify(reply="You are sending messages quickly. Please wait a moment and try again.", action=None, sources=[]), 429
    data = request.get_json(silent=True) or {}
    msg = str(data.get("message", "")).strip()[:600]
    if not msg:
        return jsonify(error="empty message"), 400
    history = [{"role": "Visitor" if m.get("role") == "user" else "Assistant", "content": str(m.get("content", ""))[:600]}
               for m in (data.get("history") or [])[-6:] if isinstance(m, dict)]
    c = content()
    more, docker = live_data(c)
    return jsonify(rag.reply(msg, history, rag.build_docs(c, more, docker)))


@app.route("/healthz")
def healthz():
    return "ok"


@app.errorhandler(404)
def not_found(_):
    return render_template("404.html", c=content()), 404


@app.after_request
def headers(resp):
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    if resp.mimetype in ("text/css", "image/svg+xml", "image/jpeg"):
        resp.headers.setdefault("Cache-Control", "public, max-age=86400")
    return resp


if __name__ == "__main__":
    app.run(debug=True)
