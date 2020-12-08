# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AccountPartnerLedgerReport(models.AbstractModel):
    _inherit = "account.partner.ledger"
    
    @api.model
    def _get_partner_ledger_lines(self, options, line_id=None):
        '''
         Get lines for the whole report or for a specific line.
        TODO: Enhancement add order by date ASC
        :param options: The report options.
        :return: A list of lines, each one represented by a dictionary.
        '''
        lines = []
        unfold_all = options.get('unfold_all') or (self._context.get('print_mode') and not options['unfolded_lines'])
        
        expanded_partner = line_id and self.env['res.partner'].browse(int(line_id[8:]))
        partners_results = self._do_query(options, expanded_partner=expanded_partner)
        
        total_initial_balance = total_debit = total_credit = total_balance = 0.0
        for partner, results in partners_results:
            is_unfolded = 'partner_%s' % partner.id in options['unfolded_lines']
            
            # res.partner record line.
            partner_sum = results.get('sum', {})
            partner_init_bal = results.get('initial_balance', {})
            
            initial_balance = partner_init_bal.get('balance', 0.0)
            debit = partner_sum.get('debit', 0.0)
            credit = partner_sum.get('credit', 0.0)
            balance = initial_balance + partner_sum.get('balance', 0.0)
            
            lines.append(self._get_report_line_partner(options, partner, initial_balance, debit, credit, balance))
            
            total_initial_balance += initial_balance
            total_debit += debit
            total_credit += credit
            total_balance += balance
            
            if unfold_all or is_unfolded:
                cumulated_balance = initial_balance
                
                # account.move.line record lines.
                amls = results.get('lines', [])
                
                load_more_remaining = len(amls)
                load_more_counter = self._context.get('print_mode') and load_more_remaining or self.MAX_LINES
                for aml in sorted(amls, key=lambda i: i['date'], reverse=False):
                    # Don't show more line than load_more_counter.
                    if load_more_counter == 0:
                        break
                    
                    cumulated_init_balance = cumulated_balance
                    cumulated_balance += aml['balance']
                    lines.append(self._get_report_line_move_line(options, partner, aml, cumulated_init_balance,
                                                                 cumulated_balance))
                    
                    load_more_remaining -= 1
                    load_more_counter -= 1
                
                if load_more_remaining > 0:
                    # Load more line.
                    lines.append(self._get_report_line_load_more(
                        options,
                        partner,
                        self.MAX_LINES,
                        load_more_remaining,
                        cumulated_balance,
                    ))
        
        if not line_id:
            # Report total line.
            lines.append(self._get_report_line_total(
                options,
                total_initial_balance,
                total_debit,
                total_credit,
                total_balance
            ))
        return lines
    
    @api.model
    def _load_more_lines(self, options, line_id, offset, load_more_remaining, progress):
        ''' Get lines for an expanded line using the load more.
        :param options: The report options.
        :return:        A list of lines, each one represented by a dictionary.
        '''
        lines = []
        
        expanded_partner = line_id and self.env['res.partner'].browse(int(line_id[9:]))
        
        load_more_counter = self.MAX_LINES
        
        # Fetch the next batch of lines.
        amls_query, amls_params = self._get_query_amls(options, expanded_partner=expanded_partner, offset=offset, limit=load_more_counter)
        self._cr.execute(amls_query, amls_params)
        amls = self._cr.dictfetchall()
        for aml in sorted(amls, key=lambda i: i['date'], reverse=False):
            # Don't show more line than load_more_counter.
            if load_more_counter == 0:
                break
            
            cumulated_init_balance = progress
            progress += aml['balance']
            
            # account.move.line record line.
            lines.append(self._get_report_line_move_line(options, expanded_partner, aml, cumulated_init_balance, progress))
            
            offset += 1
            load_more_remaining -= 1
            load_more_counter -= 1
        
        if load_more_remaining > 0:
            # Load more line.
            lines.append(self._get_report_line_load_more(
                options,
                expanded_partner,
                offset,
                load_more_remaining,
                progress,
            ))
        return lines
