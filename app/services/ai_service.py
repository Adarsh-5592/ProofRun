
import httpx

from app.core.config import settings


SYSTEM_PROMPT = """
You are ProofRun, an AI coding assistant.

Generate Python code based on the user's request.

Rules:
- Return only executable Python code.
- Do not execute the code.
- Do not include explanations outside the code.
- Do not use Markdown code fences.
- Keep solutions simple and self-contained.
- Avoid unnecessary external dependencies.
"""

MAX_GENERATED_CODE_BYTES = 256 * 1024


class AIServiceError(Exception):
    """Raised when code generation fails."""


def clean_generated_code(content: str) -> str:
    """Validate and clean the generated Python code."""

    if not isinstance(content, str):
        raise AIServiceError("AI returned an invalid response.")

    code = content.strip()

    if not code:
        raise AIServiceError("AI returned empty code.")

    # Remove Markdown fences only when they wrap the entire response.
    lines = code.splitlines()

    if (
        len(lines) >= 3
        and lines[0].strip().startswith("```")
        and lines[-1].strip() == "```"
    ):
        code = "\n".join(lines[1:-1]).strip()

    if not code:
        raise AIServiceError("AI returned empty code.")

    if len(code.encode("utf-8")) > MAX_GENERATED_CODE_BYTES:
        raise AIServiceError("Generated code exceeds the maximum allowed size.")

    return code


async def generate_code(prompt: str) -> dict:
    """Generate Python code using the configured AI provider."""

    if not isinstance(prompt, str) or not prompt.strip():
        raise AIServiceError("A valid prompt is required.")

    if settings.ai_provider == "mock":
        return {
            "code": "print('Hello from ProofRun mock mode!')",
            "model": "mock",
            "provider": "mock",
        }

    if settings.ai_provider != "vultr":
        raise AIServiceError("Unsupported AI provider.")

    if not settings.vultr_inference_api_key:
        raise AIServiceError("Vultr Inference API key is not configured.")

    payload = {
        "model": settings.vultr_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt.strip()},
        ],
        "temperature": 0.2,
        "max_tokens": 2048,
    }

    headers = {
        "Authorization": f"Bearer {settings.vultr_inference_api_key}",
        "Content-Type": "application/json",
    }

    timeout = httpx.Timeout(
        connect=10.0,
        read=60.0,
        write=10.0,
        pool=10.0,
    )

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{settings.vultr_base_url.rstrip('/')}/chat/completions",
                headers=headers,
                json=payload,
            )

            response.raise_for_status()

        result = response.json()

    except httpx.TimeoutException as exc:
        raise AIServiceError("Vultr inference request timed out.") from exc

    except httpx.HTTPStatusError as exc:
        raise AIServiceError(
            f"Vultr inference returned HTTP {exc.response.status_code}."
        ) from exc

    except httpx.RequestError as exc:
        raise AIServiceError("Could not connect to Vultr inference.") from exc

    except ValueError as exc:
        raise AIServiceError("Vultr returned an invalid JSON response.") from exc

    try:
        choices = result["choices"]
        message = choices[0]["message"]
        content = message["content"]

    except (KeyError, IndexError, TypeError):
        raise AIServiceError("Vultr returned an unexpected response format.")

    code = clean_generated_code(content)

    return {
        "code": code,
        "model": settings.vultr_model,
        "provider": "vultr",
    }
