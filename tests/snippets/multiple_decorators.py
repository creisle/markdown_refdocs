from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import view_config


@view_config(route_name='swagger', renderer='lims:templates/swagger.mak', permission=NO_PERMISSION_REQUIRED)
@view_config(route_name='swagger.json', renderer='json', permission=NO_PERMISSION_REQUIRED)
def swagger(request):
    '''I am a docstring'''
    pass
