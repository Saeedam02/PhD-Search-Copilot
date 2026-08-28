from docx import Document

from phd_search_agent.profile_ingest import extract_text


def test_extract_docx(tmp_path):
    path = tmp_path / "cv.docx"
    doc = Document()
    doc.add_paragraph("Control Engineering")
    doc.save(path)
    assert "Control Engineering" in extract_text(path)
