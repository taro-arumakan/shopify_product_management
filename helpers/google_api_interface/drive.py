import io
import logging
import os
import pathlib
import re
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from PIL import Image

logger = logging.getLogger(__name__)


class GoogleDriveApiInterface:
    """
    Google Drive API Interface, inherited by GoogleApiInterface.
    """

    @staticmethod
    def natural_compare(k):
        def convert(text):
            return int(text) if text.isdigit() else text.lower()

        return [convert(c) for c in re.split("([0-9]+)", k)]

    def drive_images_to_local(
        self, folder_id, local_dir, filename_prefix="", sort_key_func=natural_compare
    ):
        os.makedirs(local_dir, exist_ok=True)
        image_details = self.get_drive_image_details(folder_id)
        image_details.sort(
            key=lambda f: sort_key_func(f["name"])
        )  # sort by natural order
        file_ids = [image["id"] for image in image_details]
        local_paths = [
            os.path.join(
                local_dir, f"{filename_prefix}_{str(seq).zfill(3)}_{image['name']}"
            )
            for seq, image in enumerate(image_details)
        ]
        return [
            self.download_and_process_image(file_id, local_path)
            for file_id, local_path in zip(file_ids, local_paths)
        ]

    def get_drive_image_details(self, folder_id):
        results = (
            self.drive_service.files()
            .list(
                q=f"'{folder_id}' in parents",
                pageSize=1000,
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
            )
            .execute()
        )
        items = results.get("files", [])
        return [
            item
            for item in items
            if item["mimeType"].startswith("image/")
            and not item["name"].startswith(".")
        ]

    def download_and_process_image(self, file_id, local_path):
        if not os.path.exists(local_path):
            logger.info(f"  starting download of {file_id} to {local_path}")
            self.download_file_from_drive(file_id, local_path)
            local_path = self.resize_image_to_limit(local_path, local_path)
        return local_path

    def download_file_from_drive(self, file_id, destination_path):
        request = self.drive_service.files().get_media(fileId=file_id)
        fh = io.FileIO(destination_path, "wb")
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            logger.debug(f"Download {int(status.progress() * 100)}%.")

    def rename_file_extension(self, file_path, image_mode):
        ext = {"RGBA": ".png"}.get(image_mode, ".jpg")
        p = pathlib.Path(file_path)
        if ext != p.suffix:
            new_path = os.path.join(p.parent, f"{p.stem}{ext}")
            logger.info(f"renaming output file to {new_path}")
            os.rename(file_path, new_path)
            return new_path
        return file_path

    def resize_image_to_limit(
        self, image_path, output_path, max_megapixels=15, max_mb=15
    ):
        file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
        with Image.open(image_path) as img:
            current_megapixels = (img.width * img.height) / 1_000_000
            if current_megapixels > max_megapixels or file_size_mb > max_mb:
                if current_megapixels > max_megapixels:
                    scale_factor = (max_megapixels / current_megapixels) ** 0.5
                    new_width = int(img.width * scale_factor)
                    new_height = int(img.height * scale_factor)
                else:
                    new_width, new_height = img.width, img.height

                resized_img = img.resize((new_width, new_height), Image.LANCZOS)
                if resized_img.mode == "RGBA":
                    kwargs = dict(format="PNG", optimize=True, compress_level=9)
                else:
                    kwargs = dict(format="JPEG", quality=85)
                resized_img.save(output_path, **kwargs)
                logger.info(
                    f"Image resized to {new_width}x{new_height} pixels and saved as {kwargs}"
                )
            image_mode = img.mode
        return self.rename_file_extension(output_path, image_mode)

    def find_by_folder_id_by_name(self, parent_folder_id, item_name, item_type=None):
        """
        Find an item by its name inside a given parent folder.

        :param parent_folder_id: ID of the parent folder where the search is performed.
        :param item_name: Name of the item to search for.
        :return: item meta of the folder if found, None otherwise.
        """

        item_name = item_name.replace("'", "\\'")
        query = (
            f"'{parent_folder_id}' in parents and "
            f"name='{item_name}' and "
            "trashed=false"
        )
        if item_type == "folder":
            query += " and mimeType='application/vnd.google-apps.folder'"
        results = (
            self.drive_service.files()
            .list(
                q=query,
                pageSize=10,  # Assuming there are not too many items with the same name
                fields="files(id, name, webViewLink)",
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
            )
            .execute()
        )
        items = results.get("files", [])
        if items and len(items) > 1:
            raise RuntimeError(
                f"Multiple items found with the name '{item_name}' in parent folder '{parent_folder_id}'."
            )
        elif items:
            return items[0]

    def find_folder_id_by_name(self, parent_folder_id, folder_name):
        folder = self.find_by_folder_id_by_name(
            parent_folder_id=parent_folder_id, item_name=folder_name, item_type="folder"
        )
        if folder:
            return folder["id"]

    def find_or_create_folder_by_name(self, parent_folder_id, folder_name):
        if folder_id := self.find_folder_id_by_name(
            parent_folder_id=parent_folder_id, folder_name=folder_name
        ):
            res = folder_id
        else:
            file_metadata = {
                "name": folder_name,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [parent_folder_id],
            }

            folder = (
                self.drive_service.files()
                .create(body=file_metadata, fields="id", supportsAllDrives=True)
                .execute()
            )

            res = folder["id"]
        return res

    def list_folders(self, parent_folder_id):
        query = f"'{parent_folder_id}' in parents and mimeType='application/vnd.google-apps.folder'"
        results = (
            self.drive_service.files()
            .list(
                q=query,
                pageSize=1000,
                fields="files(id, name)",
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
            )
            .execute()
        )
        return results["files"]

    def upload_to_drive(self, filepath, mimetype, folder_id):
        """upload a local file to Google Drive folder"""
        media = MediaIoBaseUpload(
            open(filepath, "rb"), mimetype=mimetype, resumable=True
        )
        f = (
            self.drive_service.files()
            .create(
                body={"name": os.path.basename(filepath), "parents": [folder_id]},
                media_body=media,
                fields="id",
                supportsAllDrives=True,
            )
            .execute()
        )
        logger.info(f"Uploaded: {f.get('id')}")

    def make_public_by_file_id(self, file_id):
        self.drive_service.permissions().create(
            fileId=file_id,
            body={"type": "anyone", "role": "reader"},
            supportsAllDrives=True,
        ).execute()

    def make_private_by_file_id(self, file_id):
        # List permissions and delete the 'anyone' one
        perms = (
            self.drive_service.permissions()
            .list(
                fileId=file_id,
                supportsAllDrives=True,
            )
            .execute()
        )
        for perm in perms.get("permissions", []):
            if perm["type"] == "anyone":
                self.drive_service.permissions().delete(
                    fileId=file_id,
                    permissionId=perm["id"],
                    supportsAllDrives=True,
                ).execute()

    def get_direct_url(self, file_id):
        return f"https://drive.google.com/uc?export=download&id={file_id}"  # Direct download link format
