def test_robotic_signature_detection(mocker):
    # GIVEN: A mock commit with 40% comment density and 5s delta
    from miner import calculate_comment_ratio, is_commit_suspect

    # Mock diff containing 2 code lines and 2 comment lines (50%)
    mock_diff = (
        "+ print('hello')\n+ # AI generated comment\n+ x = 10\n+ '''Docstring'''"
    )

    # WHEN: Calculating ratio and suspicion
    ratio = calculate_comment_ratio(mock_diff)
    suspect = is_commit_suspect(
        delta_seconds=5, total_changes=4, entropy=2.0, comment_ratio=ratio
    )

    # EXPECT: Suspect is True due to is_robotic (speed + high comments)
    assert ratio == 0.5
    assert suspect is True
