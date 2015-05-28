def includeme(config):
    """ Activate the forum; usually called via
    ``config.include('pyracms_forum')`` instead of being invoked
    directly. """
    config.include('pyramid_jinja2')
    config.add_jinja2_search_path("pyracms_gallery:templates")
    config.add_route('create_album', '/gallery/create_album')
    config.add_route('update_album', '/gallery/update_album/{album_id:\d+}')
    config.add_route('show_album', '/gallery/album/{album_id:\d+}')
    config.add_route('delete_album', '/gallery/delete_album/{album_id:\d+}')
    config.add_route('show_picture', '/gallery/picture/{album_id:\d+}/' +
                                     '{picture_id:\d+}')
    config.add_route('update_picture', '/gallery/update_picture/{album_id:\d+}'
                                       + '/{picture_id:\d+}')
    config.add_route('delete_picture', 
                     '/gallery/delete_picture/{album_id:\d+}/{picture_id:\d+}')
    config.scan("pyracms_gallery.views")

