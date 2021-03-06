from cornice import Service
from colander import MappingSchema, SchemaNode, String, SequenceSchema
from pyramid.httpexceptions import HTTPAccepted

from addonreg.tasks import record_new_hash

addon = Service(name='addon', path='/addon')
addon_hash = Service(name='hash', path='/hash')
addons = Service(name='hashes', path='/addons')


class AddonSchema(MappingSchema):
    id = SchemaNode(String(), location='body', type='str')
    sha256 = SchemaNode(String(), location='body', type='str')


class Addon(MappingSchema):
    id = SchemaNode(String(), type='str')
    sha256 = SchemaNode(String(), type='str')


class Addons(SequenceSchema):
    addons = Addon()


class AddonsSchema(MappingSchema):
    addons = Addons(location='body')


@addons.post(schema=AddonsSchema)
def get_addons(request):
    addons = [(addon['id'], addon['sha256'])
              for addon in request.validated['addons']]

    # returns a list of registered (id, hash)
    registered = request.backend.hashes_exists(addons)
    addons = [{'id': idx, 'sha256': sha256,
               'registered': (idx, sha256) in registered}
              for (idx, sha256) in addons]
    return {'addons': addons}


@addon.post(schema=AddonSchema)
def get_addon(request):
    """Checks if an addon with the given id and hash had been registered.

    The parameters should be passed in the body of the request::

        {'id': 'addonid@example.com',
         'sha256': 'the hash of the addon, to check'}

    The service will return the same keys, in addition with a new one named
    'registered', which will be set to True of False, depending if the addon
    was found registered or not.

    """
    addon_id = request.validated['id']
    sha256 = request.validated['sha256']
    response = {'id': addon_id, 'sha256': sha256}

    registered = request.backend.hash_exists(addon_id, sha256)
    response['registered'] = registered
    return response


@addon_hash.post(schema=AddonSchema)
def add_addon_hash(request):
    """Registers a new hash for a given addon.

    This call is async, meaning that it will be queued to avoid disturbing too
    much the other endpoints which are more critical.

    The parameters should be passed in the body of the request::

        {'id': 'addonid@example.com',
         'sha256': 'the hash of the addon, to check'}

    The server should answer with a 202 Accepted HTTP status code.
    """
    record_new_hash.delay(request.validated['id'], request.validated['sha256'])
    return HTTPAccepted()
