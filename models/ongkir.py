from odoo import models, fields, api, _
import requests
import json
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    provinsi_now = fields.Many2one("res.country.state", string='Provinsi Sekarang', related='partner_id.state_id')
    kota_now = fields.Many2one("vit.kota", string='Kota Sekarang', related='partner_id.kota')
    provinsi = fields.Many2one("provinsi.list", string='Provinsi')
    destinasi = fields.Many2one("kota.list", string='Kota')

    total_berat = fields.Integer(string='Total Berat', readonly=True)
    kurir = fields.Char(string='Kurir', readonly=True)
    layanan = fields.Char(string='Layanan', readonly=True)
    deskripsi = fields.Char(string='Deskripsi', readonly=True)
    harga = fields.Integer(string='Harga', readonly=True)
    estimasi = fields.Char(string='Estimasi', readonly=True)

    @api.onchange('provinsi')
    def _provinsi_onchange(self):
        res = {}
        res['domain'] = {'destinasi': [
            ('province_id', '=', self.provinsi.province_id)]}
        return res

    def getBiaya(self):
        produk = self.env['stock.move'].search([('picking_id', '=', self.id)])
        total_berat = 0
        for barangku in produk:
            berat_sementara = barangku.product_id.weight*3000
            total_berat += berat_sementara
        # print total_berat

        api = self.env['api.list'].search([('active', '=', True)])
        if not api:
            raise UserError(
                'Mohon melakukan pengisian Api atau melakukan pengaktifan Api.  ')
        url = api[0].api_url + "/cost"
        destinasi = self.destinasi.city_id
        berat = total_berat
        headers = {'content-type': 'application/x-www-form-urlencoded',
                   'key': api[0].api_key}
        if destinasi == '' or destinasi == 0:
            raise UserError('Mohon melengkapi data Provinsi dan Kota')
        else:
                
            record_set = self.env['ongkir.list'].search([('id_inv', '=', self.id)])
            record_set.unlink()

            # list_kurir = ['pos', 'tiki', 'jne', 'pcp', 'esl', 'rpx', 'pandu', 'wahana', 'jnt', 'pahala', 'cahaya', 'sap', 'jet', 'indah', 'dse', 'slis', 'first', 'ncs', 'star']
            list_kurir = ['pos', 'tiki', 'jne', 'wahana',
                        'jnt', 'lion', 'ncs', 'sicepat']
            minimum_cost = {
                'total_berat': total_berat,
                'kurir': '',
                'layanan': '',
                'deskripsi': '',
                'harga': 0,
                'estimasi': '',
                'note': '',
            }

            x = 0
            for kurir in list_kurir:
                data = "origin=445&destination={0}&weight={1}&courier={2}&originType=city&destinationType=city".format(
                    destinasi, berat, kurir)
                response = requests.post(url, headers=headers, data=data).json()
                # print kurir
                # print response
                if response['rajaongkir']:
                    if response['rajaongkir']['status']['code'] == 200:
                        results = response['rajaongkir']['results']
                        for hasil in results:
                            # print hasil['code']
                            # print hasil['name']
                            for hasilku in hasil['costs']:
                                # print hasilku['service']
                                # print hasilku['description']
                                for hasilakhir in hasilku['cost']:
                                    # print hasilakhir['value']
                                    # print hasilakhir['etd']
                                    # print hasilakhir['note']
                                    if hasilakhir['value'] != 0:
                                        if '3' in hasilakhir['etd']:
                                            if minimum_cost['harga'] == 0:
                                                minimum_cost['harga'] = hasilakhir['value']

                                            if minimum_cost['harga'] > hasilakhir['value']:
                                                minimum_cost['code'] = hasil['code']
                                                minimum_cost['kurir'] = hasil['name']
                                                minimum_cost['layanan'] = hasilku['service']
                                                minimum_cost['deskripsi'] = hasilku['description']
                                                minimum_cost['harga'] = hasilakhir['value']
                                                minimum_cost['estimasi'] = hasilakhir['etd'].replace(
                                                    " HARI", "")
                                                minimum_cost['note'] = hasilakhir['note']

                                            self.env['ongkir.list'].create({
                                                'id_inv': self.id,
                                                'code': hasil['code'],
                                                'name': hasil['name'],
                                                'service': hasilku['service'],
                                                'description': hasilku['description'],
                                                'value': hasilakhir['value'],
                                                'etd': hasilakhir['etd'].replace(" HARI", ""),
                                                'note': hasilakhir['note']
                                            })
                    else:
                        res_error = response['rajaongkir']['status']['description'].split(
                            ". ")
                        raise UserError(res_error[1])
                x += 1
            self.total_berat = minimum_cost['total_berat']
            self.kurir = minimum_cost['kurir']
            self.layanan = minimum_cost['layanan']
            self.deskripsi = minimum_cost['deskripsi']
            self.harga = minimum_cost['harga']
            self.estimasi = minimum_cost['estimasi']
            self.note = minimum_cost['note']
            if x == len(list_kurir):
                return {
                    'name': 'List Ongkir',
                    'view_mode': 'tree',
                    'view_id': False,
                    'view_type': 'form',
                    'res_model': 'ongkir.list',
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                    'domain': [('id_inv', '=', self.id)],

                }


