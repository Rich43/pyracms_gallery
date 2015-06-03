import os
import sys
from pyracms.lib.settingslib import SettingsLib
from pyracms.lib.userlib import UserLib
from pyramid.security import Allow, Everyone
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyracms.models import DBSession, Base, MenuGroup, Menu, Settings
from pyracms.factory import RootFactory
from ..models import GalleryPicture, GalleryAlbum

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd)) 
    sys.exit(1)

def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        u = UserLib()
        u.create_group("gallery", "Gallery Group")
        acl = RootFactory()
        acl.__acl__.append((Allow, Everyone, 'show_album'))
        acl.__acl__.append((Allow, Everyone, 'show_picture'))
        acl.__acl__.append((Allow, "group:gallery", "group:gallery"))
        acl.__acl__.append((Allow, "group:gallery", "create_album"))
        acl.__acl__.append((Allow, "group:gallery", "update_album"))
        acl.__acl__.append((Allow, "group:gallery", "delete_album"))
        acl.__acl__.append((Allow, "group:gallery", "update_picture"))
        acl.__acl__.append((Allow, "group:gallery", "delete_picture"))

        group = MenuGroup("picture_admin")
        DBSession.add(Menu("Edit", "/gallery/update_picture/%(album_id)s/" +
                           "%(picture_id)s", 1, group, 'update_picture'))
        DBSession.add(Menu("Delete", "/gallery/delete_picture/%(album_id)s/" +
                           "%(picture_id)s", 2, group, 'delete_picture'))

        group = MenuGroup("album_admin")
        DBSession.add(Menu("Edit", "/gallery/update_album/%(album_id)s", 1,
                           group, 'update_album'))
        DBSession.add(Menu("Delete", "/gallery/delete_album/%(album_id)s", 2,
                           group, 'delete_album'))

        s = SettingsLib()
        s.create("PYRACMS_GALLERY")
        s.update("DEFAULTGROUPS", s.show_setting("DEFAULTGROUPS") +
                 "gallery\n")
