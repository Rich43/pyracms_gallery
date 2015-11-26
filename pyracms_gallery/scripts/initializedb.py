import os
import sys
from pyracms.lib.menulib import MenuLib
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
        acl.__acl__.append((Allow, "group:admin", "gallery_mod"))
        acl.__acl__.append((Allow, "group:gallery", "group:gallery"))
        acl.__acl__.append((Allow, "group:gallery", "create_album"))
        acl.__acl__.append((Allow, "group:gallery", "update_album"))
        acl.__acl__.append((Allow, "group:gallery", "delete_album"))
        acl.__acl__.append((Allow, "group:gallery", "update_picture"))
        acl.__acl__.append((Allow, "group:gallery", "delete_picture"))
        acl.__acl__.append((Allow, "group:gallery", "default_picture"))

        m = MenuLib()
        group = m.add_group("picture_admin")
        m.add_menu_item_route("Edit", "update_picture", 1, group,
                              'update_picture')
        m.add_menu_item_route("Delete", "delete_picture", 2, group,
                              'delete_picture')
        m.add_menu_item_route("Set as default picture", "default_picture", 3,
                              group, 'default_picture')

        group = m.add_group("album_admin")
        m.add_menu_item_route("Edit", "update_album", 1, group, 'update_album')
        m.add_menu_item_route("Delete", "delete_album", 2, group,
                              'delete_album')

        m.add_menu_item_route("Create Album", "create_album", 30,
                              m.show_group("admin_area"), 'create_album')
        s = SettingsLib()
        s.create("PYRACMS_GALLERY")
        s.update("DEFAULTGROUPS", s.show_setting("DEFAULTGROUPS") +
                 "gallery\n")
