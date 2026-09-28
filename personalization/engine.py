"""Pure transformations for bounded personalization variants."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


ALLOWED_ADAPTATIONS = {
    "language", "text_complexity", "interface_style", "output_modality",
    "response_timing", "runtime_context",
}


class ValidationError(ValueError):
    """Raised when a profile requests a change outside the modeled boundary."""


def validate_agent(agent: dict[str, Any]) -> None:
    states = agent.get("states")
    if not agent.get("name") or not isinstance(states, list) or not states:
        raise ValidationError("An agent needs a name and at least one state.")
    ids = [state.get("id") for state in states]
    if any(not state_id for state_id in ids) or len(ids) != len(set(ids)):
        raise ValidationError("State identifiers must be present and unique.")
    missing = set(agent.get("protected_states", [])) - set(ids)
    if missing:
        raise ValidationError(f"Protected states are not in the model: {sorted(missing)}")


def validate_profile(profile: dict[str, Any]) -> None:
    if not profile.get("id") or not isinstance(profile.get("conditions"), dict):
        raise ValidationError("A profile needs an id and conditions.")
    for adaptation in profile.get("adaptations", []):
        kind = adaptation.get("kind")
        if kind not in ALLOWED_ADAPTATIONS:
            raise ValidationError(f"Unsupported adaptation: {kind!r}")
        if "value" not in adaptation:
            raise ValidationError(f"Adaptation {kind!r} has no value.")


def _simplify(text: str) -> str:
    replacements = {
        "short explanation": "brief description",
        "provide": "give", "practical information": "useful details",
        "explanation": "short description", "collection": "museum",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text


def _translate_to_french(text: str) -> str:
    """Small deterministic catalog for the bundled example; unknown text stays inspectable."""
    catalog = {
        "Welcome to the museum guide. I can help you explore the collection.":
            "Bienvenue dans le guide du musée. Je peux vous aider à explorer le musée.",
        "Ask about an artwork, an artist, or practical information.":
            "Posez une question sur une œuvre, un artiste ou des informations utiles.",
        "I can provide a short explanation of an artwork and suggest a next step.":
            "Je peux donner une courte description d’une œuvre et proposer une prochaine étape.",
    }
    return catalog.get(text, text)


def derive_variant(agent: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    """Apply approved static adaptations and preserve the base model's state structure."""
    validate_agent(agent)
    validate_profile(profile)
    variant = deepcopy(agent)
    variant["profile_id"] = profile["id"]
    variant["profile_conditions"] = deepcopy(profile["conditions"])
    variant["presentation"] = {}
    variant["runtime"] = {}

    adaptations = {item["kind"]: item["value"] for item in profile.get("adaptations", [])}
    for state in variant["states"]:
        replies = list(state.get("replies", []))
        if adaptations.get("language") == "fr":
            replies = [_translate_to_french(reply) for reply in replies]
        if adaptations.get("text_complexity") == "simple":
            replies = [_simplify(reply) for reply in replies]
        state["replies"] = replies

    for key in ("interface_style", "output_modality"):
        if key in adaptations:
            variant["presentation"][key] = deepcopy(adaptations[key])
    for key in ("response_timing", "runtime_context"):
        if key in adaptations:
            variant["runtime"][key] = adaptations[key]
    return variant
