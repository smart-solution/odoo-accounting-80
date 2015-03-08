# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Smart Solution BVBA
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

{
    'name': 'Multi Analytical Account for Assets',
    'version': '1.0',
    'author': 'Smart Solution (fabian.semal@smartsolution.be)',
    'website': 'www.smartsolution.be',
    'category': 'Analytic Accounting',
    'description': """Multi analytical assignation for assets
    """,
#    'depends': ['product', 'sale', 'purchase', 'account_accountant', 'natuurpunt_account', 'base_vat', 'natuurpunt_activa', 'natuurpunt_purchase'],
    'depends': ['account_asset', 'account_multi_analytic'],
    'data': [
#        'security/multi_analytic_dimension_security.xml',
#        'base/res_company_view.xml',
        'account/asset_view.xml',
#        'analytic/analytic_view.xml',
#        'security/ir.model.access.csv',

    ],
    'installable': True,
    'auto_install': False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
