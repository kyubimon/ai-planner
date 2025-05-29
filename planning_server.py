import json

import google.generativeai as genai
import yaml
from fastmcp import FastMCP

from settings import settings

genai.configure(api_key=settings.GEMINI_API_KEY)


def load_team_rules(rules_id: str) -> dict:
    """Loads a specific set of team rules from a YAML file."""
    try:
        with open(f"rules/{rules_id}.yaml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {"error": "Rules not found"}


def build_rfc_prompt(feature: str, rules: dict) -> str:
    """Builds a detailed prompt for Gemini to generate an RFC."""
    template = rules.get("rfc_template", "## Summary\n## Goals\n## Approach")
    style = rules.get("code_style", "Default")
    return f"""
    You are a senior software architect.
    Based on our team rules (style: {style}),
    please generate an RFC document for the feature: '{feature}'.
    Use this Markdown template:\n{template}\n
    Ensure you include sections for Summary, Goals, Technical Approach, and Risks.
    Output only the RFC document content.
    """


def build_tasks_prompt(rfc: str, rules: dict) -> str:
    """Builds a prompt for Gemini to generate tasks from an RFC."""
    task_rules = rules.get("task_rules", "Standard rules apply.")
    return f"""
    You are an expert project manager.
    Given the following RFC:\n{rfc}\n
    And our task rules: {task_rules}\n
    Generate a list of tasks as a valid JSON array.
    Each task object in the array must have these keys: 'name' (string),
    'description' (string), and 'priority' (string: 'High', 'Medium', or 'Low').
    Output *only* the JSON array and nothing else.
    """


mcp = FastMCP(name="GeminiPlanningAssistant", version="0.1.1")


@mcp.tool()
def create_rfc(feature_description: str, rules_id: str = "default") -> str:
    """
    Generates an RFC document using Gemini based on a feature
    description and team rules.

    Args:
        feature_description: A clear description of the feature.
        rules_id: The identifier for the team rules to use.
    """
    rules = load_team_rules(rules_id)
    if "error" in rules:
        raise ValueError(f"Rules not found: {rules_id}")

    prompt = build_rfc_prompt(feature_description, rules)
    print(f"Generating RFC with Gemini...")

    try:
        model = genai.GenerativeModel(settings.GEMINI_MODEL_NAME)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        raise ConnectionError(f"Failed to generate RFC from Gemini: {e}")


@mcp.tool()
def generate_tasks(rfc_content: str, rules_id: str = "default") -> str:
    """
    Generates a task list in JSON format using Gemini based on an RFC
    and team rules.

    Args:
        rfc_content: The full text content of the RFC document.
        rules_id: The identifier for the team rules to use.
    """
    rules = load_team_rules(rules_id)
    if "error" in rules:
        raise ValueError(f"Rules not found: {rules_id}")

    prompt = build_tasks_prompt(rfc_content, rules)
    print(f"Generating Tasks with Gemini...")

    try:
        model = genai.GenerativeModel(settings.GEMINI_MODEL_NAME)
        response = model.generate_content(prompt)

        cleaned_text = response.text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]

        try:
            json.loads(cleaned_text)
            return cleaned_text
        except json.JSONDecodeError:
            print(f"Warning: Gemini did not return valid JSON. Returning raw text.")
            return response.text

    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        raise ConnectionError(f"Failed to generate tasks from Gemini: {e}")


if __name__ == "__main__":
    print("Starting Gemini-powered FastMCP server...")
    mcp.run()
