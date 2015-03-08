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
from openerp import api, _
import time
from datetime import datetime


#class account_journal(osv.osv):
#    _inherit = "account.journal"
#    _columns = {
#        'payment_order_exclude': fields.boolean('Not included in payment order'),
#    }

class account_account(osv.osv):
    _inherit = "account.account"
    _columns = {
        'dimension_ids': fields.one2many('account.account.analytic.dimension', 'account_id', 'Analytic Dimension'),
    }


class account_account_analytic_dimension(osv.osv):
    _name = 'account.account.analytic.dimension'
    _columns = {
        'account_id': fields.many2one('account.account', 'Account'),
        'dimension_id': fields.many2one('account.analytic.dimension', 'Analytic Dimension'),
        'analytic_account_required': fields.boolean('Analytic Account Required')
    }


class account_invoice(osv.osv):

    _inherit = 'account.invoice'

#    _columns = {
#        'dimension_user_id': fields.many2one('res.users', 'Resp. for analytic assignment'),
#    } 

    def copy(self, cr, uid, id, default=None, context=None):
        res = super(account_invoice, self).copy(cr, uid, id, default=default, context=context)
        self.button_reset_taxes(cr, uid, [res], context=context)
        return res

#    def default_get(self, cr, uid, fields, context=None):
#        """Set invoice date and period"""
#        if context is None:
#            context = {}
#        result = super(account_invoice, self).default_get(cr, uid, fields, context=context)
#        result['date_invoice'] = datetime.now().strftime('%Y-%m-%d')
#        period = self.pool.get('account.period').find(cr, uid)
#        result['period_id'] = period and period[0]
#        return result

#    def button_reset_taxes(self, cr, uid, ids, context=None):
#        if context is None:
#            context = {} 
#        if not '__copy_data_seen' in context and not 'calc_taxes_done' in context:
#            ctx = context.copy()
#            ait_obj = self.pool.get('account.invoice.tax')
#            for id in ids: 
#                cr.execute("DELETE FROM account_invoice_tax WHERE invoice_id=%s AND manual is False", (id,))
#                partner = self.browse(cr, uid, id, context=ctx).partner_id
#                if partner.lang:
#                    ctx.update({'lang': partner.lang})
#                for tax in ait_obj.compute(cr, uid, id, context=ctx).values():
#                    inv_tax_id = ait_obj.create(cr, uid, tax)
#                    # Clear the dimension records
#                    clear_lines = self.pool.get('wizard.data').search(cr, uid, [('wiz_invoice_line_id','=',tax['invoice_line_id']),('invoice_tax_id','=',inv_tax_id)])
#                    self.pool.get('wizard.data').unlink(cr, uid, clear_lines)
#                    # Create the dimension records if the accounts matches (non-deductible taxes)
#                    line_account = self.pool.get('account.invoice.line').browse(cr, uid, tax['invoice_line_id']).account_id.id
#                    if line_account == tax['account_id']:
#                        inv_lines = self.pool.get('wizard.data').search(cr, uid, [('wiz_invoice_line_id','=',tax['invoice_line_id']),
#                            ('invoice_tax_id','=',False)])
#                        for line in inv_lines:
#                            self.pool.get('wizard.data').copy(cr, uid, line, default={'wiz_invoice_id':tax['invoice_id'], 'wiz_invoice_line_id':False, 'invoice_tax_id':inv_tax_id}, context=context)
#
#            # Update the stored value (fields.function), so we write to trigger recompute
#            #self.write(cr, uid, ids, {'invoice_line':[]}, context=ctx)
#        return True 


    @api.multi
    def check_tax_lines(self, compute_taxes):
        account_invoice_tax = self.env['account.invoice.tax']
        company_currency = self.company_id.currency_id
        if not self.tax_line:
            for tax in compute_taxes.values():
                account_invoice_tax.create(tax)
        else:
            tax_key = []
            precision = self.env['decimal.precision'].precision_get('Account')
            for tax in self.tax_line:
                if tax.manual:
                    continue
                key = (tax.tax_code_id.id, tax.base_code_id.id, tax.account_id.id, tax.invoice_line_id.id)
                tax_key.append(key)
                if key not in compute_taxes:
                    raise except_orm(_('Warning!'), _('Global taxes defined, but they are not in invoice lines !'))
                base = compute_taxes[key]['base']
#                if float_compare(abs(base - tax.base), company_currency.rounding, precision_digits=precision) == 1:
                if abs(base - tax.base) > company_currency.rounding:
                    raise except_orm(_('Warning!'), _('Tax base different!\nClick on compute to update the tax base.'))
            for key in compute_taxes:
                if key not in tax_key:
                    raise except_orm(_('Warning!'), _('Taxes are missing!\nClick on compute button.'))


#    def action_move_create(self, cr, uid, ids, context=None):
#        data_obj = self.pool.get('wizard.data')
#        invoice_obj = self.pool.get('account.invoice')
#        inv_line_obj = self.pool.get('account.invoice.line')
#        move_line_obj = self.pool.get('account.move.line')
#        analytic_obj = self.pool.get('account.analytic.line')
#           
#        if context is None:
#            context = {}
#        context['calc_taxes_done'] = True
#
#        for invoice in self.browse(cr, uid, ids):
#            
#            # Check if all required analytic entries are filled
#            for line in invoice.invoice_line:
#                for dimension in line.account_id.dimension_ids:
#                    if dimension.analytic_account_required:
#                        recs = self.pool.get('wizard.data').search(cr, uid, [('wiz_invoice_line_id','=',line.id)])
#                        if not recs:
#                            raise osv.except_osv(_('Error'),_('A required analytic account is not set for the line %s, the dimension %s'%(line.name,dimension.dimsension_id.sequence)))
#
#            # Check for required dependent dimensions
#            for line in invoice.invoice_line:
#                dim_recs = self.pool.get('wizard.data').search(cr, uid, [('wiz_invoice_line_id','=',line.id),('analytic_account_id','!=',False)])
#                for dim_rec in self.pool.get('wizard.data').browse(cr, uid, dim_recs):
#                    if not dim_rec.analytic_account_id.dimensions_mandatory:
#                        continue
#                    # Get the required dimensions type
#                    required_dims = []
#                    for ana_dim in dim_rec.analytic_account_id.allowed_account_ids:
#                        required_dims.append(ana_dim.dimension_id.id)
#                        required_dims = list(set(required_dims))
#                        for rdim in required_dims:
#                            dim_check = self.pool.get('wizard.data').search(cr, uid, [('wiz_invoice_line_id','=',line.id),
#                                ('distribution_id','=',rdim),('analytic_account_id','!=',False)])
#                            if not dim_check:
#                                raise osv.except_osv(_('Error'),_('A dependent analytic account is not set for the line %s'%(line.name)))
#            
#            # Check if the analytic account is in the asset
#            for line in invoice.invoice_line:
#                if line.asset_id:
#                    if line.analytic_dimension_1_id.id != line.asset_id.analytic_dimension_1_id.id and \
#                        line.analytic_dimension_1_id.id != False:
#                            raise osv.except_osv(_('Error'),_('Analytic accounts for the line %s do not correspond with those as defined for the asset.'%(line.name)))
#                    if line.analytic_dimension_2_id.id != line.asset_id.analytic_dimension_2_id.id and \
#                        line.analytic_dimension_2_id.id != False:
#                            raise osv.except_osv(_('Error'),_('Analytic accounts for the line %s do not correspond with those as defined for the asset.'%(line.name)))
#                    if line.analytic_dimension_3_id.id != line.asset_id.analytic_dimension_3_id.id and \
#                        line.analytic_dimension_3_id.id != False:
#                            raise osv.except_osv(_('Error'),_('Analytic accounts for the line %s do not correspond with those as defined for the asset.'%(line.name)))
#                
#
#        # Taking this out of the for-loop so it gets called only once.
#        res = super(account_invoice, self).action_move_create(cr, uid, ids, context=context)
#
#        # Rewrite the due date in the account move lines based on the due date of the invoice (to avoid odoo bug that recompute the due date even if it is modified on the invoice)
#        for invoice in self.browse(cr, uid, ids):
#            if invoice.move_id:
#                update_ids = []
#                for line in invoice.move_id.line_id:
#                    if line.date_maturity:
#                        update_ids.append(line.id)
#                self.pool.get('account.move.line').write(cr, uid, update_ids, {'date_maturity':invoice.date_due})
#
#        return True
#

    @api.model
    def line_get_convert(self, line, part, date):
        res = super(account_invoice, self).line_get_convert(line, part, date)
        res['invoice_line_id'] = line.get('invoice_line_id', False)
        res['invoice_tax_id'] = line.get('invoice_tax_id', False)
        return res

