from odoo import models, fields, api, _
import requests
import json
from odoo.exceptions import UserError
import datetime

class TrackingResi(models.Model):
    _name = 'ongkir.tracking'

    list_kurir = [
                    ('pos', 'Pos Indonesia'), 
                    ('lion', 'Lion Parcel'),
                    ('ninja', 'Ninja Express'),
                    ('ide', 'ID Express'),
                    ('sicepat', 'SiCepat Express'),
                    ('sap', 'SAP Express'),
                    ('ncs', 'Nusantara Card Semesta'),
                    ('rex', 'Royal Express Indonesia'),
                    ('sap', 'SAP Express'),
                    ('sentral', 'Sentral Cargo'),
                    ('wahana', 'Wahana Prestasi Logistik '),
                    ('jnt', 'J&T Express'),
                    ('jet', 'JET Express'),
                    ('dse', '21 Express'),
                    ('first', 'First Logistics'),
                    ('idl', 'IDL Cargo'),
    ]
    list_kurir.sort()

    no_resi = fields.Char(string='No Resi', required=True)
    kurir = fields.Selection(list_kurir, string='Kurir', required=True, default="")


    tracking_resi_detail = fields.One2many(comodel_name='ongkir.history.resi',inverse_name='id_track', string='History', ondelete="cascade")

    courier_code = fields.Char(string='Kode Kurir', readonly=True)
    courier_name = fields.Char(string='Kurir', readonly=True)
    waybill_number = fields.Char(string='No Resi', readonly=True)
    service_code = fields.Char(string='Layanan', readonly=True)
    waybill_date = fields.Char(string='Tanggal', readonly=True)
    shipper_name = fields.Char(string='Pengirim', readonly=True)
    receiver_name = fields.Char(string='Penerima', readonly=True)
    origin = fields.Char(string='Kota Asal', readonly=True)
    destination = fields.Char(string='Kota Tujuan', readonly=True)
    status = fields.Char(string='Status', readonly=True)
    pod_receiver = fields.Char(string='Penerima Paket', readonly=True)
    pod_date = fields.Char(string='Tanggal Diterima', readonly=True)

    def trackResi(self):
        api = self.env['api.list'].search([('active', '=', True)])
        if not api:
            raise UserError('Mohon melakukan pengisian Api atau melakukan pengaktifan Api.  ')
        url = api[0].api_url + "/waybill"
        no_resi = self.no_resi
        kurir = self.kurir
        headers = {'content-type': 'application/x-www-form-urlencoded',
                   'key': api[0].api_key}
    
        record = self.env['ongkir.history.resi'].search([('id_track', '=', self.id)])
        record.unlink()
        
        data = "waybill={0}&courier={1}".format(no_resi,kurir)
        response = requests.post(url, headers=headers, data=data).json()
        if response['rajaongkir']:
            print response
            if response['rajaongkir']['status']['code'] == 200:
                result = response['rajaongkir']['result']

                self.courier_code = result['summary']['courier_code']
                self.courier_name = result['summary']['courier_name']
                self.waybill_number = result['summary']['waybill_number']
                self.service_code = result['summary']['service_code']
                tanggal_waktu_kirim = result['summary']['waybill_date'] + " " + result['details']['waybill_time']
                # tanggal_waktu_kirim = datetime.datetime.strptime(tanggal_waktu_kirim, '%Y-%m-%d %H:%M').strftime("%d %B %Y, %H:%M")
                self.waybill_date = tanggal_waktu_kirim
                self.shipper_name = result['summary']['shipper_name']
                self.receiver_name = result['summary']['receiver_name']
                self.origin = result['summary']['origin']
                self.destination = result['summary']['destination']
                self.status = result['summary']['status']
                tanggal_waktu_datang = result['delivery_status']['pod_date'] + " " + result['delivery_status']['pod_time']
                # tanggal_waktu_datang = datetime.datetime.strptime(tanggal_waktu_datang, '%Y-%m-%d %H:%M').strftime("%d %B %Y, %H:%M")
                self.pod_receiver = result['delivery_status']['pod_receiver']
                self.pod_date = tanggal_waktu_datang
                
                x = 1
                for manifest in result['manifest']:
                    print(manifest)
                    tanggal_waktu = manifest['manifest_date'] + " " + manifest['manifest_time']
                    # tanggal_waktu = datetime.datetime.strptime(tanggal_waktu, '%Y-%m-%d %H:%M').strftime("%d %B %Y, %H:%M")
                    self.env['ongkir.history.resi'].create({
                        'id_track' : self.id,
                        'manifest_code' : x,
                        'manifest_description' : manifest['manifest_description'],
                        'manifest_date': tanggal_waktu,
                        'city_name' : manifest['city_name'],
                    })
                    x+=1
            else:
                res_error = response['rajaongkir']['status']['description'].split(". ")
                raise UserError(res_error[1])
        else:
            res_error = response['rajaongkir']['status']['description'].split(". ")
            raise UserError(res_error[1])
