import os
import tomllib
from typing import Any, Dict

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.toml")

def load_config() -> Dict[str, Any]:
    """
    Load the entire configuration from config.toml.
    """
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Config file not found at {CONFIG_PATH}")
    
    with open(CONFIG_PATH, "rb") as f:
        return tomllib.load(f)

def get_agent_config(agent_name: str) -> Dict[str, Any]:
    """
    Get configuration for a specific agent, merging with default settings.
    """
    config = load_config()
    default_config = config.get("default", {})
    agent_config = config.get(agent_name, {})
    
    # Merge: defaults are overridden by agent specific config
    # 1. Base Default
    merged = default_config.copy()
    
    # 2. Env specific Default (dev/prod)
    env = os.environ.get("APP_ENV", "dev")
    env_config = default_config.get(env, {})
    if isinstance(env_config, dict):
        merged.update(env_config)
    
    # 3. Agent specific overrides
    agent_config = config.get(agent_name, {})
    merged.update(agent_config)
    
    # 4. Agent specific Env overrides (future proofing, e.g. [spec_agent.prod])
    agent_env_config = agent_config.get(env, {})
    if isinstance(agent_env_config, dict):
        merged.update(agent_env_config)
    
    return merged
