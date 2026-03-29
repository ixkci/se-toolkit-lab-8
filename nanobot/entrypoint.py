import os
import json

def main():
    with open("config.json", "r") as f:
        config = json.load(f)

    # LLM провайдер
    config.setdefault("providers", {}).setdefault("custom", {})
    config["providers"]["custom"]["apiKey"] = os.environ.get("LLM_API_KEY", "")
    config["providers"]["custom"]["apiBase"] = os.environ.get("LLM_API_BASE_URL", "http://qwen-code-api:8000/v1")

    config.setdefault("agents", {}).setdefault("defaults", {})
    config["agents"]["defaults"]["model"] = os.environ.get("LLM_API_MODEL", "coder-model")

    # Настройки Gateway
    config.setdefault("gateway", {})
    config["gateway"]["host"] = os.environ.get("NANOBOT_GATEWAY_CONTAINER_ADDRESS", "0.0.0.0")
    if "NANOBOT_GATEWAY_CONTAINER_PORT" in os.environ:
        config["gateway"]["port"] = int(os.environ["NANOBOT_GATEWAY_CONTAINER_PORT"])

    # Инструменты MCP
    mcp = config.setdefault("tools", {}).setdefault("mcpServers", {})
    
    mcp["lms"] = {
        "command": "python",
        "args": ["-m", "mcp_lms"],
        "env": {
            "NANOBOT_LMS_BACKEND_URL": os.environ.get("NANOBOT_LMS_BACKEND_URL", ""),
            "NANOBOT_LMS_API_KEY": os.environ.get("NANOBOT_LMS_API_KEY", "")
        }
    }
    
    mcp["webchat"] = {
        "command": "python",
        "args": ["-m", "mcp_webchat"],
        "env": {
            "NANOBOT_UI_RELAY_URL": f"http://127.0.0.1:{os.environ.get('NANOBOT_UI_RELAY_PORT', '8766')}",
            "NANOBOT_UI_RELAY_TOKEN": os.environ.get("NANOBOT_ACCESS_KEY", "")
        }
    }

    # Настройки канала webchat
    webchat = config.setdefault("channels", {}).setdefault("webchat", {})
    webchat["enabled"] = True
    webchat["allowFrom"] = ["*"]
    webchat["host"] = os.environ.get("NANOBOT_WEBCHAT_CONTAINER_ADDRESS", "0.0.0.0")
    if "NANOBOT_WEBCHAT_CONTAINER_PORT" in os.environ:
        webchat["port"] = int(os.environ["NANOBOT_WEBCHAT_CONTAINER_PORT"])
    webchat["accessKey"] = os.environ.get("NANOBOT_ACCESS_KEY", "")

    # Сохраняем и запускаем
    with open("config.resolved.json", "w") as f:
        json.dump(config, f, indent=2)

    os.execvp("uv", ["uv", "run", "nanobot", "gateway", "--config", "config.resolved.json", "--workspace", "./workspace"])

if __name__ == "__main__":
    main()
