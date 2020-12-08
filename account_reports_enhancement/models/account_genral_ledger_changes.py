# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
# Ahmed Salama Code Start ---->


class AccountGeneralLedgerReport(models.AbstractModel):
	_inherit = "account.general.ledger"
	
	@api.model
	def _get_general_ledger_lines(self, options, line_id=None):
		'''
		 Get lines for the whole report or for a specific line.
		TODO: Enhancement add order by date ASC
		:param options: The report options.
		:return: A list of lines, each one represented by a dictionary.
		'''
		lines = []
		aml_lines = []
		options_list = self._get_options_periods_list(options)
		unfold_all = options.get('unfold_all') or (self._context.get('print_mode') and not options['unfolded_lines'])
		date_from = fields.Date.from_string(options['date']['date_from'])
		company_currency = self.env.company.currency_id
		
		expanded_account = line_id and self.env['account.account'].browse(int(line_id[8:]))
		accounts_results, taxes_results = self._do_query(options_list, expanded_account=expanded_account)
		
		total_debit = total_credit = total_balance = 0.0
		for account, periods_results in accounts_results:
			# No comparison allowed in the General Ledger. Then, take only the first period.
			results = periods_results[0]
			
			is_unfolded = 'account_%s' % account.id in options['unfolded_lines']
			
			# account.account record line.
			account_sum = results.get('sum', {})
			account_un_earn = results.get('unaffected_earnings', {})
			
			# Check if there is sub-lines for the current period.
			max_date = account_sum.get('max_date')
			has_lines = max_date and max_date >= date_from or False
			
			amount_currency = account_sum.get('amount_currency', 0.0) + account_un_earn.get('amount_currency', 0.0)
			debit = account_sum.get('debit', 0.0) + account_un_earn.get('debit', 0.0)
			credit = account_sum.get('credit', 0.0) + account_un_earn.get('credit', 0.0)
			balance = account_sum.get('balance', 0.0) + account_un_earn.get('balance', 0.0)
			
			lines.append(
				self._get_account_title_line(options, account, amount_currency, debit, credit, balance, has_lines))
			
			total_debit += debit
			total_credit += credit
			total_balance += balance
			
			if has_lines and (unfold_all or is_unfolded):
				# Initial balance line.
				account_init_bal = results.get('initial_balance', {})
				
				cumulated_balance = account_init_bal.get('balance', 0.0) + account_un_earn.get('balance', 0.0)
				
				lines.append(self._get_initial_balance_line(
					options, account,
					account_init_bal.get('amount_currency', 0.0) + account_un_earn.get('amount_currency', 0.0),
					account_init_bal.get('debit', 0.0) + account_un_earn.get('debit', 0.0),
					account_init_bal.get('credit', 0.0) + account_un_earn.get('credit', 0.0),
					cumulated_balance,
					))
				
				# account.move.line record lines.
				amls = results.get('lines', [])
				
				load_more_remaining = len(amls)
				load_more_counter = self._context.get('print_mode') and load_more_remaining or self.MAX_LINES
				
				for aml in sorted(amls, key=lambda i: i['date'], reverse=False):
					# Don't show more line than load_more_counter.
					if load_more_counter == 0:
						break
					
					cumulated_balance += aml['balance']
					lines.append(self._get_aml_line(options, account, aml, company_currency.round(cumulated_balance)))
					
					load_more_remaining -= 1
					load_more_counter -= 1
					aml_lines.append(aml['id'])
				
				if load_more_remaining > 0:
					# Load more line.
					lines.append(self._get_load_more_line(
						options, account,
						self.MAX_LINES,
						load_more_remaining,
						cumulated_balance,
					))
				
				# Account total line.
				lines.append(self._get_account_total_line(
					options, account,
					account_sum.get('amount_currency', 0.0),
					account_sum.get('debit', 0.0),
					account_sum.get('credit', 0.0),
					account_sum.get('balance', 0.0),
				))
		
		if not line_id:
			# Report total line.
			lines.append(self._get_total_line(
				options,
				total_debit,
				total_credit,
				company_currency.round(total_balance),
			))
			
			# Tax Declaration lines.
			journal_options = self._get_options_journals(options)
			if len(journal_options) == 1 and journal_options[0]['type'] in ('sale', 'purchase'):
				lines += self._get_tax_declaration_lines(
					options, journal_options[0]['type'], taxes_results
				)
		if self.env.context.get('aml_only'):
			return aml_lines
		return lines

# Ahmed Salama Code End.