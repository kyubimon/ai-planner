# ai-planner

A software development planning assistant that leverages Google Gemini and FastMCP to automate the generation of RFCs (Request for Comments) and detailed engineering task lists, following customizable team rules.

## Features

- **AI-powered RFC Generation:** Automatically create detailed RFC documents for new features using your team's preferred template and style.
- **Task Breakdown:** Generate prioritized, well-structured engineering tasks from RFCs, including estimations and assignments.
- **Customizable Rules:** Define your own templates, code style, and task breakdown rules in YAML files under `rules/`.
- **FastMCP Integration:** Exposes tools as MCP endpoints for easy integration with other systems.

## Requirements

- Python 3.12+
- Google Gemini API key

## Installation

1. **Clone the repository:**

   ```bash
   git clone <repo-url>
   cd ai-planner
   ```

2. **Set up a virtual environment:**

   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   # or, if using uv:
   uv pip install --system
   ```

## Environment Variables

Create a `.env` file in the project root with the following variables:

```env
GEMINI_API_KEY=your_google_gemini_api_key
GEMINI_MODEL_NAME=gemini-1.5-pro # or your preferred Gemini model
```

## Usage

### Start the Planning Server

```bash
python planning_server.py
# or, if using FastMCP CLI:
fastmcp run planning_server.py
```

### Example: Generate an RFC and Tasks

You can use the exposed MCP tools programmatically or via the FastMCP interface:

- `create_rfc(feature_description: str, rules_id: str = "default_rules") -> str`
- `generate_tasks(rfc_content: str, rules_id: str = "default_rules") -> str`

### Customizing Rules

Edit or add YAML files in the `rules/` directory to define:

- RFC templates
- Code style and policies
- Task breakdown and prioritization rules

See `rules/default_rules.yaml` for a comprehensive example.

## Project Structure

```
.
├── planning_server.py      # Main FastMCP server and tool definitions
├── main.py                # Simple hello-world entry point
├── rules/                 # Team rules and templates (YAML)
│   └── default_rules.yaml
├── pyproject.toml         # Project metadata and dependencies
├── uv.lock                # Lock file for reproducible installs
├── .env                   # (Not tracked) Your API keys and config
└── README.md
```

## License

MIT

## Author

Fabian Zorro
