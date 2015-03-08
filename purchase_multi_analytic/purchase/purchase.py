# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013-Today Acespritech Solutions Pvt Ltd
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc
from openerp.osv.orm import browse_record_list, browse_record, browse_null


class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'

    _columns = {
        'analytic_dimension_1_id': fields.many2one('account.analytic.account', 'Dimension 1'),
        'analytic_dimension_2_id': fields.many2one('account.analytic.account', 'Dimension 2'),
        'analytic_dimension_3_id': fields.many2one('account.analytic.account', 'Dimension 3'),
        'analytic_dimension_1_required': fields.boolean("Analytic Dimension 1 Required"),
        'analytic_dimension_2_required': fields.boolean("Analytic Dimension 2 Required"),
        'analytic_dimension_3_required': fields.boolean("Analytic Dimension 3 Required"),
    }
purchase_order_line()

#class purchase_requisition(osv.osv):
#
#    _inherit = "purchase.requisition"
#
#    def make_purchase_order(self, cr, uid, ids, partner_id, context=None):
#        """
#        Create New RFQ for Supplier
#        """
#        if context is None:
#            context = {}
#        assert partner_id, 'Supplier should be specified'
#        purchase_order = self.pool.get('purchase.order')
#        purchase_order_line = self.pool.get('purchase.order.line')
#        res_partner = self.pool.get('res.partner')
#        fiscal_position = self.pool.get('account.fiscal.position')
#        supplier = res_partner.browse(cr, uid, partner_id, context=context)
#        supplier_pricelist = supplier.property_product_pricelist_purchase or False
#        res = {}
#        porders = []
#        for requisition in self.browse(cr, uid, ids, context=context):
##            if supplier.id in filter(lambda x: x, [rfq.state <> 'cancel' and rfq.partner_id.id or None for rfq in requisition.purchase_ids]):
##                 raise osv.except_osv(_('Warning!'), _('You have already one %s purchase order for this partner, you must cancel this purchase order to create a new quotation.') % rfq.state)
#            location_id = requisition.warehouse_id.lot_input_id.id
#            notes = False
##            if not context['skip_note']:
##                notes = requisition.name + ' - ' + requisition.warehouse_id.name + ' - ' + (requisition.description or "")
#            purchase_id = purchase_order.create(cr, uid, {
#                        'origin': requisition.name,
#                        'partner_id': supplier.id,
#                        'pricelist_id': supplier_pricelist.id,
#                        'location_id': location_id,
#                        'company_id': requisition.company_id.id,
#                        'fiscal_position': supplier.property_account_position and supplier.property_account_position.id or False,
#                        'requisition_id':requisition.id,
#                        #'notes':requisition.description,
##                        'notes': notes,
#                        'warehouse_id':requisition.warehouse_id.id ,
#            })
#            res[requisition.id] = purchase_id
#            porders.append(purchase_id)
#            for line in requisition.line_ids:
#                if 'requisition_lines' not in context or ('requisition_lines' in context and context['requisition_lines'] and line.id in context['requisition_lines']):
#                    product = line.product_id
#                    seller_price, qty, default_uom_po_id, date_planned = self._seller_details(cr, uid, line, supplier, context=context)
#                    taxes_ids = product.supplier_taxes_id
#                    taxes = fiscal_position.map_tax(cr, uid, supplier.property_account_position, taxes_ids)
#                    line_id = purchase_order_line.create(cr, uid, {
#                        'order_id': purchase_id,
#                        'name': line.name,
#                        'product_qty': qty,
#                        'product_id': product.id,
#                        'price_unit' : line.product_price_unit,
#                        'product_uom': line.product_uom_id.id,
#                        #'product_uom': default_uom_po_id,
#                        #'price_unit': seller_price,
#                        'date_planned': date_planned,
#                        'taxes_id': [(6, 0, taxes)],
#                        'analytic_dimension_1_id': line.analytic_dimension_1_id and line.analytic_dimension_1_id.id or False,
#                        'analytic_dimension_2_id': line.analytic_dimension_2_id and line.analytic_dimension_2_id.id or False,
#                        'analytic_dimension_3_id': line.analytic_dimension_3_id and line.analytic_dimension_3_id.id or False,
#                        'analytic_dimension_1_required': line.analytic_dimension_1_required,
#                        'analytic_dimension_2_required': line.analytic_dimension_2_required,
#                        'analytic_dimension_3_required': line.analytic_dimension_3_required,
#                        'requisition_id': line.requisition_id.id,
#                        'requisition_line_id': line.id,
#                    }, context=context)
#
#                    if line_id:
#                        self.pool.get('purchase.requisition.line').write(cr, uid, [line.id], {'state':'done'})
#    
#        return res
#
#
#
#class purchase_requisition_line(osv.osv):
#
#    _inherit = 'purchase.requisition.line'
#
#    _columns = {
#        'analytic_dimension_1_id': fields.many2one('account.analytic.account', 'Dimension 1'),
#        'analytic_dimension_2_id': fields.many2one('account.analytic.account', 'Dimension 2'),
#        'analytic_dimension_3_id': fields.many2one('account.analytic.account', 'Dimension 3'),
#        'analytic_dimension_1_required': fields.boolean("Analytic Dimension 1 Required"),
#        'analytic_dimension_2_required': fields.boolean("Analytic Dimension 2 Required"),
#        'analytic_dimension_3_required': fields.boolean("Analytic Dimension 3 Required"),
#    }
#purchase_requisition_line()

