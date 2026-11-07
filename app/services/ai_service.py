import httpx

from app.core.config import settings


SYSTEM_PROMPT = """
You are ProofRun, an AI coding assistant.

Generate Python code based on the user's request.

Rules:
- Return only executable Python code.
- Do not use Markdown code fences.
- Do not execute the code.
- Do not include explanations outside the code.
- Keep solutions simple and self-contained.
"""


async def generate_code(prompt: str) -> dict:
    """Generate Python code using the configured AI provider."""

    if settings.ai_provider == "mock":
        return {
            "code": "print('Hello from ProofRun mock mode!')",
            "model": "mock",
            "provider": "mock",
        }

    if settings.ai_provider == "vultr":
        if not settings.vultr_inference_api_key:
            raise RuntimeError("Vultr Inference API key is not configured.")

        payload = {
            "model": settings.vultr_model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 2048,
        }

        headers = {
            "Authorization": f"Bearer {settings.vultr_inference_api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.vultr_base_url.rstrip('/')}/chat/completions",
                headers=headers,
                json=payload,
            )

        response.raise_for_status()
        result = response.json()

        code = result["choices"][0]["message"]["content"]

        if not code or not code.strip():
            raise RuntimeError("Vultr returned an empty code response.")

        return {
            "code": code.strip(),
            "model": settings.vultr_model,
            "provider": "vultr",
        }

    raise RuntimeError(
        f"Unsupported AI provider: {settings.ai_provider}"
    )
