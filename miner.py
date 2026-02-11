import sys

import git
from rich.console import Console
from rich.table import Table

console = Console()


def is_commit_suspect(delta_seconds: int, total_changes: int, entropy: float) -> bool:
    """v0.2.0 Heuristic: Flags high-speed pastes OR extreme density."""
    is_too_fast = delta_seconds < 15 and total_changes > 50
    is_too_dense = entropy > 150
    return is_too_fast or is_too_dense


def audit_repository(repo_path=".", target_author=None):
    try:
        repo = git.Repo(repo_path)
        commits = [
            c
            for c in repo.iter_commits(max_count=50)
            if not target_author or c.author.name == target_author
        ]

        table = Table(title=f"Origin-Miner v0.3.0 | Path: {repo_path}")
        table.add_column("Hash", style="cyan", no_wrap=True)
        table.add_column("Changes", style="blue")
        table.add_column("Files", style="magenta")
        table.add_column("Entropy", style="dim white")
        table.add_column("Time Delta", style="bold yellow")

        suspect_count = 0

        for i in range(len(commits) - 1):
            curr, prev = commits[i], commits[i + 1]
            delta_seconds = curr.committed_date - prev.committed_date

            total_changes = curr.stats.total["lines"]
            # Convert PathLike to str for Pylance and joining
            file_names = [str(f) for f in curr.stats.files.keys()]
            files_touched = len(file_names)
            entropy = total_changes / files_touched if files_touched > 0 else 0

            # Formatting file list for the multi-line UI
            files_display = "\n".join(file_names[:5])
            if files_touched > 5:
                files_display += f"\n[dim]...and {files_touched - 5} more[/dim]"

            is_suspicious = is_commit_suspect(delta_seconds, total_changes, entropy)
            color = "red" if is_suspicious else "yellow"
            if is_suspicious:
                suspect_count += 1

            table.add_row(
                curr.hexsha[:7],
                f"{total_changes} lines",
                files_display,
                f"{entropy:.1f}",
                f"[{color}]{delta_seconds}s[/{color}]",
            )

        console.print(table)
        if suspect_count > 0:
            console.print(
                f"\n[bold red]v0.3.0 ALERT:[/bold red] Found {suspect_count} anomalies."
            )

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    audit_repository(path)


if __name__ == "__main__":
    main()
