# External Scouting

For large context windows (1M+ tokens). Use Gemini or OpenCode CLI.

## Tool Selection
SCALE <= 3: gemini CLI | SCALE 4-5: opencode CLI | SCALE >= 6: internal

## Config
Read .claude/.ck.json: gemini.model (default: gemini-3-flash-preview)

## Gemini (SCALE <= 3)
```
gemini -y -m <model> "[prompt]"
```

## OpenCode (SCALE 4-5)
```
opencode run "[prompt]" --model opencode/grok-code
```

## Install Check
`which gemini` / `which opencode`. Not installed -> ask user to install or fallback to internal.

## Timeout
3-minute. Skip timed-out. Don't restart. Persistent failures -> internal.
