"""
TODO: Beef up security, check permissions
TODO: Write documentation
"""
from cornice import Service
from cornice.validators import colander_body_validator
from pyracms.lib.userlib import UserLib
from pyracms.lib.filelib import FileLib, APIFileNotFound
from pyracms_gallery.lib.gallerylib import (GalleryLib, AlbumNotFound,
                                            PictureNotFound)
from .deform_schemas.gallery import CreateAlbum, EditPicture
from pyracms.web_service_views import (valid_qs_int, valid_token,
                                       valid_permission, valid_file_key,
                                       APP_JSON)

g = GalleryLib()
u = UserLib()
ALBUM = "album"
PICTURE = "picture"

def quick_get_matchdict(request):
    display_name = request.json_body.get('display_name') or ""
    description = request.json_body.get('description') or ""
    tags = request.json_body.get('tags') or ""
    return display_name, description, tags

def check_owner(request, obj_id, album_or_picture):
    if album_or_picture == ALBUM:
        obj = g.show_album(obj_id)
    elif album_or_picture == PICTURE:
        obj = g.show_picture(obj_id)
    else:
        raise Exception("Invalid argument %s" % album_or_picture)
    if (valid_permission(request, 'gallery_mod') or
        obj.user == request.validated['user_db']):
        return True
    else:
        request.errors.add('body', 'access_denied', 'Access denied')
    return False

def valid_album_id(request, **kwargs):
    valid_qs_int(request, "album_id")


def valid_picture_id(request, **kwargs):
    valid_qs_int(request, "picture_id")


album = Service(name='api_gallery_album', path='/api/gallery/album',
                description="Create, read, update, delete albums")


@album.get(validators=valid_album_id)
def api_album_read(request):
    """Gets an album from the database."""
    try:
        album = g.show_album(int(request.params['album_id']))
    except AlbumNotFound:
        request.errors.add('querystring', 'album_not_found',
                           'album not found.')
        return
    # TODO: List Pictures
    return {"status": "ok", "display_name": album.display_name,
            "description": album.description,
            "number_of_pictures": album.pictures.count()}


@album.put(schema=CreateAlbum, content_type=APP_JSON,
           validators=(valid_token, colander_body_validator))
def api_album_create(request):
    """
    Creates an album.
    :param request: Standard pyramid request object.
    :return: JSON dictionary.
    """
    if not valid_permission(request, "create_album"):
        request.errors.add('body', 'access_denied', 'Access denied')
        return
    user = request.validated['user_db']
    display_name, description, tags = quick_get_matchdict(request)
    album_id = g.create_album(display_name, description, user)
    return {"status": "created", "album_id": album_id}


@album.patch(schema=CreateAlbum, content_type=APP_JSON,
             validators=(valid_token, valid_album_id,
                         colander_body_validator))
def api_album_update(request):
    """
    Updates an album.
    :param request: Standard pyramid request object.
    :return: JSON dictionary.
    """
    if not valid_permission(request, "update_album"):
        request.errors.add('body', 'access_denied', 'Access denied')
        return
    display_name, description, tags = quick_get_matchdict(request)
    album_id = request.params.get("album_id")
    if not check_owner(request, album_id, ALBUM):
        return
    g.update_album(album_id, display_name, description)
    return {"status": "updated", "album_id": album_id}


@album.delete(validators=(valid_album_id, valid_token))
def api_album_delete(request):
    """
    Deletes an album.
    :param request: Standard pyramid request object.
    :return: JSON dictionary.
    """
    if not valid_permission(request, "delete_album"):
        request.errors.add('body', 'access_denied', 'Access denied')
        return
    album_id = int(request.params.get("album_id"))
    if not check_owner(request, album_id, ALBUM):
        return
    try:
        g.delete_album(album_id, request)
        return {"status": "deleted"}
    except AlbumNotFound:
        request.errors.add('querystring', 'not_found', 'Album Not Found')


picture = Service(name='api_gallery_picture', path='/api/gallery/picture',
                  description="Create, read, update, delete pictures")


@picture.get(validators=valid_picture_id)
def api_picture_read(request):
    """Gets a picture from the database."""
    try:
        picture = g.show_picture(int(request.params['picture_id']))
    except PictureNotFound:
        request.errors.add('querystring', 'picture_not_found',
                           'picture not found.')
        return
    # TODO: More Detailed Listing
    return {"status": "ok", "display_name": picture.display_name,
            "description": picture.description}


@picture.put(schema=EditPicture, content_type=APP_JSON,
             validators=(valid_token, valid_album_id, colander_body_validator,
                         valid_file_key))
def api_picture_create(request):
    """
    Creates a picture.
    :param request: Standard pyramid request object.
    :return: JSON dictionary.
    """
    if not valid_permission(request, "update_picture"):
        request.errors.add('body', 'access_denied', 'Access denied')
        return
    # TODO: Create a BBThread
    f = FileLib(request)
    f.api_delete_expired()
    try:
        api_file_obj = f.api_show(request.json_body["file_key"])
    except APIFileNotFound:
        request.errors.add('body', 'file_not_found',
                           'file key not found.')
        return
    file_obj = api_file_obj.file_obj
    if not file_obj.is_picture and not file_obj.is_video:
        request.errors.add('body', 'invalid_file',
                           'file is not a valid picture or a video.')
        return
    try:
        album = g.show_album(int(request.params['album_id']))
    except AlbumNotFound:
        request.errors.add('querystring', 'album_not_found',
                           'album not found.')
        return
    user = request.validated['user_db']
    display_name, description, tags = quick_get_matchdict(request)
    picture_id = g.create_picture_api(album, file_obj, user, request,
                                      display_name, description, tags)
    return {"status": "created", "picture_id": picture_id.id}


@picture.patch(schema=EditPicture, content_type=APP_JSON,
               validators=(valid_token, valid_picture_id,
                           colander_body_validator))
def api_picture_update(request):
    """
    Updates a picture.
    :param request: Standard pyramid request object.
    :return: JSON dictionary.
    """
    if not valid_permission(request, "update_picture"):
        request.errors.add('body', 'access_denied', 'Access denied')
        return
    display_name, description, tags = quick_get_matchdict(request)
    picture_id = request.params.get("picture_id")
    if not check_owner(request, picture_id, PICTURE):
        return
    g.update_picture(picture_id, display_name, description)
    return {"status": "updated", "picture_id": picture_id}


@picture.delete(validators=(valid_picture_id, valid_token))
def api_picture_delete(request):
    """
    Deletes a picture.
    :param request: Standard pyramid request object.
    :return: JSON dictionary.
    """
    if not valid_permission(request, "delete_picture"):
        request.errors.add('body', 'access_denied', 'Access denied')
        return
    picture_id = int(request.params.get("picture_id"))
    if not check_owner(request, picture_id, PICTURE):
        return
    try:
        g.delete_picture(picture_id, request)
        return {"status": "deleted"}
    except PictureNotFound:
        request.errors.add('querystring', 'not_found', 'Picture Not Found')
