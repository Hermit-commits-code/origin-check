import argparse
import json
import os
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime as dt

import git
from rich.console import Console
from rich.table import Table

from analyzer import ForensicEngine
from database import DatabaseManager

VERSION = "1.0.0"

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
        current = repo.commit(curr_sha)
        previous = repo.commit(prev_sha)
        delta_seconds = current.committed_date - previous.committed_date

        scores = []
        differences = previous.diff(current, create_patch=True)

        for d in differences:
            file_path = d.b_path or d.a_path
            diff_content = d.diff
            if isinstance(diff_content, bytes):
                difference_text = diff_content.decode("utf-8", errors="ignore")
            else:
                difference_text = str(diff_content or "")

            # v0.8.0 Fix: Connect the variables to the Engine
            score = ForensicEngine.analyze_diff(
                file_path, difference_text, delta_seconds
            )
            scores.append(score)
        # Return the average score of all the files in this particular commit.
        final_ratio = sum(scores) / len(scores) if scores else 0.0
        return curr_sha, final_ratio
    except Exception:
        return curr_sha, 0.0


def is_commit_suspect(ai_score: float) -> bool:
    """v0.8.1: Simplified threshold based on ForensicEngine output."""
    # We flag any commit where the AI probability exceeds 75%
    return ai_score > 0.75


def audit_repository(repo_path=".", target_author=None):
    """
    v1.0.0: Full forensic audit with Velocity (LPM) metrics and
    calibrated AI scoring.
    """
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

        # 1. Cache Lookup Phase
        needed_work = []
        ratios_map = {}

        for i in range(len(commits) - 1):
            curr_sha = commits[i].hexsha
            prev_sha = commits[i + 1].hexsha

            # Check SQLite first
            cached = db.get_cached_commit(curr_sha)
            if cached:
                # cached is a tuple: (ai_score, is_suspicious, entropy)
                ratios_map[curr_sha] = cached[0]
            else:
                needed_work.append((repo_path, prev_sha, curr_sha))

        # 2. Compute Phase (Only for Cache Misses)
        if needed_work:
            console.print(f"[blue]Analyzing {len(needed_work)} new commits...[/blue]")
            with ProcessPoolExecutor() as executor:
                new_results = list(executor.map(process_commit_diff, needed_work))
                for sha, ratio in new_results:
                    ratios_map[sha] = ratio

        # 3. Reporting & Persistence Phase
        # Updated Title and Columns for v1.0.0
        table = Table(title=f"Origin-Miner v{VERSION} | Forensic Auditor")
        table.add_column("Hash", style="cyan")
        table.add_column("Changes", style="blue")
        table.add_column("Files", style="magenta")
        table.add_column("AI Score", style="green")
        table.add_column("Time Delta", style="bold yellow")
        table.add_column("Velocity", style="bold cyan")  # New Velocity Column

        for i in range(len(commits) - 1):
            curr, prev = commits[i], commits[i + 1]
            # Ensure at least 1 second to avoid division by zero in velocity
            delta_seconds = max(curr.committed_date - prev.committed_date, 1)

            total_changes = curr.stats.total["lines"]
            file_names = [str(f) for f in curr.stats.files.keys()]
            files_touched = len(file_names)
            entropy = total_changes / files_touched if files_touched > 0 else 0

            # v1.0.0: Lines Per Minute (LPM) calculation
            lpm = (total_changes / delta_seconds) * 60

            # Retrieve pre-calculated AI score
            ai_score = ratios_map.get(curr.hexsha, 0.0)

            # v0.8.1 Gate: Simplified suspicion check
            is_suspicious = is_commit_suspect(ai_score)
            color = "red" if is_suspicious else "yellow"

            # Save/Update Cache
            db.save_commit(curr.hexsha, ai_score, is_suspicious, entropy)

            # Format file display
            files_display = "\n".join(file_names[:3])
            if files_touched > 3:
                files_display += f"\n[dim]...and {files_touched - 3} more[/dim]"

            # Add Row with new Velocity data
            table.add_row(
                curr.hexsha[:7],
                f"{total_changes} lines",
                files_display,
                f"{ai_score:.1%}",
                f"[{color}]{delta_seconds}s[/{color}]",
                f"{lpm:.1f} LPM",  # Visualizing the speed of code injection
            )

            report_data.append(
                {
                    "hash": curr.hexsha[:7],
                    "author": curr.author.name,
                    "timestamp": dt.fromtimestamp(curr.committed_date).isoformat(),
                    "changes": total_changes,
                    "files": file_names,
                    "ai_score": round(ai_score, 4),
                    "lpm": round(lpm, 2),
                    "delta_seconds": delta_seconds,
                    "is_suspicious": is_suspicious,
                }
            )

        console.print(table)
        return report_data

    except Exception as e:
        console.print(f"[bold red]Error during audit:[/bold red] {e}")
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

    CACHE_NAME = ".miner_cache.db"

    if args.clear_cache:
        if os.path.exists(CACHE_NAME):
            os.remove(CACHE_NAME)
            # Also attempt to remove the non-hidden one if it exists from previous bugs
            if os.path.exists("miner_cache.db"):
                os.remove("miner_cache.db")
            console.print("[bold green]✔ All forensic caches cleared.[/bold green]")
    results = audit_repository(args.path, args.author)

    if args.export and results:
        with open(args.export, "w") as f:
            json.dump(results, f, indent=4)
        console.print(f"\n[bold green]Report exported to {args.export}[/bold green]")


if __name__ == "__main__":
    main()
