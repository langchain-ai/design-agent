"""Settings parsing and the exact-id capability registry."""

from __future__ import annotations

import pytest

from design_agent.config import ModelSpec, Settings
from design_agent.models.factory import build_chat_model, resolve_model
from design_agent.models.registry import (
    CAPABILITY_REGISTRY,
    HIGH_EFFORT_MIN_OUTPUT_TOKENS,
    UNKNOWN_MODEL,
    ModelConfigurationError,
    ToolDisclosure,
    capabilities_for,
)


def settings(**values: object) -> Settings:
    return Settings(_env_file=None, **values)  # type: ignore[call-arg]


def test_model_spec_parses_provider_and_gateway() -> None:
    spec = ModelSpec.parse("anthropic:claude-opus-5-5")
    assert (spec.provider, spec.model, spec.via_gateway) == ("anthropic", "claude-opus-5-5", False)
    gateway = ModelSpec.parse("langsmith:anthropic/claude-opus-5-5")
    assert gateway.via_gateway and str(gateway.upstream) == "anthropic:claude-opus-5-5"
    with pytest.raises(ValueError, match="provider:model"):
        ModelSpec.parse("claude-opus-5-5")


def test_lookup_is_exact_never_substring() -> None:
    assert capabilities_for(ModelSpec.parse("anthropic:claude-opus-5-5")).verified
    assert capabilities_for(ModelSpec.parse("anthropic:claude-opus-5-5-preview")) is UNKNOWN_MODEL
    assert capabilities_for(ModelSpec.parse("anthropic:claude-opus")) is UNKNOWN_MODEL


def test_gateway_and_custom_base_url_never_claim_native_search() -> None:
    gateway = capabilities_for(ModelSpec.parse("langsmith:anthropic/claude-opus-5-5"))
    assert gateway.disclosure is ToolDisclosure.PORTABLE_SELECTOR
    proxied = capabilities_for(
        ModelSpec.parse("openai:gpt-6-sol"), base_url="https://proxy.example"
    )
    assert proxied.disclosure is ToolDisclosure.PORTABLE_SELECTOR
    assert (
        capabilities_for(ModelSpec.parse("openai:gpt-6-sol")).disclosure
        is ToolDisclosure.PROVIDER_NATIVE
    )


def test_lead_defaults_to_high_effort_and_look_to_low() -> None:
    s = settings()
    assert resolve_model(s, "lead").effort == "high"
    assert resolve_model(s, "look").effort == "low"


def test_unsupported_effort_is_refused_with_choices() -> None:
    with pytest.raises(ModelConfigurationError, match="choose one of"):
        resolve_model(settings(model_effort="ultra"), "lead")


def test_high_effort_gets_the_output_floor() -> None:
    resolved = resolve_model(settings(model_effort="max"), "lead")
    assert resolved.max_output_tokens is not None
    assert resolved.max_output_tokens >= HIGH_EFFORT_MIN_OUTPUT_TOKENS


def test_models_without_vision_are_refused_for_looking_roles() -> None:
    with pytest.raises(ModelConfigurationError, match="image input"):
        resolve_model(settings(model="mystery:model-1"), "lead")
    with pytest.raises(ModelConfigurationError, match="look"):
        resolve_model(settings(look_model="mystery:model-1"), "look")


def test_anthropic_model_is_built_with_registry_behavior() -> None:
    model = build_chat_model(settings(anthropic_api_key="sk-test"), "lead")
    assert model.max_retries == 0  # type: ignore[attr-defined]
    assert model.max_tokens == 128_000  # type: ignore[attr-defined]
    assert model.effort == "high"  # type: ignore[attr-defined]
    assert model.thinking == {"type": "adaptive"}  # type: ignore[attr-defined]


def test_base_url_requires_a_named_key(monkeypatch: pytest.MonkeyPatch) -> None:
    s = settings(model="openai:gpt-6-sol", model_base_url="https://llm.example/v1")
    with pytest.raises(ModelConfigurationError, match="MODEL_API_KEY_ENV"):
        build_chat_model(s, "lead")
    monkeypatch.setenv("EXAMPLE_KEY", "secret")
    s = settings(
        model="openai:gpt-6-sol",
        model_base_url="https://llm.example/v1",
        model_api_key_env="EXAMPLE_KEY",
    )
    assert build_chat_model(s, "lead").openai_api_base == "https://llm.example/v1"  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    "model_id", sorted(k for k in CAPABILITY_REGISTRY if k.startswith(("anthropic:", "openai:")))
)
def test_registry_agrees_with_installed_provider_profiles(model_id: str) -> None:
    provider, model = model_id.split(":", 1)
    if provider == "anthropic":
        from langchain_anthropic.data._profiles import _PROFILES
    else:
        from langchain_openai.data._profiles import _PROFILES
    profile = _PROFILES.get(model)
    assert profile is not None, f"{model_id} is not a model the installed package knows"
    caps = CAPABILITY_REGISTRY[model_id]
    assert caps.vision == bool(profile.get("image_inputs"))
    assert caps.max_output_tokens == profile.get("max_output_tokens")
    assert caps.context_window == profile.get("max_input_tokens")
    if profile.get("reasoning_effort_levels"):
        assert caps.efforts == frozenset(profile["reasoning_effort_levels"])


def test_secrets_never_appear_in_repr() -> None:
    s = settings(anthropic_api_key="sk-very-secret")
    assert "sk-very-secret" not in repr(s)
    assert "sk-very-secret" not in str(s.model_dump())


def test_brand_path_falls_back_to_the_sample_brand(tmp_path) -> None:  # type: ignore[no-untyped-def]
    (tmp_path / "examples/brands/example-studio").mkdir(parents=True)
    assert settings().resolved_brand_path(tmp_path) == tmp_path / "examples/brands/example-studio"
    (tmp_path / "workspace/brand").mkdir(parents=True)
    (tmp_path / "workspace/brand/brand.toml").write_text("name = 'x'\n")
    assert settings().resolved_brand_path(tmp_path) == tmp_path / "workspace/brand"
