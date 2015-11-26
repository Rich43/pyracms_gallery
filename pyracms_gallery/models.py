from datetime import datetime

from pyracms.models import Base, Files
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.sql.expression import desc
from sqlalchemy import Integer, Unicode, DateTime, Boolean, UnicodeText, \
    UniqueConstraint

class GalleryPicture(Base):
    __tablename__ = 'gallerypicture'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)
    display_name = Column(Unicode(128), index=True, default="")
    description = Column(UnicodeText, default='')
    created = Column(DateTime, default=datetime.now)
    private = Column(Boolean, default=False, index=True)
    album_id = Column(Integer, ForeignKey('galleryalbum.id'), 
                      nullable=False)
    album_obj = relationship("GalleryAlbum", foreign_keys=[album_id])
    file_id = Column(Integer, ForeignKey('files.id'), nullable=True)
    file_obj = relationship(Files, cascade="all, delete")
    thread_id = Column(Integer, nullable=False, default=-1)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship("User")
    tags = relationship("GalleryPictureTags", cascade="all, delete, " +
                                                      "delete-orphan")
    votes = relationship("GalleryPictureTags", lazy="dynamic",
                         cascade="all, delete, delete-orphan")

class GalleryAlbum(Base):
    __tablename__ = 'galleryalbum'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)
    display_name = Column(Unicode(128), index=True, nullable=False)
    description = Column(UnicodeText, default='')
    created = Column(DateTime, default=datetime.now)
    private = Column(Boolean, default=False, index=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship("User")
    default_picture_id = Column(Integer, ForeignKey('gallerypicture.id'),
                                nullable=True)
    default_picture = relationship("GalleryPicture",
                                   foreign_keys=[default_picture_id])
    pictures = relationship(GalleryPicture,
                            cascade="all, delete, delete-orphan",
                            lazy="dynamic",
                            order_by=desc(GalleryPicture.created),
                            foreign_keys=[GalleryPicture.album_id])

class GalleryPictureTags(Base):
    __tablename__ = 'gallerypicturetags'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(128), index=True, nullable=False)
    page_id = Column(Integer, ForeignKey('gallerypicture.id'))
    page = relationship(GalleryPicture)

    def __init__(self, name):
        self.name = name

class GalleryPictureVotes(Base):
    __tablename__ = 'gallerypicturevotes'
    __table_args__ = (UniqueConstraint('user_id', 'page_id'),
                      {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'})

    id = Column(Integer, primary_key=True)
    page_id = Column(Integer, ForeignKey('gallerypicture.id'))
    page = relationship(GalleryPicture)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship("User")
    like = Column(Boolean, nullable=False, index=True)

    def __init__(self, user, like):
        self.user = user
        self.like = like