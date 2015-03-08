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

class account_asset_asset(osv.osv):

    _inherit = "account.asset.asset"

    _columns = {
        'account_id': fields.related('category_id', 'account_expense_depreciation_id',  type='many2one', relation="account.account", string='Depreciation Expense Account', store=False, readonly=True),
        'analytic_dimension_1_id': fields.many2one('account.analytic.account', 'Dimension 1', domain=[('type','!=','view')]),
        'analytic_dimension_2_id': fields.many2one('account.analytic.account', 'Dimension 2', domain=[('type','!=','view')]),
        'analytic_dimension_3_id': fields.many2one('account.analytic.account', 'Dimension 3', domain=[('type','!=','view')]),
        'analytic_dimension_1_required': fields.boolean("Analytic Dimension 1 Required"),
        'analytic_dimension_2_required': fields.boolean("Analytic Dimension 2 Required"),
        'analytic_dimension_3_required': fields.boolean("Analytic Dimension 3 Required"),
    }    

    def onchange_category_id(self, cr, uid, ids, category_id, context=None):
        """Check for required dimension"""
        result = super(account_asset_asset, self).onchange_category_id(cr, uid, ids, category_id, context=context)
        category = self.pool.get('account.asset.category').browse(cr, uid, category_id)
        result['value']['analytic_dimension_1_required'] = False
        result['value']['analytic_dimension_2_required'] = False
        result['value']['analytic_dimension_3_required'] = False
        for dimension in category.account_expense_depreciation_id.dimension_ids:
            if dimension.analytic_account_required:
                if dimension.dimension_id.name == 'Interne Dimensie':
                    result['value']['analytic_dimension_1_required'] = True
                if dimension.dimension_id.name == 'Netwerk Dimensie':
                    result['value']['analytic_dimension_2_required'] = True
                if dimension.dimension_id.name == 'Projecten, Contracten, Fondsen':
                    result['value']['analytic_dimension_3_required'] = True
#        result['value']['account_id'] = category.account_expense_depreciation_id.id
        return result

account_asset_asset()

class account_asset_depreciation_line(osv.osv):

    _inherit = 'account.asset.depreciation.line'

    def create_move(self, cr, uid, ids, context=None):
        """Assign analytical dimsnsions to account move lines and rename the account move"""
        move_ids = super(account_asset_depreciation_line, self).create_move(cr, uid, ids, context=context)
        for move in self.pool.get('account.move').browse(cr, uid, move_ids):
            # Rename the journal entry
#            self.pool.get('account.move').write(cr, uid, [move.id], {'name':'/'}, context=context)

            # Assign the dimensions
            for line in move.line_id:
                dimensions = {}
                if line.asset_id:
                    dimensions['analytic_dimension_1_id'] = line.asset_id.analytic_dimension_1_id.id
                    dimensions['analytic_dimension_2_id'] = line.asset_id.analytic_dimension_2_id.id
                    dimensions['analytic_dimension_3_id'] = line.asset_id.analytic_dimension_3_id.id
                    self.pool.get('account.move.line').write(cr, uid, [line.id], dimensions, context=context)

#            if move.journal_id.entry_posted:
#                self.pool.get('account.move').button_validate(cr, uid, [move.id], context=context)
        return move_ids

account_asset_depreciation_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
