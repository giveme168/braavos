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

    material2 = ImageMaterial.get(material.id)
    material2.image_link = "test_link"
    material2.click_link = "test_link"
    material2.monitor_link = "test_link"

    assert material2.image_link == "test_link"
    assert material2.click_link == "test_link"
    assert material2.monitor_link == "test_link"

    material3 = ImageMaterial.get(material2.id)
    assert material3.image_link == "test_link"
    assert material3.click_link == "test_link"
    assert material3.monitor_link == "test_link"
