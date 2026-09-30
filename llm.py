"""LLM provider pool. API keys and model names come from the environment.

Each *_MODEL variable may list several model names separated by commas; they are tried in order.
A provider needs both an API key and at least one model name, otherwise it is skipped.
"""
import logging, os, re, time

from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger(__name__)

# name, API key env vars, module, class, model-name env var
PROVIDERS = [
    ("groq", ("GROQ_API_KEY",), "langchain_groq", "ChatGroq", "GROQ_MODEL"),
    ("gemini", ("GEMINI_API_KEY", "GOOGLE_API_KEY"), "langchain_google_genai", "ChatGoogleGenerativeAI", "GEMINI_MODEL"),
    ("openai", ("OPENAI_API_KEY",), "langchain_openai", "ChatOpenAI", "OPENAI_MODEL"),
    ("anthropic", ("ANTHROPIC_API_KEY",), "langchain_anthropic", "ChatAnthropic", "ANTHROPIC_MODEL"),
]
_models, _cool = {}, {}  # _cool[(provider, model)] = time until which that model is skipped
WAIT_RE = re.compile(r"retry in ([\d.]+)\s*s", re.I)


def _key(keys):
    return next((os.environ[k] for k in keys if os.environ.get(k)), None)


def _names(p):
    return [m.strip() for m in os.environ.get(p[4], "").split(",") if m.strip()]


def _ready(p):
    """Use a provider only when both its API key and a model name are set."""
    return bool(_key(p[1]) and _names(p))


def available():
    return [p[0] for p in PROVIDERS if _ready(p)]


def _model(p, model):
    name, keys, module, cls, _ = p
    if (name, model) not in _models:
        klass = getattr(__import__(module, fromlist=[cls]), cls)  # imported only when its provider is configured
        extra = {"google_api_key": _key(keys)} if name == "gemini" else {}
        _models[(name, model)] = klass(model=model, temperature=0.2, max_tokens=2048, timeout=25, max_retries=0, **extra)
    return _models[(name, model)]


def _text(content):
    if isinstance(content, str):
        return content
    return "".join(b.get("text", "") for b in content if isinstance(b, dict))


def _cooldown(exc, first_try):
    """Seconds to skip this model after a failure; 0 means retry it once right away."""
    msg = str(exc)
    low = msg.lower()
    if "429" in msg or "resource_exhausted" in low or "quota" in low:  # quota: retrying only burns more requests
        m = WAIT_RE.search(msg)
        return float(m.group(1)) + 1 if m else 60
    if any(t in low for t in ("503", "unavailable", "overloaded", "timed out", "timeout")):
        return 0 if first_try else 30  # temporary overload: one quick retry
    return 300  # bad key, unknown model, and so on


def ask(system, user):
    """Text from the first working provider/model (priority: Groq, Gemini, OpenAI, Anthropic)."""
    tried = []
    for p in PROVIDERS:
        if not _ready(p):
            continue
        for model in _names(p):
            if _cool.get((p[0], model), 0) > time.time():
                continue
            tried.append(f"{p[0]}/{model}")
            for attempt in (1, 2):
                try:
                    text = _text(_model(p, model).invoke([("system", system), ("human", user)]).content).strip()
                    if text:
                        return text
                    break  # empty answer: try the next model
                except Exception as exc:
                    wait = _cooldown(exc, attempt == 1)
                    log.warning("%s / %s failed (attempt %d): %s", p[0], model, attempt, str(exc)[:300])
                    if wait == 0:
                        time.sleep(2)
                        continue
                    _cool[(p[0], model)] = time.time() + wait
                    break
    raise RuntimeError("no LLM provider succeeded (tried: %s)" % (", ".join(tried) or "none available right now"))