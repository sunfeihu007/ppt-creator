# AGY Native Image Routing Design

**Date:** 2026-07-25  
**Target release:** v2.2.0  
**Status:** Strategy approved; written design pending final review

## 1. Objective

Update PPT Creator so that image generation follows the host client's native capability by default:

1. In AGY CLI, use AGY's built-in `generate_image` tool and its Gemini image model.
2. In Codex, use Codex's built-in `image_gen` tool.
3. In other clients, use the Gemini API when a Google API key is configured.
4. Keep AGY CLI and Codex CLI subprocess routes available only as explicit compatibility bridges, not as default routes.
5. Prevent a presentation from silently mixing image providers or models.

The README, skill instructions, scripts, tests, and installed local copies must describe and implement the same behavior.

## 2. Confirmed capabilities

### AGY CLI

- AGY exposes a native `generate_image` tool.
- Current local AGY records show that this tool uses `gemini-3.1-flash-image`, the Nano Banana 2 / Flash image model.
- The native tool accepts a prompt, aspect ratio, and image name, and saves the result beneath AGY's image workspace.
- The current tool schema does not expose a model selector or a dedicated reference-image field.
- AGY's non-interactive `agy -p` path exists, but local smoke tests returned no usable output. It must therefore be treated as an experimental bridge rather than the default AGY path.

### Codex

- Codex exposes a native `image_gen` tool backed by the Codex image-generation capability.
- This native route remains the default inside Codex.
- Codex must not invoke AGY merely because AGY is installed.

### Other clients

- Other clients use the Gemini API through `scripts/gen_image.py`.
- The default Gemini model changes from the preview identifier to the stable `gemini-3.1-flash-image`.
- `GOOGLE_API_KEY` or `GEMINI_API_KEY` is required for this route.

## 3. Routing model

Routing is capability-based and is decided before the first page image is generated.

| Environment or explicit choice | Default transport | Default model | Credential |
|---|---|---|---|
| AGY with native `generate_image` | AGY native tool | `gemini-3.1-flash-image` | AGY account/session |
| Codex with native `image_gen` | Codex native tool | Codex built-in image model | Codex account/session |
| Other client | Gemini API | `gemini-3.1-flash-image` | Google API key |
| Explicit `--provider agy` bridge | `agy -p` subprocess | AGY native image model | AGY account/session |
| Explicit `--provider codex` bridge | Codex CLI subprocess | Codex image model | Codex account/session |

The skill instructions, rather than an unreliable environment variable, determine whether the current agent has an AGY-native or Codex-native image tool.

### Default selection

1. If the current agent has AGY's native `generate_image`, select and lock `agy/native`.
2. Otherwise, if the current agent has Codex's native `image_gen`, select and lock `codex/native`.
3. Otherwise, select `gemini/api` only when a supported API key is available.
4. If none is available, stop before image production and report the exact configuration needed.

### Explicit bridges

- `--provider agy` invokes the AGY CLI bridge and runs a preflight check before generating images.
- `--provider codex` invokes the existing Codex CLI bridge.
- These bridges are opt-in and are never preferred by `auto` when the host has a native tool.
- An explicitly selected provider fails clearly if it is unavailable; it does not silently switch models.

## 4. Provider locking and fallback

The provider, transport, and model are written to `plan.json` before parallel image generation starts.

- Fallback is allowed only during preflight and only for `auto`.
- Once the provider is locked, every page in that run uses the same provider/model combination.
- A mid-run provider failure stops the affected work and reports the error.
- Switching providers after generation has begun requires an explicit user decision and a new generation run.
- The skill must never quietly mix AGY, Gemini API, and Codex images within one presentation.

This keeps visual style reproducible and preserves the existing style/color compatibility rules.

## 5. Data model

The plan state gains optional image-generation metadata:

```json
{
  "provider": "agy",
  "image_transport": "native",
  "image_model": "gemini-3.1-flash-image"
}
```

Allowed logical providers are `agy`, `codex`, and `gemini`. Allowed transports are `native`, `cli`, and `api`.

Backward compatibility requirements:

- Existing plans containing only `provider: "codex"` or `provider: "gemini"` continue to load.
- Missing `image_transport` and `image_model` fields are inferred from the selected route.
- State migration must not rewrite unrelated plan content.

Only the main coordinating agent writes `plan.json`. Parallel image workers use `--no-state` or return results to the coordinator.

## 6. Implementation structure

### Skill instructions

