import io
import os
import re
import logging
from googleapiclient.http import MediaIoBaseDownload
from PIL import Image

class GoogleDriveApiInterface:
    '''
    Google Drive API Interface, inherited by GoogleApiInterface.
    '''
    logger = logging.getLogger(f"{__module__}.{__qualname__}")

    @staticmethod
    def natural_compare(k):
        def convert(text):
            return int(text) if text.isdigit() else text.lower()
        return [convert(c) for c in re.split('([0-9]+)', k)]

    def drive_images_to_local(self, folder_id, local_dir, filename_prefix='', sort_key_func=natural_compare):
        os.makedirs(local_dir, exist_ok=True)
        image_details = self.get_drive_image_details(folder_id)
        image_details.sort(key=lambda f: sort_key_func(f['name']))        # sort by natural order
        file_ids = [image['id'] for image in image_details]
        local_paths = [os.path.join(local_dir, f"{filename_prefix}_{str(seq).zfill(3)}_{image['name']}") for seq, image in enumerate(image_details)]
        return [self.download_and_process_image(file_id, local_path) for file_id, local_path in zip(file_ids, local_paths)]

    def get_drive_image_details(self, folder_id):
        results = self.drive_service.files().list(
                            q=f"'{folder_id}' in parents",
                            pageSize=1000,
                            includeItemsFromAllDrives=True,
                            supportsAllDrives=True,
                        ).execute()
        items = results.get('files', [])
        return [item for item in items if item['mimeType'].startswith('image/')]

    def download_and_process_image(self, file_id, local_path):
        if not os.path.exists(local_path):
            self.logger.info(f"  starting download of {file_id} to {local_path}")
            self.download_file_from_drive(file_id, local_path)
            self.resize_image_to_limit(local_path, local_path)
        return local_path

    def download_file_from_drive(self, file_id, destination_path):
        request = self.drive_service.files().get_media(fileId=file_id)
        fh = io.FileIO(destination_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            self.logger.debug(f"Download {int(status.progress() * 100)}%.")

    def resize_image_to_limit(self, image_path, output_path, max_megapixels=20):
        with Image.open(image_path) as img:
            current_megapixels = (img.width * img.height) / 1_000_000
            if current_megapixels > max_megapixels:
                scale_factor = (max_megapixels / current_megapixels) ** 0.5
                new_width = int(img.width * scale_factor)
                new_height = int(img.height * scale_factor)

                resized_img = img.resize((new_width, new_height), Image.LANCZOS)
                if resized_img.mode == 'RGBA':
                    kwargs = dict(format='PNG')
                else:
                    kwargs = dict(format='JPEG', quarity=85)
                resized_img.save(output_path, **kwargs)
                self.logger.info(f"Image resized to {new_width}x{new_height} pixels and saved as {kwargs}")

    def find_folder_id_by_name(self, parent_folder_id, folder_name):
        """
        Find a folder ID by its name inside a given parent folder.

        :param parent_folder_id: ID of the parent folder where the search is performed.
        :param folder_name: Name of the folder to search for.
        :return: The ID of the folder if found, None otherwise.
        """
        # Query for folders with the specified name inside the parent folder
        folder_name = folder_name.replace("'", "\\'")
        query = f"'{parent_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and name='{folder_name}'"
        results = self.drive_service.files().list(
            q=query,
            pageSize=10,  # Assuming there are not too many folders with the same name
            fields="files(id, name)",
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
        ).execute()

        items = results.get('files', [])
        if items and len(items) > 1:
            raise RuntimeError(f"Multiple folders found with the name '{folder_name}' in parent folder '{parent_folder_id}'.")
        return items[0]['id']

    def list_folders(self, parent_folder_id):
        query = f"'{parent_folder_id}' in parents and mimeType='application/vnd.google-apps.folder'"
        results = self.drive_service.files().list(
                q=query,
                pageSize=1000,
                fields="files(id, name)",
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
            ).execute()
        return results['files']
