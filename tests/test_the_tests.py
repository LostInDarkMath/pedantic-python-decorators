from pathlib import Path

def test_all_test_files_follow_pytest_naming_convention():
    tests_dir = Path(__file__).parent
    invalid_files = []

    for path in tests_dir.rglob("*.py"):
        name = path.name

        if name in {"__init__.py", "conftest.py"}:
            continue

        if not name.startswith("test_"):
            invalid_files.append(path.relative_to(tests_dir))

    assert not invalid_files, (
        "Found Python files in tests/ that do not follow pytest naming conventions:\n"
        + "\n".join(str(p) for p in invalid_files)
    )
