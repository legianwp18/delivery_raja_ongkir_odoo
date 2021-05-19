from odoo import models, fields, api
import requests
import json

class Provinsi(models.Model):
    _name = 'provinsi.list'
    _rec_name = 'province'

    province_id = fields.Integer()
    province = fields.Char()

    
