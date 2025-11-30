import tempfile
from unittest import mock

import pytest

from wbdata import cache


def test_get_cache_returns_working_cache():
    """Test that get_cache creates a working cache."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_cache = cache.get_cache(path=f"{tmpdir}/test_cache")
        test_cache["key"] = "value"
        assert test_cache["key"] == "value"
        test_cache.close()


def test_get_cache_recovers_from_corrupted_cache():
    """Test that get_cache recovers gracefully from a corrupted cache file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_path = f"{tmpdir}/test_cache"

        # Create and populate a cache
        test_cache = cache.get_cache(path=cache_path)
        test_cache["key"] = "value"
        test_cache.close()

        # Create a mock that raises SystemError on first call, then works on second
        call_count = [0]
        original_getattr = cache.shelved_cache.PersistentCache.__getattr__

        def mock_getattr(self, item):
            # Only intercept expire calls on the first cache instance
            if item == "expire":
                call_count[0] += 1
                if call_count[0] == 1:
                    raise SystemError("Negative size passed to PyBytes")
            return original_getattr(self, item)

        # Mock __getattr__ to simulate corruption when expire() is called
        with mock.patch.object(
            cache.shelved_cache.PersistentCache, "__getattr__", mock_getattr
        ):
            # This should recover and create a new cache
            new_cache = cache.get_cache(path=cache_path)

        # The new cache should work (but the old value will be lost)
        new_cache["new_key"] = "new_value"
        assert new_cache["new_key"] == "new_value"
        new_cache.close()


def test_remove_cache_files():
    """Test that _remove_cache_files removes all cache-related files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_path = f"{tmpdir}/test_cache"

        # Create a cache which will create files
        test_cache = cache.get_cache(path=cache_path)
        test_cache["key"] = "value"
        test_cache.close()

        # Remove the cache files
        cache._remove_cache_files(cache_path)

        # Verify cache files are removed (new cache should be empty)
        new_cache = cache.get_cache(path=cache_path)
        with pytest.raises(KeyError):
            _ = new_cache["key"]
        new_cache.close()