#    def write(self, cr, uid, ids, vals, context=None):
#        """ Modify the dimension entry"""
#        wiz_data_obj = self.pool.get('wizard.data')
#        res = super(account_invoice, self).write(cr, uid, ids, vals, context=context)
#
#        # Check fro dimension user constraint
#        mod_obj = self.pool.get('ir.model.data')
#        model_data_ids = mod_obj.search(cr, uid,[('model', '=', 'res.groups'), ('name', '=', 'group_multi_analytic_dimenion_user')], context=context)
#        res_id = mod_obj.read(cr, uid, model_data_ids, fields=['res_id'], context=context)[0]['res_id']
#        dim_group = self.pool.get('res.groups').browse(cr, uid, res_id)
#        gp_users = [x.id for x in dim_group.users]
#        for mod_field in vals:
#            if uid in gp_users and mod_field not in ('invoice_line','dimension_user_id'):
#                raise osv.except_osv(_('Error'),_("You can only modify the following: analytic assignment, number plate, employee as well as responsible (tab ‘Other info’)"))
#
#        return res


class account_invoice_line(osv.osv):
    _inherit = 'account.invoice.line'

    _columns = {
#        'sale_order_line_id': fields.many2one('sale.order.line', 'Sales Order Line'),
#        'purchase_order_line_id': fields.many2one('purchase.order.line', 'Purchase Order Line'),
        'analytic_dimension_1_id': fields.many2one('account.analytic.account', 'Dimension 1', domain=[('type','!=','view')]),
        'analytic_dimension_2_id': fields.many2one('account.analytic.account', 'Dimension 2', domain=[('type','!=','view')]),
        'analytic_dimension_3_id': fields.many2one('account.analytic.account', 'Dimension 3', domain=[('type','!=','view')]),
        'analytic_dimension_1_required': fields.boolean("Analytic Dimension 1 Required"),
        'analytic_dimension_2_required': fields.boolean("Analytic Dimension 2 Required"),
        'analytic_dimension_3_required': fields.boolean("Analytic Dimension 3 Required"),
    }

    _order = 'id'
#
#    def default_get(self, cr, uid, fields, context=None):
#        """Check for required dimension"""
#        if context is None:
#            context = {}
#        result = super(account_invoice_line, self).default_get(cr, uid, fields, context=context)
#
#        if 'account_id' in result and result['account_id']:
#            account = self.pool.get('account.account').browse(cr, uid, result['account_id'])
#            for dimension in account.dimension_ids:
#                if dimension.analytic_account_required:
#                    if dimension.dimsension_id.sequence == 'Interne Dimensie':
#                        result['analytic_dimension_1_required'] = True
#                    if dimension.dimsension_id.sequence == 'Netwerk Dimensie':
#                        result['analytic_dimension_2_required'] = True
#                    if dimension.dimsension_id.sequence == 'Projecten, Contracten, Fondsen':
#                        result['analytic_dimension_3_required'] = True
#
#        # Copy the values of the last created line
#        if 'id' in context and context['id']:
#            lines = self.pool.get('account.invoice').read(cr, uid, context['id'], ['invoice_line'])['invoice_line']
#            if lines:
#                line = self.pool.get('account.invoice.line').browse(cr, uid, max(lines))
#                result['account_id'] = line.account_id.id
#                result['analytic_dimension_1_id'] = line.analytic_dimension_1_id.id
#                result['analytic_dimension_2_id'] = line.analytic_dimension_2_id.id
#                result['analytic_dimension_3_id'] = line.analytic_dimension_3_id.id
#                result['name'] = line.name
#                result['product_id'] = line.product_id.id
#                result['price_unit'] = line.price_unit
#                result['discount'] = line.discount
#                result['quantity'] = line.quantity
#                result['fleet_id'] = line.fleet_id.id
#                result['employee_id'] = line.employee_id.id
#                result['uos_id'] = line.uos_id.id
#                taxes = []
#                for tax in line.invoice_line_tax_id:
#                    taxes.append(tax.id)
#                result['invoice_line_tax_id'] = [(6,0,taxes)]
#        return result

    def onchange_account_id(self, cr, uid, ids, product_id, partner_id, inv_type, fposition_id, account_id):
        """Check for required dimension"""
        result =  {'value':{}}
        if account_id:
            account = self.pool.get('account.account').browse(cr, uid, account_id)
            result['value']['analytic_dimension_1_required'] = False
            result['value']['analytic_dimension_2_required'] = False
            result['value']['analytic_dimension_3_required'] = False
#            result['value']['fleet_mandatory'] = False
#            result['value']['employee_mandatory'] = False
#            result['value']['asset_mandatory'] = False

            allowed_dims = []
            for dimension in account.dimension_ids:
                allowed_dims.append(dimension.dimension_id.sequence)
                if dimension.analytic_account_required:
                    if dimension.dimension_id.sequence == 1:
                        result['value']['analytic_dimension_1_required'] = True
                    if dimension.dimension_id.sequence == 2:
                        result['value']['analytic_dimension_2_required'] = True
                    if dimension.dimension_id.sequence == 3:
                        result['value']['analytic_dimension_3_required'] = True

            # Check for allowed dimensions and remove accounts from line if needed
            if 1 not in allowed_dims:
                result['value']['analytic_dimension_1_id'] = False
            if 2 not in allowed_dims:
                result['value']['analytic_dimension_2_id'] = False
            if 3 not in allowed_dims:
                result['value']['analytic_dimension_3_id'] = False

#            if account.fleet_mandatory:
#                result['value']['fleet_mandatory'] = True
#            if account.employee_mandatory:
#                result['value']['employee_mandatory'] = True
#            if account.asset_mandatory:
#                result['value']['asset_mandatory'] = True

        return result


    def create(self, cr, uid, data, context=None):
        if context is None:
            context = {}
        result = super(account_invoice_line, self).create(cr, uid, data, context=context)
        inv_line = self.browse(cr, uid, result)
   
        # Check if the dimension is from the right dimension
        if inv_line.analytic_dimension_1_id and inv_line.analytic_dimension_1_id.dimension_id.sequence != 1:
            raise osv.except_osv(_('Error'),_('The analytic account for dimension 1 is not from the right dimension for the line %s'%(inv_line.name)))
        if inv_line.analytic_dimension_2_id and inv_line.analytic_dimension_2_id.dimension_id.sequence != 2:
            raise osv.except_osv(_('Error'),_('The analytic account for dimension 2 is not from the right dimension for the line %s'%(inv_line.name)))
        if inv_line.analytic_dimension_3_id and inv_line.analytic_dimension_3_id.dimension_id.sequence != 3:
            raise osv.except_osv(_('Error'),_('The analytic account for dimension 3 is not from the right dimension for the line %s'%(inv_line.name)))

        return result


    def write(self, cr, uid, ids, vals, context=None):
        """ Modify the dimension entry"""
        res = super(account_invoice_line, self).write(cr, uid, ids, vals, context=context)

#        # Check fro dimension user constraint
#        mod_obj = self.pool.get('ir.model.data')
#        model_data_ids = mod_obj.search(cr, uid,[('model', '=', 'res.groups'), ('name', '=', 'group_multi_analytic_dimenion_user')], context=context)
#        res_id = mod_obj.read(cr, uid, model_data_ids, fields=['res_id'], context=context)[0]['res_id']
#        dim_group = self.pool.get('res.groups').browse(cr, uid, res_id)
#        gp_users = [x.id for x in dim_group.users]
#        for mod_field in vals:
#            if uid in gp_users and mod_field not in ('analytic_dimension_1_id','analytic_dimension_1_id','analytic_dimension_1_id','fleet_id', 'employee_id'):
#                raise osv.except_osv(_('Error'),_("You can only modify the following: analytic assignment, number plate, employee as well as responsible (tab ‘Other info’)"))


        for line in self.browse(cr, uid, ids):
            if 'analytic_dimension_1_id' in vals and vals['analytic_dimension_1_id']:
                # Check if the analytic account is from the righ dimension
                acc = self.pool.get('account.analytic.account').browse(cr, uid, vals['analytic_dimension_1_id'])
                if acc.dimension_id and acc.dimension_id.sequence != 1:
                    raise osv.except_osv(_('Error'),_('The analytic account for dimension 1 is not from the right dimension'))

            if 'analytic_dimension_2_id' in vals and vals['analytic_dimension_2_id']:
                # Check if the analytic account is from the righ dimension
                acc = self.pool.get('account.analytic.account').browse(cr, uid, vals['analytic_dimension_2_id'])
                if acc.dimension_id and acc.dimension_id.sequence != 2:
                    raise osv.except_osv(_('Error'),_('The analytic account for dimension 2 is not from the right dimension'))

            if 'analytic_dimension_3_id' in vals and vals['analytic_dimension_3_id']:
                # Check if the analytic account is from the righ dimension
                acc = self.pool.get('account.analytic.account').browse(cr, uid, vals['analytic_dimension_3_id'])
                if acc.dimension_id.sequence != 3:
                    raise osv.except_osv(_('Error'),_('The analytic account for dimension 3 is not from the right dimension'))

        return res

    @api.model
    def move_line_get_item(self, line):
        print "IN IT ..."
        return {
            'type': 'src',
            'name': line.name.split('\n')[0][:64],
            'price_unit': line.price_unit,
            'quantity': line.quantity,
            'price': line.price_subtotal,
            'account_id': line.account_id.id,
            'product_id': line.product_id.id,
            'uos_id': line.uos_id.id,
            'account_analytic_id': line.account_analytic_id.id,
            'taxes': line.invoice_line_tax_id,
            'invoice_line_id': line.id,
        }

