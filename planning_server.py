import json
import os
import sys

import google.generativeai as genai
import yaml
from dotenv import load_dotenv
from fastmcp import FastMCP

# from fastmcp.typing import ToolContext # Si necesitas contexto

# --- Cargar .env y Configurar Gemini ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("ERROR CRÍTICO: GEMINI_API_KEY no definida. Crea un archivo .env.")

genai.configure(api_key=api_key)
GEMINI_MODEL_NAME = "gemini-1.5-flash"


# --- Helper Functions ---
def load_team_rules(rules_id: str) -> dict:
    """Loads a specific set of team rules from a YAML file."""
    try:
        with open(f"rules/{rules_id}.yaml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(
            f"SERVER ERROR: Rules file 'rules/{rules_id}.yaml' not found.",
            file=sys.stderr,
        )
        return {"error": "Rules not found"}


def build_rfc_prompt(feature: str, rules: dict) -> str:
    """Builds a detailed prompt for Gemini to generate an RFC."""
    template = rules.get("rfc_template", "## Summary\n## Goals\n## Approach")
    style = rules.get("code_style", "Default")
    return f"""
    You are a senior software architect. Based on our team rules (style: {style}),
    generate an RFC document for the feature: '{feature}'.
    Use this Markdown template:\n{template}\n
    Ensure you include sections for Summary, Goals, Technical Approach, and Risks.
    Output *only* the RFC document content as clean Markdown.
    """


def build_tasks_prompt(rfc: str, rules: dict) -> str:
    """Builds a prompt for Gemini to generate tasks from an RFC."""
    task_rules = rules.get("task_rules", "Standard rules apply.")
    return f"""
    You are an expert project manager. Given the following RFC:\n{rfc}\n
    And our task rules: {task_rules}\n
    Generate a list of tasks as a valid JSON array.
    Each task object must have 'name', 'description', and 'priority' keys.
    Output *only* the JSON array and nothing else. Ensure it's valid JSON.
    """


# --- Initialize FastMCP Server ---
mcp = FastMCP(name="GeminiPlanningAssistantMCP", version="1.0.0")
print("SERVER INFO: Initializing FastMCP + Gemini Assistant", file=sys.stderr)
sys.stderr.flush()

# --- Define Tools using Decorators ---


@mcp.tool()
def createRFC(feature_description: str, rules_id: str = "default") -> str:
    """
    Generates an RFC document using Gemini.
    """
    print(f"SERVER INFO: createRFC called with: {feature_description}", file=sys.stderr)
    sys.stderr.flush()
    rules = load_team_rules(rules_id)
    if "error" in rules:
        print(f"SERVER ERROR: {rules['error']}", file=sys.stderr)
        raise ValueError(f"Rules not found: {rules_id}")

    prompt = build_rfc_prompt(feature_description, rules)

    try:
        model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        response = model.generate_content(prompt)
        print("SERVER INFO: Gemini RFC generation successful.", file=sys.stderr)
        sys.stderr.flush()
        return response.text
    except Exception as e:
        print(f"SERVER ERROR: Gemini API call failed: {e}", file=sys.stderr)
        sys.stderr.flush()
        raise ConnectionError(f"Failed to generate RFC from Gemini: {e}")


@mcp.tool()
def generateTasks(rfc_content: str, rules_id: str = "default") -> str:
    """
    Generates a task list in JSON format using Gemini.
    """
    print(f"SERVER INFO: generateTasks called.", file=sys.stderr)
    sys.stderr.flush()
    rules = load_team_rules(rules_id)
    if "error" in rules:
        print(f"SERVER ERROR: {rules['error']}", file=sys.stderr)
        raise ValueError(f"Rules not found: {rules_id}")

    prompt = build_tasks_prompt(rfc_content, rules)

    try:
        model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        response = model.generate_content(prompt)
        cleaned_text = (
            response.text.strip().removeprefix("```json").removesuffix("```").strip()
        )
        try:
            json.loads(cleaned_text)
            print("SERVER INFO: Gemini Task generation successful.", file=sys.stderr)
            sys.stderr.flush()
            return cleaned_text
        except json.JSONDecodeError:
            print(
                f"SERVER WARNING: Gemini did not return valid JSON. Returning raw: {response.text[:100]}...",
                file=sys.stderr,
            )
            sys.stderr.flush()
            return response.text  # Return raw if parsing fails
    except Exception as e:
        print(f"SERVER ERROR: Gemini API call failed: {e}", file=sys.stderr)
        sys.stderr.flush()
        raise ConnectionError(f"Failed to generate tasks from Gemini: {e}")


# --- Running the Server ---
if __name__ == "__main__":
    print(
        "SERVER INFO: Starting FastMCP server via __main__ (usually run via 'fastmcp run')...",
        file=sys.stderr,
    )
    sys.stderr.flush()
    mcp.run()