Update `SKILL.md` and the image-generation phase guidance to:

- explain the three default environments;
- direct AGY agents to call native `generate_image`;
- direct Codex agents to call native `image_gen`;
- direct other clients to the Gemini API;
- perform provider preflight and lock before sample generation;
- document the AGY native tool's current reference-image limitation;
- preserve the sample approval and QA gates.

### Scripts

Refactor provider-specific logic out of the orchestration path:

- `scripts/gen_image.py` remains the command-line entry point and owns common validation/post-processing.
- `scripts/image_providers.py` owns availability checks and CLI/API adapters.
- The AGY bridge creates a unique image name, runs `agy -p`, locates the generated artifact, and normalizes it to the requested output path.
- Native AGY and native Codex calls remain agent-tool operations; the script records/imports their outputs rather than pretending it can directly call those in-process tools.
- Common post-processing normalizes generated JPEG/PNG output into the expected workspace format.

### Concurrency

- AGY native workers use unique names derived from page IDs to avoid image collisions.
- Codex native workers retain the existing parallel-worker pattern.
- Gemini API workers continue using isolated `--no-state` execution.
- The coordinator performs the only plan-state update after results are verified.

## 7. Error handling

- Missing Google API key: fail before generation with the supported environment-variable names.
- Missing AGY or Codex CLI for an explicit bridge: fail with an installation/action message.
- AGY print-mode health check failure: mark the bridge unavailable and do not create partial page output.
- Native tool output not found: report the expected image name and searched location.
- Unsupported model or provider value: fail validation before any image request.
- Output normalization failure: retain the original artifact path in the error for recovery.

No credentials, OAuth tokens, or API-key values may be written to `plan.json`, logs, README examples, or test fixtures.

## 8. Testing and verification

Automated tests will cover:

- capability and credential detection;
- default routing for AGY, Codex, and other clients;
- stable Gemini model selection;
- provider locking and no mid-run silent fallback;
- backward-compatible plan loading;
- explicit AGY/Codex bridge failures;
- AGY output discovery and image normalization;
- command construction without exposing credentials.

External image generation is excluded from the normal test suite. An opt-in AGY smoke test may run only when explicitly enabled, so routine tests do not consume credits or depend on an interactive session.

Release verification includes:

1. Python/unit tests.
2. Skill structure and plan validation checks.
3. README command/example review.
4. Clean Git status after commit.
5. Local Codex and AGY skill-copy synchronization.
6. Push of the completed v2.2.0 changes to GitHub `main`.

## 9. Documentation changes

README will include:

- a three-environment routing table;
- the default models and credential requirements;
- AGY native usage and the Nano Banana 2 model identity;
- Codex native ImageGen behavior;
- Gemini API setup for other clients;
- explicit bridge examples and their non-default/experimental status;
- the no-mixed-provider rule;
- migration notes from v2.1.1.

Version references in README, `SKILL.md`, and any package metadata will be synchronized to v2.2.0.

## 10. Non-goals

This release will not:

- make the AGY CLI bridge the default inside Codex;
- force AGY's Pro image model when its native tool selects Flash;
- reverse-engineer AGY's internal transport;
- introduce an unofficial third-party Gemini wrapper;
- add or alter PPT styles or color palettes.

The requested style and palette research will be performed after v2.2.0 is implemented and pushed. It will compare Huashu Design, Guizang PPT Skill, and PPT Master and will produce recommendations only.

## 11. Acceptance criteria

The work is complete when:

- AGY instructions default to its native Gemini image tool;
- Codex instructions default to native Codex ImageGen;
- other clients use the stable Gemini Flash image model through an API key;
- explicit CLI bridges remain available without becoming defaults;
- provider/model locking prevents silent visual-provider mixing;
- tests and validation checks pass;
- README and version references are current;
- local Codex and AGY installations match the repository;
- the completed release is committed and pushed to GitHub `main`;
- a separate style/color recommendation is delivered without changing current style files.

## 12. Research references

- [Google Codelab: Build an agent with Companion and AGY CLI](https://codelabs.developers.google.com/companion-adk-beginner/instructions)
- [Google Codelab: Antigravity CLI hands-on](https://codelabs.developers.google.com/antigravity-cli-hands-on)
- [Gemini API image generation documentation](https://ai.google.dev/gemini-api/docs/image-generation)
- [OpenAI GPT Image 2 model documentation](https://developers.openai.com/api/docs/models/gpt-image-2)