class account_move(osv.osv):

    _name = 'account.move'
    _inherit = ['account.move','mail.thread']

#    def _check_centralisation(self, cursor, user, ids, context=None):
#        """deactivate the constraint"""
#        return True

    def post(self, cr, uid, ids, context=None):
        print "IN POST"
        analytic_obj = self.pool.get('account.analytic.line')
#        data_obj = self.pool.get('wizard.data')
        for move in self.browse(cr, uid, ids, context=context):
            # Check if all required analytic entries are filled
            for line in move.line_id:
                for dimension in line.account_id.dimension_ids:
                    if dimension.analytic_account_required:
                        if dimension.dimension_id.sequence == 1 and not line.analytic_dimension_1_id:
                            raise osv.except_osv(_('Error'),_('A required analytic account is not set for the line %s, dimension %s'%(line.name,dimension.dimsension_id.sequence)))
                        if dimension.dimension_id.sequence == 2 and not line.analytic_dimension_2_id:
                            raise osv.except_osv(_('Error'),_('A required analytic account is not set for the line %s, dimension %s'%(line.name,dimension.dimsension_id.sequence)))
                        if dimension.dimension_id.sequence == 3 and not line.analytic_dimension_3_id:
                            raise osv.except_osv(_('Error'),_('A required analytic account is not set for the line %s, dimension %s'%(line.name,dimension.dimsension_id.sequence)))

            # Check if the dimension is from the right dimension
            for line in move.line_id:
                if line.analytic_dimension_1_id and line.analytic_dimension_1_id.dimension_id.sequence != 1:
                    raise osv.except_osv(_('Error'),_('The analytic account for dimension 1 is not from the right dimension'))
                if line.analytic_dimension_2_id and line.analytic_dimension_2_id.dimension_id.sequence != 2:
                    raise osv.except_osv(_('Error'),_('The analytic account for dimension 2 is not from the right dimension'))
                if line.analytic_dimension_3_id and line.analytic_dimension_3_id.dimension_id.sequence != 3:
                    raise osv.except_osv(_('Error'),_('The analytic account for dimension 3 is not from the right dimension'))

            # Check if the dimensions are allowed
            for line in move.line_id:
                # Get the dimensions (analytic accounts)
                dim_ids = []
                dim_ids.append(line.analytic_dimension_1_id.id)
                dim_ids.append(line.analytic_dimension_2_id.id)
                dim_ids.append(line.analytic_dimension_3_id.id)
                dim_ids = filter(None, dim_ids)

                if len(dim_ids) == 1:
                    continue

                # Get all allowed analytic accounts
                allowed_accounts = []
                for dim_id in dim_ids:
                    allowed_accounts_search = self.pool.get('account.analytic.account').read(cr, uid, dim_id, ['allowed_account_ids'])
                    if 'allowed_account_ids' in allowed_accounts_search:
                        allowed_accounts += allowed_accounts_search['allowed_account_ids']

                print "DIM IDS:",dim_ids
                for dim_id in dim_ids:
                    print "DIM:",dim_id
                    print "allowed accounts:",allowed_accounts
                    if dim_id not in allowed_accounts:
                        raise osv.except_osv(_('Error'),_('A non-authorized analytic account is set for the line %s'%(line.name)))
                 
#            # Check for required dependent dimensions
#            for line in move.line_id:
#                dim_recs = self.pool.get('wizard.data').search(cr, uid, [('move_line_id','=',line.id),('analytic_account_id','!=',False)])
#                for dim_rec in self.pool.get('wizard.data').browse(cr, uid, dim_recs):
#                    if not dim_rec.analytic_account_id.dimensions_mandatory:
#                        continue
#                    # Get the required dimensions type
#                    required_dims = []
#                    for ana_dim in dim_rec.analytic_account_id.allowed_account_ids:
#                        required_dims.append(ana_dim.dimension_id.id)
#                        required_dims = list(set(required_dims))
#                        for rdim in required_dims:
#                            dim_check = self.pool.get('wizard.data').search(cr, uid, [('move_line_id','=',line.id),
#                                ('distribution_id','=',rdim),('analytic_account_id','!=',False)])
#                            if not dim_check:
#                                if line.statement_line_id:
#                                    raise osv.except_osv(_('Error'),_('A dependent analytic account is not set for the line %s\nStmt Ref: %s'%(line.name,line.statement_line_id.ref)))
#                                raise osv.except_osv(_('Error'),_('A dependent analytic account is not set for the line %s'%(line.name)))
#
            result = super(account_move, self).post(cr, uid, [move.id], context=context)

            for line in move.line_id:

                if line.debit:
                    amount = -line.debit
                elif line.credit:
                    amount = line.credit
                else:
                    continue

                if not line.journal_id.analytic_journal_id:
                    raise osv.except_osv(_('Error'),_('Please assign an analytic journal to this financial journal : %s'%(move.journal_id.name)))

                if line.analytic_dimension_1_id:
                    vals = {
                        'name': line.name,
                        'date': line.date,
                        'account_id': line.analytic_dimension_1_id.id,
                        'journal_id': line.journal_id.analytic_journal_id.id,
                        'amount': amount,
                        'amount_currency': line.amount_currency,
                        'ref': move.name,
                        'product_id': line.product_id and line.product_id.id or False,
                        'unit_amount': line.quantity,
                        'general_account_id': line.account_id.id,
                        'move_id': line.id,
                        'uid_id': uid,
                        'period_id': move.period_id.id
                    }
                    analytic_obj.create(cr, uid, vals, context=context)

                if line.analytic_dimension_2_id:
                    vals = {
                        'name': line.name,
                        'date': line.date,
                        'account_id': line.analytic_dimension_2_id.id,
                        'journal_id': line.journal_id.analytic_journal_id.id,
                        'amount': amount,
                        'amount_currency': line.amount_currency,
                        'ref': move.name,
                        'product_id': line.product_id and line.product_id.id or False,
                        'unit_amount': line.quantity,
                        'general_account_id': line.account_id.id,
                        'move_id': line.id,
                        'uid_id': uid,
                        'period_id': move.period_id.id
                    }
                    analytic_obj.create(cr, uid, vals, context=context)

                if line.analytic_dimension_3_id:
                    vals = {
                        'name': line.name,
                        'date': line.date,
                        'account_id': line.analytic_dimension_3_id.id,
                        'journal_id': line.journal_id.analytic_journal_id.id,
                        'amount': amount,
                        'amount_currency': line.amount_currency,
                        'ref': move.name,
                        'product_id': line.product_id and line.product_id.id or False,
                        'unit_amount': line.quantity,
                        'general_account_id': line.account_id.id,
                        'move_id': line.id,
                        'uid_id': uid,
                        'period_id': move.period_id.id
                    }
                    analytic_obj.create(cr, uid, vals, context=context)

        return True


    def button_cancel(self, cr, uid, ids, context=None):
        """Delete the analytic entries for cancelled account moves"""
        res =  super(account_move, self).button_cancel(cr, uid, ids, context=context)
#        self.write(cr, uid, ids, {'modified':True})
        if res:
            for move in self.browse(cr, uid, ids):
                lines = []
                for line in move.line_id:
                    lines.append(line.id)
                if lines:
                    ana_lines = self.pool.get('account.analytic.line').search(cr, uid, [('move_id','in',lines)])
                    self.pool.get('account.analytic.line').unlink(cr, uid ,ana_lines)
        return res


