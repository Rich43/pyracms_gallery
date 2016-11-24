from colander import Schema, SchemaNode, String, Integer
from deform import FileData
from deform.widget import (FileUploadWidget, TextInputWidget, TextAreaWidget,
                           HiddenWidget)
from pyracms.deform_schemas.userarea_admin import tmpstore


class PictureUpload(Schema):
    picture = SchemaNode(FileData(), widget=FileUploadWidget(tmpstore))


class CreateAlbum(Schema):
    display_name = SchemaNode(String(), widget=TextInputWidget(size=40),
                              location="body", type='str')
    description = SchemaNode(String(),
                             widget=TextAreaWidget(cols=100, rows=20),
                             location="body", type='str')


class EditPicture(Schema):
    display_name = SchemaNode(String(), widget=TextInputWidget(size=40),
                              location="body", type='str')
    description = SchemaNode(String(),
                             widget=TextAreaWidget(cols=100, rows=20),
                             location="body", type='str')
    tags = SchemaNode(String(), widget=TextInputWidget(size=40), missing='',
                      location="body", type='str')
