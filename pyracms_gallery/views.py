from pyramid.view import view_config

@view_config(route_name='create_album', permission='create_album')
def create_album(context, request):
    pass
    
@view_config(route_name='show_album', permission='show_album')
def show_album(context, request):
    pass

@view_config(route_name='rename_album', permission='rename_album')
def rename_album(context, request):
    pass
    
@view_config(route_name='delete_album', permission='delete_album')
def delete_album(context, request):
    pass
    
@view_config(route_name='create_picture', permission='create_picture')
def create_picture(context, request):
    pass
    
@view_config(route_name='show_picture', permission='show_picture')
def show_picture(context, request):
    pass
    
@view_config(route_name='delete_picture', permission='delete_picture')
def delete_picture(context, request):
    pass
