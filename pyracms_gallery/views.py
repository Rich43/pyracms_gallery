from pyracms.lib.helperlib import rapid_deform, redirect, get_username
from pyracms.lib.userlib import UserLib
from pyramid.httpexceptions import HTTPForbidden, HTTPNotFound
from pyramid.security import has_permission
from pyramid.view import view_config
from .deform_schemas.gallery import CreateAlbum, PictureUpload, EditPicture
from .lib.gallerylib import GalleryLib, AlbumNotFound, InvalidPicture
from os.path import splitext

u = UserLib()

def split_ext(path):
    return splitext(path)[0]

def check_owner(context, request):
    album_id = request.matchdict.get('album_id')
    g = GalleryLib()
    page = g.show_album(album_id)
    if (has_permission('gallery_mod', context, request) or
        page.user == u.show(get_username(request))):
        return True
    else:
        raise HTTPForbidden

@view_config(route_name='create_album', permission='create_album',
             renderer='deform.jinja2')
@view_config(route_name='update_album', permission='create_album',
             renderer='deform.jinja2')
def create_album(context, request):
    g = GalleryLib()
    def create_album_submit(context, request, deserialized, bind_params):
        album_id = request.matchdict.get("album_id")
        if album_id:
            g.update_album(album_id, deserialized['display_name'],
                           deserialized['description'])
        else:
            album_id = g.create_album(deserialized['display_name'],
                                      deserialized['description'],
                                      u.show(get_username(request)))
        return redirect(request, "show_album", album_id=str(album_id))
    description = ""
    display_name = ""
    album_id = request.matchdict.get("album_id")
    if album_id:
        g = GalleryLib()
        album = g.show_album(album_id)
        description = album.description
        display_name = album.display_name
    return rapid_deform(context, request, CreateAlbum, create_album_submit,
                        description=description, display_name=display_name)

@view_config(route_name='show_album', permission='show_album',
             renderer='gallery/album.jinja2')
def show_album(context, request):
    g = GalleryLib()
    album_id = request.matchdict.get('album_id')
    try:
        album = g.show_album(album_id)
    except AlbumNotFound:
        raise HTTPNotFound
    def picture_upload_submit(context, request, deserialized, bind_params):
        source = deserialized.get("picture")
        try:
            g.create_picture(album, source['fp'], source['mimetype'],
                             source['filename'],
                             u.show(get_username(request)), request)
        except InvalidPicture:
            pass
        return redirect(request, "show_album", album_id=str(album_id))
    return rapid_deform(context, request, PictureUpload, picture_upload_submit,
                        album_id=album_id, album=album, split_ext=split_ext)


    
@view_config(route_name='delete_album', permission='delete_album')
def delete_album(context, request):
    check_owner(context, request)
    g = GalleryLib()
    album_id = request.matchdict.get('album_id')
    g.delete_album(album_id, request)
    return redirect(request, "home")
    
@view_config(route_name='show_picture', permission='show_picture',
             renderer='gallery/picture.jinja2')
def show_picture(context, request):
    g = GalleryLib()
    album_id = request.matchdict.get('album_id')
    picture_id = request.matchdict.get('picture_id')
    return dict(picture=g.show_picture(picture_id), split_ext=split_ext,
                album_id=album_id, picture_id=picture_id)

@view_config(route_name='update_picture', permission='update_picture',
             renderer='deform.jinja2')
def update_picture(context, request):
    check_owner(context, request)
    g = GalleryLib()
    picture_id = request.matchdict.get("picture_id")
    def update_picture_submit(context, request, deserialized, bind_params):
        album_id = request.matchdict.get("album_id")
        g.update_picture(picture_id, deserialized['display_name'],
                         deserialized['description'], deserialized['tags'])
        return redirect(request, "show_album", album_id=str(album_id))
    album = g.show_picture(picture_id)
    return rapid_deform(context, request, EditPicture, update_picture_submit,
                        description=album.description,
                        display_name=album.display_name)

@view_config(route_name='delete_picture', permission='delete_picture')
def delete_picture(context, request):
    check_owner(context, request)
    g = GalleryLib()
    album_id = request.matchdict.get('album_id')
    picture_id = request.matchdict.get('picture_id')
    g.delete_picture(picture_id, request)
    return redirect(request, "show_album", album_id=album_id)

@view_config(route_name='default_picture', permission='default_picture')
def default_picture(context, request):
    check_owner(context, request)
    g = GalleryLib()
    album_id = request.matchdict.get('album_id')
    picture_id = request.matchdict.get('picture_id')
    g.default_picture(picture_id, album_id)
    return redirect(request, "show_album", album_id=album_id)