class account_move_line(osv.osv):

    _inherit = 'account.move.line'

    _columns = {
        'invoice_line_id': fields.many2one('account.invoice.line', 'Invoice Line'),
        'invoice_tax_id': fields.many2one('account.invoice.tax', 'Invoice Tax Line'),
        'statement_line_id': fields.many2one('account.bank.statement.line', 'Bank Statement Line'),
        'analytic_dimension_1_id': fields.many2one('account.analytic.account', 'Dimension 1', domain=[('type','!=','view')]),
        'analytic_dimension_2_id': fields.many2one('account.analytic.account', 'Dimension 2', domain=[('type','!=','view')]),
        'analytic_dimension_3_id': fields.many2one('account.analytic.account', 'Dimension 3', domain=[('type','!=','view')]),
        'analytic_dimension_1_required': fields.boolean("Analytic Dimension 1 Required"),
        'analytic_dimension_2_required': fields.boolean("Analytic Dimension 2 Required"),
        'analytic_dimension_3_required': fields.boolean("Analytic Dimension 3 Required"),
#        'partner_ref': fields.related('partner_id', 'ref', type='char', string='Partner Reference', store=True, readonly=True),
#        'move_ref': fields.related('move_id', 'name', type='char', size=64, string='Move Ref'),
    }
#
#    _order = 'invoice_line_id'
#
#    
#    def default_get(self, cr, uid, fields, context=None):
#        """Check for required dimension"""
#        if context is None:
#            context = {}
#        result = super(account_move_line, self).default_get(cr, uid, fields, context=context)
#        if 'account_id' in result and result['account_id']:
#            account = self.pool.get('account.account').browse(cr, uid, result['account_id'])
#            for dimension in account.dimension_ids:
#                if dimension.analytic_account_required:
#                    if dimension.dimsension_id.sequence == 'Interne Dimensie':
#                        result['analytic_dimension_1_required'] = True
#                    if dimension.dimsension_id.sequence == 'Netwerk Dimensie':
#                        result['analytic_dimension_2_required'] = True
#                    if dimension.dimsension_id.sequence == 'Projecten, Contracten, Fondsen':
#                        result['analytic_dimension_3_required'] = True
#        return result

    def onchange_account_id(self, cr, uid, ids, account_id=False, partner_id=False, context=None):
        """Check for required analytic dimensions"""
        if not account_id:
            return {}
        result =  super(account_move_line, self).onchange_account_id(cr, uid, ids, account_id, partner_id, context=context)

        account = self.pool.get('account.account').browse(cr, uid, account_id)
        result['value']['analytic_dimension_1_required'] = False
        result['value']['analytic_dimension_2_required'] = False
        result['value']['analytic_dimension_3_required'] = False

        allowed_dims = []
        for dimension in account.dimension_ids:
            allowed_dims.append(dimension.dimension_id.sequence)
            if dimension.analytic_account_required:
                if dimension.dimension_id.sequence == 1:
                    result['value']['analytic_dimension_1_required'] = True
                if dimension.dimension_id.sequence == 2:
                    result['value']['analytic_dimension_2_required'] = True
                if dimension.dimension_id.sequence == 3:
                    result['value']['analytic_dimension_3_required'] = True

        # Check for allowed dimensions and remove accounts from line if needed
        if 1 not in allowed_dims:
            result['value']['analytic_dimension_1_id'] = False
        if 2 not in allowed_dims:
            result['value']['analytic_dimension_2_id'] = False
        if 3 not in allowed_dims:
            result['value']['analytic_dimension_3_id'] = False

        return result

    def create(self, cr, uid, data, context=None):
        # If coming from an invoice line
        inv_id = False
        #print "AML DATA:",data
        if 'invoice_line_id' in data and data['invoice_line_id']:
            print "FROM INVOICE LINE:",data
            line = self.pool.get('account.invoice.line').browse(cr, uid, data['invoice_line_id'])
            inv_id = line.invoice_id.id
            data['analytic_dimension_1_id'] = line.analytic_dimension_1_id.id
            data['analytic_dimension_2_id'] = line.analytic_dimension_2_id.id
            data['analytic_dimension_3_id'] = line.analytic_dimension_3_id.id
            return super(account_move_line, self).create(cr, uid, data, context=context)

        # If coming from an invoice tax line
        inv_id = False
        if 'invoice_tax_id' in data and data['invoice_tax_id']:
            print "FROM INVOICE TAX LINE:",data
            tax_line = self.pool.get('account.invoice.tax').browse(cr, uid, data['invoice_tax_id'])
            inv_id = tax_line.invoice_id.id
            dimensions = []
            print "TAX LINE DIMS:",tax_line.account_id.dimension_ids
            print "TAX LINE ACC:",tax_line.account_id.code
            for dim in tax_line.account_id.dimension_ids:
                dimensions.append(dim.dimension_id.id)
            dim1 = tax_line.invoice_line_id.analytic_dimension_1_id.dimension_id and tax_line.invoice_line_id.analytic_dimension_1_id.dimension_id.id
            dim2 = tax_line.invoice_line_id.analytic_dimension_2_id.dimension_id and tax_line.invoice_line_id.analytic_dimension_2_id.dimension_id.id
            dim3 = tax_line.invoice_line_id.analytic_dimension_3_id.dimension_id and tax_line.invoice_line_id.analytic_dimension_3_id.dimension_id.id
            print "DIM1:",dim1
            print "DIM2:",dim2
            print "DIM3:",dim3

            print "ACC:",tax_line.tax_id.account_collected_id

            # Dont copy the dimension for deductible taxes (Tax lines with an account without dimensions defined)
            if tax_line.invoice_id.type in ['in_invoice','out_invoice'] and not tax_line.tax_id.account_collected_id:
                print "YOP"
                if dim1 in dimensions:
                    data['analytic_dimension_1_id'] = tax_line.invoice_line_id.analytic_dimension_1_id.id
                if dim2 in dimensions:
                    data['analytic_dimension_2_id'] = tax_line.invoice_line_id.analytic_dimension_2_id.id
                if dim3 in dimensions:
                    data['analytic_dimension_3_id'] = tax_line.invoice_line_id.analytic_dimension_3_id.id

            if tax_line.invoice_id.type in ['in_refund','out_refund'] and not tax_line.tax_id.account_paid_id:
                if dim1 in dimensions:
                    data['analytic_dimension_1_id'] = tax_line.invoice_line_id.analytic_dimension_1_id.id
                if dim2 in dimensions:
                    data['analytic_dimension_2_id'] = tax_line.invoice_line_id.analytic_dimension_2_id.id
                if dim3 in dimensions:
                    data['analytic_dimension_3_id'] = tax_line.invoice_line_id.analytic_dimension_3_id.id

            print "DATA:",data

