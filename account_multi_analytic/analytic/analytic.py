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
from openerp import _

class account_analytic_account(osv.osv):
    _inherit = 'account.analytic.account'
    _columns = {
        'dimension_id': fields.many2one('account.analytic.dimension', 'Analytical Dimension'),
        'allowed_account_ids': fields.many2many('account.analytic.account', 'account_analytic_account_allowed_rel', 'account_id', 'allowed_account_id', 'Allowed Analytic Accounts'),
        'dimensions_mandatory': fields.boolean('Dependent Dimensions Mandatory'),
        'active': fields.boolean('Active'),
        'default_dimension_1_id': fields.many2one('account.analytic.account', 'Default Analytic Account for Dimension 1'),
        'default_dimension_2_id': fields.many2one('account.analytic.account', 'Default Analytic Account for Dimension 2'),
        'default_dimension_3_id': fields.many2one('account.analytic.account', 'Default Analytic Account for Dimension 3'),
        'dimension_sequence': fields.related('dimension_id', 'sequence', type="integer", string="Dimension Sequence", store=True),
    }

    _order = 'code'

    _defaults = {
        'active': True,
    }

    def name_get(self, cr, uid, ids, context=None):
        """Display the analytic account as [code] name"""
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not len(ids):
            return []

        res = []
        for account in self.browse(cr, uid, ids, context=context):
            if account.code:
                name = '[%s] %s'%(account.code,account.name)
            else:
                name = account.name
            res.append((account.id,name))
        return res


    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        """Filter analytic accounts by dimension"""
        user  = self.pool.get('res.users').browse(cr, uid, uid)
        ids = []
        if not args:
            args = []
        if context is None:
            context = {}
        if context.get('distribution_id'):
            args += [('dimension_id', '=', context['distribution_id'])]

        if context.get('dimension'):
	    allowed_dimensions = []
            if 'account_id' in context:
		    # Check for allowed dimension in financial documents
		    account_dimensions = self.pool.get('account.account').read(cr, uid, context.get('account_id'), ['dimension_ids'])['dimension_ids']
		    for accdim in self.pool.get('account.account.analytic.dimension').browse(cr, uid, account_dimensions):
			allowed_dimensions.append(accdim.dimension_id.id)
	    elif 'analytic_account_id' in context:
		    # Set all dimensions allowed
		    allowed_dimensions = self.pool.get('account.analytic.dimension').search(cr, uid, [], context=context)
		    allowed_accounts = self.read(cr, uid, context['analytic_account_id'], ['allowed_account_ids'])['allowed_account_ids']
                    args += [('id','in',allowed_accounts)]
            else:
                    # Byass the control to allow all existion analytic accounts (for new v8 statements) and for purchasing
		    allowed_dimensions = self.pool.get('account.analytic.dimension').search(cr, uid, [], context=context)
		    allowed_accounts = self.pool.get('account.analytic.account').search(cr, uid, [], context=context)
                    args += [('id','in',allowed_accounts)]

            if context['dimension'] == 1:
                dimension_ids = self.pool.get('account.analytic.dimension').search(cr, uid, [('sequence','=',1),('company_id','=',user.company_id.id)])
                if dimension_ids and (dimension_ids[0] in allowed_dimensions):
                    args += [('dimension_id','in',dimension_ids)]

                    if 'dimension2' in context and context['dimension2']:
                        allowed_accounts2 = self.read(cr, uid, context['dimension2'], ['allowed_account_ids'])['allowed_account_ids']
                        args += [('id','in',allowed_accounts2)]
                    if 'dimension3' in context and context['dimension3']:
                        allowed_accounts3 = self.read(cr, uid, context['dimension3'], ['allowed_account_ids'])['allowed_account_ids']
                        args += [('id','in',allowed_accounts3)]
                else:
                    return False

            if context['dimension'] == 2:
                dimension_ids = self.pool.get('account.analytic.dimension').search(cr, uid, [('sequence','=',2),('company_id','=',user.company_id.id)])
                if dimension_ids and (dimension_ids[0] in allowed_dimensions):
                    args += [('dimension_id','in',dimension_ids)]
                    
                    if 'dimension1' in context and context['dimension1']:
                        allowed_accounts1 = self.read(cr, uid, context['dimension1'], ['allowed_account_ids'])['allowed_account_ids']
                        args += [('id','in',allowed_accounts1)]
                    if 'dimension3' in context and context['dimension3']:
                        allowed_accounts3 = self.read(cr, uid, context['dimension3'], ['allowed_account_ids'])['allowed_account_ids']
                        args += [('id','in',allowed_accounts3)]
                else:
                    return False

            if context['dimension'] == 3:
                dimension_ids = self.pool.get('account.analytic.dimension').search(cr, uid, [('sequence','=',3),('company_id','=',user.company_id.id)])
                if dimension_ids and (dimension_ids[0] in allowed_dimensions):
                    args += [('dimension_id','in',dimension_ids)]

                    if 'dimension1' in context and context['dimension1']:
                        allowed_accounts1 = self.read(cr, uid, context['dimension1'], ['allowed_account_ids'])['allowed_account_ids']
                        args += [('id','in',allowed_accounts1)]
                    if 'dimension2' in context and context['dimension2']:
                        allowed_accounts2 = self.read(cr, uid, context['dimension2'], ['allowed_account_ids'])['allowed_account_ids']
                        args += [('id','in',allowed_accounts2)]
                else:
                    return False

        if name:
            ids = self.search(cr, uid, [('code', 'ilike', name)] + args, limit=limit, context=context)
            if not ids:
                domain = []
                for name2 in name.split('/'):
                    name = name2.strip()
                    ids = self.search(cr, uid, domain + [('name', 'ilike', name)] + args, limit=limit, context=context)
                    if not ids: break
                    domain = [('parent_id','in',ids)]
        else:
            ids = self.search(cr, uid, args, context=context, limit=limit)

        return self.name_get(cr, uid, ids, context)

    def create(self, cr, uid, vals, context=None):
        """Doesn't allow 2 acccounts with same code for the same company"""
        if 'code' in vals and vals['code']:
            acc_ids = self.search(cr, uid, [('code','=',vals['code']),('company_id','=',vals['company_id']),'|',('active','=',True),('active','=',False)])
            if acc_ids:
                raise osv.except_osv(_('Error!'), _('An analytic account already exist for that reference in the same company'))

        """Create the analytical account in the allowed account"""
        res =  super(account_analytic_account, self).create(cr, uid, vals, context=context)
        if 'allowed_account_ids' in vals and vals['allowed_account_ids'] and vals['allowed_account_ids'][0][2] :
            context['no_loop_write'] = True        
            self.write(cr, uid, vals['allowed_account_ids'][0][2], {'allowed_account_ids':[(4,res)]}, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        """Create the analytical account in the allowed account"""
        for account in self.browse(cr, uid ,ids):
            """Doesn't allow 2 acccounts with same code for the same company"""
            if 'code' in vals and vals['code']:
                acc_ids = self.search(cr, uid, [('code','=',vals['code']),('company_id','=',account.company_id.id),'|',('active','=',True),('active','=',False)])
                if acc_ids:
                    raise osv.except_osv(_('Error!'), _('An analytic account already exist for that reference in the same company'))
            if 'allowed_account_ids' in vals and vals['allowed_account_ids'] and 'no_loop_write' not in context:
                new_accounts = vals['allowed_account_ids'][0][2]
                old_accounts = []
                for acc in account.allowed_account_ids:
                    old_accounts.append(acc.id)

                if len(new_accounts) > len(old_accounts):
                    # If accounts are added
                    added_accounts = list(set(new_accounts) - set(old_accounts))
                    context['no_loop_write'] = True        
                    self.write(cr, uid, added_accounts, {'allowed_account_ids':[(4,account.id)]}, context=context)
                elif len(new_accounts) < len(old_accounts):
                    # If accounts are removed
                    removed_accounts = list(set(old_accounts) - set(new_accounts))
                    context['no_loop_write'] = True        
                    self.write(cr, uid, removed_accounts, {'allowed_account_ids':[(3,account.id)]}, context=context)
                elif set(new_accounts) != set(old_accounts):
                    # if account are replaced
                    replaced_new_accounts = list(set(new_accounts) - set(old_accounts))
                    replaced_old_accounts = list(set(old_accounts) - set(new_accounts))
                    context['no_loop_write'] = True        
                    self.write(cr, uid, replaced_new_accounts, {'allowed_account_ids':[(4,account.id)]}, context=context)
                    self.write(cr, uid, replaced_old_accounts, {'allowed_account_ids':[(3,account.id)]}, context=context)

        return super(account_analytic_account, self).write(cr, uid, ids, vals, context=context)

    def copy(self, cr, uid, id, default=None, context=None):
        """Clear child accounts, code, and lines at copy"""
        if not default:
            default = {}
        analytic = self.browse(cr, uid, id, context=context)
        default.update(
            child_ids = False,
            code = False,
            line_ids = False,
            name = _("%s (copy)") % (analytic['name']))
        return super(account_analytic_account, self).copy(cr, uid, id, default, context=context)


class account_analytic_line(osv.osv):

    _inherit = 'account.analytic.line'

    _columns = {
#        'period_id': fields.many2one('account.period', 'Accounting Period'),
#        'journal_entry_id': fields.related('move_id', 'move_id', type='many2one', relation='account.move', string='Journal Entry'),
        'dimension_id': fields.related('account_id', 'dimension_id', type='many2one', relation='account.analytic.dimension', string='Dimension', store=True),
    }

#    def create(self, cr, uid, vals, context=None):
#        """Set the proper sign for amount not in EUR"""
#        res = super(account_analytic_line, self).create(cr, uid, vals=vals, context=context)
#
#        line = self.browse(cr, uid, res)
#
#        if line.move_id and line.move_id.currency_id and line.move_id.currency_id.name != 'EUR':
#            if line.move_id.debit != 0.0:
#                amount = -line.move_id.debit
#            elif line.move_id.credit != 0.0:
#                amount = line.move_id.credit
#            else:
#                amount = 0.0
#            self.write(cr, uid, [res], {'amount':amount})
#
#        return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
