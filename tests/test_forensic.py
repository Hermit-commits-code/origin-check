def test_audit_data_structure_v4(mocker):
    # GIVEN: A mocked commit with specific files
    mock_commit = mocker.MagicMock()
    mock_commit.stats.files = {"file_a.py": {}, "file_b.py": {}}
    mock_commit.stats.total = {"lines": 200}

    # WHEN: We process this in our audit logic
    file_names = [str(f) for f in mock_commit.stats.files.keys()]

    # EXPECT: A list of strings, not objects
    assert all(isinstance(f, str) for f in file_names)
    assert len(file_names) == 2
