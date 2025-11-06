import base64
import logging
from urllib.parse import urlparse

from supabase import create_client

from adapter.storage_adapter import IStorageAdapter
from domain.error.errors import StorageDeleteError, StorageUploadError


class SupabaseStorageAdapter(IStorageAdapter):
    def __init__(
        self,
        supabase_url: str,
        supabase_key: str,
        bucket_name: str = "images",
    ) -> None:
        self._client = create_client(supabase_url, supabase_key)
        self._bucket_name = bucket_name
        self._supabase_url = supabase_url

    async def upload_image(self, image_data: str, user_id: str, plant_id: str) -> str:
        try:
            image_bytes, extension = self._decode_base64_image(image_data)
            file_path = self._generate_file_path(user_id, plant_id, extension)

            self._client.storage.from_(self._bucket_name).upload(
                path=file_path,
                file=image_bytes,
                file_options={"content-type": f"image/{extension}"},
            )

            public_url = self._client.storage.from_(self._bucket_name).get_public_url(
                file_path,
            )

            return public_url

        except Exception as error:
            logging.exception("Failed to upload image to storage")
            error_message = f"Storage upload failed: {error!s}"
            raise StorageUploadError(error_message) from error

    async def delete_image(self, image_url: str) -> bool:
        try:
            file_path = self._extract_file_path_from_url(image_url)

            result = self._client.storage.from_(self._bucket_name).remove([file_path])

            return len(result) > 0

        except Exception as error:
            logging.exception("Failed to delete image from storage")
            error_message = f"Storage delete failed: {error!s}"
            raise StorageDeleteError(error_message) from error

    def _decode_base64_image(self, data_url: str) -> tuple[bytes, str]:
        try:
            if "," in data_url:
                header, encoded = data_url.split(",", 1)
                mime_type = header.split(":")[1].split(";")[0]
            else:
                encoded = data_url
                mime_type = "image/jpeg"

            image_bytes = base64.b64decode(encoded)
            extension = self._get_file_extension(mime_type)

            return image_bytes, extension

        except Exception as error:
            error_message = f"Failed to decode base64 image: {error!s}"
            raise ValueError(error_message) from error

    def _get_file_extension(self, mime_type: str) -> str:
        mime_to_ext = {
            "image/jpeg": "jpg",
            "image/jpg": "jpg",
            "image/png": "png",
            "image/webp": "webp",
            "image/gif": "gif",
        }
        return mime_to_ext.get(mime_type.lower(), "jpg")

    def _generate_file_path(self, user_id: str, plant_id: str, extension: str) -> str:
        return f"{user_id}/{plant_id}.{extension}"

    def _extract_file_path_from_url(self, url: str) -> str:
        parsed = urlparse(url)
        path_parts = parsed.path.split(
            f"/storage/v1/object/public/{self._bucket_name}/",
        )
        if len(path_parts) > 1:
            return path_parts[1]
        return parsed.path.split("/")[-1]
