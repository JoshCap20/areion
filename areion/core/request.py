class HttpRequest:
    def __init__(self, method, path, headers):
        self.method = method
        self.path = path
        self.headers = headers
        self.metadata = {}

    def add_header(self, key, value):
        self.headers[key] = value

    def get_header(self, key):
        return self.headers.get(key)

    def add_metadata(self, key, value):
        self.metadata[key] = value

    def get_metadata(self, key):
        return self.metadata.get(key)

    def __repr__(self):
        return f"<HttpRequest method={self.method} path={self.path} headers={self.headers} metadata={self.metadata}>"
    
    def as_dict(self):
        return {
            "method": self.method,
            "path": self.path,
            "headers": self.headers,
            "metadata": self.metadata
        }
