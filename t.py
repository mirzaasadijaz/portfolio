"""Health check for every configured LLM provider/model.

Run from the project folder:  python check_llm.py
"""
import sys
import time

import llm  # loads .env and reuses the same settings as the app


def hint(exc):
    e = f"{type(exc).__name__} {exc}".lower()
    if "modulenotfound" in e or "importerror" in e:
        return "package missing; run: pip install -r requirements.txt"
    if "empty reply" in e:
        return "model returned no text; try another model"
    if "429" in e or "resource_exhausted" in e or "quota" in e:
        return "quota or rate limit reached; wait a minute or add another model or provider"
    if "503" in e or "unavailable" in e or "overloaded" in e:
        return "provider is overloaded right now; retry shortly"
    if "404" in e or "not_found" in e or "not found" in e or "does not exist" in e:
        return "model name is wrong or retired; check the *_MODEL value"
    if any(t in e for t in ("401", "403", "api key", "permission", "unauthenticated")):
        return "API key rejected; check the key and that it can use this model"
    if "timeout" in e or "timed out" in e:
        return "request timed out; retry"
    return "unrecognised error; see the message above"


def main():
    ok = total = 0
    for p in llm.PROVIDERS:
        name, keys, _, _, model_env = p
        key, models = llm._key(keys), llm._names(p)
        if not key and not models:
            print(f"{name:10} not configured")
            continue
        if not key or not models:
            print(f"{name:10} SKIPPED: {'no API key' if not key else model_env + ' is empty'}")
            continue
        for model in models:
            total += 1
            start = time.time()
            try:
                reply = llm._model(p, model).invoke(
                    [("system", "This is a health check."), ("human", "Reply with one word: ready")])
                text = llm._text(reply.content).strip()
                if not text:
                    raise ValueError("empty reply")
                ok += 1
                print(f"{name:10} OK      {model}  ({time.time() - start:.1f}s)  reply: {text[:40]!r}")
            except Exception as exc:
                print(f"{name:10} FAILED  {model}  ({time.time() - start:.1f}s)")
                print(f"           {str(exc)[:240]}")
                print(f"           -> {hint(exc)}")
    print(f"\n{ok} of {total} model(s) working")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()