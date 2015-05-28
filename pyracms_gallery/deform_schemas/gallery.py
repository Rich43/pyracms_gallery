from colander import Schema, SchemaNode, String
from deform import FileData
from deform.widget import FileUploadWidget, TextInputWidget, TextAreaWidget
from pyracms.deform_schemas.userarea_admin import tmpstore

class PictureUpload(Schema):
    picture = SchemaNode(FileData(), widget=FileUploadWidget(tmpstore))

class CreateAlbum(Schema):
    display_name = SchemaNode(String(), widget=TextInputWidget(size=40))
    description = SchemaNode(String(), widget=TextAreaWidget(cols=140, rows=20))

class EditPicture(Schema):
    display_name = SchemaNode(String(), widget=TextInputWidget(size=40))
    description = SchemaNode(String(), widget=TextAreaWidget(cols=140, rows=20))