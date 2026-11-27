import os
import uuid

import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from django.core.files.storage import Storage


class CloudinaryStorage(Storage):
    """Guarda las imágenes de productos en Cloudinary.

    Usa la variable CLOUDINARY_URL que el SDK de Cloudinary lee sola.
    """

    def _public_id(self, name):
        return os.path.splitext(name)[0]

    def _open(self, name, mode='rb'):
        raise NotImplementedError('No se leen archivos directamente de Cloudinary.')

    def _save(self, name, content):
        base, ext = os.path.splitext(os.path.basename(name))
        folder = os.path.dirname(name)
        nombre_unico = f'{folder}/{base}_{uuid.uuid4().hex[:8]}{ext}'.lstrip('/')
        cloudinary.uploader.upload(
            content,
            public_id=self._public_id(nombre_unico),
            resource_type='image',
            overwrite=False,
        )
        return nombre_unico

    def delete(self, name):
        if name:
            cloudinary.uploader.destroy(self._public_id(name), resource_type='image')

    def exists(self, name):
        return False

    def url(self, name):
        url, _ = cloudinary_url(self._public_id(name), secure=True, resource_type='image')
        return url

    def size(self, name):
        return 0
