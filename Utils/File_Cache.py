# Creates a json file to store the cache. This is a simple implementation of a file cache.
import json
import os


class File_Cache:
    def __init__(self, cache_file, buffer_count = 100):
        self.cache_file = cache_file
        self.cache = {}
        self.out_of_sync_counter = 0
        self.buffer_count = buffer_count
        
        if not os.path.exists(self.cache_file):
            # create folder if not exists
            folder = os.path.dirname(self.cache_file)
            if not os.path.exists(folder):
                os.makedirs(folder)
            with open(self.cache_file, 'w') as f:
                f.write(json.dumps({}))
        
        self.__read_cache__()
        
    def __read_cache__(self):
        try:
            with open(self.cache_file, 'r') as f:
                self.cache = json.loads(f.read())
        except:
            self.cache = {}
    
    def __write__(self):
        with open(self.cache_file, 'w') as f:
            f.write(json.dumps(self.cache, indent=4))

    def flush(self):
        if self.out_of_sync_counter > 0:
            self.__write__()
            self.out_of_sync_counter = 0
            
    def write(self, force=False):        
        # write every 100 access
        if self.out_of_sync_counter >= self.buffer_count or force:
            self.flush()
            return
        self.out_of_sync_counter += 1
        
            
    def get(self, key, default=None):
        return self.cache.get(key, None)
    
    def set(self, key, value):
        self.cache[key] = value
        self.write()
        
    def remove(self, key):
        del self.cache[key]
        self.write()
        
    def get_keys(self) -> list[str]:
        return self.cache.keys() # type: ignore
    
    def get_values(self):
        return self.cache.values()
    
    def contains(self, key):
        return key in self.cache
    
    def close(self):
        self.__write__()
        
    def __del__(self):
        if self.out_of_sync_counter > 0:
            self.__write__()