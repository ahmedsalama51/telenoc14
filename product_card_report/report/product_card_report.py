# -*- coding: utf-8 -*-
import logging
from pytz import timezone, UTC

from odoo import models, api
from datetime import datetime
_logger = logging.getLogger(__name__)
grey = "\x1b[38;21m"
yellow = "\x1b[33;21m"
red = "\x1b[31;21m"
bold_red = "\x1b[31;1m"
reset = "\x1b[0m"
green = "\x1b[32m"
blue = "\x1b[34m"
# Ahmed Salama Code Start ---->


class ProductCardReport(models.AbstractModel):
    _name = 'report.product_card_report.product_card_report'
    
    def _get_sum_move_lines_history(self, data):
        move_obj = self.env['stock.move.line']
        product_obj = self.env['product.product']
        product = product_obj.sudo().browse(data['product_id'][0])
        main_domain = ['|',
                       ('location_id', 'in', data.get('location_ids')),
                       ('location_dest_id', 'in', data.get('location_ids')),
                       ('product_id', '=', data.get('product_id')[0]),
                       ('date', '<', data.get('date_from')),
                       ('state', 'in', data.get('states_value'))
                       ]
        all_moves = move_obj.sudo().search(main_domain)
        total_value = total_in_qty = total_out_qty = 0.0
        for move_line in all_moves:
            # Type in ----> وارد
            price = move_line.move_id.price_unit or move_line.product_id.standard_price
            if move_line.location_dest_id.id in data['location_ids']:
                total_in_qty += move_line.qty_done
                if price:
                    total_value += move_line.qty_done * price
            # Type out ----> صادر
            elif move_line.location_id.id in data['location_ids']:
                total_out_qty -= move_line.qty_done
                if price:
                    total_value -= move_line.qty_done * price
        total_balance = total_in_qty + total_out_qty
        # TODO: Use value from main product cost
        # total_value = total_balance * product.standard_price
        result = {
            'total_in_qty': total_in_qty,
            'total_out_qty': total_out_qty,
            'start_balance': total_balance,
            'start_value': round(total_value, 3),
            'current_cost': product.standard_price,
        }
        return result
    
    def _get_move_lines(self, data):
        move_obj = self.env['stock.move.line']
        # TODO: only for developer details
        # Type out (credit)----> صادر ('location_id','=',data['location_id'])
        # Type in (debit)----> وارد ('location_dest_id', '=', data['location_id']),
        main_domain = ['|',
                       ('location_id', 'in', data.get('location_ids')),
                       ('location_dest_id', 'in', data.get('location_ids')),
                       ('product_id', '=', data.get('product_id')[0]),
                       ('date', '>=', data.get('date_from')),
                       ('date', '<=', data.get('date_to')),
                       ('state', 'in', data.get('states_value'))]
        moves = move_obj.sudo().search(main_domain, order="date asc")
        _logger.info(blue + "All moves: %s " % moves + reset)
        move_list = []
        for i, move_line in enumerate(moves):
            if i == 0:
                # First Line
                previous = self._get_sum_move_lines_history(data)
                prev_balance = previous['start_balance']
            else:
                previous = move_list[i - 1]
                prev_balance = previous['balance']
            qty = move_line.qty_done
            debit = credit = 0.0
            location = False
            move_type = False
            # Check for move type
            if move_line.location_dest_id.id in data['location_ids']:
                debit = qty
                move_type = 'in'
                location = move_line.location_dest_id.complete_name
            elif move_line.location_id.id in data['location_ids']:
                credit = qty
                move_type = 'out'
                location = move_line.location_id.complete_name
            
            balance = debit - credit
            price = move_line.move_id.price_unit or move_line.product_id.standard_price
            current_balance = prev_balance + balance
            # Getting correct date
            old_tz = timezone('UTC')
            tz = self.env.user.tz
            tz = timezone(tz)
            date = old_tz.localize(move_line.date).astimezone(tz)
            move_dict = {
                'date': datetime.strftime(date, '%d/%m/%Y %H:%M:%S'),
                'number': move_line.picking_id.name,
                'type': move_line.move_id.picking_type_id and
                        move_line.move_id.picking_type_id.code or 'incoming',
                # TODO:: if it have no picking it should be inventory action/ TO BE CHECKED ON THE FUTURE
                'move_type': move_type,
                'location': location,
                'debit': debit,
                'credit': credit,
                'balance': current_balance,
                'price_unit': price,
                'value': move_line.curr_cost,
                
            }
            _logger.info(yellow + "Dict moves: %s " % move_dict + reset)
            move_list.append(move_dict)
        return move_list, moves
    
    @api.model
    def _get_report_values(self, docids, data=None):
        data = data if data is not None else {}
        # move_obj = self.env['stock.move']
        product = self.env['product.product'].sudo().browse(data['form']['product_id'][0])
        moves_details = self._get_move_lines(data['form'])
        return {
            # 'doc_ids': moves_details[1].ids,
            # 'doc_model': move_obj,
            'doc_ids': data.get('ids', data.get('active_ids')),
            'doc_model': self.env['product.card.report.wizard'],
            'docs': self.env.user,
            'data': dict(
                data,
                product=product,
                states=data['form']['states'],
                location_ids=self.env['stock.location'].sudo().browse(data['form']['location_ids']).mapped('complete_name'),
                get_move_lines=moves_details[0],
                get_sum_move_lines_history=self._get_sum_move_lines_history(data['form']),
                date_from=data['form']['date_from'],
                date_to=data['form']['date_to'],
            
            ),
        }

# Ahmed Salama Code End.
