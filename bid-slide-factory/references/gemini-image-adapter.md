# Gemini Image Adapter

Model resolution order:

1. List available models from Gemini API (if API key and model list access available).
2. If unavailable, parse latest names from official docs/changelog.
3. Select the first available image-capable model.
4. On error or quota/rate limit, emit fallback image directives and continue deck generation.

Fallback policy:

- Use neutral placeholder visuals.
- Keep citation slide unchanged.
- Mark image fidelity as `degraded` in run metadata.
