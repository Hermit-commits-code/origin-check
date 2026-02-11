# Origin-Check: Technical Reference

This document tracks the rationale behind the codebase, serving as a map for the auditing logic.

| Component   | Logic / Line                                                | Purpose                                                                             |
|:------------|:------------------------------------------------------------|:------------------------------------------------------------------------------------|
| **Engine**  | `import git`                                                | Connects Python to the local `.git` metadata using GitPython.                       |
| **UI**      | `from rich.console import Console`                          | Initializes the terminal "painter" for formatted output.                            |
| **UI**      | `from rich.table import Table`                              | Structural container for displaying commit metadata in a grid.                      |
| **Time**    | `from datetime import datetime`                             | Converts Git's Unix timestamps (seconds) into ISO-standard time.                    |
| **Setup**   | `console = Console()`                                       | Global instance for printing themed output.                                         |
| **Entry**   | `def audit_repository(path)`                                | Encapsulates logic to allow for future CLI argument passing.                        |
| **Safety**  | `try:`                                                      | Prevents terminal "vomit" (stack traces) if run in a non-git folder.                |
| **Data**    | `repo = git.Repo(path)`                                     | The "handshake" that validates and opens the local history.                         |
| **History** | `repo.iter_commits(max=20)`                                 | Grabs the 20 most recent snapshots for delta analysis.                              |
| **Visuals** | `table.add_column("Hash")`                                  | Shows the short-form SHA (unique identifier) for each commit.                       |
| **Visuals** | `table.add_column("Author")`                                | Identifies the contributor identity.                                                |
| **Visuals** | `table.add_column("Timestamp")`                             | Displays the absolute wall-clock time of the work.                                  |
| Logic       | `for i in range(len(commits) - 1):`                         | Steps through the list to compare a commit with its immediate predecessor.          |
| Logic       | `curr = commits[i]`                                         | Selects the "newer" commit in the current iteration of the comparison loop.         |
| Logic       | `prev = commits[i + 1]`                                     | Selects the "older" commit to serve as the baseline for the time delta calculation. |
| Logic       | `delta_seconds = curr.committed_date - prev.committed_date` | Calculates the raw elapsed time (in seconds) between two consecutive commits.       |
| Logic       | `dt_str = ...strftime(...)`                                 | Converts the machine-readable Unix timestamp into a human-readable calendar format. |
| Logic       | `delta_str = ...`                                           | Formats the raw seconds into a readable 'm/s' string for easier visual auditing.    |
| Logic       | `table.add_row(...)`                                        | Commits the processed data (Short Hash, Author, Date, Delta) into a new table row.  |
| UI          | `console.print(table)`                                      | Renders the final, populated data table to the terminal window.                     |
| Safety      | `except Exception as e:`                                    | Catches errors (like missing .git folders) to prevent the script from crashing.     |
| UI          | `console.print(f"[bold red]Error...`                        | Outputs a styled error message to the user if the audit fails.                      |
| Logic       | `if __name__ == "__main__":`                                | Ensures the script only executes when run directly, not when imported.              |
| Logic       | `audit_repository(".")`                                     | The final trigger that launches the audit on the current folder.                    |
| Analysis    | `color = "red" if delta_seconds < 10 else "yellow"`         | Implements a threshold to visually flag suspiciously fast (AI-speed) commits.       |
| UI          | `f"[{color}]{delta_str}[/{color}]"`                         | Uses Rich markup to dynamically color the delta text based on audit severity.       |
| Logic       | `suspect_count = 0`                                         | Initializes a tracker to quantify the severity of the audit findings.               |
| UI          | `f"[{color}]{delta_str}[/{color}]"`                         | Injects Rich markup tags to highlight "High Velocity" commits in red.               |
| UI          | `console.print(f"\n[bold red]ALERT...")`                    | Provides a summary verdict after processing the full commit list.                   |
