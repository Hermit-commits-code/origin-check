from miner import audit_repository


def test_audit_repository_non_git_dir(mocker):
    # GIVEN: A directory that is NOT a git repo
    # We "mock" git.Repo to raise an error immediately
    mocker.patch("git.Repo", side_effect=Exception("Invalid Git Room"))

    # We also mock console.print so we don't clutter the test output
    mock_print = mocker.patch("miner.console.print")

    # WHEN: We run the audit
    audit_repository("/fake/path")

    # EXPECT: The error message was printed gracefully instead of crashing
    mock_print.assert_called_with("[bold red]Error:[/bold red] Invalid Git Room")