#            if tax_line.account_id == tax_line.invoice_line_id.account_id and tax_line.invoice_line_id.asset_id:
#                data['asset_id'] = tax_line.invoice_line_id.asset_id.id
#            if tax_line.account_id == tax_line.invoice_line_id.account_id and tax_line.invoice_line_id.employee_id:
#                data['employee_id'] = tax_line.invoice_line_id.employee_id.id
#            if tax_line.account_id == tax_line.invoice_line_id.account_id and tax_line.invoice_line_id.fleet_id:
#                data['fleet_id'] = tax_line.invoice_line_id.fleet_id.id

            return super(account_move_line, self).create(cr, uid, data, context=context)

        # If coming from a bank statement
        if 'statement_line_id' in data and data['statement_line_id']:
            line = self.pool.get('account.bank.statement.line').browse(cr, uid, data['statement_line_id'])
            statement_id = line.statement_id.id
            data['analytic_dimension_1_id'] = line.analytic_dimension_1_id.id
            data['analytic_dimension_2_id'] = line.analytic_dimension_2_id.id
            data['analytic_dimension_3_id'] = line.analytic_dimension_3_id.id
            return super(account_move_line, self).create(cr, uid, data, context=context)

        result = super(account_move_line, self).create(cr, uid, data, context=context)

        line = self.browse(cr, uid, result)
   
        # Check if the dimension is from the right dimension
        if line.analytic_dimension_1_id and line.analytic_dimension_1_id.dimension_id.sequence != 1:
            raise osv.except_osv(_('Error'),_('The analytic account for dimension 1 is not from the right dimension for the line %s'%(line.name)))
        if line.analytic_dimension_2_id and line.analytic_dimension_2_id.dimension_id.sequence != 2:
            raise osv.except_osv(_('Error'),_('The analytic account for dimension 2 is not from the right dimension for the line %s'%(line.name)))
        if line.analytic_dimension_3_id and line.analytic_dimension_3_id.dimension_id.sequence != 3:
            raise osv.except_osv(_('Error'),_('The analytic account for dimension 3 is not from the right dimension for the line %s'%(line.name)))

        return result


    def write(self, cr, uid, ids, vals, context=None, check=False, update_check=True):
        """ Modify the dimension entry"""

        if context is None:
            context = {}

        analytic_obj = self.pool.get('account.analytic.line')
        res = super(account_move_line, self).write(cr, uid, ids, vals=vals, context=context, check=check, update_check=update_check)
        for line in self.browse(cr, uid, ids):
            
            if line.move_id.state == 'draft':
                continue

            # Check for required dependent dimensions
            if 'analytic_dimension_1_id' in vals and vals['analytic_dimension_1_id']:
                acc = self.pool.get('account.analytic.account').browse(cr, uid, vals['analytic_dimension_1_id'])
                if acc.dimensions_mandatory: 
                    required_dims = []
                    for allowed_acc in acc.allowed_account_ids:
                        required_dims.append(allowed_acc.dimension_id.id)
                        required_dims = list(set(required_dims))
                    for dimension in self.pool.get('account.analytic.dimension').browse(cr, uid, required_dims):
                        if (dimension.sequence == 2 and not line.analytic_dimension_2_id) or \
                            (dimension.sequence == 3 and not line.analytic_dimension_3_id):
                            raise osv.except_osv(_('Error'),_('A dependent analytic account is not set for the line %s'%(line.name)))

            if 'analytic_dimension_2_id' in vals and vals['analytic_dimension_2_id']:
                print "2"
                acc = self.pool.get('account.analytic.account').browse(cr, uid, vals['analytic_dimension_2_id'])
                if acc.dimensions_mandatory: 
                    required_dims = []
                    for allowed_acc in acc.allowed_account_ids:
                        required_dims.append(allowed_acc.dimension_id.id)
                        required_dims = list(set(required_dims))
                    for dimension in self.pool.get('account.analytic.dimension').browse(cr, uid, required_dims):
                        if (dimension.sequence == 1 and not line.analytic_dimension_1_id) or \
                            (dimension.sequence == 3 and not line.analytic_dimension_3_id):
                            raise osv.except_osv(_('Error'),_('A dependent analytic account is not set for the line %s'%(line.name)))

            if 'analytic_dimension_3_id' in vals and vals['analytic_dimension_3_id']:
                print "3"
                acc = self.pool.get('account.analytic.account').browse(cr, uid, vals['analytic_dimension_3_id'])
                if acc.dimensions_mandatory: 
                    required_dims = []
                    for allowed_acc in acc.allowed_account_ids:
                        required_dims.append(allowed_acc.dimension_id.id)
                        required_dims = list(set(required_dims))
                    for dimension in self.pool.get('account.analytic.dimension').browse(cr, uid, required_dims):
                        if (dimension.sequence == 1 and not line.analytic_dimension_1_id) or \
                            (dimension.sequence == 2 and not line.analytic_dimension_2_id):
                            raise osv.except_osv(_('Error'),_('A dependent analytic account is not set for the line %s'%(line.name)))

            if 'analytic_dimension_1_id' in vals and not vals['analytic_dimension_1_id']:
                print "-1"
                if line.analytic_dimension_2_id and line.analytic_dimension_2_id.dimensions_mandatory:
                    for allowed_acc in line.analytic_dimension_2_id.allowed_account_ids:
                        if allowed_acc.dimension_id.sequence == 1:
                            raise osv.except_osv(_('Error'),_('A dependent analytic account is not set for the line %s'%(line.name)))
                if line.analytic_dimension_3_id and line.analytic_dimension_3_id.dimensions_mandatory:
                    for allowed_acc in line.analytic_dimension_3_id.allowed_account_ids:
                        if allowed_acc.dimension_id.sequence == 1:
                            raise osv.except_osv(_('Error'),_('A dependent analytic account is not set for the line %s'%(line.name)))

            if 'analytic_dimension_2_id' in vals and not vals['analytic_dimension_2_id']:
                print "-2"
                if line.analytic_dimension_1_id and line.analytic_dimension_1_id.dimensions_mandatory:
                    for allowed_acc in line.analytic_dimension_1_id.allowed_account_ids:
                        if allowed_acc.dimension_id.sequence == 2:
                            raise osv.except_osv(_('Error'),_('A dependent analytic account is not set for the line %s'%(line.name)))
                if line.analytic_dimension_3_id and line.analytic_dimension_3_id.dimensions_mandatory:
                    for allowed_acc in line.analytic_dimension_3_id.allowed_account_ids:
                        if allowed_acc.dimension_id.sequence == 2:
                            raise osv.except_osv(_('Error'),_('A dependent analytic account is not set for the line %s'%(line.name)))

            if 'analytic_dimension_3_id' in vals and not vals['analytic_dimension_3_id']:
                print "-3"
                if line.analytic_dimension_1_id and line.analytic_dimension_1_id.dimensions_mandatory:
                    for allowed_acc in line.analytic_dimension_1_id.allowed_account_ids:
                        if allowed_acc.dimension_id.sequence == 3:
                            raise osv.except_osv(_('Error'),_('A dependent analytic account is not set for the line %s'%(line.name)))
                if line.analytic_dimension_2_id and line.analytic_dimension_2_id.dimensions_mandatory:
                    for allowed_acc in line.analytic_dimension_2_id.allowed_account_ids:
                        if allowed_acc.dimension_id.sequence == 3:
                            raise osv.except_osv(_('Error'),_('A dependent analytic account is not set for the line %s'%(line.name)))

            acc_line = False
            if 'analytic_dimension_1_id' in vals and vals['analytic_dimension_1_id']:
                # Check if the analytic account is from the righ dimension
                dimension = self.pool.get('account.analytic.dimension').search(cr, uid, [('sequence','=',1)])
                acc_line = self.pool.get('account.analytic.line').search(cr, uid, [('move_id','=',line.id),('dimension_id','in',dimension)])
                acc = self.pool.get('account.analytic.account').browse(cr, uid, vals['analytic_dimension_1_id'])
                if acc.dimsension_id.sequence != 'Interne Dimensie':
                    raise osv.except_osv(_('Error'),_('The analytic account for dimension 1 is not from the right dimension'))

                if acc_line:
                    # If an analytic entry exists modify it
                    self.pool.get('account.analytic.line').write(cr, uid, acc_line, {'account_id':vals['analytic_dimension_1_id']})
                else:
                    dimension = self.pool.get('account.analytic.dimension').search(cr, uid, [('sequence','=',1)])
                    dims1 = wiz_data_obj.search(cr, uid, [('move_line_id','=',line.id),('distribution_id','in',dimension)])
                    if dims1:
                        # Update the dimension entry
                        wiz_data_obj.write(cr, uid, dims1, {'analytic_account_id':vals['analytic_dimension_1_id']})
                    else:
                        # Create the dimension entry
                        acc = self.pool.get('account.analytic.account').browse(cr, uid, vals['analytic_dimension_1_id'])
                        wiz_data_obj.create(cr, uid, {
                        'wiz_move_id': line.move_id.id,
                        'move_line_id': line.id,
                        'distribution_id': acc.dimension_id.id,
                        'analytic_account_id': acc.id or False,
                        })

                        vals = {
                            'name': line.name,
                            'date': line.date,
                            'account_id': vals['analytic_dimension_1_id'],
                            'journal_id': line.journal_id.analytic_journal_id.id,
                            'amount': line.credit - line.debit,
                            'amount_currency': line.amount_currency,
                            'ref': line.move_id.name,
                            'product_id': line.product_id and line.product_id.id or False,
                            'unit_amount': line.quantity,
                            'general_account_id': line.account_id.id,
                            'move_id': line.id,
                            'user_id': uid,
                            'period_id': line.move_id.period_id.id
                        }
                        analytic_obj.create(cr, uid, vals, context=context)

            if 'analytic_dimension_1_id' in vals and not vals['analytic_dimension_1_id']:
                #If dimesnion removed delete the dimension entry
                dimension = self.pool.get('account.analytic.dimension').search(cr, uid, [('sequence','=',1)])
                acc_line_del = self.pool.get('account.analytic.line').search(cr, uid, [('move_id','=',line.id),('dimension_id','in',dimension)])
                self.pool.get('account.analytic.line').unlink(cr, uid, acc_line_del)

            acc_line = False
            if 'analytic_dimension_2_id' in vals and vals['analytic_dimension_2_id']:
                # Check if the analytic account is from the righ dimension
                dimension = self.pool.get('account.analytic.dimension').search(cr, uid, [('sequence','=',2)])
                acc_line = self.pool.get('account.analytic.line').search(cr, uid, [('move_id','=',line.id),('dimension_id','in',dimension)])
                acc = self.pool.get('account.analytic.account').browse(cr, uid, vals['analytic_dimension_2_id'])
                if acc.dimsension_id.sequence != 'Netwerk Dimensie':
                    raise osv.except_osv(_('Error'),_('The analytic account for dimension 2 is not from the right dimension'))

                if acc_line:
                    # If an analytic entry exists modify it
                    self.pool.get('account.analytic.line').write(cr, uid, acc_line, {'account_id':vals['analytic_dimension_2_id']})
                else:
                    dimension = self.pool.get('account.analytic.dimension').search(cr, uid, [('sequence','=',2)])
                    dims2 = wiz_data_obj.search(cr, uid, [('move_line_id','=',line.id),('distribution_id','in',dimension)])
                    if dims2:
                        wiz_data_obj.write(cr, uid, dims2, {'analytic_account_id':vals['analytic_dimension_2_id']})
                    else:
                        acc = self.pool.get('account.analytic.account').browse(cr, uid, vals['analytic_dimension_2_id'])
                        wiz_data_obj.create(cr, uid, {
                        'wiz_move_id': line.move_id.id,
                        'move_line_id': line.id,
                        'distribution_id': acc.dimension_id.id,
                        'analytic_account_id': acc.id or False,
                        })

                        vals = {
                            'name': line.name,
                            'date': line.date,
                            'account_id': vals['analytic_dimension_2_id'],
                            'journal_id': line.journal_id.analytic_journal_id.id,
                            'amount': line.credit - line.debit,
                            'amount_currency': line.amount_currency,
                            'ref': line.move_id.name,
                            'product_id': line.product_id and line.product_id.id or False,
                            'unit_amount': line.quantity,
                            'general_account_id': line.account_id.id,
                            'move_id': line.id,
                            'user_id': uid,
                            'period_id': line.move_id.period_id.id
                        }
                        analytic_obj.create(cr, uid, vals, context=context)

            if 'analytic_dimension_2_id' in vals and not vals['analytic_dimension_2_id']:
                #If dimesnion removed delete the dimension entry
                dimension = self.pool.get('account.analytic.dimension').search(cr, uid, [('sequence','=',2)])
                acc_line_del = self.pool.get('account.analytic.line').search(cr, uid, [('move_id','=',line.id),('dimension_id','in',dimension)])
                self.pool.get('account.analytic.line').unlink(cr, uid, acc_line_del)

            acc_line = False
            if 'analytic_dimension_3_id' in vals and vals['analytic_dimension_3_id']:
                # Check if the analytic account is from the righ dimension
                dimension = self.pool.get('account.analytic.dimension').search(cr, uid, [('sequence','=',3)])
                acc_line = self.pool.get('account.analytic.line').search(cr, uid, [('move_id','=',line.id),('dimension_id','in',dimension)])
                acc = self.pool.get('account.analytic.account').browse(cr, uid, vals['analytic_dimension_3_id'])
                if acc.dimsension_id.sequence != 'Projecten, Contracten, Fondsen':
                    raise osv.except_osv(_('Error'),_('The analytic account for dimension 3 is not from the right dimension'))

                if acc_line:
                    # If an analytic entry exists modify it
                    self.pool.get('account.analytic.line').write(cr, uid, acc_line, {'account_id':vals['analytic_dimension_3_id']})
                else:
                    dimension = self.pool.get('account.analytic.dimension').search(cr, uid, [('sequence','=',3)])
                    dims3 = wiz_data_obj.search(cr, uid, [('move_line_id','=',line.id),('distribution_id','in',dimension)])
                    if dims3:
                        wiz_data_obj.write(cr, uid, dims3, {'analytic_account_id':vals['analytic_dimension_3_id']})
                    else:
                        acc = self.pool.get('account.analytic.account').browse(cr, uid, vals['analytic_dimension_3_id'])
                        wiz_data_obj.create(cr, uid, {
                        'wiz_move_id': line.move_id.id,
                        'move_line_id': line.id,
                        'distribution_id': acc.dimension_id.id,
                        'analytic_account_id': acc.id or False,
                        })

                        vals = {
                            'name': line.name,
                            'date': line.date,
                            'account_id': vals['analytic_dimension_3_id'],
                            'journal_id': line.journal_id.analytic_journal_id.id,
                            'amount': line.credit - line.debit,
                            'amount_currency': line.amount_currency,
                            'ref': line.move_id.name,
                            'product_id': line.product_id and line.product_id.id or False,
                            'unit_amount': line.quantity,
                            'general_account_id': line.account_id.id,
                            'move_id': line.id,
                            'user_id': uid,
                            'period_id': line.move_id.period_id.id
                        }
                        analytic_obj.create(cr, uid, vals, context=context)

            if 'analytic_dimension_3_id' in vals and not vals['analytic_dimension_3_id']:
                #If dimension removed delete the dimension entry
                dimension = self.pool.get('account.analytic.dimension').search(cr, uid, [('sequence','=',3)])
                acc_line_del = self.pool.get('account.analytic.line').search(cr, uid, [('move_id','=',line.id),('dimension_id','in',dimension)])
                self.pool.get('account.analytic.line').unlink(cr, uid, acc_line_del)

        return res


