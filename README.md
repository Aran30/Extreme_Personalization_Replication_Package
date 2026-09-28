# Extreme Personalization Replication Package

This repository is a compact, self-contained proof of concept for the pipeline in *Extreme Personalization: Engineering Software Around Its Users*.

It demonstrates five ideas from the paper:

1. Explicit, reusable user-profile models.
2. Adaptations attached to profiles rather than mixed into the base application.
3. Bounded derivation of inspectable, profile-specific variants.
4. Deterministic generation of runnable conversational-agent implementations.
5. Runtime selection of the active profile and a constrained context for generative replies.

The compact reference implementation in `personalization/` uses only the Python standard library. It is accompanied by the full local editor implementation below, without imported Git history or references to the earlier replication package.

## Full editor implementation

The runnable proof-of-concept editor and its runtime are included locally:

- `BESSER-WEB-MODELING-EDITOR/` provides the browser-based modeling editor.
- `BESSER/` provides model handling, profile-aware derivation, and code generation.
- `BESSER-AGENTIC-FRAMEWORK/` executes generated agents.
- `example_agent/` is a generated personalized agent and its profile data.

Start the editor, backend, and local database with Docker:

```powershell
docker compose up --build
```

Then open `http://localhost:8080`. The backend is available on port 9000. Copy `.env.example` to `.env` and set `OPENAI_API_KEY` only if you use an editor feature that invokes a language model. Stop the stack with `docker compose down`.

To run the bundled generated agent without containers, install the included runtime and supply the required configuration values in `example_agent/config.ini`:

```powershell
pip install .\BESSER-AGENTIC-FRAMEWORK
python .\example_agent\Agent_Diagram.py
```

The included third-party-platform source remains under the MIT license in [LICENSE](LICENSE); the file retains the required notice for these copied components.

## Quick start

Requires Python 3.11 or later.

```powershell
python -m unittest discover -s tests -v
python -m personalization.pipeline examples\agent.json examples\profiles.json --output output
python output\agents\older_french_reader.py --profile older_french_reader --message "Tell me about the exhibit"
```

The pipeline writes the derived variants to `output/variants/` before it generates the runnable agents in `output/agents/`. Review the JSON variants before using generated artifacts in a production setting.

## Model boundary

The base agent declares `protected_states`. A profile adaptation may change only approved response text, presentation settings, modalities, timing, or the runtime context. Attempting to replace a protected state or use an unsupported adaptation fails validation. This makes the permitted personalization boundary executable rather than documentary.

`runtime_context` is intentionally data, not an automatic external-model call. A host application can pass it to an approved model provider at runtime; doing so remains a deployment decision.

## Layout

- `examples/` - base-agent and profile inputs.
- `personalization/` - derivation, validation, generation, and command-line pipeline.
- `tests/` - executable checks for the core invariants.
- `output/` - generated artifacts (created locally and ignored by Git).
