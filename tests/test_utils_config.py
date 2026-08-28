from pathlib import Path

from phd_search_agent.config import initialize_workspace, load_candidate, load_preferences, load_scoring
from phd_search_agent.utils import opportunity_id, slugify


def test_slug_and_id_stable():
    assert slugify("TU Delft / Control") == "tu-delft-control"
    assert opportunity_id("PhD", "TU", "https://x") == opportunity_id(
        "PhD", "TU", "https://x"
    )


def test_initialize_and_load_workspace(tmp_path):
    repo_root = Path(__file__).resolve().parents[1]
    workspace = tmp_path / "workspace"
    initialize_workspace(workspace, repo_root=repo_root)
    assert load_candidate(workspace).name == "Example Candidate"
    assert "funding" in load_preferences(workspace).model_fields
    assert load_scoring(workspace).weights["research_fit"] > 0
