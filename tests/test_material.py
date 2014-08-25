from helper import add_material
from models.material import Material


def test_material(session):
    material = add_material(name='test')
    material.props = {'a': 'aaa'}
    material.save()

    material2 = Material.get(material.id)
    assert material2.name == 'test'
    assert material2.props.get('a') == 'aaa'
