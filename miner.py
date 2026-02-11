import argparse
import json
from datetime import datetime

import git
from rich.console import Console
from rich.table import Table

console = Console()


def is_commit_suspect(delta_seconds: int, total_changes: int, entropy: float) -> bool:
    """v0.2.0 Heuristic: Flags high-speed pastes OR extreme density."""
    is_too_fast = delta_seconds < 15 and total_changes > 50
    is_too_dense = entropy > 150
    return is_too_fast or is_too_dense


def export_to_json(data, filename):
    """v0.3.0: Serializes audit data to disk."""
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        console.print(
            f"\n[bold green]EXPORT SUCCESS:[/bold green] Data saved to [cyan]{filename}[/cyan]"
        )
    except Exception as e:
        console.print(f"\n[bold red]EXPORT ERROR:[/bold red] Could not save file: {e}")


def audit_repository(repo_path=".", target_author=None):
    report_data = []
    try:
        repo = git.Repo(repo_path)
        commits = [
            c
            for c in repo.iter_commits(max_count=50)
            if not target_author or c.author.name == target_author
        ]

        table = Table(title=f"Origin-Miner v0.3.0 | Path: {repo_path}")
        table.add_column("Hash", style="cyan")
        table.add_column("Changes", style="blue")
        table.add_column("Files", style="magenta")
        table.add_column("Entropy", style="dim white")
        table.add_column("Time Delta", style="bold yellow")

        suspect_count = 0

        for i in range(len(commits) - 1):
            curr, prev = commits[i], commits[i + 1]
            delta_seconds = curr.committed_date - prev.committed_date

            total_changes = curr.stats.total["lines"]
            files_touched = len(curr.stats.files)
            entropy = total_changes / files_touched if files_touched > 0 else 0

            is_suspicious = is_commit_suspect(delta_seconds, total_changes, entropy)
            color = "red" if is_suspicious else "yellow"
            if is_suspicious:
                suspect_count += 1

            # v0.3.0 Data Collection
            report_data.append(
                {
                    "hash": curr.hexsha[:7],
                    "author": curr.author.name,
                    "timestamp": datetime.fromtimestamp(
                        curr.committed_date
                    ).isoformat(),
                    "changes": total_changes,
                    "files": files_touched,
                    "entropy": round(entropy, 2),
                    "delta_seconds": delta_seconds,
                    "is_suspicious": is_suspicious,
                }
            )

            table.add_row(
                curr.hexsha[:7],
                f"{total_changes} lines",
                f"{files_touched} files",
                f"{entropy:.1f}",
                f"[{color}]{delta_seconds}s[/{color}]",
            )

        console.print(table)
        if suspect_count > 0:
            console.print(
                f"\n[bold red]v0.3.0 ALERT:[/bold red] Found {suspect_count} anomalies."
            )

        return report_data

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        return []


def main():
    parser = argparse.ArgumentParser(
        description="Origin-Miner v0.3.0: Git Forensics & Audit Tool"
    )
    parser.add_argument(
        "path", nargs="?", default=".", help="Path to the Git repository"
    )
    parser.add_argument("--author", help="Filter audit by a specific author name")
    parser.add_argument("--export", help="Save results to a JSON file")

    args = parser.parse_args()
    results = audit_repository(args.path, target_author=args.author)

    if args.export and results:
        export_to_json(results, filename=args.export)


if __name__ == "__main__":
    main()