class account_invoice_tax(osv.osv):

    _inherit = 'account.invoice.tax'

    _columns = {
        'invoice_line_id': fields.many2one('account.invoice.line', 'Invoice Line'),
        'tax_id': fields.many2one('account.tax', 'Tax'),
    }

    @api.model
    def move_line_get(self, invoice_id):
        res = [] 
        self._cr.execute(
            'SELECT * FROM account_invoice_tax WHERE invoice_id = %s',
            (invoice_id,)
        )
        for row in self._cr.dictfetchall():
            if not (row['amount'] or row['tax_code_id'] or row['tax_amount']):
                continue
            res.append({
                'type': 'tax',
                'name': row['name'],
                'price_unit': row['amount'],
                'quantity': 1,
                'price': row['amount'] or 0.0, 
                'account_id': row['account_id'],
                'tax_code_id': row['tax_code_id'],
                'tax_amount': row['tax_amount'],
                'account_analytic_id': row['account_analytic_id'],
                'invoice_tax_id': row['id']
            })
        return res

    @api.v8
    def compute(self, invoice):
        tax_grouped = {}
#        currency = invoice.currency_id.with_context(date=invoice.date_invoice or fields.Date.context_today(invoice))
        currency = invoice.currency_id.with_context(date=invoice.date_invoice)
        company_currency = invoice.company_id.currency_id
        for line in invoice.invoice_line:
            taxes = line.invoice_line_tax_id.compute_all(
                (line.price_unit * (1 - (line.discount or 0.0) / 100.0)),
                line.quantity, line.product_id, invoice.partner_id)['taxes']
            for tax in taxes:
                val = {
                    'invoice_id': invoice.id,
                    'name': tax['name'],
                    'amount': tax['amount'],
                    'manual': False,
                    'sequence': tax['sequence'],
                    'base': currency.round(tax['price_unit'] * line['quantity']),
                    'invoice_line_id': line.id,
                }
                if invoice.type in ('out_invoice','in_invoice'):
                    val['base_code_id'] = tax['base_code_id']
                    val['tax_code_id'] = tax['tax_code_id']
                    val['base_amount'] = currency.compute(val['base'] * tax['base_sign'], company_currency, round=False)
                    val['tax_amount'] = currency.compute(val['amount'] * tax['tax_sign'], company_currency, round=False)
                    val['account_id'] = tax['account_collected_id'] or line.account_id.id
                    val['account_analytic_id'] = tax['account_analytic_collected_id']
                else:
                    val['base_code_id'] = tax['ref_base_code_id']
                    val['tax_code_id'] = tax['ref_tax_code_id']
                    val['base_amount'] = currency.compute(val['base'] * tax['ref_base_sign'], company_currency, round=False)
                    val['tax_amount'] = currency.compute(val['amount'] * tax['ref_tax_sign'], company_currency, round=False)
                    val['account_id'] = tax['account_paid_id'] or line.account_id.id
                    val['account_analytic_id'] = tax['account_analytic_paid_id']

                # If the taxes generate moves on the same financial account as the invoice line
                # and no default analytic account is defined at the tax level, propagate the
                # analytic account from the invoice line to the tax line. This is necessary
                # in situations were (part of) the taxes cannot be reclaimed,
                # to ensure the tax move is allocated to the proper analytic account.
                if not val.get('account_analytic_id') and line.account_analytic_id and val['account_id'] == line.account_id.id:
                    val['account_analytic_id'] = line.account_analytic_id.id

                key = (val['tax_code_id'], val['base_code_id'], val['account_id'], line.id)
                if not key in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['base'] += val['base']
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base_amount'] += val['base_amount']
                    tax_grouped[key]['tax_amount'] += val['tax_amount']

        for t in tax_grouped.values():
            t['base'] = currency.round(t['base'])
            t['amount'] = currency.round(t['amount'])
            t['base_amount'] = currency.round(t['base_amount'])
            t['tax_amount'] = currency.round(t['tax_amount'])

        return tax_grouped


