from app import registry


def test_insert_list_get(tmp_path):
    db = str(tmp_path / "registry.db")
    registry.init_db(db)
    registry.insert_document(db, "d1", "a.pdf", "d1.pdf", 3, 10, "2026-01-01T00:00:00")
    registry.insert_document(db, "d2", "b.pdf", "d2.pdf", 1, 2, "2026-01-02T00:00:00")
    assert [d["doc_id"] for d in registry.list_documents(db)] == ["d2", "d1"]
    assert registry.get_document(db, "d1")["chunk_count"] == 10
    assert registry.get_document(db, "missing") is None


def test_delete(tmp_path):
    db = str(tmp_path / "registry.db")
    registry.init_db(db)
    registry.insert_document(db, "d1", "a.pdf", "d1.pdf", 1, 1, "2026-01-01T00:00:00")
    registry.delete_document(db, "d1")
    assert registry.list_documents(db) == []
