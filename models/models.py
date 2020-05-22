# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

# class ResCompany(models.Model):
#     _inherit = 'res.company'

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[('andreani', 'Andreani')])

    def andreani_rate_shipment(self, order):
        raise ValidationError('Prueba')