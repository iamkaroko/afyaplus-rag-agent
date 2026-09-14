# AfyaPlus RAG Agent

An enterprise-style Retrieval-Augmented Generation (RAG) agent for medical insurance verification, clinical routing, and deterministic medication calculations.

The project combines **LangChain** for agent orchestration with **LlamaIndex** for grounded knowledge retrieval. It also includes a privacy middleware that masks supported personally identifiable information (PII) before requests reach the language model and restores approved values only at the final output boundary.

> This project was developed as an AI Engineering capstone and uses synthetic AfyaPlus policy and clinical data for demonstration purposes.

---

## Overview

The AfyaPlus RAG Agent is designed to answer questions within three supported domains:

* AfyaPlus insurance policies and coverage
* Clinical routing guidelines
* Medication volume calculations

Instead of allowing the language model to answer these questions entirely from its general knowledge, the system provides the model with controlled capabilities.

Policy and clinical questions are grounded against a local AfyaPlus knowledge base using RAG. Medication arithmetic is delegated to a deterministic calculation tool. Conversation history is maintained across turns, while supported PII is masked before entering the model-facing pipeline.

The result is a system designed around four principles:

1. **Ground responses in approved knowledge**
2. **Use deterministic tools where calculation is required**
3. **Maintain conversational context**
4. **Minimise exposure of supported PII to the language model**

---

## Architecture

The request pipeline is:

```text
Raw User Input
      │
      ▼
┌──────────────────────┐
│ Privacy Middleware   │
│                      │
│ Email → [EMAIL_1]    │
│ Phone → [PHONE_1]    │
└──────────┬───────────┘
           │
           │ Masked input
           ▼
┌──────────────────────┐
│ LangChain Agent      │
│                      │
│ ┌──────────────────┐ │
│ │ Conversation     │ │
│ │ Memory           │ │
│ └──────────────────┘ │
│                      │
│ ┌──────────────────┐ │
│ │ LlamaIndex RAG   │ │
│ └──────────────────┘ │
│                      │
│ ┌──────────────────┐ │
│ │ Medication Tool  │ │
│ └──────────────────┘ │
└──────────┬───────────┘
           │
           │ Grounded response
           ▼
┌──────────────────────┐
│ PII De-masking       │
└──────────┬───────────┘
           │
           ▼
    User-facing Output
```

The `AfyaPlusService` acts as the application-level orchestration boundary. It coordinates privacy masking, conversation memory, agent execution, and final response de-masking.

The LangChain agent then decides whether a request requires knowledge retrieval, deterministic calculation, conversational context, or a scope-limited response.

---

## Features

### Privacy-Masking Middleware

The privacy layer detects supported Kenyan PII before model invocation.

Currently supported:

* Email addresses
* Kenyan mobile phone numbers

Examples:

```text
ken@example.com
        ↓
[EMAIL_1]

0712345678
        ↓
[PHONE_1]

+254 712 345 678
        ↓
[PHONE_2]
```

Placeholders are unique within a conversation session.

The original values remain in an application-side mapping and are not intentionally inserted into the LLM-facing conversation history.

---

### Grounded RAG Pipeline

AfyaPlus policy and clinical knowledge is loaded from local Markdown documents and indexed using LlamaIndex.

The pipeline performs:

```text
Knowledge Documents
       ↓
Document Loading
       ↓
Sentence-aware Chunking
       ↓
OpenAI Embeddings
       ↓
Vector Index
       ↓
Local Persistence
       ↓
Semantic Retrieval
```

The knowledge base currently contains synthetic documents covering:

* Insurance policy
* Clinical routing
* Medication guidelines

The vector index is persisted locally so the knowledge base does not need to be rebuilt every time the application starts.

---

### LangChain Agent Orchestration

LangChain provides the orchestration layer.

The agent has access to a deliberately small tool space:

```text
search_afyaplus_knowledge
calculate_medication_volume
```

This avoids unnecessary tool overload and keeps tool selection predictable.

The agent is instructed to use retrieval for AfyaPlus policy and clinical questions rather than substituting general model knowledge when the local knowledge base does not contain an answer.

Out-of-domain questions are rejected rather than answered from unrestricted model knowledge.

---

### Deterministic Medication Calculations

