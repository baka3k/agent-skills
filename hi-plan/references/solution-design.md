# Solution Design Patterns

## Design Output Template

```yaml
architecture:
  overview: "High-level description with Mermaid diagram"
  components:
    - name: "{component_name}"
      responsibility: "{what it does}"
      interfaces: ["{public_api_1}", "{public_api_2}"]
      dependencies: ["{component_x}"]
  data_flow: "How data moves through the system"
  api_contract:
    - endpoint: "{method} {path}"
      input: "{schema}"
      output: "{schema}"
      errors: ["{error_1}", "{error_2}"]

tradeoffs:
  - decision: "{what we chose}"
    alternatives: ["{alt_1}", "{alt_2}"]
    rationale: "{why we chose this}"
    tradeoff: "{what we sacrificed}"
```

## Design Principles

1. **Align with existing patterns** — Don't introduce new architectural styles without justification
2. **Minimize coupling** — New components should depend on existing ones, not vice versa
3. **Design for testability** — Every component should be testable in isolation
4. **Error states first** — Design error handling before happy path
5. **Data ownership** — Each data entity has exactly one owner component

## Design Anti-Patterns (avoid)

- God components that do everything
- Circualr dependencies between modules
- Hidden coupling through shared mutable state
- Implicit assumptions about deployment environment