class ListOngkir(models.Model):
    _name = 'ongkir.list'

    id_inv = fields.Integer(string='Id Inventory')
    total_berat = fields.Integer(string='Total Berat')
    code = fields.Char(string='Kode')
    name = fields.Char(string='Kurir')
    service = fields.Char(string='Layanan')
    description = fields.Char(string='Deskripsi')
    value = fields.Integer(string='Harga')
    etd = fields.Char(string='Estimasi')
    note = fields.Char(string='Note')

    def pilihLayanan(self):
        record = self.env['stock.picking'].search([('id', '=', self.id_inv)])
        record.write({
            'total_berat': self.total_berat,
            'kurir': self.name,
            'layanan': self.service,
            'deskripsi': self.description,
            'harga': self.value,
            'estimasi': self.etd,
        })


class CekOngkir(models.Model):
    _name = 'ongkir.cek'

    provinsi = fields.Many2one("provinsi.list", string='Provinsi', required=True, ondelete='cascade')
    destinasi = fields.Many2one("kota.list", string='Kota', required=True, ondelete='cascade')
    berat = fields.Char(string="Berat (gr)", required=True, default=1000)
    ongkir_cek_list = fields.One2many(comodel_name='ongkir.cek.list', inverse_name='id_list', string='List Line', ondelete="cascade")

    @api.onchange('provinsi')
    def _provinsi_onchange(self):
        self.destinasi = ''
        res = {}
        res['domain'] = {'destinasi': [
            ('province_id', '=', self.provinsi.province_id)]}
        return res

    def getBiaya(self):
        api = self.env['api.list'].search([('active', '=', True)])
        if not api:
            raise UserError(
                'Mohon melakukan pengisian Api atau melakukan pengaktifan Api.  ')
        url = api[0].api_url + "/cost"
        destinasi = self.destinasi.city_id
        berat = self.berat
        headers = {'content-type': 'application/x-www-form-urlencoded',
                   'key': api[0].api_key}

        record_set = self.env['ongkir.cek.list'].search([])
        record_set.unlink()

        # record = self.env['ongkir.cek'].search([])
        # record.unlink()

        list_kurir = ['pos', 'tiki', 'jne', 'wahana',
                      'jnt', 'lion', 'ncs', 'sicepat']
        for kurir in list_kurir:
            data = "origin=445&destination={0}&weight={1}&courier={2}&originType=city&destinationType=city".format(
                destinasi, berat, kurir)
            response = requests.post(url, headers=headers, data=data).json()
            print response

            if response['rajaongkir']:
                if response['rajaongkir']['status']['code'] == 200:
                    results = response['rajaongkir']['results']
                    for hasil in results:
                        for hasilku in hasil['costs']:
                            for hasilakhir in hasilku['cost']:
                                if hasilakhir['value'] != 0:
                                    self.env['ongkir.cek.list'].create({
                                        'id_list': self.id,
                                        'name': hasil['name'],
                                        'service': hasilku['service'],
                                        'description': hasilku['description'],
                                        'value': hasilakhir['value'],
                                        'etd': hasilakhir['etd'].replace(" HARI", ""),
                                        'note': hasilakhir['note']
                                    })
                else:
                    res_error = response['rajaongkir']['status']['description'].split(". ")
                    raise UserError(res_error[1])


class ListCekOngkir(models.Model):
    _name = 'ongkir.cek.list'

    id_list = fields.Many2one(
        comodel_name='ongkir.cek', string='List', ondelete="cascade")
    name = fields.Char(string='Kurir')
    service = fields.Char(string='Layanan')
    description = fields.Char(string='Deskripsi')
    value = fields.Integer(string='Harga')
    etd = fields.Char(string='Estimasi')
    note = fields.Char(string='Note')
