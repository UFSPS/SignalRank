"""AI service wrapper for the bot.

This module exposes a single async function `generate_answer(prompt)` which will
attempt to call Google GenAI (if installed and configured via environment
variables). If the GenAI library or API key is missing, it returns a safe
fallback message so the bot remains functional during development.

Environment variables (recommended in `.env`):
- GENAI_API_KEY or GOOGLE_API_KEY : your GenAI API key
- GENAI_MODEL (optional) : model name, defaults to 'gpt-5-mini'

The implementation tries a couple of common import paths for the official
Google generative AI libraries but falls back gracefully if those imports fail.
"""

import os
import asyncio
from typing import Optional

# We try not to hard-fail at import time so the project can run without the
# 3rd-party `google-genai` package. We'll detect availability at runtime.
_GENAI_AVAILABLE = False
_GENAI_IMPORT_ERROR = None

# Try the modern, commonly used import path
from google import genai as _ggen
_GENAI_AVAILABLE = True


async def generate_answer(prompt: str, model: Optional[str] = None) -> str:
	"""Generate an answer for the given prompt using Google GenAI.

	Returns a string response. If the GenAI package or API key is missing,
	returns a helpful fallback message that includes the original prompt (trimmed).
	"""
	model = model or os.getenv("GENAI_MODEL") or "gpt-5-mini"
	api_key = os.getenv("GENAI_API_KEY") or os.getenv("GOOGLE_API_KEY")

	if not _GENAI_AVAILABLE or not api_key:
		short_prompt = (prompt[:500] + "...") if len(prompt) > 500 else prompt
		reason = "missing google-genai package" if not _GENAI_AVAILABLE else "missing API key"
		return (
			f"[AI unavailable: {reason}]\n"
			"To enable AI responses, install `google-genai` and set `GENAI_API_KEY` in your .env.\n"
			f"Prompt received: {short_prompt}"
		)

	# Offload the blocking network call to a thread so we don't block the event loop
	loop = asyncio.get_running_loop()

	def _call_genai():
		try:
			# Prefer the newer client-style API (google.genai)
			Client = getattr(_ggen, "Client", None)
			if Client:
				client = Client(api_key=api_key)
				try:
					# Preferred call for google.genai: client.models.generate_content
					resp = client.models.generate_content(model=model, contents=prompt)
					return getattr(resp, "text", getattr(resp, "content", str(resp)))
				except Exception as e:
					# If model not found (404), try listing available models and pick a compatible one
					err_str = str(e)
					if "not found" in err_str.lower() or "listmodels" in err_str.lower() or "listmodels" in err_str:
						try:
							models_resp = client.models.list_models()
							# Normalize iterable of model descriptors
							if hasattr(models_resp, "models"):
								iter_models = models_resp.models
							elif isinstance(models_resp, (list, tuple)):
								iter_models = models_resp
							elif hasattr(models_resp, "__iter__"):
								iter_models = list(models_resp)
							else:
								iter_models = [models_resp]
							candidates = []
							for m in iter_models:
								name = getattr(m, "name", getattr(m, "model", None))
								methods = getattr(m, "supported_methods", None) or getattr(m, "methods", None) or getattr(m, "capabilities", None)
								methods_text = "" if methods is None else str(methods).lower()
								# Prefer models that explicitly support content/text generation
								if methods_text and ("generate" in methods_text or "content" in methods_text or "text" in methods_text):
									candidates.append(name)
								elif name and any(tok in name.lower() for tok in ("gemini", "chat", "text", "flan", "flash")):
									candidates.append(name)
							# fallback collects first available name
							if not candidates:
								# try generic extraction of names as a final fallback
								names = [getattr(x, "name", None) or getattr(x, "model", None) for x in iter_models]
								chosen = next((n for n in names if n), None)
							else:
								chosen = candidates[0]
							if chosen:
								resp2 = client.models.generate_content(model=chosen, contents=prompt)
								return getattr(resp2, "text", getattr(resp2, "content", str(resp2)))
						except Exception as e2:
							# Return both errors for debugging
							return f"[GenAI list_models retry failed] original: {e} ; list_models error: {e2}"
					# If it's some other client error, fall through to generic error handling
					return f"[GenAI client error] {e}"
			# Fall back to the older library surface if present
			try:
				_ggen.configure(api_key=api_key)
				resp = _ggen.generate_text(model=model, prompt=prompt)
				return getattr(resp, "text", getattr(resp, "content", str(resp)))
			except Exception:
				# Try an alternative: some versions use a `Client` object with different shape
				ClientAlt = getattr(_ggen, "Client", None)
				if ClientAlt:
					client_alt = ClientAlt(api_key=api_key)
					resp = client_alt.generate_text(model=model, prompt=prompt)
					return getattr(resp, "text", getattr(resp, "content", str(resp)))
				# If we reach here, raise to be caught below
				raise
		except Exception as e:
			return f"[GenAI call failed] {e}"

	result = await loop.run_in_executor(None, _call_genai)
	# Ensure the returned value is a plain string
	return str(result)
