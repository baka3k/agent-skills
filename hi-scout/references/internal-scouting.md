# Internal Scouting

Use when external tools unavailable or SCALE >= 6.

## Prompt Template
```
Quickly scout {DIRECTORY} for: {TARGET}
Use Glob/Grep. List files with descriptions. Timeout 3m.
Report: ## Found Files + path/file.ext - description
```

## Directory Division
src/ | lib/ | tests/ | config/ | api/ | types/
No overlap. Spawn all in single message.

## File Chunking
<500 lines: read entire
500-1500: 2-3 chunks via Bash sed
>1500: ceil(lines/500) chunks

## Timeout
3 min per agent. Skip non-responders. Deduplicate paths.
