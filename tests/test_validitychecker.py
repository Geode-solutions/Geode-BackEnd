import os
import base64

ID = os.environ.get('ID')
baseRoute = f"/{ID}/validitychecker"

def test_versions(client):
    response = client.get(f"{baseRoute}/versions")
    assert response.status_code == 200
    versions = response.json["versions"]
    assert type(versions) is list
    for version in versions:
        assert type(version) is dict

def test_allowedfiles(client):
    response = client.get(f"{baseRoute}/allowedfiles")
    assert response.status_code == 200
    extensions = response.json["extensions"]
    assert type(extensions) is list
    list_extensions = ["dat", "dev", "dxf", "lso", "ml", "msh", "obj", "og_brep", "og_edc2d", "og_edc3d", "og_grp", "og_hso3d", "og_psf2d", "og_psf3d", "og_pso3d", "og_pts2d", "og_pts3d", "og_rgd2d", "og_rgd3d", "og_sctn", "og_strm", "og_tsf2d", "og_tsf3d", "og_tso3d", "og_vts", "og_xsctn", "ply", "smesh", "stl", "svg", "ts", "txt", "vtp", "vtu", "wl"]

    for extension in list_extensions:
        assert extension in extensions

def test_allowedobjects(client):
    # Normal test with filename "corbi.og_brep"
    response = client.post(f"{baseRoute}/allowedobjects", data={"filename": "corbi.og_brep"})
    assert response.status_code == 200
    objects = response.json["objects"]
    assert type(objects) is list
    assert "BRep" in objects

    # Normal test with filename .vtu
    response = client.post(f"{baseRoute}/allowedobjects", data={"filename": "toto.vtu"})
    assert response.status_code == 200
    objects = response.json["objects"]
    list_objects = ["HybridSolid3D", "PolyhedralSolid3D", "TetrahedralSolid3D"]
    for object in list_objects:
        assert object in objects

    # Test with stupid filename
    response = client.post(f"{baseRoute}/allowedobjects", data={"filename": "toto.tutu"})
    assert response.status_code == 200
    objects = response.json["objects"]
    assert type(objects) is list
    assert not objects

    # Test without filename
    response = client.post(f"{baseRoute}/allowedobjects")
    assert response.status_code == 400
    error_message = response.json["error_message"]
    assert error_message == "No file sent"

def test_uploadfile(client):
    # Test with file
    response = client.post(f'{baseRoute}/uploadfile',
        data = {
            'file': base64.b64encode(open('./tests/corbi.og_brep', 'rb').read()),
            'filename': 'corbi.og_brep',
            'filesize': os.path.getsize('./tests/corbi.og_brep')
        }
    )

    assert response.status_code == 200
    message = response.json["message"]
    assert message == 'File uploaded'

    # Test without file
    response = client.post(f'{baseRoute}/uploadfile',
        data = {
            'filename': 'corbi.og_brep',
        }
    )

    assert response.status_code == 400
    error_message = response.json["error_message"]
    assert error_message == 'No file sent'

    # Test without filename
    response = client.post(f'{baseRoute}/uploadfile',
        data = {
            'file': base64.b64encode(open('./tests/corbi.og_brep', 'rb').read()),
        }
    )

    assert response.status_code == 400
    error_message = response.json["error_message"]
    assert error_message == 'No filename sent'

def test_testnames(client):
    ObjectArray = [
        "BRep"
        , "CrossSection"
        , "EdgedCurve2D"
        , "EdgedCurve3D"
        , "Graph"
        , "HybridSolid3D"
        , "PointSet2D"
        , "PointSet3D"
        , "PolygonalSurface2D"
        , "PolygonalSurface3D"
        , "PolyhedralSolid3D"
        , "RegularGrid2D"
        , "RegularGrid3D"
        , "Section"
        , "StructuralModel"
        , "TetrahedralSolid3D"
        , "TriangulatedSurface2D"
        , "TriangulatedSurface3D"
        , "VertexSet"
    ]

    for object in ObjectArray:
        # Normal test with all objects
        response = client.post(f"{baseRoute}/testsnames", data={"object": object})
        assert response.status_code == 200
        modelChecks = response.json["modelChecks"]
        assert type(modelChecks) is list
        for modelCheck in modelChecks:
            assert type(modelCheck) is dict
            is_leaf = modelCheck['is_leaf']
            route = modelCheck['route']
            children = modelCheck['children']
            assert type(is_leaf) is bool
            assert type(route) is str
            assert type(children) is list
            for check in children:
                assert type(check) is dict
                if check['is_leaf'] == True:
                    response_test = client.post(f"{baseRoute}/inspectfile",
                        data = {
                                'object': 'BRep',
                                'filename': 'corbi.og_brep',
                                'test': check['route']
                        }
                    )

                    assert response_test.status_code == 200
                    