Medication arithmetic is handled by a structured LangChain tool instead of relying on language-model arithmetic.

The calculation is:

```text
volume_ml = prescribed_dose_mg / concentration_mg_per_ml
```

For example:

```text
Prescribed dose: 500 mg
Concentration: 250 mg/mL

500 / 250 = 2.00 mL
```

The tool validates inputs and rejects:

* Zero doses
* Negative doses
* Zero or negative concentrations
* Invalid numeric inputs

Missing clinical values should be clarified rather than guessed.

The calculation tool performs arithmetic only. Its output should not be interpreted as a prescription or independent treatment recommendation.

---

### Stateful Conversation Memory

The application maintains conversation history for the active session.

For example:

```text
User:
What is the outpatient MRI co-payment?

Assistant:
The standard outpatient MRI co-payment is KES 2,000.

User:
Does it require prior authorisation?
```

The second question can be interpreted in the context of the first because the previous conversation messages are supplied to the agent.

Conversation memory stores the **masked representation** of supported PII rather than the raw value.

---

### Scope Guardrails

The agent is restricted to:

* AfyaPlus insurance
* Clinical routing
* Supported medication calculations

For example:

```text
Who won the FIFA World Cup in 2010?
```

is outside the supported domain and should be rejected.

This reduces the risk of the system silently switching from grounded AfyaPlus information to unrelated general model knowledge.

---

## Project Structure

```text
afyaplus-rag-agent/
├── app/
│   ├── __init__.py
│   ├── agent.py
│   ├── config.py
│   ├── memory.py
│   ├── privacy.py
│   ├── rag.py
│   ├── service.py
│   └── tools.py
│
├── knowledge/
│   ├── clinical_routing.md
│   ├── insurance_policy.md
│   └── medication_guidelines.md
│
├── scripts/
│   ├── build_index.py
│   ├── test_agent.py
│   └── test_retrieval.py
│
├── tests/
│   ├── test_agent.py
│   ├── test_memory.py
│   ├── test_privacy.py
│   ├── test_rag.py
│   ├── test_service.py
│   └── test_tools.py
│
├── .env.example
├── .gitignore
├── main.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

### Component Responsibilities

| Component    | Responsibility                                         |
| ------------ | ------------------------------------------------------ |
| `privacy.py` | Masks and restores supported PII                       |
| `rag.py`     | Loads, indexes, persists, and retrieves knowledge      |
| `tools.py`   | Exposes retrieval and deterministic calculation tools  |
| `memory.py`  | Maintains conversation history                         |
| `agent.py`   | Configures and executes the LangChain agent            |
| `service.py` | Coordinates the complete privacy-safe request pipeline |
| `config.py`  | Loads environment configuration                        |
| `main.py`    | Provides the interactive CLI                           |

---

## Requirements

* Python 3.11+
* OpenAI API key

---

## Setup

Clone the repository:

```bash
git clone <repository-url>
cd afyaplus-rag-agent
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Install the project in editable mode:

```bash
pip install -e .
```

This allows scripts executed from the repository to import the `app` package consistently.

---

## Environment Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Configure:

```text
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-4o-mini
```

The `.env` file is excluded from Git and should never be committed.

---

## Building the Knowledge Index

The RAG index can be built explicitly using:

```bash
python scripts/build_index.py
```

The generated index is persisted under:

```text
storage/
```

The `storage/` directory is excluded from Git because it contains generated vector-index artifacts.

The application can also build the index when no persisted index is available.

---

## Running the Application

Start the interactive assistant:

```bash
python main.py
```

Example:

```text
============================================================
AfyaPlus Health Assistant
============================================================
Ask about AfyaPlus insurance, clinical routing, or medication calculations.
Type 'exit' to quit.
Type 'clear' to reset the conversation.

You: What is the outpatient MRI co-payment?

AfyaPlus: The standard outpatient MRI co-payment is KES 2,000.

You: Does it require prior authorisation?

AfyaPlus: Yes, outpatient MRI scans require prior authorisation before the procedure is performed.
```

Enter:

```text
clear
```

to reset both conversation history and the session PII mapping.

Enter:

```text
exit
```

to terminate the application.

---

## RAG Design

### Document Loading