class account_bank_statement_line(osv.osv):

    _inherit = 'account.bank.statement.line'

    _columns = {
        'analytic_dimension_1_id': fields.many2one('account.analytic.account', 'Dimension 1', domain=[('type','!=','view')]),
        'analytic_dimension_2_id': fields.many2one('account.analytic.account', 'Dimension 2', domain=[('type','!=','view')]),
        'analytic_dimension_3_id': fields.many2one('account.analytic.account', 'Dimension 3', domain=[('type','!=','view')]),
        'analytic_dimension_1_required': fields.boolean("Analytic Dimension 1 Required"),
        'analytic_dimension_2_required': fields.boolean("Analytic Dimension 2 Required"),
        'analytic_dimension_3_required': fields.boolean("Analytic Dimension 3 Required"),
#        'partner_ref': fields.related('partner_id', 'ref', type='char', string='Partner Reference', store=True, readonly=True),
    }

#    def default_get(self, cr, uid, fields, context=None):
#        """Check for required dimension"""
#        if context is None:
#            context = {}
#        result = super(account_bank_statement_line, self).default_get(cr, uid, fields, context=context)
#        if 'account_id' in result and result['account_id']:
#            account = self.pool.get('account.account').browse(cr, uid, result['account_id'])
#            for dimension in account.dimension_ids:
#                if dimension.analytic_account_required:
#                    if dimension.dimsension_id.sequence == 'Interne Dimensie':
#                        result['analytic_dimension_1_required'] = True
#                    if dimension.dimsension_id.sequence == 'Netwerk Dimensie':
#                        result['analytic_dimension_2_required'] = True
#                    if dimension.dimsension_id.sequence == 'Projecten, Contracten, Fondsen':
#                        result['analytic_dimension_3_required'] = True
#        return result

    def onchange_account_id(self, cr, uid, ids, account_id, context=None):
        """Check for required dimension"""
        result = {}
        account = self.pool.get('account.account').browse(cr, uid, account_id)
        result['analytic_dimension_1_required'] = False
        result['analytic_dimension_2_required'] = False
        result['analytic_dimension_3_required'] = False
#        result['employee_mandatory'] = False
#        result['partner_mandatory'] = False

        if account_id:
            allowed_dims = []
            for dimension in account.dimension_ids:
                allowed_dims.append(dimension.dimsension_id.sequence)
                if dimension.analytic_account_required:
                    if dimension.dimension_id.sequence == 1:
                        result['analytic_dimension_1_required'] = True
                    if dimension.dimension_id.sequence == 2:
                        result['analytic_dimension_2_required'] = True
                    if dimension.dimension_id.sequence == 3:
                        result['analytic_dimension_3_required'] = True

            # Check for allowed dimensions and remove accounts from line if needed
            if 1 not in allowed_dims:
                result['analytic_dimension_1_id'] = False
            if 2 not in allowed_dims:
                result['analytic_dimension_2_id'] = False
            if 3 not in allowed_dims:
                result['analytic_dimension_3_id'] = False

#            if account.employee_mandatory:
#                result['employee_mandatory'] = True
#                result['asset_mandatory'] = True
#            if account.partner_mandatory:
#                result['partner_mandatory'] = True

        return {'value':result}

    def create(self, cr, uid, data, context=None):
        """Check on the dimensions"""
        result = super(account_bank_statement_line, self).create(cr, uid, data, context=context)

        dims= []
        dims.append(data.get('analytic_dimension_1_id'))
        dims.append(data.get('analytic_dimension_2_id'))
        dims.append(data.get('analytic_dimension_3_id'))
        dims = filter(None, dims)

        line = self.browse(cr, uid, result) 

        # Check if the dimension is from the right dimension
        if line.analytic_dimension_1_id and line.analytic_dimension_1_id.dimension_id.sequence != 1:
            raise osv.except_osv(_('Error'),_('The analytic account for dimension 1 is not from the right dimension for the line %s'%(line.name)))
        if line.analytic_dimension_2_id and line.analytic_dimension_2_id.dimension_id.sequence != 2:
            raise osv.except_osv(_('Error'),_('The analytic account for dimension 2 is not from the right dimension for the line %s'%(line.name)))
        if line.analytic_dimension_3_id and line.analytic_dimension_3_id.dimension_id.sequence != 3:
            raise osv.except_osv(_('Error'),_('The analytic account for dimension 3 is not from the right dimension for the line %s'%(line.name)))

        return result 


    def write(self, cr, uid, ids, vals, context=None):
        """ Modify the dimension entry"""
        res = super(account_bank_statement_line, self).write(cr, uid, ids, vals=vals, context=context)

        if type(ids) != type([]):
            ids = [ids]

        for line in self.browse(cr, uid, ids):
            if 'analytic_dimension_1_id' in vals and vals['analytic_dimension_1_id']:
                # Check if the analytic account is from the righ dimension
                acc = self.pool.get('account.analytic.account').browse(cr, uid, vals['analytic_dimension_1_id'])
                if acc.dimension_id and acc.dimension_id.sequence != 1:
                    raise osv.except_osv(_('Error'),_('The analytic account for dimension 1 is not from the right dimension'))

            if 'analytic_dimension_2_id' in vals and vals['analytic_dimension_2_id']:
                acc = self.pool.get('account.analytic.account').browse(cr, uid, vals['analytic_dimension_2_id'])
                if acc.dimension_id and acc.dimension_id.sequence != 2:
                    raise osv.except_osv(_('Error'),_('The analytic account for dimension 2 is not from the right dimension'))

            if 'analytic_dimension_3_id' in vals and vals['analytic_dimension_3_id']:
                # Check if the analytic account is from the righ dimension
                acc = self.pool.get('account.analytic.account').browse(cr, uid, vals['analytic_dimension_3_id'])
                if acc.dimension_id and acc.dimension_id.sequence != 3:
                    raise osv.except_osv(_('Error'),_('The analytic account for dimension 3 is not from the right dimension'))

        return res


class account_bank_statement(osv.osv):

    _inherit = 'account.bank.statement'

    _columns = {
            'stmt_controlled': fields.boolean('Controlled'),            
	    'stmt_ctrl_log': fields.text('Control Log'),
    }

    def _prepare_bank_move_line(self, cr, uid, st_line, move_id, amount, company_currency_id,context=None):
        """Add the statement_line_id in the account move line"""        
        res = super(account_bank_statement, self)._prepare_bank_move_line(cr, uid, st_line, move_id, amount, company_currency_id, context=context)
        res['statement_line_id'] = st_line.id
        return res

