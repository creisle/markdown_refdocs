# multiple_decorators

## swagger()

I am a docstring

```python
@view_config(route_name='swagger', renderer='lims:templates/swagger.mak', permission=NO_PERMISSION_REQUIRED)
@view_config(route_name='swagger.json', renderer='json', permission=NO_PERMISSION_REQUIRED)
def swagger(request):
```

**Args**

- request
