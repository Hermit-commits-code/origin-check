from miner import calculate_comment_ratio, process_commit_diff


def test_calculate_comment_ratio_logic():
    # GIVEN: A diff with exactly 50% comments
    mock_diff = (
        "+ def new_func():\n"  # Code
        "+     # This is a comment\n"  # Comment
        "+     return True\n"  # Code
        "+     '''Docstring'''"  # Comment
    )

    # WHEN: We calculate the ratio
    ratio = calculate_comment_ratio(mock_diff)

    # EXPECT: 0.5 (2 comments out of 4 added lines)
    assert ratio == 0.5


def test_worker_result_structure(mocker):
    # GIVEN: A mock repository and commit hashes
    mock_repo = mocker.patch("git.Repo")
    mock_instance = mock_repo.return_value
    mock_instance.git.diff.return_value = "+ # Comment\n+ x = 1"

    args = ("/fake/path", "prev_sha_123", "curr_sha_456")

    # WHEN: The worker process runs
    sha, ratio = process_commit_diff(args)

    # EXPECT: The worker returns the CURRENT sha and the correct ratio
    assert sha == "curr_sha_456"
    assert ratio == 0.5


def test_parallel_mapping_consistency():
    # GIVEN: Simulated results from multiple worker processes
    raw_results = [("hash_a", 0.10), ("hash_b", 0.45), ("hash_c", 0.05)]

    # WHEN: The main process converts these to a map
    ratios_map = dict(raw_results)

    # EXPECT: Data integrity is maintained
    assert ratios_map["hash_b"] == 0.45
    assert len(ratios_map) == 3
