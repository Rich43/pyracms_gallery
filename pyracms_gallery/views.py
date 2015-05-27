from pyracms.lib.helperlib import rapid_deform, redirect
from pyramid.view import view_config
from pyramid.exceptions import HTTPNotFound
from .deform_schemas.gallery import CreateAlbum, PictureUpload
from .lib.gallerylib import GalleryLib, AlbumNotFound, InvalidPicture
from os.path import splitext

def split_ext(path):
    return splitext(path)[0]

@view_config(route_name='create_album', permission='create_album',
             renderer='pyracms:templates/deform.jinja2')
def create_album(context, request):
    def create_album_submit(context, request, deserialized, bind_params):
        album_id = GalleryLib().create_album(deserialized['display_name'])
        return redirect(request, "show_album", album_id=str(album_id))
    return rapid_deform(context, request, CreateAlbum, create_album_submit)
    
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
                             source['filename'], request)
        except InvalidPicture:
            pass
        return redirect(request, "show_album", album_id=str(album_id))
    return rapid_deform(context, request, PictureUpload, picture_upload_submit,
                        album_id=album_id, display_name=album.display_name,
                        pictures=album.pictures, split_ext=split_ext)

@view_config(route_name='rename_album', permission='rename_album')
def rename_album(context, request):
    return redirect(request, "home")
    
@view_config(route_name='delete_album', permission='delete_album')
def delete_album(context, request):
    g = GalleryLib()
    album_id = request.matchdict.get('album_id')
    g.delete_album(album_id, request)
    return redirect(request, "home")
    
@view_config(route_name='show_picture', permission='show_picture',
             renderer='gallery/picture.jinja2')
def show_picture(context, request):
    g = GalleryLib()
    picture_id = request.matchdict.get('picture_id')
    return dict(picture=g.show_picture(picture_id), split_ext=split_ext)
    
@view_config(route_name='delete_picture', permission='delete_picture')
def delete_picture(context, request):
    g = GalleryLib()
    album_id = request.matchdict.get('album_id')
    picture_id = request.matchdict.get('picture_id')
    g.delete_picture(picture_id, request)
    return redirect(request, "show_album", album_id=album_id)
