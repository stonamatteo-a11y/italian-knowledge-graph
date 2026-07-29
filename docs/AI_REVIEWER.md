# AI Reviewer

The AI Reviewer produces advisory suggestions about graph content. Suggestions may help
maintainers identify labels, hierarchy placement, isolation, or relationship patterns that
deserve human attention.

The reviewer is not part of canonical validation:

- suggestions never become Validator findings;
- suggestions do not make a graph valid or invalid;
- the reviewer never modifies the Knowledge Graph;
- maintainers decide whether any suggestion should become a reviewed contribution.

The initial provider uses deterministic local heuristics and no AI service. The provider
interface allows future OpenAI, Ollama, or local-model integrations without coupling those
systems to the Validator.

The project authority model remains:

> AI proposes. Validator verifies. Humans decide.
