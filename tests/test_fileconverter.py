import os
import base64

ID = os.environ.get('ID')
baseRoute = f"/{ID}/fileconverter"

def test_versions(client):
    response = client.get(f'{baseRoute}/versions')
    assert response.status_code == 200
    versions = response.json['versions']
    assert type(versions) is list
    for version in versions:
        assert type(version) is dict

def test_allowedfiles(client):
    response = client.get(f'{baseRoute}/allowedfiles')
    assert response.status_code == 200
    extensions = response.json['extensions']
    assert type(extensions) is list
    list_extensions = ["dat", "dev", "dxf", "lso", "ml", "msh", "obj", "og_brep", "og_edc2d", "og_edc3d", "og_grp", "og_hso3d", "og_psf2d", "og_psf3d", "og_pso3d", "og_pts2d", "og_pts3d", "og_rgd2d", "og_rgd3d", "og_sctn", "og_strm", "og_tsf2d", "og_tsf3d", "og_tso3d", "og_vts", "og_xsctn", "ply", "smesh", "stl", "svg", "ts", "txt", "vtp", "vtu", "wl"]
    for extension in list_extensions:
        assert extension in extensions

def test_allowedobjects(client):
    # Normal test with filename 'corbi.og_brep'
    response = client.post(f'{baseRoute}/allowedobjects', data={'filename': 'corbi.og_brep'})
    assert response.status_code == 200
    objects = response.json['objects']
    assert type(objects) is list
    assert 'BRep' in objects

    # Normal test with filename .vtu
    response = client.post(f'{baseRoute}/allowedobjects', data={'filename': 'toto.vtu'})
    assert response.status_code == 200
    objects = response.json['objects']
    list_objects = ['HybridSolid3D', 'PolyhedralSolid3D', 'TetrahedralSolid3D']
    for object in list_objects:
        assert object in objects

    # Test with stupid filename
    response = client.post(f'{baseRoute}/allowedobjects', data={'filename': 'toto.tutu'})
    assert response.status_code == 200
    objects = response.json['objects']
    assert type(objects) is list
    assert not objects

    # Test without filename
    response = client.post(f'{baseRoute}/allowedobjects')
    assert response.status_code == 400
    error_message = response.json['error_message']
    assert error_message == 'No file sent'

def test_outputfileextensions(client):
    # Normal test with object
    response = client.post(f'{baseRoute}/outputfileextensions', data={'object': 'BRep'})
    assert response.status_code == 200
    outputfileextensions = response.json['outputfileextensions']
    assert type(outputfileextensions) is list
    list_outputfileextensions = ['msh', 'og_brep']
    for outputfileextension in list_outputfileextensions:
        assert outputfileextension in outputfileextensions

    # Normal test with object
    response = client.post(f'{baseRoute}/outputfileextensions', data={'object': 'TriangulatedSurface3D'})
    assert response.status_code == 200
    outputfileextensions = response.json['outputfileextensions']
    assert type(outputfileextensions) is list
    list_outputfileextensions = ['obj', 'og_tsf3d', 'stl', 'vtp']
    for outputfileextension in list_outputfileextensions:
        assert outputfileextension in outputfileextensions

    # Normal test with object
    response = client.post(f'{baseRoute}/outputfileextensions', data={'object': 'StructuralModel'})
    assert response.status_code == 200
    outputfileextensions = response.json['outputfileextensions']
    assert type(outputfileextensions) is list
    list_outputfileextensions = ['lso', 'ml', 'msh', 'og_brep', 'og_strm']
    for outputfileextension in list_outputfileextensions:
        assert outputfileextension in outputfileextensions

    # Test without object
    response = client.post(f'{baseRoute}/outputfileextensions')
    assert response.status_code == 400
    error_message = response.json['error_message']
    assert error_message == 'No object sent'

def test_convertfile(client):
    # Normal test with object/file/filename/extension
    object = 'BRep'
    filename = 'corbi.og_brep'
    file = base64.b64encode(open('./tests/corbi.og_brep', 'rb').read())
    filesize = int(os.path.getsize('./tests/corbi.og_brep'))
    extension = 'msh'

    response = client.post(f'{baseRoute}/convertfile',
        data = {
            'object': object,
            'file': file,
            'filename': filename,
            'filesize': filesize,
            'extension': extension
        }
    )

    assert response.status_code == 200
    assert type((response.data)) is bytes
    assert len((response.data)) > 0

    # Test without object
    response = client.post(f'{baseRoute}/convertfile',
        data = {
            'file': file,
            'filename': filename,
            'filesize': filesize,
            'extension': extension
        }
    )

    assert response.status_code == 400
    error_message = response.json['error_message']
    assert error_message == 'No object sent'

    # Test without file
    response = client.post(f'{baseRoute}/convertfile',
        data = {
            'object': object,
            'filename': filename,
            'filesize': filesize,
            'extension': extension
        }
    )

    assert response.status_code == 400
    error_message = response.json['error_message']
    assert error_message == 'No file sent'

    # Test without filename
    response = client.post(f'{baseRoute}/convertfile',
        data = {
            'object': object,
            'file': file,
            'filesize': filesize,
            'extension': extension
        }
    )

    assert response.status_code == 400
    error_message = response.json['error_message']
    assert error_message == 'No filename sent'

    # Test without filesize
    response = client.post(f'{baseRoute}/convertfile',
        data = {
            'object': object,
            'file': file,
            'filename': filename,
            'extension': extension
        }
    )

    assert response.status_code == 400
    error_message = response.json['error_message']
    assert error_message == 'No filesize sent'

    # Test without extension
    response = client.post(f'{baseRoute}/convertfile',
        data = {
            'object': object,
            'file': file,
            'filename': filename,
            'filesize': filesize
        }
    )

    assert response.status_code == 400
    error_message = response.json['error_message']
    assert error_message == 'No extension sent'
