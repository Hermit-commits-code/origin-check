from miner import is_commit_suspect


def test_is_commit_suspect_velocity_alert():
    """Flag: Commit is too fast AND has significant volume."""
    assert is_commit_suspect(delta_seconds=5, total_changes=100, entropy=10.0) is True


def test_is_commit_suspect_entropy_alert():
    """Flag: Commit is slow but incredibly dense (The Big Paste)."""
    assert (
        is_commit_suspect(delta_seconds=600, total_changes=200, entropy=200.0) is True
    )


def test_is_commit_suspect_normal_refactor():
    """Ignore: Large volume spread across many files."""
    assert (
        is_commit_suspect(delta_seconds=300, total_changes=500, entropy=10.0) is False
    )


def test_is_commit_suspect_quick_fix():
    """Ignore: Very fast delta but tiny volume (Typo fix)."""
    assert is_commit_suspect(delta_seconds=3, total_changes=2, entropy=2.0) is False


def test_is_commit_suspect_threshold_boundaries():
    """Verify: Exact boundary conditions do not trigger."""
    assert is_commit_suspect(delta_seconds=15, total_changes=50, entropy=150.0) is False
