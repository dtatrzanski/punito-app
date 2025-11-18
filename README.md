# Punito

Punito is an automated GenAI assistant that ingests a Java class, slices it into dependency-aware chunks, and generates comprehensive JUnit 4 + Mockito 3 tests by prompting a hosted Llama 3.3 model through LangChain. The tool is packaged as a Python CLI application so teams can produce incremental, reviewable unit tests that live alongside their source code.【F:pyproject.toml†L1-L14】【F:punito/tests_generator/generator.py†L22-L141】

## Features
- **Chunk-by-chunk planning and generation** – Public methods are expanded into dependency-specific blocks, planned with the `planner_prompt` template, and turned into compilable tests through a second LangChain runnable, keeping plans and code in sync per method.【F:punito/tests_generator/generator.py†L36-L109】【F:punito/resources/prompts/planner_prompt.yaml†L1-L120】
- **LLM endpoint abstraction** – A custom `LlamaChatModel` wraps any HTTP-compatible Llama endpoint (defaulting to the Capgemini-hosted 70B instruct model) and exposes synchronous plus streaming calls to LangChain pipelines.【F:punito/chat_model/llama_chat_model.py†L12-L210】【F:settings.toml†L1-L5】
- **Deterministic post-processing** – Generated snippets are merged into a single `*MockitoTest` file, preserving imports, annotations, mocks, helper methods, and removing near-duplicate test bodies via AST- and hash-based analysis.【F:punito/tests_generator/generator.py†L112-L141】【F:punito/processing/postprocessor.py†L1-L233】
- **Ready-to-run CLI and dev scripts** – `python -m punito` handles the whole flow for a Java file, while scripts in `dev_scripts/` let you debug single functions or entire classes during development.【F:punito/__main__.py†L1-L41】【F:dev_scripts/generate_tests_for_class.py†L1-L21】【F:dev_scripts/plan_and_generate_tests.py†L1-L36】
- **Regression tests for the chunker** – Unit tests built with `unittest` ensure the Java parser correctly resolves nested dependency graphs before code generation starts.【F:punito/tests/processing/test_preprocessor.py†L1-L120】

## Architecture in Brief
1. **CLI entrypoint** – Parses the Java class path and instantiates a timestamped `TestsGenerator`.【F:punito/__main__.py†L1-L41】
2. **Pre-processing** – `punito.processing` builds a dependency-aware map of public methods, associated helper calls, imports, and fields to keep each chunk self-sufficient.【F:punito/tests_generator/generator.py†L112-L128】【F:punito/processing/postprocessor.py†L1-L139】
3. **Prompt pipeline** – Each chunk runs through a two-step LangChain pipeline (`plan` → `tests`) backed by YAML prompts stored in `punito/resources/prompts/`.【F:punito/tests_generator/generator.py†L36-L109】【F:punito/resources/prompts/planner_prompt.yaml†L1-L120】
4. **LLM invocation** – `LlamaChatModel` posts messages to the configured endpoint and streams results back into the runnable chain.【F:punito/chat_model/llama_chat_model.py†L45-L179】
5. **Post-processing & output** – All generated fragments merge into `generated_tests/<pkg_version>/<timestamp>/<ClassName>/`, including per-function artifacts and the final consolidated Mockito test class with duplicate detection.【F:punito/tests_generator/generator.py†L23-L141】【F:punito/processing/postprocessor.py†L1-L233】

## Requirements
- Python 3.12+
- Poetry for dependency management
- Access to an HTTP endpoint serving the configured Llama-compatible model

Runtime dependencies (installed via Poetry) include Dynaconf for configuration, Loguru for logging, httpx for HTTP calls, PyYAML for prompt templating, javalang for Java parsing, and LangChain for orchestration.【F:pyproject.toml†L7-L14】

## Setup
1. **Install dependencies**
   ```bash
   poetry install
   ```
2. **Configure model access** – Update `settings.toml` or provide Dynaconf-compatible environment variables for `BASE_URL`, `MODEL`, and `ENDPOINT` to point at your inference server.【F:settings.toml†L1-L5】【F:punito/chat_model/llama_chat_model.py†L190-L210】
3. **(Optional) Add test fixtures** – Place reusable Mockito examples under `punito/resources/test_examples/` if you want to reference a different seed file than the bundled `PanelControllerExampleMockitoTest.java`. The generator loads this sample automatically when assembling prompts.【F:punito/tests_generator/generator.py†L112-L125】

## Usage
Run the CLI against a Java class:
```bash
poetry run python -m punito path/to/MyClass.java
```
This command writes per-function plans/tests plus a merged `MyClassMockitoTest` file under `generated_tests/<version>/<timestamp>/<ClassName>/tests_per_public_function/`. The structure makes it easy to diff outputs per public method and surface a single ready-to-run test class to reviewers.【F:punito/__main__.py†L1-L41】【F:punito/tests_generator/generator.py†L23-L141】

### Customizing prompts
Update the YAML templates in `punito/resources/prompts/` (e.g., `planner_prompt.yaml` and `tester_prompt.yaml`) to enforce internal conventions around naming, mocking, or verification semantics. Each prompt supports LangChain templating with placeholders such as `execution_function_name`, `tested_function_name`, and `source_code`.【F:punito/tests_generator/generator.py†L36-L91】【F:punito/resources/prompts/planner_prompt.yaml†L1-L120】

### Development helpers
Use the scripts in `dev_scripts/` when you need finer control:
- `generate_tests_for_class.py` runs the full pipeline for a hard-coded class path (handy for smoke tests).【F:dev_scripts/generate_tests_for_class.py†L1-L21】
- `plan_and_generate_tests.py` focuses on a single function, letting you inspect intermediate plan/test artifacts saved under `dev_scripts/debug`.【F:dev_scripts/plan_and_generate_tests.py†L1-L36】

## Repository Layout
```
punito-app/
├── punito/
│   ├── chat_model/        # LlamaChatModel + factory that loads Dynaconf settings
│   ├── processing/        # Java parsing, chunking, and post-processing utilities
│   ├── resources/         # Prompt templates and Mockito example tests
│   ├── tests_generator/   # Generation pipeline, runnables, and helper utilities
│   └── utils/             # Config, IO, and path helpers shared across modules
├── dev_scripts/           # Local debugging helpers for class/function-level runs
├── settings.toml          # Default Dynaconf settings for the model endpoint
├── pyproject.toml         # Poetry project metadata and dependencies
└── README.md
```
Refer to the source files in each directory for detailed docstrings and inline comments.【F:punito/chat_model/llama_chat_model.py†L12-L210】【F:punito/tests_generator/generator.py†L22-L141】【F:punito/resources/prompts/planner_prompt.yaml†L1-L120】

## Testing
Run the Python test suite (currently focused on the preprocessing layer) with:
```bash
poetry run pytest
```
These tests validate the dependency-expansion logic that drives chunk creation, ensuring the downstream LLM sees all required helper methods before generating tests.【F:punito/tests/processing/test_preprocessor.py†L1-L120】

## Troubleshooting
- **Model errors or timeouts** – Confirm the endpoint and credentials defined in `settings.toml` are reachable; `LlamaChatModel` simply forwards HTTP errors from the upstream service.【F:punito/chat_model/llama_chat_model.py†L45-L127】
- **Unexpected or duplicate tests** – Check the per-function outputs saved under `generated_tests/.../tests_per_public_function/` and review the deduplication logs in `punito/processing/postprocessor.py` to tweak prompts or adjust the duplicate-removal heuristics.【F:punito/tests_generator/generator.py†L23-L140】【F:punito/processing/postprocessor.py†L190-L232】
