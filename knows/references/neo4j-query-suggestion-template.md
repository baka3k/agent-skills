# Neo4j Query Suggestion Template

`knows` v1 does not execute direct Neo4j queries. It can propose queries for follow-up.

## Output Shape

Use this exact structure:

```text
Neo4j Query Suggestion:
- Mục tiêu:
- Vì sao cần query này:
- Cypher đề xuất:
- Kỳ vọng kết quả:
- Cách diễn giải kết quả:
```

## Pattern A: Find callers of a function

```cypher
MATCH (caller)-[:CALLS*1..4]->(target {name: $function_name})
RETURN caller.name AS caller, target.name AS target
LIMIT 200;
```

## Pattern B: Trace downstream impact

```cypher
MATCH p=(start {name: $entry_name})-[:CALLS|USES|DEPENDS_ON*1..5]->(n)
RETURN p
LIMIT 100;
```

## Pattern C: Locate workflows containing a function

```cypher
MATCH (w:Workflow)-[:HAS_STEP]->(f {symbol_id: $function_id})
RETURN w.name AS workflow, f.name AS function
LIMIT 100;
```

## Guardrails

- Keep query scope bounded (`LIMIT`, depth cap).
- Explain expected columns/nodes before running.
- Do not claim facts from suggested queries that were not executed.
