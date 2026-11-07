
import httpx
import pytest

from app.services import ai_service


@pytest.mark.asyncio
async def test_mock_provider_returns_code(monkeypatch):
    monkeypatch.setattr(ai_service.settings, "ai_provider", "mock")

    result = await ai_service.generate_code("Print hello")

    assert result["provider"] == "mock"
    assert result["model"] == "mock"
    assert "print(" in result["code"]


def test_clean_generated_code_removes_markdown_fence():
    content = "```python\nprint('Hello')\n```"

    result = ai_service.clean_generated_code(content)

    assert result == "print('Hello')"


def test_clean_generated_code_preserves_normal_code():
    content = "print('Hello')"

    result = ai_service.clean_generated_code(content)

    assert result == content


def test_clean_generated_code_rejects_empty_content():
    with pytest.raises(ai_service.AIServiceError):
        ai_service.clean_generated_code("   ")


def test_clean_generated_code_rejects_non_string():
    with pytest.raises(ai_service.AIServiceError):
        ai_service.clean_generated_code(None)


def test_clean_generated_code_rejects_oversized_content():
    content = "x" * (ai_service.MAX_GENERATED_CODE_BYTES + 1)

    with pytest.raises(ai_service.AIServiceError):
        ai_service.clean_generated_code(content)


@pytest.mark.asyncio
async def test_vultr_provider_returns_generated_code(monkeypatch):
    monkeypatch.setattr(ai_service.settings, "ai_provider", "vultr")
    monkeypatch.setattr(
        ai_service.settings,
        "vultr_inference_api_key",
        "test-api-key",
    )
    monkeypatch.setattr(ai_service.settings, "vultr_model", "test-model")

    async def mock_post(self, url, **kwargs):
        assert url.endswith("/chat/completions")
        assert kwargs["headers"]["Authorization"] == "Bearer test-api-key"

        return httpx.Response(
            200,
            request=httpx.Request("POST", url),
            json={
                "choices": [
                    {
                        "message": {
                            "content": "print('Hello from Vultr')"
                        }
                    }
                ]
            },
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    result = await ai_service.generate_code("Print hello")

    assert result["code"] == "print('Hello from Vultr')"
    assert result["model"] == "test-model"
    assert result["provider"] == "vultr"


@pytest.mark.asyncio
async def test_vultr_provider_rejects_unexpected_response(monkeypatch):
    monkeypatch.setattr(ai_service.settings, "ai_provider", "vultr")
    monkeypatch.setattr(
        ai_service.settings,
        "vultr_inference_api_key",
        "test-api-key",
    )

    async def mock_post(self, url, **kwargs):
        return httpx.Response(
            200,
            request=httpx.Request("POST", url),
            json={"unexpected": "response"},
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    with pytest.raises(ai_service.AIServiceError):
        await ai_service.generate_code("Print hello")


@pytest.mark.asyncio
async def test_vultr_provider_handles_timeout(monkeypatch):
    monkeypatch.setattr(ai_service.settings, "ai_provider", "vultr")
    monkeypatch.setattr(
        ai_service.settings,
        "vultr_inference_api_key",
        "test-api-key",
    )

    async def mock_post(self, url, **kwargs):
        raise httpx.ReadTimeout("Request timed out")

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    with pytest.raises(
        ai_service.AIServiceError,
        match="timed out",
    ):
        await ai_service.generate_code("Print hello")


@pytest.mark.asyncio
async def test_vultr_provider_handles_http_error(monkeypatch):
    monkeypatch.setattr(ai_service.settings, "ai_provider", "vultr")
    monkeypatch.setattr(
        ai_service.settings,
        "vultr_inference_api_key",
        "test-api-key",
    )

    async def mock_post(self, url, **kwargs):
        return httpx.Response(
            401,
            request=httpx.Request("POST", url),
            json={"error": "Unauthorized"},
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    with pytest.raises(
        ai_service.AIServiceError,
        match="HTTP 401",
    ):
        await ai_service.generate_code("Print hello")


@pytest.mark.asyncio
async def test_vultr_provider_rejects_empty_code(monkeypatch):
    monkeypatch.setattr(ai_service.settings, "ai_provider", "vultr")
    monkeypatch.setattr(
        ai_service.settings,
        "vultr_inference_api_key",
        "test-api-key",
    )

    async def mock_post(self, url, **kwargs):
        return httpx.Response(
            200,
            request=httpx.Request("POST", url),
            json={
                "choices": [
                    {"message": {"content": "   "}}
                ]
            },
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    with pytest.raises(ai_service.AIServiceError):
        await ai_service.generate_code("Print hello")
