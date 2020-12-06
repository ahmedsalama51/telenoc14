# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2017-today Ascetic Business Solution <www.asceticbs.com>
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
#################################################################################

{
    'name': "Force Date",
    'author': 'Telenoc, Ahmed Salama',
    'category': 'Inventory',
    'summary': """Product Card Report""",
    'website': 'http://www.telenoc.org',
    'license': 'AGPL-3',
    'description': """
    This module add force confirmation date on sale order and picking to avoid capture current date
""",
    'version': '.3',
    'depends': ['stock', 'sale', 'sale_stock'],
    'data': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
