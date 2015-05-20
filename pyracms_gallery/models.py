from datetime import datetime
from pyracms.models import Base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.sql.expression import desc
from sqlalchemy.types import Integer, Unicode, UnicodeText, DateTime, Boolean

class GalleryPicture(Base):
    __tablename__ = 'gallerypicture'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)
    display_name = Column(Unicode(128), index=True, nullable=False)
    created = Column(DateTime, default=datetime.now)
    private = Column(Boolean, default=False, index=True)
    album_id = Column(Integer, ForeignKey('galleryalbum.id'), 
                      nullable=False)
    album_obj = relationship("GalleryAlbum")
    file_id = Column(Integer, ForeignKey('files.id'), nullable=False)
    file_obj = relationship(Files, cascade="all, delete")
    thread_id = Column(Integer, nullable=False, default=-1)
    
class GalleryAlbum(Base):
    __tablename__ = 'galleryalbum'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)
    display_name = Column(Unicode(128), index=True, nullable=False)
    created = Column(DateTime, default=datetime.now)
    private = Column(Boolean, default=False, index=True)
    pictures = relationship(GalleryPicture,
                            cascade="all, delete, delete-orphan",
                            lazy="dynamic",
                            order_by=desc(GalleryPicture.created))
