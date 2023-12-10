import os
import uuid
import logging

from azure.storage.blob import BlobBlock
from azure.storage.blob import BlobServiceClient

class storage():

    def init_app(self, app):
        # STORAGE BLOB SERVICE CLIENT
        logging.info('Setting Azure Blob Storage connection')
        self.blob_service_client = BlobServiceClient.from_connection_string(app.config["AZURE_STORAGE_CONNECTION_STRING"])

    def download_blob(self, container, blob):
        logging.info('Donwloading blob from: conatiner: ' + container + ', blob: ' + blob)
        blob_client = self.blob_service_client.get_blob_client(container=container, blob=blob)
        blob = blob_client.download_blob(connection_timeout=600).readall()
        return blob

    def upload_blob(self, content, container, blob):
        logging.info('Uploading blob into: conatiner: ' + container + ', blob: ' + blob)
        blob_client = self.blob_service_client.get_blob_client(container=container, blob=blob)
        blob_client.upload_blob(content, overwrite=True, connection_timeout=600)

    def delete_blob(self, container, blob):
        logging.info('Deleting blob into: conatiner: ' + container + ', blob: ' + blob)
        container_client = self.blob_service_client.get_container_client(container=container)
        container_client.delete_blob(blob=blob)

    def list_blobs(self, container, blob_path=None):
        container_client = self.blob_service_client.get_container_client(container=container)
        blob_iter = container_client.list_blobs(name_starts_with=blob_path)
        blob_list = [blob.name for blob in blob_iter]
        return blob_list

    def blob_exists(self, container, blob):
        blob_client = self.blob_service_client.get_blob_client(container=container, blob=blob)
        return blob_client.exists()
    
    def upload_large_blob(self, content, container, blob):
        logging.info('Uploading blob into: conatiner: ' + container + ', blob: ' + blob)
        blob_client = self.blob_service_client.get_blob_client(container=container, blob=blob)

        block_list = []
        chunk_size = 1024*1024*4

        chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]

        for chunk in chunks:
            blk_id = str(uuid.uuid4())
            blob_client.stage_block(block_id=blk_id, data=chunk) 
            block_list.append(BlobBlock(block_id=blk_id))

        blob_client.commit_block_list(block_list)
    
    def list_containers(self):
        containers_iterator = list(self.blob_service_client.list_containers())
        containers_list = [container.name for container in containers_iterator]
        return containers_list
    
    def create_container(self, container):
        logging.info('Creating conatiner: ' + container)
        self.blob_service_client.create_container(container)