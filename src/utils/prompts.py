import os

def load_prompt(prompt_name: str) -> str:
    """
    Load a prompt file from the prompts directory.
    Removes YAML frontmatter if present.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    prompt_path = os.path.join(project_root, "prompts", f"{prompt_name}.md")
    
    if not os.path.exists(prompt_path):
        raise FileNotFoundError(f"Prompt file not found at {prompt_path}")
        
    with open(prompt_path, "r", encoding="utf-8") as f:
        content = f.read()
        # Remove frontmatter if present
        if content.startswith("---"):
            try:
                # Find second --- starting from index 3
                second_dash_index = content.find("---", 3)
                if second_dash_index != -1:
                    return content[second_dash_index + 3:].strip()
            except ValueError:
                pass
        return content
