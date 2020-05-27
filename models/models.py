# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

import requests

class ResCompany(models.Model):
    _inherit = 'res.company'

    sucursalOrigen = fields.Char(string='Sucursal de Origen', help='Sucursal desde donde sale el pedido. Opcional')
    codigoCliente = fields.Char(string='Código de Cliente', help='Código de Cliente Andreani. Obligatorio.')
    contratoSucursal = fields.Char(string='Contrato para envíos a sucursal', help='Número de Contrato para envíos a sucursal Andreani. Obligatorio.')
    contratoDomicilio = fields.Char(string='Contrato para envíos estándar a domicilio', help='Número de Contrato para envíos a domicilio. Obligatorio.')
    contratoUrgente = fields.Char(string='Contrato para envíos urgentes a domicilio', help='Número de Contrato para envíos a sucursal de forma urgente. Obligatorio.')

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    bulto_andreani = fields.Integer('Bulto para Andreani', default=1, help='Número de Bulto para enviar por Andreani. Productos con el mismo número serán agrupados bajo el mismo bulto.')

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    urlRateShipment = 'https://api.andreani.com/v1/tarifas'

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
            sucursalOrigen = '&sucursalOrigen=' + order.company_id.sucursalOrigen

        if order.order_line:
            for p in order.order_line:
                if p.product_id.weight == False or p.product_id.volume == False:
                    raise ValidationError('Error: El producto ' + p.product_id.name + ' debe tener peso en Kilos o Volumen en métros cúbicos.')

                if bultos:
                    for bulto in bultos:
                        if bulto['num'] == p.bulto_andreani:
                            bulto['valorDeclarado'] += p.price_total
                            bulto['kilos'] += p.product_id.weight * p.product_uom_qty
                            bulto['volumen'] += p.product_id.volume * 1000000 * p.product_uom_qty
                        else:
                            bultos.append({
                                'valorDeclarado': p.price_total,
                                'kilos': p.product_id.weight * p.product_uom_qty,
                                'volumen': p.product_id.volume * 1000000 * p.product_uom_qty,
                                'num': p.bulto_andreani
                            })
                else:
                    bultos.append({
                        'valorDeclarado': p.price_total,
                        'kilos': p.product_id.weight * p.product_uom_qty,
                        'volumen': p.product_id.volume * 1000000 * p.product_uom_qty,
                        'num': p.bulto_andreani
                    })
        else:
            raise ValidationError('No se puede enviar una orden sin pedidos.')

        for n, b in enumerate(bultos, start=0):
            bultosString += '&bultos[' + str(n) + '][valorDeclarado]=' + str(b['valorDeclarado'])
            bultosString += '&bultos[' + str(n) + '][kilos]=' + str(b['kilos'])
            bultosString += '&bultos[' + str(n) + '][volumen]=' + str(b['volumen'])

        print(self.urlRateShipment +
        '?cpDestino=' + cpDestino + 
        '&contrato=' + order.company_id.contratoDomicilio +
        '&cliente=' + order.company_id.codigoCliente
        + sucursalOrigen + bultosString)

        r = requests.get(url = self.urlRateShipment +
        '?cpDestino=' + cpDestino + 
        '&contrato=' + order.company_id.contratoDomicilio +
        '&cliente=' + order.company_id.codigoCliente
        + sucursalOrigen + bultosString)
        
        if r.status_code == 200:
            data = r.json()
            return {
                'success': True,
                'price': float(data['tarifaConIva']['total']),
                'error_message': False,
                'warning_message': False
            }
        elif r.status_code == 401:
            return {
                'success': False,
                'price': 0,
                'error_message': 'Error de autorización, revise sus credenciales.',
                'warning_message': False
            }
        elif r.status_code == 408:
            return {
                'success': False,
                'price': 0,
                'error_message': 'Error. La solicitud está tomando demasiado tiempo en procesarse, intente nuevamente.',
                'warning_message': False
            }
        elif r.status_code == 500:
            return {
                'success': False,
                'price': 0,
                'error_message': 'Error interno. Intente nuevamente.',
                'warning_message': False
            }
        elif r.status_code == 503:
            return {
                'success': False,
                'price': 0,
                'error_message': 'Error interno. El servidor se encuentra saturado, espere unos minutos y vuelva a intentarlo.',
                'warning_message': False
            }
        else:
            data = r.json()
            return {
                'success': False,
                'price': 0,
                'error_message': 'Algo salió mal. Error n° ' + str(r.status_code) + '. ' + str(data['detail']),
                'warning_message': False
            }
