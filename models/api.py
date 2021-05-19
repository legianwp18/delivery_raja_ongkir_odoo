from odoo import models, fields, api
import requests
import json
from odoo.exceptions import UserError

class Api(models.Model):
    _name = 'api.list'

    api_key = fields.Char(required=True)
    api_url = fields.Char(required=True)
    active = fields.Boolean()

    def syncProvinsi(self):
        if self.active == False:
            raise UserError(
                'Mohon melakukan pengisian Api atau melakukan pengaktifan Api. ')
        url = self.api_url + "/province"
        headers = {'content-type': 'application/json',
                'key': self.api_key}
        data = {}
        response = requests.get(url, headers=headers,
                                data=json.dumps(data)).json()
        
        record_set = self.env['provinsi.list'].search([])
        record_set.unlink()

        if response['rajaongkir']:
            if 'results' in response['rajaongkir']:
                results = response['rajaongkir']['results']
                for hasil in results:
                    self.env['provinsi.list'].create({
                        'province_id': hasil['province_id'],
                        'province': hasil['province'],
                    })
            else:
                raise UserError('Sinkronisasi gagal pastikan api key dan api url sudah benar.')
        else:
            raise UserError('Sinkronisasi gagal pastikan api key dan api url sudah benar.')


    def syncKota(self):
        if self.active == False:
            raise UserError(
                'Mohon melakukan pengisian Api atau melakukan pengaktifan Api. ')
        url = self.api_url + "/city"
        url = "https://pro.rajaongkir.com/api/city"
        headers = {'content-type': 'application/json',
                   'key': self.api_key}
        data = {}
        response = requests.get(url, headers=headers,
                                data=json.dumps(data)).json()
        
        record_set = self.env['kota.list'].search([])
        record_set.unlink()

        if response['rajaongkir']:
            if 'results' in response['rajaongkir']:
                results = response['rajaongkir']['results']
                for hasil in results:
                    self.env['kota.list'].create({
                        'city_id': hasil['city_id'],
                        'province_id': hasil['province_id'],
                        'province': hasil['province'],
                        'type': hasil['type'],
                        'city_name': hasil['city_name'],
                        'postal_code': hasil['postal_code'],
                    })
            else:
                raise UserError('Sinkronisasi gagal pastikan api key dan api url sudah benar.')
        else:
            raise UserError('Sinkronisasi gagal pastikan api key dan api url sudah benar.')
