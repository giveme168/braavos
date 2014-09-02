from helper import add_material
from models.material import Material, ImageMaterial, MATERIAL_TYPE_PICTURE


def test_material(session):
    material = add_material(name='test')
    material.props = {'a': 'aaa'}
    material.save()

    material2 = Material.get(material.id)
    assert material2.name == 'test'
    assert material2.props.get('a') == 'aaa'


def test_image_material(session):
    material = add_material(name='test', material_type=MATERIAL_TYPE_PICTURE)
    assert material.name == 'test'

    material2 = ImageMaterial.get(material.id)
    material2.name = 'test2'
    material2.image_file = "test_file2"
    material2.click_link = "test_link2"
    material2.monitor_link = "test_link2"
    material2.save()

    assert material2.name == 'test2'
    assert material2.image_file == "test_file2"
    assert material2.click_link == "test_link2"
    assert material2.monitor_link == "test_link2"

    material3 = ImageMaterial.get(material2.id)
    assert material3.name == 'test2'
    assert material3.image_file == "test_file2"
    assert material3.click_link == "test_link2"
    assert material3.monitor_link == "test_link2"
