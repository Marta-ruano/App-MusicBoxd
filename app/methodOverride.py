from urllib.parse import parse_qs
from io import BytesIO

class MethodOverrideMiddleware:
    allowed_methods = {"GET", "POST", "PUT", "DELETE", "PATCH"}

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        if environ.get("REQUEST_METHOD", "") == "POST":
            try:
                request_body_size = int(environ.get("CONTENT_LENGTH", 0))
            except (ValueError, TypeError):
                request_body_size = 0

            body = environ["wsgi.input"].read(request_body_size)
            environ["wsgi.input"] = BytesIO(body)

            content_type = (environ.get("CONTENT_TYPE") or "").lower()

            method = ""

            if "application/x-www-form-urlencoded" in content_type:
                try:
                    form_data = parse_qs(body.decode("utf-8", errors="ignore"))
                    method = (form_data.get("_method", [""])[0] or "").upper()
                except Exception:
                    method = ""

            elif "multipart/form-data" in content_type:
                try:
                    marker = b'name="_method"'
                    idx = body.find(marker)
                    if idx != -1:
                        sep = body.find(b"\r\n\r\n", idx)
                        if sep != -1:
                            start = sep + 4
                            end = body.find(b"\r\n", start)
                            if end != -1:
                                method = body[start:end].decode("utf-8", errors="ignore").strip().upper()
                except Exception:
                    method = ""

            if method in self.allowed_methods:
                environ["REQUEST_METHOD"] = method

            environ["wsgi.input"].seek(0)

        return self.app(environ, start_response)