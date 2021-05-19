# -*- coding: utf-8 -*-
{
    'name': "Raja Ongkir",
    'summary': """
        Cek ongkos kirim.""",
    'description': """
        Module untuk mengecek ongkor kirim pada suatu kabupaten.
    """,
    'author': "Legian Wahyu P",
    'website': "",
    'category': 'Ongkir',
    'version': '0.1',
    'depends': ['base', 'stock', 'asa_delivery_method'],
    'data': [
        'views/api.xml',
        'views/ongkir.xml',
        'views/provinsi.xml',
        'views/kota.xml',
        'views/cek.xml',
        'views/tracking.xml',
        'views/inc_tracking.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    "application": False,
}
