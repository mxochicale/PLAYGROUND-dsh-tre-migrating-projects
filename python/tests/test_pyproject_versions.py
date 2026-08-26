"""
Unit tests that validate the [project.dependencies] list in pyproject.toml.

What is checked
----------------
1. pyproject.toml exists and is valid TOML.
2. Every dependency string parses as a valid PEP 508 requirement.
3. Every dependency is pinned with an exact version (`==`) -- no ranges,
   no unpinned packages -- since this project is meant to be fully
   reproducible.
4. The pinned version string is a valid, normalizable PEP 440 version
   (catches typos like "1.16..2" or accidental extra characters).
5. There are no duplicate package names (case-insensitive, normalized).
6. Package names only use characters allowed by PEP 508 naming rules.
7. (Optional / non-fatal) If a pinned package is installed in the current
   environment, its installed version matches the pin. This is skipped
   automatically for packages that aren't installed, so this test suite
   can run in a bare environment (e.g. CI without the full install step).

Run with:
    pytest tests/test_pyproject_versions.py -v
"""

from __future__ import annotations

import sys
import tomllib
from importlib import metadata
from pathlib import Path

import pytest
from packaging.requirements import InvalidRequirement, Requirement
from packaging.version import InvalidVersion, Version

# ---------------------------------------------------------------------------
# Locate and load pyproject.toml
# ---------------------------------------------------------------------------


def _find_pyproject() -> Path:
    """Search this file's directory and its parents for pyproject.toml."""
    here = Path(__file__).resolve().parent
    for candidate_dir in [here, *here.parents]:
        candidate = candidate_dir / "pyproject.toml"
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "Could not locate pyproject.toml relative to the test file."
    )


PYPROJECT_PATH = _find_pyproject()


@pytest.fixture(scope="session")
def pyproject_data() -> dict:
    with PYPROJECT_PATH.open("rb") as fh:
        return tomllib.load(fh)


@pytest.fixture(scope="session")
def raw_dependencies(pyproject_data: dict) -> list[str]:
    return pyproject_data["project"]["dependencies"]


@pytest.fixture(scope="session")
def parsed_requirements(raw_dependencies: list[str]) -> list[Requirement]:
    requirements = []
    for dep in raw_dependencies:
        try:
            requirements.append(Requirement(dep))
        except InvalidRequirement as exc:
            pytest.fail(f"Dependency string {dep!r} is not a valid requirement: {exc}")
    return requirements


# ---------------------------------------------------------------------------
# Structural tests
# ---------------------------------------------------------------------------


def test_pyproject_file_exists():
    assert PYPROJECT_PATH.exists(), "pyproject.toml not found"


def test_pyproject_is_valid_toml(pyproject_data: dict):
    assert "project" in pyproject_data
    assert "dependencies" in pyproject_data["project"]


def test_dependencies_list_is_not_empty(raw_dependencies: list[str]):
    assert len(raw_dependencies) > 0, "dependencies list should not be empty"


def test_dependencies_are_strings(raw_dependencies: list[str]):
    assert all(isinstance(dep, str) for dep in raw_dependencies)


# ---------------------------------------------------------------------------
# Requirement / pin format tests
# ---------------------------------------------------------------------------


def test_every_dependency_parses_as_valid_requirement(raw_dependencies: list[str]):
    """Each active (non-comment) dependency must be PEP 508-parseable."""
    for dep in raw_dependencies:
        try:
            Requirement(dep)
        except InvalidRequirement as exc:
            pytest.fail(f"Invalid requirement string {dep!r}: {exc}")


def test_every_dependency_is_exact_pinned(parsed_requirements: list[Requirement]):
    """
    Fail if any dependency uses a non-exact specifier (e.g. >=, ~=, <, no
    specifier at all) or pins more than one version constraint.
    """
    offenders = []
    for req in parsed_requirements:
        specs = list(req.specifier)
        if len(specs) != 1 or specs[0].operator != "==":
            offenders.append(str(req))

    assert not offenders, (
        "The following dependencies are not pinned with a single '==' "
        f"specifier: {offenders}"
    )


def test_pinned_versions_are_valid_pep440(parsed_requirements: list[Requirement]):
    bad = []
    for req in parsed_requirements:
        version_str = next(iter(req.specifier)).version
        try:
            Version(version_str)
        except InvalidVersion:
            bad.append(f"{req.name}=={version_str}")
    assert not bad, f"Invalid PEP 440 version strings: {bad}"


def test_no_duplicate_package_names(parsed_requirements: list[Requirement]):
    """Package names are compared case-insensitively with '-'/'_' normalized,
    matching PEP 503 normalization rules."""

    def normalize(name: str) -> str:
        return name.lower().replace("_", "-").replace(".", "-")

    seen: dict[str, str] = {}
    duplicates = []
    for req in parsed_requirements:
        key = normalize(req.name)
        if key in seen:
            duplicates.append((seen[key], req.name))
        else:
            seen[key] = req.name

    assert not duplicates, f"Duplicate package entries found: {duplicates}"


def test_no_extras_or_markers_unless_intended(parsed_requirements: list[Requirement]):
    """
    Sanity check: none of the pinned dependencies should silently carry
    environment markers or extras, since none are expected in this file.
    Remove/adjust this test if the project intentionally adds markers later.
    """
    with_markers = [str(r) for r in parsed_requirements if r.marker is not None]
    with_extras = [str(r) for r in parsed_requirements if r.extras]

    assert not with_markers, f"Unexpected environment markers: {with_markers}"
    assert not with_extras, f"Unexpected extras: {with_extras}"


# ---------------------------------------------------------------------------
# Cross-check against the currently installed environment (best-effort)
# ---------------------------------------------------------------------------


def test_requires_python_matches_running_interpreter(pyproject_data: dict):
    from packaging.specifiers import SpecifierSet

    requires_python = pyproject_data["project"].get("requires-python")
    if not requires_python:
        pytest.skip("requires-python not set in pyproject.toml")

    running_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    assert Version(running_version) in SpecifierSet(requires_python), (
        f"Running interpreter {running_version} does not satisfy "
        f"requires-python={requires_python!r}"
    )


def pytest_generate_tests(metafunc):
    """Dynamically parametrize the installed-version check against the
    dependencies actually declared in pyproject.toml."""
    if metafunc.function.__name__ == "test_installed_version_matches_pin":
        with PYPROJECT_PATH.open("rb") as fh:
            data = tomllib.load(fh)
        deps = data["project"]["dependencies"]
        reqs = [Requirement(d) for d in deps]
        metafunc.parametrize("req", reqs, ids=[r.name for r in reqs])


def test_installed_version_matches_pin(req: Requirement):
    """
    If the package happens to be installed in the current interpreter,
    verify its installed version matches the pin exactly. Packages that
    aren't installed are skipped rather than failed, so this suite can run
    before `pip install`/`uv sync` as well as after.
    """
    try:
        installed_version = metadata.version(req.name)
    except metadata.PackageNotFoundError:
        pytest.skip(f"{req.name} is not installed in this environment")

    pinned_version = next(iter(req.specifier)).version
    assert Version(installed_version) == Version(pinned_version), (
        f"{req.name}: installed={installed_version} pinned={pinned_version}"
    )
