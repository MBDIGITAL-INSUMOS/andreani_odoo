# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

import requests

class ResCompany(models.Model):
    _inherit = 'res.company'

    sucursalOrigen = fields.Char(string='Sucursal de Origen', help='Sucursal desde donde se sale el pedido. Opcional')

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    ancho_caja = fields.Float(string='Ancho Caja', help='Ancho de la Caja en Centímetros')
    alto_caja = fields.Float(string='Alto Caja', help='Alto de la Caja en Centímetros')
    largo_caja = fields.Float(string='Largo Caja', help='Largo de la Caja en Centímetros')

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
        '&bultos[0][valorDeclarado]=1200&bultos[0][kilos]=1.3')
        
        if r.status_code == 200:
            data = r.json()
            raise ValidationError(data['pesoAforado'])
        elif r.status_code == 401:
            raise ValidationError('Error de autorización, revise sus credenciales.')
        elif r.status_code == 408:
            raise ValidationError('Error. La solicitud está tomando demasiado tiempo en procesarse, intente nuevamente.')
        elif r.status_code == 500:
            raise ValidationError('Error interno. Intente nuevamente.')
        elif r.status_code == 503:
            raise ValidationError('Error interno. El servidor se encuentra saturado, espere unos minutos y vuelva a intentarlo.')
        else:
            raise ValidationError('Algo salió mal. Contacte con su Administrador. Error número ' + str(r.status_code))