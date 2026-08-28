"""Configuration loading, workspace initialization, and YAML helpers."""

from __future__ import annotations

import shutil
from importlib.resources import files
from pathlib import Path
from typing import Any, TypeVar

import yaml
from pydantic import BaseModel

from .models import CandidateProfile, ScoringConfig, SearchPreferences

T = TypeVar("T", bound=BaseModel)

DEFAULT_WORKSPACE = Path("workspace")


def read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data or {}


def write_yaml(path: Path, value: BaseModel | dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = value.model_dump(mode="json", exclude_none=False) if isinstance(value, BaseModel) else value
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")


def load_model(path: Path, model_type: type[T]) -> T:
    return model_type.model_validate(read_yaml(path))


def load_candidate(workspace: Path = DEFAULT_WORKSPACE) -> CandidateProfile:
    return load_model(workspace / "config" / "candidate.yaml", CandidateProfile)


def load_preferences(workspace: Path = DEFAULT_WORKSPACE) -> SearchPreferences:
    return load_model(workspace / "config" / "search_preferences.yaml", SearchPreferences)


def load_scoring(workspace: Path = DEFAULT_WORKSPACE) -> ScoringConfig:
    return load_model(workspace / "config" / "scoring.yaml", ScoringConfig)


def initialize_workspace(
    workspace: Path = DEFAULT_WORKSPACE,
    repo_root: Path | None = None,
    force: bool = False,
) -> list[Path]:
    """Create local private workspace and copy example configuration.

    Returns a list of created/copied paths for CLI reporting.
    """

    created: list[Path] = []
    dirs = [
        workspace / "config",
        workspace / "private" / "cv",
        workspace / "private" / "transcript",
        workspace / "private" / "thesis",
        workspace / "private" / "publications",
        workspace / "private" / "supporting",
        workspace / "applications",
        workspace / "reports",
        workspace / "approvals",
        workspace / "state",
    ]
    for directory in dirs:
        directory.mkdir(parents=True, exist_ok=True)
        created.append(directory)

    destinations = {
        "candidate.yaml": workspace / "config" / "candidate.yaml",
        "search_preferences.yaml": workspace / "config" / "search_preferences.yaml",
        "scoring.yaml": workspace / "config" / "scoring.yaml",
    }
    if repo_root is not None:
        # Explicit repo_root is mainly useful to contributors/tests working
        # directly from the source tree.
        sources = {
            "candidate.yaml": repo_root / "config" / "candidate.example.yaml",
            "search_preferences.yaml": repo_root / "config" / "search_preferences.example.yaml",
            "scoring.yaml": repo_root / "config" / "scoring.example.yaml",
        }
        for name, destination in destinations.items():
            if force or not destination.exists():
                shutil.copyfile(sources[name], destination)
                created.append(destination)
    else:
        # Installed wheels/containers do not necessarily contain the repository
        # root, so defaults are shipped as package resources.
        defaults = files("phd_search_agent.defaults")
        for name, destination in destinations.items():
            if force or not destination.exists():
                destination.write_text(defaults.joinpath(name).read_text(encoding="utf-8"), encoding="utf-8")
                created.append(destination)
    return created
