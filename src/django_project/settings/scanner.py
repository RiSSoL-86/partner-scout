from django_project.settings import env

# --- Crawl (step 1) --------------------------------------------------------
CRAWLER_MAX_PAGES = env.int("CRAWLER_MAX_PAGES", default=50)
CRAWLER_MAX_DEPTH = env.int("CRAWLER_MAX_DEPTH", default=2)
CRAWLER_PAGE_TIMEOUT = env.int("CRAWLER_PAGE_TIMEOUT", default=30000)
CRAWLER_CONCURRENCY = env.int("CRAWLER_CONCURRENCY", default=5)
CRAWLER_HEADLESS = env.bool("CRAWLER_HEADLESS", default=True)
CRAWLER_SCORE_THRESHOLD = env.float("CRAWLER_SCORE_THRESHOLD", default=0.3)

# --- Gate LLM (step 1, runs inside crawl4ai via litellm) -------------------
CRAWLER_MAX_CONTENT_CHARS = env.int(
    "CRAWLER_MAX_CONTENT_CHARS",
    default=12000,
)
CRAWLER_LLM_MODEL = env("CRAWLER_LLM_MODEL", default="openai/gpt-4.1-mini")
CRAWLER_LLM_TEMPERATURE = env.float("CRAWLER_LLM_TEMPERATURE", default=0.0)
