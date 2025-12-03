import wbdata.cache as cache


def test_get_cache_recovers_from_corruption(tmp_path, monkeypatch):
    cache_path = tmp_path / "cachefile"
    cache_path.write_bytes(b"corrupt")

    call_count = {"value": 0}

    class FakeCache:
        def expire(self):
            call_count["value"] += 1
            if call_count["value"] == 1:
                raise SystemError("boom")

    monkeypatch.setattr(
        cache.shelved_cache, "PersistentCache", lambda *args, **kwargs: FakeCache()
    )

    result = cache.get_cache(path=cache_path, ttl_days=1, max_size=1)

    assert isinstance(result, FakeCache)
    assert call_count["value"] == 2  # retried after clearing corruption
    assert not cache_path.exists()


def test_clear_cache_files_removes_shelve_variants(tmp_path):
    base = tmp_path / "cachefile"
    variants = [
        base,
        base.with_suffix(".db"),
        base.with_suffix(".dat"),
        base.with_suffix(".dir"),
        base.with_suffix(".bak"),
        tmp_path / "cachefile.extra",
    ]
    for path in variants:
        if path.suffix == ".dir":
            path.mkdir()
        else:
            path.write_text("x")

    cache._clear_cache_files(base)

    for path in variants:
        assert not path.exists()
