from canari.maltego.message import *

__author__ = 'foo-manroot'
__copyright__ = 'Copyright 2018, utils Project'
__credits__ = []

__license__ = 'GPLv3'
__version__ = '0.1'
__maintainer__ = 'foo-manroot'
__email__ = 'foo@oi.m8'
__status__ = 'Development'


class WHOISregister(Entity):
    _category_ = 'Personal'
    _namespace_ = 'custom'

    registrant_country = StringEntityField('registrant.country', display_name='Registrant Country')
    tech_city = StringEntityField('tech.city', display_name='Tech City')
    registrant_postal_code = StringEntityField('registrant.postal_code', display_name='Registrant Postal Code')
    creation = DateEntityField('creation', display_name='Creation date')
    registrant_email = StringEntityField('registrant.email', display_name='Registrant email')
    registrant_state = StringEntityField('registrant.state', display_name='Registrant State')
    admin_country = StringEntityField('admin.country', display_name='Admin Country')
    properties_domain = StringEntityField('properties.domain', display_name='Domain', is_value=True)
    registrant_street = StringEntityField('registrant.street', display_name='Registrant Street')
    tech_email = StringEntityField('tech.email', display_name='Tech email')
    tech_phone = StringEntityField('tech.phone', display_name='Tech Phone')
    tech_street = StringEntityField('tech.street', display_name='Tech Street')
    tech_postal_code = StringEntityField('tech.postal_code', display_name='Tech Postal Code')
    tech_state = StringEntityField('tech.state', display_name='Tech State')
    status = StringEntityField('status', display_name='Domain Status')
    tech_name = StringEntityField('tech.name', display_name='Tech Name')
    admin_email = StringEntityField('admin.email', display_name='Admin email')
    admin_name = StringEntityField('admin.name', display_name='Admin Name')
    admin_postal_code = StringEntityField('admin.postal_code', display_name='Admin Postal Code')
    updates = StringEntityField('updates', display_name='Updates Dates')
    tech_country = StringEntityField('tech.country', display_name='Tech Country')
    registrant_name = StringEntityField('registrant.name', display_name='Registrant Name')
    admin_street = StringEntityField('admin.street', display_name='Admin Street')
    registrant_phone = StringEntityField('registrant.phone', display_name='Registrant Phone')
    registrar = StringEntityField('registrar', display_name='Registrar')
    admin_city = StringEntityField('admin.city', display_name='Admin City')
    admin_phone = StringEntityField('admin.phone', display_name='Admin Phone')
    registrant_city = StringEntityField('registrant.city', display_name='Registrant City')
    admin_state = StringEntityField('admin.state', display_name='Admin State')

