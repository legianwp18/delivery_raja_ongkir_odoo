# -*- coding: utf-8 -*-
from odoo import http

# class Ongkir(http.Controller):
#     @http.route('/ongkir/ongkir/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ongkir/ongkir/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ongkir.listing', {
#             'root': '/ongkir/ongkir',
#             'objects': http.request.env['ongkir.ongkir'].search([]),
#         })

#     @http.route('/ongkir/ongkir/objects/<model("ongkir.ongkir"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ongkir.object', {
#             'object': obj
#         })