Knowledge documents are loaded from the local `knowledge/` directory using LlamaIndex's directory reader.

The current knowledge base uses Markdown documents, but the retrieval layer is separated from the agent so additional supported document types can be incorporated later.

### Chunking

The index uses sentence-aware splitting with:

```text
chunk_size = 512
chunk_overlap = 80
```

The goal is to preserve enough surrounding semantic context while keeping retrieved chunks compact.

The demonstration knowledge base is intentionally small, so some documents may result in only a small number of chunks. Production policy manuals would naturally produce a larger retrieval corpus.

### Embeddings

Embeddings use:

```text
text-embedding-3-small
```

The vector index is persisted locally after ingestion.

### Retrieval

The retriever uses:

```text
similarity_top_k = 3
```

Candidate chunks are additionally filtered using:

```text
MIN_SIMILARITY_SCORE = 0.40
```

The `0.40` threshold is **not treated as a universal semantic similarity threshold**.

It was selected for this demonstration corpus after comparing relevant and deliberately irrelevant queries. Relevant AfyaPlus questions scored materially above unrelated questions in the test corpus.

In a production environment, this threshold should be evaluated and calibrated against a representative retrieval dataset.

### Source Metadata

Retrieved context includes source metadata such as the originating knowledge filename.

This improves traceability and supports audit-oriented retrieval behavior.

---

## Agent and Tool Design

The agent uses a deliberately constrained tool set.

### Knowledge Retrieval Tool

```text
search_afyaplus_knowledge
```

This tool is intended for questions involving:

* Insurance coverage
* Authorisation requirements
* Clinical routing
* Internal medication guidelines

If retrieval does not produce context above the configured relevance threshold, the tool reports that sufficiently relevant AfyaPlus knowledge was not found.

### Medication Calculation Tool

```text
calculate_medication_volume
```

This tool performs deterministic medication-volume arithmetic with structured inputs.

Type hints and docstrings provide LangChain with a clear input schema and tool description.

Defensive validation prevents calculations with invalid values.

---

## Token and Cost Management

Prompt and retrieval design directly affect inference cost.

The project uses several controls to limit unnecessary token consumption.

### Small Retrieval Window

Only the top three candidate chunks are retrieved:

```text
top_k = 3
```

This prevents the full knowledge base from being inserted into every model request.

### Relevance Filtering

Retrieved chunks below the configured similarity threshold are discarded.

This reduces both irrelevant context and unnecessary prompt tokens.

### Controlled Chunk Size

The 512-token chunk size provides enough context for policy interpretation without passing entire documents to the model.

### Persisted Embeddings

The vector index is stored locally after ingestion.

This avoids rebuilding and re-embedding the entire knowledge base every time the application starts.

### Focused System Prompt

The agent prompt defines a narrow operational scope and a small number of explicit rules instead of supplying large amounts of static policy content directly in the prompt.

### Model Configuration

The model can be configured through:

```text
OPENAI_MODEL
```

The default configuration uses:

```text
gpt-4o-mini
```

which provides a practical cost/performance tradeoff for this demonstration.

---

## Privacy and Compliance Guardrails

The project uses privacy-by-design principles to reduce unnecessary exposure of supported PII.

### Input Boundary

Raw user input is processed by `PrivacyContext` before agent execution.

For example:

```text
Raw input:
My phone is 0712345678.

Model-facing input:
My phone is [PHONE_1].
```

### Session-Unique Placeholders

PII placeholders are maintained across the conversation:

```text
0711111111 → [PHONE_1]
0722222222 → [PHONE_2]
```

This prevents different values in the same conversation from accidentally sharing the same placeholder.

### Masked Memory

Conversation memory receives the masked user message.

Therefore supported raw PII does not need to be stored in the model-facing conversation history.

### Separate PII Mapping

The placeholder-to-value mapping remains within the application-side privacy context.

It is not intentionally supplied as part of the LLM message history.

### Output Boundary

If an approved model response contains a known placeholder, the application can restore the corresponding value immediately before returning the response to the user.

For example:

```text
Model response:
We have recorded [PHONE_1].

Final output:
We have recorded 0712345678.
```

The de-masked response is returned to the user, while conversation memory retains the masked version.