#    def button_control_bankstmt(self, cr, uid, ids, context=None):
#        """Control the bank statement"""
#        data_obj = self.pool.get('wizard.data')
#        statement_obj = self.pool.get('account.statement')
#        statement_line_obj = self.pool.get('account.statement.line')
#        move_line_obj = self.pool.get('account.move.line')
#        analytic_obj = self.pool.get('account.analytic.line')
#
#        for statement in self.browse(cr, uid, ids):
#           
#	    ctrl = True
# 
#            # Check if all required analytic entries are filled
#            for line in statement.line_ids:
#                for dimension in line.account_id.dimension_ids:
#                    if dimension.analytic_account_required:
#                        recs = self.pool.get('wizard.data').search(cr, uid, [('statement_line_id','=',line.id)])
#                        if not recs:
#                            #raise osv.except_osv(_('Error'),_('A required analytic account is not set for the dimension %s'%(dimension.dimsension_id.sequence)))
#                            self.write(cr, uid, [statement.id], {'stmt_ctrl_log':'\nA required analytic account is not set for the dimension %s'%(dimension.dimsension_id.sequence)})
#			    ctrl = True
#
#            # Check for required dependent dimensions
#            for line in statement.line_ids:
#                dim_recs = self.pool.get('wizard.data').search(cr, uid, [('statement_line_id','=',line.id),('analytic_account_id','!=',False)])
#                for dim_rec in self.pool.get('wizard.data').browse(cr, uid, dim_recs):
#                    if not dim_rec.analytic_account_id.dimensions_mandatory:
#                        continue
#                    # Get the required dimensions type
#                    required_dims = []
#                    for ana_dim in dim_rec.analytic_account_id.allowed_account_ids:
#                        required_dims.append(ana_dim.dimension_id.id)
#                        required_dims = list(set(required_dims))
#                        for rdim in required_dims:
#                            dim_check = self.pool.get('wizard.data').search(cr, uid, [('statement_line_id','=',line.id),
#                                ('distribution_id','=',rdim),('analytic_account_id','!=',False)])
#                            if not dim_check:
#                                #raise osv.except_osv(_('Error'),_('A dependent analytic account is not set for the statement line: %s'%(line.ref)))
#                            	self.write(cr, uid, [statement.id], {'stmt_ctrl_log':'\nA dependent analytic account is not set for the statement line: %s'%(line.ref)})
#			    	ctrl = True
#
#                for accdim in line.account_id.dimension_ids:
#                    if accdim.dimension_id.sequence == 1 and accdim.analytic_account_required and not line.analytic_dimension_1_id:
#                        #raise osv.except_osv(_('Error'),_('The analytic account 1 is required but not set for the statement line: %s'%(line.ref)))
#                        self.write(cr, uid, [statement.id], {'stmt_ctrl_log':'\nThe analytic account 1 is required but not set for the statement line: %s'%(line.ref)})
#			ctrl = True
#                    if accdim.dimension_id.sequence == 2 and accdim.analytic_account_required and not line.analytic_dimension_2_id:
#                        #raise osv.except_osv(_('Error'),_('The analytic account 2 is required but not set for the statement line: %s'%(line.ref)))
#                        self.write(cr, uid, [statement.id], {'stmt_ctrl_log':'\nThe analytic account 2 is required but not set for the statement line: %s'%(line.ref)})
#			ctrl = True
#                    if accdim.dimension_id.sequence == 3 and accdim.analytic_account_required and not line.analytic_dimension_3_id:
#                        #raise osv.except_osv(_('Error'),_('The analytic account 3 is required but not set for the statement line: %s'%(line.ref)))
#                        self.write(cr, uid, [statement.id], {'stmt_ctrl_log':'\nThe analytic account 3 is required but not set for the statement line: %s'%(line.ref)})
#			ctrl = True
#
#                if line.account_id.partner_mandatory and not line.partner_id:
#                    #raise osv.except_osv(_('Error'),_('A required partner is not present on the line %s'%(line.ref)))
#                    self.write(cr, uid, [statement.id], {'stmt_ctrl_log':'\nA required partner is not present on the line %s'%(line.ref)})
#		    ctrl = True
#                if line.account_id.employee_mandatory and not line.employee_id:
#                    #raise osv.except_osv(_('Error'),_('A required employee is not present on the line %s'%(line.ref)))
#                    self.write(cr, uid, [statement.id], {'stmt_ctrl_log':'\nA required partner is not present on the line %s'%(line.ref)})
#	            ctrl = True	
#
#	    if not ctrl:
#                self.write(cr, uid, [statement.id], {'stmt_controlled':True})    
#
#        return True


#    def button_confirm_bank(self, cr, uid, ids, context=None):
#        """Create the anaytic entries for the dimensions"""
#        data_obj = self.pool.get('wizard.data')
#        statement_obj = self.pool.get('account.statement')
#        statement_line_obj = self.pool.get('account.statement.line')
#        move_line_obj = self.pool.get('account.move.line')
#        analytic_obj = self.pool.get('account.analytic.line')
#
#        for statement in self.browse(cr, uid, ids):
#
#            if not statement.stmt_controlled:
#
#                # Check if all required analytic entries are filled
#                for line in statement.line_ids:
#                    for dimension in line.account_id.dimension_ids:
#                        if dimension.analytic_account_required:
#                            recs = self.pool.get('wizard.data').search(cr, uid, [('statement_line_id','=',line.id)])
#                            if not recs:
#                                raise osv.except_osv(_('Error'),_('A required analytic account is not set for the dimension %s'%(dimension.dimsension_id.sequence)))
#
#                # Check for required dependent dimensions
#                for line in statement.line_ids:
#                    dim_recs = self.pool.get('wizard.data').search(cr, uid, [('statement_line_id','=',line.id),('analytic_account_id','!=',False)])
#                    for dim_rec in self.pool.get('wizard.data').browse(cr, uid, dim_recs):
#                        if not dim_rec.analytic_account_id.dimensions_mandatory:
#                            continue
#                        # Get the required dimensions type
#                        required_dims = []
#                        for ana_dim in dim_rec.analytic_account_id.allowed_account_ids:
#                            required_dims.append(ana_dim.dimension_id.id)
#                            required_dims = list(set(required_dims))
#                            for rdim in required_dims:
#                                dim_check = self.pool.get('wizard.data').search(cr, uid, [('statement_line_id','=',line.id),
#                                    ('distribution_id','=',rdim),('analytic_account_id','!=',False)])
#                                if not dim_check:
#                                    raise osv.except_osv(_('Error'),_('A dependent analytic account is not set for the statement line: %s'%(line.ref)))
#
#                    for accdim in line.account_id.dimension_ids:
#                        if accdim.dimension_id.sequence == 1 and accdim.analytic_account_required and not line.analytic_dimension_1_id:
#                            raise osv.except_osv(_('Error'),_('The analytic account 1 is required but not set for the statement line: %s'%(line.ref)))
#                        if accdim.dimension_id.sequence == 2 and accdim.analytic_account_required and not line.analytic_dimension_2_id:
#                            raise osv.except_osv(_('Error'),_('The analytic account 2 is required but not set for the statement line: %s'%(line.ref)))
#                        if accdim.dimension_id.sequence == 3 and accdim.analytic_account_required and not line.analytic_dimension_3_id:
#                            raise osv.except_osv(_('Error'),_('The analytic account 3 is required but not set for the statement line: %s'%(line.ref)))
#
#                    if line.account_id.partner_mandatory and not line.partner_id:
#                        raise osv.except_osv(_('Error'),_('A required partner is not present on the line %s'%(line.ref)))
#                    if line.account_id.employee_mandatory and not line.employee_id:
#                        raise osv.except_osv(_('Error'),_('A required employee is not present on the line %s'%(line.ref)))
#
#    #                if line.account_id.fleet_mandatory and not line.fleet_id:
#    #                    raise osv.except_osv(_('Error'),_('A required plate number is not present on the line %s'%(line.ref)))
#    #                if line.account_id.asset_mandatory and not line.asset_id:
#    #                    raise osv.except_osv(_('Error'),_('A required asset is not present on the line %s'%(line.ref)))
#
#            res = super(account_bank_statement, self).button_confirm_bank(cr, uid, [statement.id], context=context)
#
#            acc_ids = data_obj.search(cr, uid, [('statement_id','=', statement.id),
#                                                 ('statement_line_id','!=',False),
#                                                 ('analytic_account_id','!=', False)], order='distribution_id', context=context)
#
#            for wiz_data in data_obj.browse(cr, uid, acc_ids, context=context):
#
#                    # Only create analytic line for the allowed dimensions
#                    dimensions = []
#                    for dim in wiz_data.statement_line_id.account_id.dimension_ids:
#                        dimensions.append(dim.dimension_id.id)
#        
#                    if wiz_data.distribution_id.id in dimensions: 
#                        statement = wiz_data.statement_id
#                        statement_line = wiz_data.statement_line_id
#
#                        # Find the statement line move
#                        move_ids = self.pool.get('account.move.line').search(cr, uid, [('statement_line_id','=',statement_line.id)])
#                        move_id = False
#                        if move_ids:
#                             move_id = move_ids[0]
#                        data_obj.write(cr, uid, [wiz_data.id], {'move_line_id':move_id})
#
##                        vals = {
##                            'name': statement_line.name,
##                            'date': statement_line.date,
##                            'account_id': wiz_data.analytic_account_id.id,
##                            'journal_id': statement.journal_id.analytic_journal_id.id or None,
##                            'amount': statement_line.amount,
##                            'ref': statement_line.name,
##                            'unit_amount': 1,
##                            'general_account_id': statement_line.account_id.id,
##                            'move_id': move_id,
##                            'user_id': uid,
##                            'period_id': statement.period_id.id
##                        }
##                        analine_res = analytic_obj.create(cr, uid, vals, context=context)
#
#        return True

#    def button_cancel(self, cr, uid, ids, context=None):
#        context.update({'allow_delete':True})
#        return super(account_bank_statement, self).button_cancel(cr, uid, ids, context=context)
#
#    def button_statement_lines(self, cr, uid, ids, context=None):
#      return {
#        'view_type':'form',
#        'view_mode':'tree,form',
#        'res_model':'account.bank.statement.line',
#        'view_id':False,
#        'type':'ir.actions.act_window',
#        'domain':[('statement_id','in',ids)],
#        'context':context,
#      }

#    def button_journal_entries(self, cr, uid, ids, context=None):
#      ctx = (context or {}).copy()
#      ctx['journal_id'] = self.browse(cr, uid, ids[0], context=context).journal_id.id
#      return {
#        'view_type':'form',
#        'view_mode':'tree,form',
#        'res_model':'account.move.line',
#        'view_id':False,
#        'type':'ir.actions.act_window',
#        'domain':[('statement_id','in',ids)],
#        'context':ctx,
#      }   

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
