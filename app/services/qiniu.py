import os


class QiniuService:
    def __init__(self):
        self.access_key = os.getenv("QINIU_ACCESS_KEY", "")
        self.secret_key = os.getenv("QINIU_SECRET_KEY", "")
        self.bucket_name = os.getenv("QINIU_BUCKET_NAME", "")
        self.upload_domain = os.getenv("QINIU_UPLOAD_DOMAIN", "")

    def is_configured(self) -> bool:
        return bool(
            self.access_key and self.secret_key and self.bucket_name and self.upload_domain
        )

    def generate_upload_token(self, key: str, expires_in: int = 3600) -> str:
        """Generate Qiniu upload token for a specific key."""
        if not self.is_configured():
            raise RuntimeError("Qiniu is not configured")

        try:
            from qiniu import Auth
        except ImportError:
            raise RuntimeError("qiniu SDK is not installed")

        auth = Auth(self.access_key, self.secret_key)
        token = auth.upload_token(self.bucket_name, key, expires_in)
        return token
