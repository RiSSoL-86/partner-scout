from django_project.settings import env

CRAWLER_MAX_PAGES = env.int("CRAWLER_MAX_PAGES", default=1500)
CRAWLER_PAGE_TIMEOUT = env.int("CRAWLER_PAGE_TIMEOUT", default=30000)
CRAWLER_CONCURRENCY = env.int("CRAWLER_CONCURRENCY", default=5)
CRAWLER_HEADLESS = env.bool("CRAWLER_HEADLESS", default=True)
CRAWLER_LLM_MODEL = env("CRAWLER_LLM_MODEL", default="openai/gpt-4.1-mini")
CRAWLER_LLM_TEMPERATURE = env.float("CRAWLER_LLM_TEMPERATURE", default=0.0)
