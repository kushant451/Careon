from config.settings import OPENAI_API_KEY, USE_AI
from config.llm_config import LLM_MODEL, LLM_MAX_TOKENS
from utils.logger import get_logger

logger = get_logger(__name__)
_client = None

if USE_AI:
    try:
        from openai import OpenAI
        _client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("OpenAI client initialised (model: %s)", LLM_MODEL)
    except Exception as exc:
        logger.warning("OpenAI init failed → offline fallback. Reason: %s", exc)

def chat(prompt, temperature=0.7):
    if not _client:
        return None
    try:
        response = _client.chat.completions.create(
            model=LLM_MODEL, max_tokens=LLM_MAX_TOKENS,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as exc:
        logger.error("OpenAI API call failed: %s", exc)
        return None