from pyracms import DBSession
from pyracms.lib.filelib import FileLib
from pyracms.lib.taglib import TagLib, GALLERY
from sqlalchemy.orm.exc import NoResultFound
from ..models import GalleryAlbum, GalleryPicture, GalleryPictureTags


class AlbumNotFound(Exception):
    pass
class PictureNotFound(Exception):
    pass
class InvalidPicture(Exception):
    pass
class GalleryLib:
    """
    A library to manage the gallery database.
    """

    def __init__(self):
        self.t = TagLib(GalleryPictureTags, GALLERY)

    def create_album(self, display_name, description, user, protected=False):
        album = GalleryAlbum()
        album.display_name = display_name
        album.description = description
        album.user = user
        album.protected = protected
        DBSession.add(album)
        DBSession.flush()
        return album.id

    def show_album(self, album_id):
        try:
            page = DBSession.query(GalleryAlbum).filter_by(id=album_id).one()
        except NoResultFound:
            raise AlbumNotFound
        return page

    def update_album(self, album_id, display_name, description, tags=''):
        album = self.show_album(album_id)
        album.display_name = display_name
        album.description = description

    def delete_album(self, album_id, request):
        album = self.show_album(album_id)
        for item in album.pictures:
            self.delete_picture(item.id, request)
        DBSession.delete(album)

    def create_picture(self, album_obj, file_obj, mimetype, filename,
                       user, request, display_name="", tags=''):
        file_lib = FileLib(request)
        aio_obj = file_lib.write(filename, file_obj, mimetype, True)
        if not aio_obj.is_picture and not aio_obj.is_video:
            file_lib.delete(aio_obj)
            raise InvalidPicture
        picture = GalleryPicture()
        picture.album_obj = album_obj
        picture.file_obj = aio_obj
        picture.display_name = display_name
        picture.user = user
        self.t.set_tags(picture, tags)
        DBSession.add(picture)
        album_obj.pictures.append(picture)
        DBSession.flush()
        return picture.id

    def show_picture(self, picture_id):
        try:
            page = DBSession.query(GalleryPicture).filter_by(
                id=picture_id).one()
        except NoResultFound:
            raise PictureNotFound
        return page

    def update_picture(self, picture_id, display_name, description, tags=''):
        pic = self.show_picture(picture_id)
        pic.display_name = display_name
        pic.description = description
        self.t.set_tags(pic, tags)

    def delete_picture(self, picture_id, request):
        picture = self.show_picture(picture_id)
        file_lib = FileLib(request)
        file_lib.delete(picture.file_obj)
        DBSession.delete(picture)

    def default_picture(self, picture_id, album_id):
        album = self.show_album(album_id)
        album.default_picture_id = picture_id