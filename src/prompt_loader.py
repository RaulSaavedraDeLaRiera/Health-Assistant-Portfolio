"""Load agent prompts from local files. Default language: English. Spanish in translations/ES/."""

from pathlib import Path
import os

_language_log_shown = False


def load_agent_prompt(agent_name: str) -> str:
    """Load agent prompt from local file.
    - LANGUAGE: EN by default loads from agents/prompts/; ES loads from agents/prompts/translations/ES/
    - LOCAL_PROMPTS is always True in this portfolio; no Firestore.
    """
    project_root = Path(__file__).parent.parent
    language = os.getenv("LANGUAGE", "EN").upper().strip()
    global _language_log_shown
    if language and language != "EN" and not _language_log_shown:
        print(f"[INFO] Language: {language}. Loading prompts from translations/{language}/")
        _language_log_shown = True
    if language and language != "EN":
        translation_path = project_root / "agents" / "prompts" / "translations" / language / f"{agent_name}.txt"
        if translation_path.exists():
            local_path = translation_path
        else:
            print(f"[INFO] No translation for {agent_name} in {language}, using English")
            local_path = project_root / "agents" / "prompts" / f"{agent_name}.txt"
    else:
        local_path = project_root / "agents" / "prompts" / f"{agent_name}.txt"
    try:
        if local_path.exists():
            return local_path.read_text(encoding="utf-8").strip()
        return ""
    except Exception as e:
        print(f"[ERROR] Loading prompt for {agent_name}: {e}")
        return ""
