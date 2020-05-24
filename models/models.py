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
        bultos = []
        bultosString = ''

        if order.partner_shipping_id.zip == False:
            raise ValidationError('¡El Cliente debe tener código postal!')
        else:
            cpDestino = order.partner_shipping_id.zip

        if order.company_id.sucursalOrigen:
            sucursalOrigen = order.company_id.sucursalOrigen

        if order.order_line:
            for p in order.order_line:
                if p.product_id.weight == False:
                    raise ValidationError('Error: El producto ' + p.product_id.name + ' debe tener peso en Kilos.')
                if p.product_id.product_tmpl_id.largo_caja == False or p.product_id.product_tmpl_id.ancho_caja == False or p.product_id.product_tmpl_id.alto_caja == False:
                    raise ValidationError('Error: Las dimensiones de la caja del producto ' + p.product_id.name + ' no están establecidas.')

                bultos.append({
                    'valorDeclarado': p.price_total,
                    'kilos': p.product_id.weight * p.product_uom_qty,
                    'largoCm': p.product_id.product_tmpl_id.largo_caja * p.product_uom_qty,
                    'anchoCm': p.product_id.product_tmpl_id.ancho_caja,
                    'altoCm': p.product_id.product_tmpl_id.alto_caja,
                })
        else:
            raise ValidationError('No se puede enviar una orden sin pedidos.')

        for n, b in enumerate(bultos, start=0):
            bultosString += '&bultos[' + str(n) + '][valorDeclarado]=' + str(b['valorDeclarado'])
            bultosString += '&bultos[' + str(n) + '][kilos]=' + str(b['kilos'])
            bultosString += '&bultos[' + str(n) + '][largoCm]=' + str(b['largoCm'])
            bultosString += '&bultos[' + str(n) + '][anchoCm]=' + str(b['anchoCm'])
            bultosString += '&bultos[' + str(n) + '][altoCm]=' + str(b['altoCm'])

        r = requests.get(url = self.urlRateShipment +
        '?cpDestino=' + cpDestino + 
        '&contrato=400006709' +
        '&cliente=CL0003750' +
        '&sucursalOrigen=' + sucursalOrigen + bultosString)
        
        if r.status_code == 200:
            data = r.json()
            raise ValidationError(data['tarifaConIva']['total'])
        elif r.status_code == 401:
            raise ValidationError('Error de autorización, revise sus credenciales.')
        elif r.status_code == 408:
            raise ValidationError('Error. La solicitud está tomando demasiado tiempo en procesarse, intente nuevamente.')
        elif r.status_code == 500:
            raise ValidationError('Error interno. Intente nuevamente.')
        elif r.status_code == 503:
            raise ValidationError('Error interno. El servidor se encuentra saturado, espere unos minutos y vuelva a intentarlo.')
        else:
            raise ValidationError('Algo salió mal. Contacte con su Administrador. Error número ' + str(r.status_code) + '. ' + str(r.detail))