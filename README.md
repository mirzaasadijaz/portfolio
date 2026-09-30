# Asad Ijaz portfolio (Flask)

Run locally: `pip install -r requirements.txt && python app.py`

Deploy: push to GitHub, create a Render Blueprint from this repo (uses `render.yaml`), then add your domain under Settings > Custom Domains. Optionally set `GITHUB_TOKEN` (no scopes needed) to lift GitHub's API rate limit.

Add content by editing `content.json` only:
- `projects`: append an object with `title`, `repo`, `summary`, `tags`, `url` (optional `live`). Pinned repos are excluded from the automatic "More on GitHub" list.
- `experience`, `education`, `skills`, `links`: append entries in the same shape.
- GitHub repos and Docker Hub images are fetched live and cached for an hour; if either service is down the section is skipped, not broken.
- `GET /api/projects` returns the same data as JSON.

`areas` in `content.json` drives the Experience accordion (order = display order). Give a project `areas` ids to make it filterable under Selected work.

## Chat assistant
`rag.py` is a LangGraph agent: it classifies the question, retrieves from your portfolio content (`content.json` plus live GitHub and Docker Hub data), grades the passages, rewrites the query once if they are weak, and falls back to the model's own knowledge only when the portfolio has nothing. Contact requests hand the visitor to the form.

Set any of `GROQ_API_KEY`, `GEMINI_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`. Providers without a key are skipped; order of use is Groq, Gemini, OpenAI, Anthropic, and a failing provider is skipped for five minutes. With no key at all the bot answers straight from retrieval. Optional model overrides: `GROQ_MODEL`, `GEMINI_MODEL`, `OPENAI_MODEL`, `ANTHROPIC_MODEL`.

## Contact form (EmailJS)
Create an EmailJS service and template, set `EMAILJS_SERVICE_ID`, `EMAILJS_TEMPLATE_ID`, `EMAILJS_PUBLIC_KEY`. The template can use `{{from_name}}`, `{{from_email}}`, `{{reply_to}}` and `{{message}}`.
