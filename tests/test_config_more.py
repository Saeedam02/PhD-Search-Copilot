from phd_search_agent.config import read_yaml, write_yaml
from phd_search_agent.models import CandidateProfile


def test_write_and_read_yaml(tmp_path):
    path = tmp_path / "profile.yaml"
    write_yaml(path, CandidateProfile(name="Ada"))
    assert read_yaml(path)["name"] == "Ada"


def test_read_empty_yaml_returns_dict(tmp_path):
    path = tmp_path / "empty.yaml"
    path.write_text("", encoding="utf-8")
    assert read_yaml(path) == {}
