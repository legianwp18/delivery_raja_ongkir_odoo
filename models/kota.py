from odoo import models, fields, api
import requests
import json

class Kota(models.Model):
    _name = 'kota.list'
    _rec_name='city_name'

    province_id = fields.Integer()
    province = fields.Char()

    city_id = fields.Integer()
    province_id = fields.Integer()
    province = fields.Char()
    type = fields.Char()
    city_name = fields.Char()
    postal_code = fields.Char()
    
