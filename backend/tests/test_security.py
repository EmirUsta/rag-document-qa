from app.security import has_pdf_extension, make_safe_filename, sniff_is_pdf


def test_safe_filename_ignores_user_input():
    doc_id, stored = make_safe_filename("../../etc/passwd.pdf")
    assert stored == f"{doc_id}.pdf"
    assert "/" not in stored and ".." not in stored


def test_safe_filename_is_unique():
    assert make_safe_filename("a.pdf")[0] != make_safe_filename("a.pdf")[0]


def test_pdf_extension_case_insensitive():
    assert has_pdf_extension("Rapor.PDF")
    assert not has_pdf_extension("rapor.pdf.exe")


def test_magic_bytes():
    assert sniff_is_pdf(b"%PDF-1.7\n")
    assert not sniff_is_pdf(b"MZ\x90\x00")