### Kenya Data Protection Act, 2019

The architecture is designed to support principles relevant to the **Kenya Data Protection Act, 2019**, particularly data minimisation and privacy by design.

The current implementation should not be interpreted as proof of full legal or regulatory compliance.

Production deployment would require additional controls such as:

* Authentication and authorisation
* Encryption in transit and at rest
* Secrets management
* Access controls
* Secure audit logging
* Data retention and deletion policies
* Broader PII/entity detection
* Consent and lawful-processing controls where applicable
* Operational security controls
* Formal legal and compliance review

---

## Safety Limitations

This project is an educational demonstration and not a production medical decision system.

The included knowledge files contain synthetic AfyaPlus information.

The system should not be used as a substitute for:

* Professional medical diagnosis
* Clinical judgement
* Emergency medical services
* Prescription decisions
* Authoritative insurance verification

The medication tool performs deterministic arithmetic only.

The privacy middleware currently recognises supported email addresses and Kenyan mobile phone formats. It does not constitute a general-purpose PII detection or data-loss-prevention system.

---

## Testing

Run the complete automated test suite:

```bash
pytest -v
```

The test suite covers:

* Email masking
* Kenyan phone-number masking
* PII restoration
* Session-unique placeholders
* Conversation memory
* RAG retrieval
* Relevance filtering
* Source metadata
* Medication calculations
* Invalid medication inputs
* Agent conversation orchestration
* Privacy-safe service orchestration
* PII exclusion from model-facing messages
* PII exclusion from conversation memory
* Final response de-masking

At the time of completion, the project contains:

```text
38 passing tests
```

A deprecation warning may currently be emitted from the LlamaIndex LangChain bridge because it imports `langchain-community`. This originates from the dependency integration rather than the application code and does not currently prevent the test suite from passing.

---

## Manual Agent Testing

A real model integration test is available at:

```text
scripts/test_agent.py
```

Run:

```bash
python scripts/test_agent.py
```

This verifies multi-turn behavior using the configured model.

For example:

```text
USER:
What is the outpatient MRI co-payment?

ASSISTANT:
The standard outpatient MRI co-payment is KES 2,000.

USER:
Does it require prior authorisation?

ASSISTANT:
Yes, outpatient MRI scans require prior authorisation before the procedure is performed.
```

The follow-up demonstrates that conversation history is available to the agent.

---


## Design Decisions

### Why LangChain?

LangChain provides the orchestration layer responsible for connecting the language model with structured tools and conversation messages.

### Why LlamaIndex?

LlamaIndex provides the document ingestion, embedding, vector indexing, persistence, and semantic retrieval layer.

The responsibilities are deliberately separated:

```text
LangChain
    ↓
"What should the agent do?"

LlamaIndex
    ↓
"What relevant knowledge should be retrieved?"
```

### Why Not Let the LLM Perform Medication Arithmetic?

Language models generate probable token sequences and should not be treated as deterministic calculators.

Medication arithmetic is therefore delegated to a validated Python function.

### Why Mask PII Before the Agent?

Masking after model invocation would be too late because the raw value would already have crossed the model boundary.

The privacy middleware therefore runs before agent execution.

### Why Store Masked Responses in Memory?

If a model response references `[PHONE_1]`, the application can restore the value for the user without placing the restored value back into model-facing memory.

This keeps the privacy boundary intact across multiple turns.

---

## Future Improvements

Potential production improvements include:

* Hybrid semantic and keyword retrieval
* Reranking retrieved documents
* Larger retrieval evaluation datasets
* Automated retrieval-quality metrics
* More comprehensive PII detection
* Encrypted session-level PII storage
* Persistent conversation storage with retention controls
* Authentication and role-based access control
* Structured audit events
* Observability and tracing
* Rate limiting
* Prompt-injection defenses for retrieved documents
* Tool-level authorization policies
* Human escalation for uncertain clinical cases
* Model fallback strategies
* Automated evaluation of groundedness and hallucination rates
* Migration away from deprecated integration dependencies as upstream libraries evolve

---

## Disclaimer

This repository is a learning and demonstration project.

All AfyaPlus policies, clinical guidelines, and examples included in the repository are synthetic and should not be treated as real insurance, medical, or clinical guidance.
