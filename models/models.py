# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

import requests

class ResCompany(models.Model):
    _inherit = 'res.company'

    sucursalOrigen = fields.Char(string='Sucursal de Origen', help='Sucursal desde donde se sale el pedido. Opcional')

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    urlRateShipment = 'https://api.qa.andreani.com/v1/tarifas'

    delivery_type = fields.Selection(selection_add=[('andreani', 'Andreani')])

    def andreani_rate_shipment(self, order):
        cpDestino = 0
        sucursalOrigen = ''

        if order.partner_shipping_id.zip == False:
            raise ValidationError('¡El Cliente debe tener código postal!')
        else:
            cpDestino = order.partner_shipping_id.zip

        if order.company_id.sucursalOrigen:
            sucursalOrigen = order.company_id.sucursalOrigen

        r = requests.get(url = self.urlRateShipment +
        '?cpDestino=' + cpDestino + 
        '&contrato=300006611' +
        '&cliente=CL0003750' +
        '&sucursalOrigen=' + sucursalOrigen +
        '&bultos[0][valorDeclarado]=1200&bultos[0][volumen]=200&bultos[0][kilos]=1.3')
        
        if r.status_code == 200:
            data = r.json()
            raise ValidationError(data['pesoAforado'])
        else:
            raise ValidationError('Algo salió mal. Contacte con su Administrador.')