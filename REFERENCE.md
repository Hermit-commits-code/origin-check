# Origin-Check: Technical Reference (v0.2.0)

This document tracks the rationale behind the codebase and serves as a map for the auditing logic.

| Component    | Logic / Line                       | Purpose                                                                             |
|:-------------|:-----------------------------------|:------------------------------------------------------------------------------------|
| **Engine**   | `import git`                       | Connects Python to the local `.git` metadata using GitPython.                       |
| **UI**       | `from rich.console import Console` | Initializes the terminal "painter" for formatted output and tables.                 |
| **Entry**    | `def main()`                       | CLI entry point defined in `pyproject.toml` for `miner-audit` command.              |
| **Data**     | `repo = git.Repo(repo_path)`       | Validates and opens the local history; handles non-git folders via `try/except`.    |
| **Entropy**  | `total_changes / files_touched`    | **New in v0.2.0:** Measures "Density" to catch mass-pasting into single files.      |
| **Analysis** | `is_too_fast or is_too_dense`      | **The Heuristic:** Flags commits if they are < 15s delta OR > 150 lines/file.       |
| **Safety**   | `if files_touched > 0 else 0`      | Prevents DivisionByZero errors on commits with no line changes (e.g., tag moves).   |
| **Testing**  | `mocker.patch("git.Repo", ...)`    | Uses `pytest-mock` to simulate repository failures for error-handling verification. |
| **Build**    | `packages = ["miner.py"]`          | Explicitly tells Hatchling to include the root script in the distribution wheel.    |
| **Env**      | `[dependency-groups]`              | Modern `uv` syntax for managing dev-only tools like `pytest`.                       |
