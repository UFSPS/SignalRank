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
try:
	# Try the modern, commonly used import path
	from google import generativeai as _ggen
	_GENAI_AVAILABLE = True
except Exception as e1:
	try:
		# Some distributions expose a top-level `genai` or `google_genai` name.
		import genai as _ggen
		_GENAI_AVAILABLE = True
	except Exception as e2:
		_GENAI_AVAILABLE = False
		_GENAI_IMPORT_ERROR = (e1, e2)


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
			# Try to configure and call the commonly used `google.generativeai` API
			try:
				# configure with API key
				_ggen.configure(api_key=api_key)
				# preferred API: generate_text
				resp = _ggen.generate_text(model=model, prompt=prompt)
				# many wrappers place the text under `text` or `content`
				return getattr(resp, "text", getattr(resp, "content", str(resp)))
			except Exception:
				# Try an alternative: some versions use a `Client` object
				Client = getattr(_ggen, "Client", None)
				if Client:
					client = Client(api_key=api_key)
					resp = client.generate_text(model=model, prompt=prompt)
					return getattr(resp, "text", getattr(resp, "content", str(resp)))
				# If we reach here, raise to be caught below
				raise
		except Exception as e:
			return f"[GenAI call failed] {e}"

	result = await loop.run_in_executor(None, _call_genai)
	# Ensure the returned value is a plain string
	return str(result)
