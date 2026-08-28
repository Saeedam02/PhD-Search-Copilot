from phd_search_agent.profile_ingest import collect_candidate_documents, extract_text


def test_collect_text_and_markdown(tmp_path):
    private = tmp_path / "private"
    (private / "cv").mkdir(parents=True)
    (private / "supporting").mkdir(parents=True)
    (private / "cv" / "cv.txt").write_text("MSc Control Engineering", encoding="utf-8")
    (private / "supporting" / "notes.md").write_text("# Projects\nMPC", encoding="utf-8")
    (private / "ignore.bin").write_bytes(b"not text")
    bundle = collect_candidate_documents(private)
    assert len(bundle.documents) == 2
    assert "MSc Control Engineering" in bundle.combined_text


def test_unsupported_file_rejected(tmp_path):
    path = tmp_path / "file.csv"
    path.write_text("a,b", encoding="utf-8")
    try:
        extract_text(path)
    except ValueError as exc:
        assert "Unsupported" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_missing_private_dir_returns_empty(tmp_path):
    bundle = collect_candidate_documents(tmp_path / "missing")
    assert bundle.documents == []
