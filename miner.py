import argparse
import json
import os
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime as dt

import git
from rich.console import Console
from rich.table import Table

from database import DatabaseManager

VERSION = "0.7.0"
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


def process_commit_diff(args):
    """v0.6.0 Performance Worker: Runs in a separate process."""
    repo_path, prev_sha, curr_sha = args
    try:
        # Re-initialize repo in worker process for thread safety
        repo = git.Repo(repo_path)
        diff = repo.git.diff(prev_sha, curr_sha)
        ratio = calculate_comment_ratio(diff)
        return curr_sha, ratio
    except Exception:
        return curr_sha, 0.0


def is_commit_suspect(
    delta_seconds: int, total_changes: int, entropy: float, comment_ratio: float = 0
) -> bool:
    """v0.5.1: Balanced heuristic for AI signature detection."""
    is_too_fast = delta_seconds < 15 and total_changes > 50
    is_too_dense = entropy > 150
    is_robotic = delta_seconds < 10 and comment_ratio > 0.40
    return is_too_fast or is_too_dense or is_robotic


def audit_repository(repo_path=".", target_author=None):
    db = DatabaseManager()
    report_data = []
    try:
        repo = git.Repo(repo_path)
        commits = [
            c
            for c in repo.iter_commits(max_count=50)
            if not target_author or c.author.name == target_author
        ]

        if len(commits) < 2:
            console.print(
                "[yellow]Not enough commits to perform delta analysis.[/yellow]"
            )
            return []
        # 1. Cache Lookup
        needed_work = []
        ratios_map = {}

        for i in range(len(commits) - 1):
            curr_sha = commits[i].hexsha
            prev_sha = commits[i + 1].hexsha

            # Check SQLite first
            cached = db.get_cached_commit(curr_sha)
            if cached:
                # cached is a tuple: (comment_ratio, is_suspicious, entropy)
                ratios_map[curr_sha] = cached[0]
            else:
                needed_work.append((repo_path, prev_sha, curr_sha))
        # 2. COMPUTE PHASE (Only for Cache Misses)
        if needed_work:
            console.print(f"[blue]Analyzing {len(needed_work)} new commits...[/blue]")
            with ProcessPoolExecutor() as executor:
                new_results = list(executor.map(process_commit_diff, needed_work))
                for sha, ratio in new_results:
                    ratios_map[sha] = ratio

        # 3. REPORTING & PERSISTENCE PHASE
        table = Table(title="Origin-Miner v0.7.0 | SQLite-Optimized")
        table.add_column("Hash", style="cyan")
        table.add_column("Changes", style="blue")
        table.add_column("Files", style="magenta")
        table.add_column("AI Score", style="green")
        table.add_column("Time Delta", style="bold yellow")

        for i in range(len(commits) - 1):
            curr, prev = commits[i], commits[i + 1]
            delta_seconds = curr.committed_date - prev.committed_date

            total_changes = curr.stats.total["lines"]
            file_names = [str(f) for f in curr.stats.files.keys()]
            files_touched = len(file_names)
            entropy = total_changes / files_touched if files_touched > 0 else 0

            # Retrieve pre-calculated ratio from v0.6.0 pool
            comment_ratio = ratios_map.get(curr.hexsha, 0.0)

            is_suspicious = is_commit_suspect(
                delta_seconds, total_changes, entropy, comment_ratio
            )
            color = "red" if is_suspicious else "yellow"
            # SAVE TO CACHE (If it wasn't there before)
            db.save_commit(curr.hexsha, comment_ratio, is_suspicious, entropy)

            files_display = "\n".join(file_names[:3])
            if files_touched > 3:
                files_display += f"\n[dim]...and {files_touched - 3} more[/dim]"

            table.add_row(
                curr.hexsha[:7],
                f"{total_changes} lines",
                files_display,
                f"{comment_ratio:.1%}",
                f"[{color}]{delta_seconds}s[/{color}]",
            )

            report_data.append(
                {
                    "hash": curr.hexsha[:7],
                    "author": curr.author.name,
                    "timestamp": dt.fromtimestamp(curr.committed_date).isoformat(),
                    "changes": total_changes,
                    "files": file_names,
                    "comment_ratio": round(comment_ratio, 4),
                    "entropy": round(entropy, 2),
                    "delta_seconds": delta_seconds,
                    "is_suspicious": is_suspicious,
                }
            )

        console.print(table)
        return report_data

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        return []


def main():
    parser = argparse.ArgumentParser(description="Origin-Miner: Forensic Git Auditor")
    parser.add_argument("--path", default=".", help="Path to git repository")
    parser.add_argument("--author", help="Filter by author name")
    parser.add_argument("--export", help="Export report to JSON file")
    # New v0.7.0 Flags
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Delete the local forensic database and start fresh",
    )

    args = parser.parse_args()

    if args.clear_cache:
        db_file = ".miner_cache.db"
        if os.path.exists(db_file):
            os.remove(db_file)
            console.print(
                "[bold green]✔ Forensic cache cleared successfully.[/bold green]"
            )
        else:
            console.print("[yellow]No cache file found to clear.[/yellow]")
        return  # Exit after clearing

    results = audit_repository(args.path, args.author)

    if args.export and results:
        with open(args.export, "w") as f:
            json.dump(results, f, indent=4)
        console.print(f"\n[bold green]Report exported to {args.export}[/bold green]")


if __name__ == "__main__":
    main()
