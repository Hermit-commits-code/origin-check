import sys

import git
from rich.console import Console
from rich.table import Table

console = Console()


def calculate_comment_ratio(diff_text: str) -> float:
    """v0.5.0: Calculates ratio of comment lines to total lines added."""
    lines = diff_text.splitlines()
    added_lines = [
        line for line in lines if line.startswith("+") and not line.startswith("+++")
    ]

    if not added_lines:
        return 0.0

    comment_count = 0
    for line in added_lines:
        clean_line = line[1:].strip()
        if clean_line.startswith(("#", "//", "/*", "*", '"""', "'''")):
            comment_count += 1

    return comment_count / len(added_lines)


def is_commit_suspect(
    delta_seconds: int, total_changes: int, entropy: float, comment_ratio: float = 0
) -> bool:
    is_too_fast = delta_seconds < 15 and total_changes > 50
    is_too_dense = entropy > 150

    # v0.5.0 Fix: If it's lightning fast and has > 40% comments, it's robotic
    # regardless of total line count.
    is_robotic = delta_seconds < 10 and comment_ratio > 0.40

    return is_too_fast or is_too_dense or is_robotic


def audit_repository(repo_path=".", target_author=None):
    report_data = []
    try:
        repo = git.Repo(repo_path)
        commits = [
            c
            for c in repo.iter_commits(max_count=50)
            if not target_author or c.author.name == target_author
        ]

        table = Table(title="Origin-Miner v0.5.0 | Semantic Intelligence")
        table.add_column("Hash", style="cyan")
        table.add_column("Changes", style="blue")
        table.add_column("Files", style="magenta")
        table.add_column("AI Score", style="dim green")  # New for v0.5.0
        table.add_column("Time Delta", style="bold yellow")

        suspect_count = 0

        for i in range(len(commits) - 1):
            curr, prev = commits[i], commits[i + 1]
            delta_seconds = curr.committed_date - prev.committed_date

            total_changes = curr.stats.total["lines"]
            file_names = [str(f) for f in curr.stats.files.keys()]
            files_touched = len(file_names)
            entropy = total_changes / files_touched if files_touched > 0 else 0

            # v0.5.0: Semantic Extraction
            diff = repo.git.diff(prev.hexsha, curr.hexsha)
            comment_ratio = calculate_comment_ratio(diff)

            is_suspicious = is_commit_suspect(
                delta_seconds, total_changes, entropy, comment_ratio
            )
            report_data.append(
                {
                    "hash": curr.hexsha[:7],
                    "author": curr.author.name,
                    "timestamp": datetime.fromtimestamp(
                        curr.committed_date
                    ).isoformat(),
                    "changes": total_changes,
                    "files": file_names,
                    "entropy": round(entropy, 2),
                    "delta_seconds": delta_seconds,
                    "is_suspicious": is_suspicious,
                }
            )
            color = "red" if is_suspicious else "yellow"
            if is_suspicious:
                suspect_count += 1

            # Formatting file list
            files_display = "\n".join(file_names[:3])
            if files_touched > 3:
                files_display += f"\n[dim]...and {files_touched - 3} more[/dim]"

            table.add_row(
                curr.hexsha[:7],
                f"{total_changes} lines",
                files_display,
                f"{comment_ratio:.1%}",  # Display ratio as percentage
                f"[{color}]{delta_seconds}s[/{color}]",
            )

        console.print(table)
        return report_data

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        return []


# main() and export logic remains same as v0.4.0...
def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    audit_repository(path)


if __name__ == "__main__":
    main()
