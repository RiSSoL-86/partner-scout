from django_project.settings import env

AGGREGATOR_LLM_MODEL = env("AGGREGATOR_LLM_MODEL", default="gpt-4.1-mini")
AGGREGATOR_LLM_TEMPERATURE = env.float(
    "AGGREGATOR_LLM_TEMPERATURE",
    default=0.0,
)
AGGREGATOR_LLM_BATCH_SIZE = env.int(
    "AGGREGATOR_LLM_BATCH_SIZE",
    default=25,
)
