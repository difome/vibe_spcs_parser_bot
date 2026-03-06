import time

class TTLCache:
    def __init__(self, ttl, max_size=5000):
        self.ttl = ttl
        self.max_size = max_size
        self._cache = {}

    def __contains__(self, key):
        if key not in self._cache:
            return False
        value, expiry = self._cache[key]
        if time.time() > expiry:
            del self._cache[key]
            return False
        return True

    def __getitem__(self, key):
        if key not in self._cache:
            raise KeyError(key)
        value, expiry = self._cache[key]
        if time.time() > expiry:
            del self._cache[key]
            raise KeyError(key)
        return value

    def __setitem__(self, key, value):
        now = time.time()
        if len(self._cache) >= self.max_size and key not in self._cache:
            # Simple eviction of expired items
            to_delete = [k for k, (_, exp) in self._cache.items() if exp < now]
            for k in to_delete:
                del self._cache[k]
            # If still full, remove the oldest (first added) entries
            if len(self._cache) >= self.max_size:
                for k in list(self._cache.keys())[:int(self.max_size * 0.1)]:
                    del self._cache[k]

        self._cache[key] = (value, now + self.ttl)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

track_info_cache = TTLCache(ttl=172800)
picture_info_cache = TTLCache(ttl=172800)
video_info_cache = TTLCache(ttl=172800)

search_cache = TTLCache(ttl=600)
picture_search_cache = TTLCache(ttl=600)
music_files_search_cache = TTLCache(ttl=600)
video_files_search_cache = TTLCache(ttl=600)

categories_cache = None
tracks_cache = TTLCache(ttl=3600)