class HistoryResi(models.Model):
    _name = 'ongkir.history.resi'

    id_track = fields.Many2one(comodel_name='ongkir.tracking', string='Tracking', ondelete="cascade")
    manifest_code = fields.Char(string="No")
    manifest_description = fields.Char(string="Deskripsi")
    manifest_date = fields.Char(string="Tanggal")
    city_name = fields.Char(string="Kota")


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    list_kurir = [
        ('pos', 'Pos Indonesia'),
        ('lion', 'Lion Parcel'),
        ('ninja', 'Ninja Express'),
        ('ide', 'ID Express'),
        ('sicepat', 'SiCepat Express'),
        ('sap', 'SAP Express'),
        ('ncs', 'Nusantara Card Semesta'),
        ('rex', 'Royal Express Indonesia'),
        ('sap', 'SAP Express'),
        ('sentral', 'Sentral Cargo'),
        ('wahana', 'Wahana Prestasi Logistik '),
        ('jnt', 'J&T Express'),
        ('jet', 'JET Express'),
        ('dse', '21 Express'),
        ('first', 'First Logistics'),
        ('idl', 'IDL Cargo'),
    ]
    list_kurir.sort()

    no_resi = fields.Char(string='No Resi')
    kurir2 = fields.Selection(list_kurir, string='Kurir', default="")

    tracking_resi_detail = fields.One2many(
        comodel_name='ongkir.history.resi.do', inverse_name='id_track', string='History Resi DO', ondelete="cascade")

    courier_code = fields.Char(string='Kode Kurir', readonly=True)
    courier_name = fields.Char(string='Kurir', readonly=True)
    waybill_number = fields.Char(string='No Resi', readonly=True)
    service_code = fields.Char(string='Layanan', readonly=True)
    waybill_date = fields.Char(string='Tanggal', readonly=True)
    shipper_name = fields.Char(string='Pengirim', readonly=True)
    receiver_name = fields.Char(string='Penerima', readonly=True)
    origin2 = fields.Char(string='Kota Asal', readonly=True)
    destination = fields.Char(string='Kota Tujuan', readonly=True)
    status = fields.Char(string='Status', readonly=True)
    pod_receiver = fields.Char(string='Penerima Paket', readonly=True)
    pod_date = fields.Char(string='Tanggal Diterima', readonly=True)

    def trackResi(self):
        api = self.env['api.list'].search([('active', '=', True)])
        if not api:
            raise UserError(
                'Mohon melakukan pengisian Api atau melakukan pengaktifan Api.  ')
        url = api[0].api_url + "/waybill"
        no_resi = self.no_resi
        kurir = self.kurir2
        headers = {'content-type': 'application/x-www-form-urlencoded',
                   'key': api[0].api_key}
        if no_resi == '' or kurir == '':
            raise UserError('Mohon melengkapi data No Resi dan Kurir')
        else:
            record = self.env['ongkir.history.resi.do'].search(
                [('id_track', '=', self.id)])
            record.unlink()

            data = "waybill={0}&courier={1}".format(no_resi, kurir)
            response = requests.post(url, headers=headers, data=data).json()
            if response['rajaongkir']:
                if response['rajaongkir']['status']['code'] == 200:
                    result = response['rajaongkir']['result']

                    self.courier_code = result['summary']['courier_code']
                    self.courier_name = result['summary']['courier_name']
                    self.waybill_number = result['summary']['waybill_number']
                    self.service_code = result['summary']['service_code']
                    tanggal_waktu_kirim = result['summary']['waybill_date'] + \
                        " " + result['details']['waybill_time']
                    # tanggal_waktu_kirim = datetime.datetime.strptime(tanggal_waktu_kirim, '%Y-%m-%d %H:%M').strftime("%d %B %Y, %H:%M")
                    self.waybill_date = tanggal_waktu_kirim
                    self.shipper_name = result['summary']['shipper_name']
                    self.receiver_name = result['summary']['receiver_name']
                    self.origin2 = result['summary']['origin']
                    self.destination = result['summary']['destination']
                    self.status = result['summary']['status']
                    tanggal_waktu_datang = result['delivery_status']['pod_date'] + \
                        " " + result['delivery_status']['pod_time']
                    # tanggal_waktu_datang = datetime.datetime.strptime(tanggal_waktu_datang, '%Y-%m-%d %H:%M').strftime("%d %B %Y, %H:%M")
                    self.pod_receiver = result['delivery_status']['pod_receiver']
                    self.pod_date = tanggal_waktu_datang

                    x = 1
                    for manifest in result['manifest']:
                        print(manifest)
                        tanggal_waktu = manifest['manifest_date'] + \
                            " " + manifest['manifest_time']
                        # tanggal_waktu = datetime.datetime.strptime(tanggal_waktu, '%Y-%m-%d %H:%M').strftime("%d %B %Y, %H:%M")
                        self.env['ongkir.history.resi.do'].create({
                            'id_track': self.id,
                            'manifest_code': x,
                            'manifest_description': manifest['manifest_description'],
                            'manifest_date': tanggal_waktu,
                            'city_name': manifest['city_name'],
                        })
                        x += 1
                else:
                    res_error = response['rajaongkir']['status']['description'].split(". ")
                    raise UserError(res_error[1])
            else:
                res_error = response['rajaongkir']['status']['description'].split(". ")
                raise UserError(res_error[1])


class HistoryResiDO(models.Model):
    _name = 'ongkir.history.resi.do'

    id_track = fields.Many2one(comodel_name='stock_picking', string='Tracking DO', ondelete="cascade")
    manifest_code = fields.Char(string="No")
    manifest_description = fields.Char(string="Deskripsi")
    manifest_date = fields.Char(string="Tanggal")
    city_name = fields.Char(string="Kota")
