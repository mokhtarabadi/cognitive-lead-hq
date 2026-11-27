# Sibling Docs: tests/README.md | Decisions: tests/DECISIONS.md
"""Shared offline double for LiteLLM provider calls in tests.

The Brain bridge sends every turn through ``litellm.responses``. Tests must
never reach the network, so this module exposes one seam: ``install()``
replaces the bridge's ``_litellm_module`` with a fake whose ``responses()``
replays a scripted list of results, mirroring the old fake-http-client shape
(``_FakeResp`` status/text/payload) plus optional raised exceptions.

Real LiteLLM error types are mirrored just closely enough for the bridge's
error translation: provider status, code, body, and message attributes.
"""

from __future__ import annotations

from typing import Any


class FakeProviderResponse:
    """Minimal stand-in for a LiteLLM Responses object.

    Accepts either a Responses-shaped ``payload`` dict (returned verbatim) or
    the old fake-HTTP kwargs (``status_code``/``text``/``payload``) so a test
    can express both success and error cases with one object.
    """

    def __init__(
        self,
        status_code: int = 200,
        text: str = "",
        payload: Any = None,
        *,
        response: Any = None,
    ) -> None:
        self.status_code = status_code
        self.text = text
        self._payload = payload
        self.headers: dict[str, str] = {"content-type": "application/json"}
        self.response = response

    def model_dump(self) -> Any:
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload

    def model_dump_json(self) -> str:
        import json

        return json.dumps(self._payload)


class FakeLiteLLMError(Exception):
    """Mirror of the LiteLLM exception surface the bridge reads."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        code: str | None = None,
        body: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.body = body
        self.response = None


class FakeLiteLLM:
    """Scripted ``litellm`` module: one scripted result per call."""

    def __init__(self, script: list[Any] | None = None) -> None:
        self.script: list[Any] = list(script or [])
        self.calls: int = 0
        self.last_kwargs: dict[str, Any] = {}
        self.all_kwargs: list[dict[str, Any]] = []
        self.suppress_debug_info = False
        self.set_verbose = None

    def responses(self, **kwargs: Any) -> Any:
        self.calls += 1
        self.last_kwargs = kwargs
        self.all_kwargs.append(kwargs)
        if not self.script:
            raise AssertionError("FakeLiteLLM.responses called with an empty script")
        item = self.script.pop(0) if len(self.script) > 1 else self.script[0]
        if isinstance(item, Exception):
            raise item
        return item


def install(
    monkeypatch: Any, script: list[Any] | None = None, bridge: Any = None
) -> FakeLiteLLM:
    """Install the fake LiteLLM on the module under test.

    ``monkeypatch`` is the pytest fixture; ``bridge`` is the imported server
    module. When ``bridge`` is omitted the seam is left untouched and the
    caller patches it — the fake is still returned so the shape matches.
    """
    fake = FakeLiteLLM(script)
    if bridge is not None:
        monkeypatch.setattr(bridge, "_litellm_module", lambda: fake)
    return fake


def responses_payload(text: str = "ok", **extra: Any) -> dict[str, Any]:
    """A minimal Responses-API success body carrying ``text`` as output."""
    payload: dict[str, Any] = {
        "id": "resp_fake",
        "model": "fake-model",
        "status": "completed",
        "output": [
            {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": text}],
            }
        ],
    }
    payload.update(extra)
    return payload
