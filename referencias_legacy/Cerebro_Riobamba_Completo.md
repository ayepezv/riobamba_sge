# RADIOGRAFÍA TÉCNICA - RIOBAMBA SGE
Fuente: siim_adm @ http://192.168.1.17:8069

## Módulo: Account (`account.account`)
**Sugerencia Tabla:** `fi_account_account`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| account_c_ids | many2many | Cuentas por Cobrar |  |
| code | char | unknown |  |
| reconcile | boolean | Allow Reconciliation | Check this box if this account allows reconciliation of journal items. |
| user_type | many2one | Account Type | Account Type is used for information purpose, to generate country-specific legal reports, and set the rules to close a fiscal year and generate opening entries. |
| company_id | many2one | Company |  |
| currency_id | many2one | Secondary Currency | Forces all moves for this account to have this secondary currency. |
| exchange_rate | float | Exchange Rate |  |
| child_id | many2many | Child Accounts |  |
| anterior_id | many2one | Anio Anterior(212..) |  |
| partner_id | many2one | Institucion a Pagar |  |
| child_consol_ids | many2many | Consolidated Children |  |
| foreign_balance | float | Foreign Balance | Total amount (in Secondary currency) for transactions held in secondary currency for this account. |
| sufijo_esigef | char | Sufijo ESIGEF? |  |
| code_aux | char | Codigo |  |
| budget_haber_id | many2one | Partida Haber |  |
| shortcut | char | Shortcut |  |
| unrealized_gain_loss | float | Unrealized Gain or Loss | Value of Loss or Gain due to changes in exchange rate when doing multi-currency transactions. |
| note | text | Note |  |
| parent_id | many2one | Parent |  |
| tercero_id | many2one | Cuenta Fondo Tercero |  |
| account_p_ids | many2many | Cuentas por Pagar |  |
| debit | float | Debit |  |
| account_comp_id | many2one | Cuenta Complementaria | Utilizada para complementar movimientos contables para gobierno. |
| account_rec_id | many2one | Cuenta de Cobro |  |
| type | selection | Internal Type | The 'Internal Type' is used for features available on different types of accounts: view can not have journal items, consolidation are accounts that can have children accounts for multi-company consolidations, payable/receivable are for partners accounts (for debit/credit computations), closed for depreciated accounts. |
| tax_ids | many2many | Default Taxes |  |
| account_pay_id | many2one | Cuenta de Pago |  |
| child_parent_ids | one2many | Children |  |
| in_stock | boolean | Afecta en Stock |  |
| active | boolean | Active | If the active field is set to False, it will allow you to hide the account without removing it. |
| adjusted_balance | float | Adjusted Balance | Total amount (in Company currency) for transactions held in secondary currency for this account. |
| esigef | boolean | Exportar a archivo ESIGEF? |  |
| company_currency_id | many2one | Company Currency |  |
| parent_right | integer | Parent Right |  |
| name | char | Name |  |
| level | integer | Level |  |
| financial_report_ids | many2many | Financial Reports |  |
| credit | float | Credit |  |
| parent_left | integer | Parent Left |  |
| budget_id | many2one | Partida Debe |  |
| currency_mode | selection | Outgoing Currencies Rate | This will select how the current currency rate for outgoing transactions is computed. In most countries the legal method is "average" but only a few software systems are able to manage this. So if you import from another software system you may have to use the rate at date. Incoming transactions always use the rate at date. |
| balance | float | Balance |  |

---
## Módulo: Templates for Accounts (`account.account.template`)
**Sugerencia Tabla:** `fi_account_account_template`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| currency_id | many2one | Secondary Currency | Forces all moves for this account to have this secondary currency. |
| code | char | Code |  |
| reconcile | boolean | Allow Reconciliation | Check this option if you want the user to reconcile entries in this account. |
| name | char | Name |  |
| child_parent_ids | one2many | Children |  |
| user_type | many2one | Account Type | These types are defined according to your country. The type contains more information about the account and its specificities. |
| shortcut | char | Shortcut |  |
| financial_report_ids | many2many | Financial Reports |  |
| note | text | Note |  |
| parent_id | many2one | Parent Account Template |  |
| nocreate | boolean | Optional create | If checked, the new chart of accounts will not contain this by default. |
| type | selection | Internal Type | This type is used to differentiate types with special effects in OpenERP: view can not have entries, consolidation are accounts that can have children accounts for multi-company consolidations, payable/receivable are for partners accounts (for debit/credit computations), closed for depreciated accounts. |
| chart_template_id | many2one | Chart Template | This optional field allow you to link an account template to a specific chart template that may differ from the one its root parent belongs to. This allow you to define chart templates that extend another and complete it with few new accounts (You don't need to define the whole structure that is common to both several times). |
| tax_ids | many2many | Default Taxes |  |

---
## Módulo: Account Type (`account.account.type`)
**Sugerencia Tabla:** `fi_account_account_type`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| close_method | selection | Deferral Method | Set here the method that will be used to generate the end of year journal entries for all the accounts of this type.   'None' means that nothing will be done.  'Balance' will generally be used for cash accounts.  'Detail' will copy each existing journal item of the previous year, even the reconciled ones.  'Unreconciled' will copy only the journal items that were unreconciled on the first day of the new fiscal year. |
| note | text | Description |  |
| code | char | Code |  |
| name | char | Account Type |  |
| report_type | selection | P&L / BS Category | This field is used to generate legal reports: profit and loss, balance sheet. |

---
## Módulo: account.addtmpl.wizard (`account.addtmpl.wizard`)
**Sugerencia Tabla:** `fi_account_addtmpl_wizard`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| cparent_id | many2one | Parent target | Creates an account with the selected template under this existing parent. |

---
## Módulo: Account Aged Trial balance Report (`account.aged.trial.balance`)
**Sugerencia Tabla:** `fi_account_aged_trial_balance`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| chart_account_id | many2one | Chart of Account | Select Charts of Accounts |
| period_length | integer | Period Length (days) |  |
| period_to | many2one | End Period |  |
| date_from | date | Start Date |  |
| direction_selection | selection | Analysis Direction |  |
| result_selection | selection | Partner's |  |
| company_id | many2one | Company |  |
| journal_ids | many2many | Journals |  |
| filter | selection | Filter by |  |
| period_from | many2one | Start Period |  |
| fiscalyear_id | many2one | Fiscal Year | Keep empty for all open fiscal year |
| date_to | date | End Date |  |
| target_move | selection | Target Moves |  |

---
## Módulo: Analytic Account (`account.analytic.account`)
**Sugerencia Tabla:** `fi_account_analytic_account`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| code | char | Code/Reference |  |
| quantity_max | float | Maximum Time | Sets the higher limit of time to work on the contract. |
| contact_id | many2one | Contact |  |
| currency_id | many2one | Currency |  |
| child_complete_ids | many2many | Account Hierarchy |  |
| partner_id | many2one | Partner |  |
| user_id | many2one | Account Manager |  |
| date_start | date | Date Start |  |
| company_id | many2one | Company |  |
| parent_id | many2one | Parent Analytic Account |  |
| state | selection | State | * When an account is created its in 'Draft' state.                                   * If any associated partner is there, it can be in 'Open' state.                                   * If any pending balance is there it can be in 'Pending'.                                    * And finally when all the transactions are over, it can be in 'Close' state.                                    * The project can be in either if the states 'Template' and 'Running'.  If it is template then we can make projects based on the template projects. If its in 'Running' state it is a normal project.                                   If it is to be reviewed then the state is 'Pending'.  When the project is completed the state is set to 'Done'. |
| complete_name | char | Full Account Name |  |
| debit | float | Debit |  |
| type | selection | Account Type | If you select the View Type, it means you won't allow to create journal entries using that account. |
| description | text | Description |  |
| child_ids | one2many | Child Accounts |  |
| date | date | Date End |  |
| name | char | Account Name |  |
| credit | float | Credit |  |
| line_ids | one2many | Analytic Entries |  |
| balance | float | Balance |  |
| quantity | float | Quantity |  |

---
## Módulo: Account Analytic Balance (`account.analytic.balance`)
**Sugerencia Tabla:** `fi_account_analytic_balance`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| date1 | date | Start of period |  |
| date2 | date | End of period |  |
| empty_acc | boolean | Empty Accounts ?  | Check if you want to display Accounts with 0 balance too. |

---
## Módulo: Account Analytic Cost Ledger (`account.analytic.cost.ledger`)
**Sugerencia Tabla:** `fi_account_analytic_cost_ledger`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| date1 | date | Start of period |  |
| date2 | date | End of period |  |

---
## Módulo: Account Analytic Cost Ledger For Journal Report (`account.analytic.cost.ledger.journal.report`)
**Sugerencia Tabla:** `fi_account_analytic_cost_ledger_journal_report`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| date1 | date | Start of period |  |
| journal | many2many | Journals |  |
| date2 | date | End of period |  |

---
## Módulo: Account Analytic Chart (`account.analytic.chart`)
**Sugerencia Tabla:** `fi_account_analytic_chart`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| from_date | date | From |  |
| to_date | date | To |  |

---
## Módulo: Account Analytic Inverted Balance (`account.analytic.inverted.balance`)
**Sugerencia Tabla:** `fi_account_analytic_inverted_balance`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| date1 | date | Start of period |  |
| date2 | date | End of period |  |

---
## Módulo: Analytic Journal (`account.analytic.journal`)
**Sugerencia Tabla:** `fi_account_analytic_journal`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| code | char | Journal Code |  |
| name | char | Journal Name |  |
| company_id | many2one | Company |  |
| active | boolean | Active | If the active field is set to False, it will allow you to hide the analytic journal without removing it. |
| line_ids | one2many | Lines |  |
| type | selection | Type | Gives the type of the analytic journal. When it needs for a document (eg: an invoice) to create analytic entries, OpenERP will look for a matching journal of the same type. |

---
## Módulo: Account Analytic Journal (`account.analytic.journal.report`)
**Sugerencia Tabla:** `fi_account_analytic_journal_report`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| date1 | date | Start of period |  |
| date2 | date | End of period |  |

---
## Módulo: Analytic Line (`account.analytic.line`)
**Sugerencia Tabla:** `fi_account_analytic_line`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| code | char | Code |  |
| user_id | many2one | User |  |
| account_id | many2one | Analytic Account |  |
| general_account_id | many2one | General Account |  |
| product_uom_id | many2one | UoM |  |
| company_id | many2one | Company |  |
| journal_id | many2one | Analytic Journal |  |
| currency_id | many2one | Account currency | The related account currency if not equal to the company one. |
| amount | float | Amount | Calculated by multiplying the quantity and the price given in the Product's cost price. Always expressed in the company main currency. |
| product_id | many2one | Product |  |
| unit_amount | float | Quantity | Specifies the amount of quantity to count. |
| date | date | Date |  |
| amount_currency | float | Amount currency | The amount expressed in the related account currency if not equal to the company one. |
| ref | char | Ref. |  |
| move_id | many2one | Move Line |  |
| name | char | Description |  |

---
## Módulo: Asset (`account.asset.asset`)
**Sugerencia Tabla:** `fi_account_asset_asset`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| code | char | Reference |  |
| method_end | date | Ending Date |  |
| prorata | boolean | Prorata Temporis | Indicates that the first depreciation entry for this asset have to be done from the purchase date instead of the first January |
| salvage_value | float | Salvage Value | It is the amount you plan to have that you cannot depreciate. |
| currency_id | many2one | Currency |  |
| partner_id | many2one | Partner |  |
| method_progress_factor | float | Degressive Factor |  |
| company_id | many2one | Company |  |
| note | text | Note |  |
| parent_id | many2one | Parent Asset |  |
| state | selection | State | When an asset is created, the state is 'Draft'. If the asset is confirmed, the state goes in 'Running' and the depreciation lines can be posted in the accounting. You can manually close an asset when the depreciation is over. If the last line of depreciation is posted, the asset automatically goes in that state. |
| method_period | integer | Period Length | State here the time during 2 depreciations, in months |
| purchase_date | date | Purchase Date |  |
| history_ids | one2many | History |  |
| method | selection | Computation Method | Choose the method to use to compute the amount of depreciation lines.   * Linear: Calculated on basis of: Gross Value / Number of Depreciations   * Degressive: Calculated on basis of: Remaining Value * Degressive Factor |
| method_number | integer | Number of Depreciations | Calculates Depreciation within specified interval |
| depreciation_line_ids | one2many | Depreciation Lines |  |
| child_ids | one2many | Children Assets |  |
| method_time | selection | Time Method | Choose the method to use to compute the dates and number of depreciation lines.   * Number of Depreciations: Fix the number of depreciation lines and the time between 2 depreciations.   * Ending Date: Choose the time between 2 depreciations and the date the depreciations won't go beyond. |
| value_residual | float | Residual Value |  |
| active | boolean | Active |  |
| name | char | Asset |  |
| purchase_value | float | Gross value  |  |
| account_move_line_ids | one2many | Entries |  |
| category_id | many2one | Asset category |  |

---
## Módulo: Asset category (`account.asset.category`)
**Sugerencia Tabla:** `fi_account_asset_category`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| method_number | integer | Number of Depreciations |  |
| account_expense_depreciation_id | many2one | Depr. Expense Account |  |
| method_progress_factor | float | Degressive Factor |  |
| method_end | date | Ending date |  |
| account_asset_id | many2one | Asset Account |  |
| account_depreciation_id | many2one | Depreciation Account |  |
| company_id | many2one | Company |  |
| journal_id | many2one | Journal |  |
| note | text | Note |  |
| prorata | boolean | Prorata Temporis | Indicates that the first depreciation entry for this asset have to be done from the purchase date instead of the first January |
| method_time | selection | Time Method | Choose the method to use to compute the dates and number of depreciation lines.   * Number of Depreciations: Fix the number of depreciation lines and the time between 2 depreciations.   * Ending Date: Choose the time between 2 depreciations and the date the depreciations won't go beyond. |
| open_asset | boolean | Skip Draft State | Check this if you want to automatically confirm the assets of this category when created by invoices. |
| method_period | integer | Period Length | State here the time between 2 depreciations, in months |
| account_analytic_id | many2one | Analytic account |  |
| method | selection | Computation Method | Choose the method to use to compute the amount of depreciation lines.   * Linear: Calculated on basis of: Gross Value / Number of Depreciations   * Degressive: Calculated on basis of: Remaining Value * Degressive Factor |
| name | char | Name |  |

---
## Módulo: Asset depreciation line (`account.asset.depreciation.line`)
**Sugerencia Tabla:** `fi_account_asset_depreciation_line`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| asset_id | many2one | Asset |  |
| name | char | Depreciation Name |  |
| parent_state | char | State of Asset |  |
| sequence | integer | Sequence of the depreciation |  |
| move_check | boolean | Posted |  |
| depreciation_date | char | Depreciation Date |  |
| amount | float | Depreciation Amount |  |
| remaining_value | float | Amount to Depreciate |  |
| move_id | many2one | Depreciation Entry |  |
| depreciated_value | float | Amount Already Depreciated |  |

---
## ⚠️ ERROR EN MÓDULO: account.asset.donar
> El sistema reportó: <Fault warning -- Object Error

Object account.asset.donar doesn't exist: ''>

---
## Módulo: Asset history (`account.asset.history`)
**Sugerencia Tabla:** `fi_account_asset_history`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| asset_id | many2one | Asset |  |
| method_number | integer | Number of Depreciations |  |
| user_id | many2one | User |  |
| name | char | History name |  |
| method_end | date | Ending date |  |
| note | text | Note |  |
| method_time | selection | Time Method | The method to use to compute the dates and number of depreciation lines. Number of Depreciations: Fix the number of depreciation lines and the time between 2 depreciations. Ending Date: Choose the time between 2 depreciations and the date the depreciations won't go beyond. |
| method_period | integer | Period Length | Time in month between two depreciations |
| date | date | Date |  |

---
## ⚠️ ERROR EN MÓDULO: account.asset.property
> El sistema reportó: <Fault warning -- Object Error

Object account.asset.property doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: account.asset.reval
> El sistema reportó: <Fault warning -- Object Error

Object account.asset.reval doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: account.asset.transfer
> El sistema reportó: <Fault warning -- Object Error

Object account.asset.transfer doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: account.asset.transfer.head
> El sistema reportó: <Fault warning -- Object Error

Object account.asset.transfer.head doesn't exist: ''>

---
## Módulo: account.ats (`account.ats`)
**Sugerencia Tabla:** `fi_account_ats`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| period_id | many2one | Periodo |  |
| document_id | many2one | Tipos Comprobantes Autorizados |  |

---
## Módulo: Tipos Comprobantes Autorizados (`account.ats.doc`)
**Sugerencia Tabla:** `fi_account_ats_doc`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| code | char | Código |  |
| name | char | Tipo Comprobante |  |

---
## Módulo: Sustento del Comprobante (`account.ats.sustento`)
**Sugerencia Tabla:** `fi_account_ats_sustento`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| code | char | Código |  |
| type | char | Tipo de Sustento |  |

---
## Módulo: Authorisation for Accounting Documents (`account.authorisation`)
**Sugerencia Tabla:** `fi_account_authorisation`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| is_electronic | boolean | Electrónica? |  |
| num_end | integer | Hasta |  |
| emision_date | date | Fecha Emision |  |
| num_start | integer | Desde |  |
| name | char | Num. de Autorizacion |  |
| type_id | many2one | Tipo de Comprobante |  |
| expiration_date | date | Fecha Vencimiento |  |
| serie_entidad | char | Establecimiento |  |
| sequence_id | many2one | Secuencia | Secuencia Alfanumerica para el documento, se debe registrar cuando pertenece a la compañia |
| serie_emision | char | Punto Emision |  |
| active | boolean | Activo |  |
| partner_id | many2one | Empresa |  |
| in_type | selection | Tipo Interno |  |

---
## Módulo: Automatic Reconcile (`account.automatic.reconcile`)
**Sugerencia Tabla:** `fi_account_automatic_reconcile`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| power | selection | Power | Number of partial amounts that can be combined to find a balance point can be chosen as the power of the automatic reconciliation |
| max_amount | float | Maximum write-off amount |  |
| reconciled | integer | Reconciled transactions |  |
| writeoff_acc_id | many2one | Account |  |
| allow_write_off | boolean | Allow write off |  |
| unreconciled | integer | Not reconciled transactions |  |
| journal_id | many2one | Journal |  |
| period_id | many2one | Period |  |
| account_ids | many2many | Accounts to Reconcile |  |

---
## Módulo: Trial Balance Report (`account.balance.report`)
**Sugerencia Tabla:** `fi_account_balance_report`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| chart_account_id | many2one | Chart of Account | Select Charts of Accounts |
| date_from | date | Start Date |  |
| period_to | many2one | End Period |  |
| company_id | many2one | Company |  |
| journal_ids | many2many | Journals |  |
| filter | selection | Filter by |  |
| period_from | many2one | Start Period |  |
| fiscalyear_id | many2one | Fiscal Year | Keep empty for all open fiscal year |
| date_to | date | End Date |  |
| display_account | selection | Display Accounts |  |
| target_move | selection | Target Moves |  |

---
## Módulo: account.bank.accounts.wizard (`account.bank.accounts.wizard`)
**Sugerencia Tabla:** `fi_account_bank_accounts_wizard`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| currency_id | many2one | Secondary Currency | Forces all moves for this account to have this secondary currency. |
| acc_name | char | Account Name. |  |
| account_type | selection | Account Type |  |
| bank_account_id | many2one | Bank Account |  |

---
## Módulo: Bank Statement (`account.bank.statement`)
**Sugerencia Tabla:** `fi_account_bank_statement`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| balance_end_cash | float | Closing Balance | Closing balance based on cashBox |
| user_id | many2one | Responsible |  |
| account_id | many2one | Account used in this journal | used in statement reconciliation domain, but shouldn't be used elswhere. |
| state | selection | State | When new statement is created the state will be 'Draft'. And after getting confirmation from the bank it will be in 'Confirmed' state. |
| closing_date | datetime | Closed On |  |
| balance_end | float | Computed Balance | Balance as calculated based on Starting Balance and transaction lines |
| balance_start | float | Starting Balance |  |
| company_id | many2one | Company |  |
| journal_id | many2one | Journal |  |
| starting_details_ids | one2many | Opening Cashbox |  |
| currency | many2one | Currency |  |
| move_line_ids | one2many | Entry lines |  |
| ending_details_ids | one2many | Closing Cashbox |  |
| period_id | many2one | Period |  |
| total_entry_encoding | float | Cash Transaction | Total cash transactions |
| date | date | Date |  |
| line_ids | one2many | Statement lines |  |
| balance_end_real | float | Ending Balance |  |
| name | char | Name | if you give the Name other then /, its created Accounting Entries Move will be with same name as statement name. This allows the statement entries to have the same references than the statement itself |

---
## Módulo: Bank Statement Line (`account.bank.statement.line`)
**Sugerencia Tabla:** `fi_account_bank_statement_line`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| analytic_account_id | many2one | Analytic Account |  |
| note | text | Notes |  |
| partner_id | many2one | Partner |  |
| statement_id | many2one | Statement |  |
| sequence | integer | Sequence | Gives the sequence order when displaying a list of bank statement lines. |
| ref | char | Reference |  |
| company_id | many2one | Company |  |
| account_id | many2one | Account |  |
| move_ids | many2many | Moves |  |
| voucher_id | many2one | Payment |  |
| amount | float | Amount |  |
| date | date | Date |  |
| type | selection | Type |  |
| amount_reconciled | float | Amount reconciled |  |
| name | char | Communication |  |

---
## Módulo: account.beneficiario (`account.beneficiario`)
**Sugerencia Tabla:** `fi_account_beneficiario`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| a_id | many2one | Registro Contable |  |
| name | many2one | Beneficiario |  |
| valor | float | Monto |  |

---
## Módulo: CashBox Line (`account.cashbox.line`)
**Sugerencia Tabla:** `fi_account_cashbox_line`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| ending_id | many2one | unknown |  |
| starting_id | many2one | unknown |  |
| subtotal | float | Sub Total |  |
| number | integer | Number |  |
| pieces | float | Values |  |

---
## Módulo: Account Central Journal (`account.central.journal`)
**Sugerencia Tabla:** `fi_account_central_journal`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| chart_account_id | many2one | Chart of Account | Select Charts of Accounts |
| date_from | date | Start Date |  |
| period_to | many2one | End Period |  |
| company_id | many2one | Company |  |
| journal_ids | many2many | Journals |  |
| filter | selection | Filter by |  |
| period_from | many2one | Start Period |  |
| fiscalyear_id | many2one | Fiscal Year | Keep empty for all open fiscal year |
| date_to | date | End Date |  |
| amount_currency | boolean | With Currency | Print Report with the currency column if the currency is different from the company currency |
| target_move | selection | Target Moves |  |

---
## Módulo: account.code.ret (`account.code.ret`)
**Sugerencia Tabla:** `fi_account_code_ret`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| descripcion | text | Descripcion |  |
| name | char | Codigo |  |

---
## Módulo: Account Common Account Report (`account.common.account.report`)
**Sugerencia Tabla:** `fi_account_common_account_report`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| chart_account_id | many2one | Chart of Account | Select Charts of Accounts |
| date_from | date | Start Date |  |
| period_to | many2one | End Period |  |
| company_id | many2one | Company |  |
| journal_ids | many2many | Journals |  |
| filter | selection | Filter by |  |
| period_from | many2one | Start Period |  |
| fiscalyear_id | many2one | Fiscal Year | Keep empty for all open fiscal year |
| date_to | date | End Date |  |
| display_account | selection | Display Accounts |  |
| target_move | selection | Target Moves |  |

---
## Módulo: Account Common Journal Report (`account.common.journal.report`)
**Sugerencia Tabla:** `fi_account_common_journal_report`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| chart_account_id | many2one | Chart of Account | Select Charts of Accounts |
| date_from | date | Start Date |  |
| period_to | many2one | End Period |  |
| company_id | many2one | Company |  |
| journal_ids | many2many | Journals |  |
| filter | selection | Filter by |  |
| period_from | many2one | Start Period |  |
| fiscalyear_id | many2one | Fiscal Year | Keep empty for all open fiscal year |
| date_to | date | End Date |  |
| amount_currency | boolean | With Currency | Print Report with the currency column if the currency is different from the company currency |
| target_move | selection | Target Moves |  |

---
## Módulo: Account Common Partner Report (`account.common.partner.report`)
**Sugerencia Tabla:** `fi_account_common_partner_report`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| chart_account_id | many2one | Chart of Account | Select Charts of Accounts |
| result_selection | selection | Partner's |  |
| date_from | date | Start Date |  |
| period_to | many2one | End Period |  |
| journal_ids | many2many | Journals |  |
| company_id | many2one | Company |  |
| filter | selection | Filter by |  |
| period_from | many2one | Start Period |  |
| fiscalyear_id | many2one | Fiscal Year | Keep empty for all open fiscal year |
| date_to | date | End Date |  |
| target_move | selection | Target Moves |  |

---
## Módulo: Account Common Report (`account.common.report`)
**Sugerencia Tabla:** `fi_account_common_report`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| chart_account_id | many2one | Chart of Account | Select Charts of Accounts |
| date_from | date | Start Date |  |
| period_to | many2one | End Period |  |
| company_id | many2one | Company |  |
| journal_ids | many2many | Journals |  |
| filter | selection | Filter by |  |
| period_from | many2one | Start Period |  |
| fiscalyear_id | many2one | Fiscal Year | Keep empty for all open fiscal year |
| date_to | date | End Date |  |
| target_move | selection | Target Moves |  |

---
## Módulo: Change Currency (`account.change.currency`)
**Sugerencia Tabla:** `fi_account_change_currency`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| currency_id | many2one | Change to | Select a currency to apply on the invoice |

---
## Módulo: Account chart (`account.chart`)
**Sugerencia Tabla:** `fi_account_chart`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| period_from | many2one | Start period |  |
| period_to | many2one | End period |  |
| target_move | selection | Target Moves |  |
| fiscalyear | many2one | Fiscal year | Keep empty for all open fiscal years |

---
## Módulo: Templates for Account Chart (`account.chart.template`)
**Sugerencia Tabla:** `fi_account_chart_template`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| property_account_expense_categ | many2one | Expense Category Account |  |
| complete_tax_set | boolean | Complete Set of Taxes | This boolean helps you to choose if you want to propose to the user to encode the sale and purchase rates or choose from list of taxes. This last choice assumes that the set of tax defined on this template is complete |
| code_digits | integer | # of Digits | No. of Digits to use for account code |
| name | char | Name |  |
| property_account_income_opening | many2one | Opening Entries Income Account |  |
| property_account_expense | many2one | Expense Account on Product Template |  |
| property_account_expense_opening | many2one | Opening Entries Expense Account |  |
| property_account_receivable | many2one | Receivable Account |  |
| property_account_payable | many2one | Payable Account |  |
| visible | boolean | Can be Visible? | Set this to False if you don't want this template to be used actively in the wizard that generate Chart of Accounts from templates, this is useful when you want to generate accounts of this template only when loading its child template. |
| property_reserve_and_surplus_account | many2one | Reserve and Profit/Loss Account | This Account is used for transferring Profit/Loss(If It is Profit: Amount will be added, Loss: Amount will be deducted.), Which is calculated from Profilt & Loss Report |
| tax_code_root_id | many2one | Root Tax Code |  |
| parent_id | many2one | Parent Chart Template |  |
| property_account_income_categ | many2one | Income Category Account |  |
| property_account_income | many2one | Income Account on Product Template |  |
| tax_template_ids | one2many | Tax Template List | List of all the taxes that have to be installed by the wizard |
| bank_account_view_id | many2one | Bank Account |  |
| account_root_id | many2one | Root Account |  |

---
## Módulo: Journal Items Analysis (`account.entries.report`)
**Sugerencia Tabla:** `fi_account_entries_report`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| move_state | selection | State |  |
| nbr | integer | # of Items |  |
| user_type | many2one | Account Type |  |
| journal_id | many2one | Journal |  |
| currency_id | many2one | Currency |  |
| fiscalyear_id | many2one | Fiscal Year |  |
| date_maturity | date | Date Maturity |  |
| year | char | Year |  |
| partner_id | many2one | Partner |  |
| analytic_account_id | many2one | Analytic Account |  |
| move_line_state | selection | State of Move Line |  |
| type | selection | Internal Type | This type is used to differentiate types with special effects in OpenERP: view can not have entries, consolidation are accounts that can have children accounts for multi-company consolidations, payable/receivable are for partners accounts (for debit/credit computations), closed for depreciated accounts. |
| company_id | many2one | Company |  |
| debit | float | Debit |  |
| ref | char | Reference |  |
| account_id | many2one | Account |  |
| period_id | many2one | Period |  |
| amount_currency | float | Amount Currency |  |
| date | date | Date |  |
| month | selection | Month |  |
| day | char | Day |  |
| reconcile_id | many2one | unknown |  |
| product_id | many2one | Product |  |
| product_uom_id | many2one | Product UOM |  |
| credit | float | Credit |  |
| date_created | date | Date Created |  |
| balance | float | Balance |  |
| quantity | float | Products Quantity |  |

---
## Módulo: Account Report (`account.financial.report`)
**Sugerencia Tabla:** `fi_account_financial_report`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| children_ids | one2many | Account Report |  |
| name | char | Report Name |  |
| level | integer | Level |  |
| credit | float | unknown |  |
| sequence | integer | Sequence |  |
| style_overwrite | selection | Financial Report Style | You can set up here the format you want this record to be displayed. If you leave the automatic formatting, it will be computed based on the financial reports hierarchy (auto-computed field 'level'). |
| sign | selection | Sign on Reports | For accounts that are typically more debited than credited and that you would like to print as negative amounts in your reports, you should reverse the sign of the balance; e.g.: Expense account. The same applies for accounts that are typically more credited than debited and that you would like to print as positive amounts in your reports; e.g.: Income account. |
| parent_id | many2one | Parent |  |
| account_type_ids | many2many | Account Types |  |
| account_ids | many2many | Accounts |  |
| debit | float | unknown |  |
| display_detail | selection | Display details |  |
| account_report_id | many2one | Report Value |  |
| balance | float | unknown |  |
| type | selection | Type |  |

---
## Módulo: Fiscal Position (`account.fiscal.position`)
**Sugerencia Tabla:** `fi_account_fiscal_position`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| name | char | Fiscal Position |  |
| company_id | many2one | Company |  |
| note | text | Notes |  |
| account_ids | one2many | Account Mapping |  |
| active | boolean | Active | By unchecking the active field, you may hide a fiscal position without deleting it. |
| tax_ids | one2many | Tax Mapping |  |

---
## Módulo: Accounts Fiscal Position (`account.fiscal.position.account`)
**Sugerencia Tabla:** `fi_account_fiscal_position_account`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| position_id | many2one | Fiscal Position |  |
| account_dest_id | many2one | Account Destination |  |
| account_src_id | many2one | Account Source |  |

---
## Módulo: Template Account Fiscal Mapping (`account.fiscal.position.account.template`)
**Sugerencia Tabla:** `fi_account_fiscal_position_account_template`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| position_id | many2one | Fiscal Mapping |  |
| account_dest_id | many2one | Account Destination |  |
| account_src_id | many2one | Account Source |  |

---
## Módulo: Taxes Fiscal Position (`account.fiscal.position.tax`)
**Sugerencia Tabla:** `fi_account_fiscal_position_tax`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| position_id | many2one | Fiscal Position |  |
| tax_dest_id | many2one | Replacement Tax |  |
| tax_src_id | many2one | Tax Source |  |

---
## Módulo: Template Tax Fiscal Position (`account.fiscal.position.tax.template`)
**Sugerencia Tabla:** `fi_account_fiscal_position_tax_template`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| position_id | many2one | Fiscal Position |  |
| tax_dest_id | many2one | Replacement Tax |  |
| tax_src_id | many2one | Tax Source |  |

---
## Módulo: Template for Fiscal Position (`account.fiscal.position.template`)
**Sugerencia Tabla:** `fi_account_fiscal_position_template`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| note | text | Notes |  |
| chart_template_id | many2one | Chart Template |  |
| tax_ids | one2many | Tax Mapping |  |
| name | char | Fiscal Position Template |  |
| account_ids | one2many | Account Mapping |  |

---
## Módulo: Fiscal Year (`account.fiscalyear`)
**Sugerencia Tabla:** `fi_account_fiscalyear`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| date_stop | date | End Date |  |
| code | char | Code |  |
| name | char | Fiscal Year |  |
| end_journal_period_id | many2one | End of Year Entries Journal |  |
| date_start | date | Start Date |  |
| company_id | many2one | Company |  |
| period_ids | one2many | Periods |  |
| state | selection | State |  |

---
## Módulo: Fiscalyear Close (`account.fiscalyear.close`)
**Sugerencia Tabla:** `fi_account_fiscalyear_close`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| fy_id | many2one | Fiscal Year to close | Select a Fiscal year to close |
| fy2_id | many2one | New Fiscal Year |  |
| period_id | many2one | Opening Entries Period |  |
| journal_id | many2one | Opening Entries Journal | Debe ser un diario de apertura y centralizado TRUE |
| report_name | char | Name of new entries | Give name of the new entries |

---
## Módulo: Fiscalyear Close state (`account.fiscalyear.close.state`)
**Sugerencia Tabla:** `fi_account_fiscalyear_close_state`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| fy_id | many2one | Fiscal Year to close | Select a fiscal year to close |

---
## Módulo: Carpeta docuemntos contables (`account.folder`)
**Sugerencia Tabla:** `fi_account_folder`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| move_ids | one2many | Comprobantes Contables |  |
| name | integer | Numero Carpeta |  |

---
## Módulo: account.folder.line (`account.folder.line`)
**Sugerencia Tabla:** `fi_account_folder_line`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| name | char | Comprobante |  |
| monto | float | Monto |  |
| f_id | many2one | Carpeta |  |
| narration | text | Descripcion |  |
| date | date | Fecha |  |
| partner_id | many2one | Beneficiario |  |

---
## Módulo: Account General Journal (`account.general.journal`)
**Sugerencia Tabla:** `fi_account_general_journal`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| chart_account_id | many2one | Chart of Account | Select Charts of Accounts |
| date_from | date | Start Date |  |
| period_to | many2one | End Period |  |
| company_id | many2one | Company |  |
| journal_ids | many2many | Journals |  |
| filter | selection | Filter by |  |
| period_from | many2one | Start Period |  |
| fiscalyear_id | many2one | Fiscal Year | Keep empty for all open fiscal year |
| date_to | date | End Date |  |
| amount_currency | boolean | With Currency | Print Report with the currency column if the currency is different from the company currency |
| target_move | selection | Target Moves |  |

---
## Módulo: Accounting Report (`accounting.report`)
**Sugerencia Tabla:** `fi_accounting_report`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| period_to_cmp | many2one | End Period |  |
| chart_account_id | many2one | Chart of Account | Select Charts of Accounts |
| fiscalyear_id_cmp | many2one | Fiscal Year | Keep empty for all open fiscal year |
| period_from_cmp | many2one | Start Period |  |
| filter_cmp | selection | Filter by |  |
| date_from | date | Start Date |  |
| enable_filter | boolean | Enable Comparison |  |
| period_to | many2one | End Period |  |
| journal_ids | many2many | Journals |  |
| date_to_cmp | date | End Date |  |
| company_id | many2one | Company |  |
| filter | selection | Filter by |  |
| period_from | many2one | Start Period |  |
| fiscalyear_id | many2one | Fiscal Year | Keep empty for all open fiscal year |
| label_filter | char | Column Label | This label will be displayed on report to show the balance computed for the given comparison filter. |
| date_from_cmp | date | Start Date |  |
| date_to | date | End Date |  |
| account_report_id | many2one | Account Reports |  |
| debit_credit | boolean | Display Debit/Credit Columns | This option allow you to get more details about your the way your balances are computed. Because it is space consumming, we do not allow to use it while doing a comparison |
| target_move | selection | Target Moves |  |

---
## Módulo: account.installer (`account.installer`)
**Sugerencia Tabla:** `fi_account_installer`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| date_stop | date | End Date |  |
| date_start | date | Start Date |  |
| company_id | many2one | Company |  |
| period | selection | Periods |  |
| charts | selection | Chart of Accounts | Installs localized accounting charts to match as closely as possible the accounting needs of your company based on your country. |
| config_logo | binary | Image |  |
| has_default_company | boolean | Has Default Company |  |

---
## Módulo: Invoice (`account.invoice`)
**Sugerencia Tabla:** `fi_account_invoice`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| origin | char | Source Document | Reference of the document that produced this invoice. |
| comment | text | Additional Information |  |
| sustento_id | many2one | Sustento del Comprobante |  |
| date_due | date | Due Date | If you use payment terms, the due date will be computed automatically at the generation of accounting entries. If you keep the payment term and the due date empty, it means direct payment. The payment term may compute several due dates, for example 50% now, 50% in one month. |
| check_total | float | Verification Total |  |
| related_invoice_id | many2one | Factura Relacionada |  |
| partner_bank_id | many2one | Bank Account | Bank Account Number to which the invoice will be paid. A Company bank account if this is a Customer Invoice or Supplier Refund, otherwise a Partner bank account number. |
| payment_term | many2one | Payment Term | If you use payment terms, the due date will be computed automatically at the generation of accounting entries. If you keep the payment term and the due date empty, it means direct payment. The payment term may compute several due dates, for example 50% now, 50% in one month. |
| move_lines | many2many | Entry Lines |  |
| amount_tax_ret_vatb | float | Base Ret. IVA |  |
| number | char | Number |  |
| responsable_id | many2one | Responsable | Responsable de Caja Chica / Fondo Rotativo |
| journal_id | many2one | Journal |  |
| taxed_ret_vatb | float | Retencion en IVA |  |
| address_invoice_id | many2one | Invoice Address |  |
| amount_tax_ret_vatsrv | float | Base Ret. IVA |  |
| no_retention_ir | boolean | No objeto de Retencion |  |
| retention_numbers | selection | Num. de Retención | Lista de Números de Retención reservados |
| tax_line | one2many | Tax Lines |  |
| auth_inv_id | many2one | Autorización | Autorización del SRI para documento recibido |
| taxed_ret_ir | float | Impuesto IR |  |
| fiscal_position | many2one | Fiscal Position |  |
| user_id | many2one | Salesman |  |
| reference | char | Invoice Reference | The partner reference of this invoice. |
| amount_ice | float | ICE |  |
| supplier_number | char | Factura de Proveedor |  |
| address_contact_id | many2one | Contact Address |  |
| amount_vat | float | Base 12 % |  |
| supplier_invoice_number | char | Num. Factura |  |
| reference_type | selection | Reference Type |  |
| company_id | many2one | Company |  |
| tipo_codigo | selection | Tipo Impuesto |  |
| amount_tax | float | Tax |  |
| retention_ir | boolean | Tiene Retencion en IR |  |
| add_disc | float | Additional Discount(%) |  |
| move_id | many2one | Journal Entry | Link to the automatically generated Journal Items. |
| has_responsable | boolean | Responsable? | El compromiso se emitio a un responsable. |
| amount_discounted | float | Descuento |  |
| type | selection | Type |  |
| invoice_line | one2many | Invoice Lines |  |
| id_ext | char | Id. Ext |  |
| internal_number | char | Invoice Number | Unique number of the invoice, computed automatically when the invoice is created. |
| account_id | many2one | Account | The partner account used for this invoice. |
| payment_ids | many2many | Payments |  |
| state | selection | State |  * The 'Draft' state is used when a user is encoding a new and unconfirmed Invoice.              * The 'Pro-forma' when invoice is in Pro-forma state,invoice does not have an invoice number.              * The 'Open' state is used when user create invoice,a invoice number is generated.Its in open state till user does not pay invoice.              * The 'Paid' state is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled.              * The 'Cancelled' state is used when user cancel invoice. |
| certificate_id | many2one | Compromiso Presupuestario |  |
| reconciled | boolean | Paid/Reconciled | It indicates that the invoice has been paid and the journal entry of the invoice has been reconciled with one or several journal entries of payment. |
| residual | float | Balance | Remaining amount due. |
| move_name | char | Journal Entry |  |
| amount_vat_cero | float | Base IVA 0% |  |
| date_invoice | date | Invoice Date | Keep empty to use the current date |
| num_to_use | char | Núm a Usar | Num. de documento a usar |
| amount_novat | float | Base No IVA |  |
| period_id | many2one | Periodo |  |
| amount_net | float | Net Amount | The amount after additional discount. |
| retention_id | many2one | Retencion de Impuestos |  |
| amount_noret_ir | float | Monto no sujeto a IR |  |
| amount_untaxed | float | Untaxed |  |
| amount_tax_retention | float | Total Retencion |  |
| new_number | char | Nuevo Número |  |
| amount_total | float | Total |  |
| reposition | char | Reposicion Referencia |  |
| currency_id | many2one | Currency |  |
| partner_id | many2one | Partner |  |
| manual_ret_num | integer | Num. Retencion |  |
| name | char | Description |  |
| create_retention_type | selection | Numerar Retención | Automatico: El sistema identificara los impuestos y creara la retencion automaticamente,     Manual: El usuario ingresara el numero de retencion     Agrupar: Podra usar la opcion para agrupar facturas del sistema en una sola retencion. |
| add_disc_amt | float | Additional Disc Amt | The additional discount on untaxed amount. |
| amount_pay | float | Total |  |
| aux_invoice | boolean | Fact auxiliar solo para ret electronica |  |
| amount_tax_ret_ir | float | Base IR |  |
| invoice_discount | float | Desc (%) |  |
| taxed_ret_vatsrv | float | Retencion en IVA |  |
| caja_fondo | boolean | Fondo Rotativo/Caja Chica |  |
| retention_vat | boolean | Tiene Retencion en IVA |  |

---
## Módulo: Cancel the Selected Invoices (`account.invoice.cancel`)
**Sugerencia Tabla:** `fi_account_invoice_cancel`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|

---
## Módulo: Confirm the selected invoices (`account.invoice.confirm`)
**Sugerencia Tabla:** `fi_account_invoice_confirm`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|

---
## Módulo: Invoice Line (`account.invoice.line`)
**Sugerencia Tabla:** `fi_account_invoice_line`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| origin | char | Origin | Reference of the document that produced this invoice. |
| sustento_id | many2one | Sustento |  |
| uos_id | many2one | Unit of Measure |  |
| base_noiva | float | Base No Iva |  |
| seq | integer | Secuencia |  |
| price_unit | float | Unit Price |  |
| price_subtotal | float | Subtotal |  |
| monto_retir | float | Ret. IR |  |
| partner_id | many2one | Partner |  |
| project_code | many2one | Centro de Costos |  |
| cxp_id | many2one | Cuenta por pagar |  |
| asset_category_id | many2one | Asset Category |  |
| base_doce | float | Base Imponible |  |
| company_id | many2one | Company |  |
| auth_id | many2one | Autorización |  |
| note | text | Notes |  |
| account_analytic_id | many2one | Analytic Account |  |
| account_id | many2one | Account | The income or expense account related to the selected product. |
| monto_retserv | float | Ret. Servicios |  |
| monto_iva | float | IVA |  |
| invoice_line_tax_id | many2many | Taxes |  |
| date_invoice | date | Fecha de Factura |  |
| discount | float | Discount (%) |  |
| invoice_number | char | Nro. Factura |  |
| base_cero | float | Base Iva 0% |  |
| obra_programa | selection | Obra / Programa |  |
| categ_id | many2one | Línea de Bien / Servicio |  |
| product_id | many2one | Product |  |
| invoice_number_complete | float | Factura Proveedor |  |
| price_total | float | Total |  |
| name | char | Description |  |
| monto_retbienes | float | Ret. Bienes |  |
| type_desc | selection | Tipo |  |
| cambiar_partida | boolean | Cambiar/Seleccionar partida manual |  |
| budget_id | many2one | Aplicación Presupuestaria |  |
| account_number | char | Cuenta |  |
| has_retention | boolean | A Pagar |  |
| invoice_id | many2one | Invoice Reference |  |
| quantity | float | Quantity |  |

---
## Módulo: Invoice Refund (`account.invoice.refund`)
**Sugerencia Tabla:** `fi_account_invoice_refund`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| date | date | Operation date | This date will be used as the invoice date for Refund Invoice and Period will be chosen accordingly! |
| filter_refund | selection | Refund Method | Refund invoice base on this type. You can not Modify and Cancel if the invoice is already reconciled |
| description | char | Description |  |
| period | many2one | Force period |  |
| journal_id | many2one | Refund Journal | You can select here the journal to use for the refund invoice that will be created. If you leave that field empty, it will use the same journal as the current invoice. |

---
## Módulo: Invoices Statistics (`account.invoice.report`)
**Sugerencia Tabla:** `fi_account_invoice_report`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| date_due | date | Due Date |  |
| partner_bank_id | many2one | Bank Account |  |
| payment_term | many2one | Payment Term |  |
| nbr | integer | # of Lines |  |
| product_qty | float | Qty |  |
| month | selection | Month |  |
| currency_id | many2one | Currency |  |
| address_invoice_id | many2one | Invoice Address Name |  |
| year | char | Year |  |
| partner_id | many2one | Partner |  |
| uom_name | char | Reference UoM |  |
| due_delay | float | Avg. Due Delay |  |
| user_id | many2one | Salesman |  |
| address_contact_id | many2one | Contact Address Name |  |
| company_id | many2one | Company |  |
| state | selection | Invoice State |  |
| type | selection | Type |  |
| account_id | many2one | Account |  |
| price_average | float | Average Price |  |
| account_line_id | many2one | Account Line |  |
| residual | float | Total Residual |  |
| fiscal_position | many2one | Fiscal Position |  |
| period_id | many2one | Force Period |  |
| currency_rate | float | Currency Rate |  |
| date | date | Date |  |
| categ_id | many2one | Category of Product |  |
| day | char | Day |  |
| delay_to_pay | float | Avg. Delay To Pay |  |
| price_total | float | Total Without Tax |  |
| product_id | many2one | Product |  |
| journal_id | many2one | Journal |  |

---
## Módulo: Invoice Tax (`account.invoice.tax`)
**Sugerencia Tabla:** `fi_account_invoice_tax`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| factor_tax | float | Multiplication factor Tax code |  |
| sequence | integer | Sequence | Gives the sequence order when displaying a list of invoice tax. |
| fiscal_year | char | Ejercicio Fiscal |  |
| factor_base | float | Multiplication factor for Base code |  |
| retention_id | many2one | Retención |  |
| num_document | char | Num. Comprobante |  |
| partner_id | many2one | SRI |  |
| pay | boolean | Pagado |  |
| percent | char | Porcentaje |  |
| company_id | many2one | Company |  |
| tax_code_id | many2one | Tax Code | The tax basis of the tax declaration. |
| cedula | char | Identificador |  |
| account_id | many2one | Tax Account |  |
| ruc | char | Identificador |  |
| tax_group | selection | Grupo |  |
| base_amount | float | Base Code Amount |  |
| base | float | Base |  |
| date | date | Fecha |  |
| base_code_id | many2one | Base Code | The account basis of the tax declaration. |
| tax_amount | float | Tax Code Amount |  |
| name | char | Tax Description |  |
| invoice_id | many2one | Invoice Line |  |
| manual | boolean | Manual |  |
| amount | float | Amount |  |
| budget_id | many2one | Partida |  |
| partner_id2 | many2one | Proveedor |  |

---
## Módulo: Journal (`account.journal`)
**Sugerencia Tabla:** `fi_account_journal`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| default_debit_account_id | many2one | Default Debit Account | It acts as a default account for debit amount |
| groups_id | many2many | Groups |  |
| update_posted | boolean | Allow Cancelling Entries | Check this box if you want to allow the cancellation the entries related to this journal or of the invoice related to this journal |
| code | char | Code | The code will be displayed on reports. |
| user_id | many2one | User | The user responsible for this journal |
| name | char | Journal Name |  |
| centralisation | boolean | Centralised counterpart | Check this box to determine that each entry of this journal won't create a new counterpart but will share the same counterpart. This is used in fiscal year closing. |
| view_id | many2one | Display Mode | Gives the view used when writing or browsing entries in this journal. The view tells OpenERP which fields should be visible, required or readonly and in which order. You can create your own view for a faster encoding in each journal. |
| group_invoice_lines | boolean | Group Invoice Lines | If this box is checked, the system will try to group the accounting lines when generating them from invoices. |
| type_control_ids | many2many | Type Controls |  |
| company_id | many2one | Company | Company related to this journal |
| default_credit_account_id | many2one | Default Credit Account | It acts as a default account for credit amount |
| currency | many2one | Currency | The currency used to enter statement |
| sequence_id | many2one | Entry Sequence | This field contains the informatin related to the numbering of the journal entries of this journal. |
| account_control_ids | many2many | Account |  |
| auth_ret_id | many2one | Autorización de Ret. | Autorizacion utilizada para documentos de retención en Facturas de Proveedor y Liquidaciones de Compra |
| allow_date | boolean | Check Date in Period | If set to True then do not accept the entry if the entry date is not into the period dates |
| analytic_journal_id | many2one | Analytic Journal | Journal for analytic entries |
| entry_posted | boolean | Skip 'Draft' State for Manual Entries | Check this box if you don't want new journal entries to pass through the 'draft' state and instead goes directly to the 'posted state' without any manual validation.  Note that journal entries that are automatically created by the system are always skipping that state. |
| type | selection | Type | Select 'Sale' for customer invoices journals. Select 'Purchase' for supplier invoices journals. Select 'Cash' or 'Bank' for journals that are used in customer or supplier payments. Select 'General' for miscellaneous operations journals. Select 'Opening/Closing Situation' for entries generated for new fiscal years. |
| auth_id | many2one | Autorización | Autorización utilizada para Facturas de Venta y Liquidaciones de Compra |

---
## Módulo: Journal Column (`account.journal.column`)
**Sugerencia Tabla:** `fi_account_journal_column`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| name | char | Column Name |  |
| sequence | integer | Sequence | Gives the sequence order to journal column. |
| view_id | many2one | Journal View |  |
| required | boolean | Required |  |
| field | selection | Field Name |  |
| readonly | boolean | Readonly |  |

---
## Módulo: Journal Period (`account.journal.period`)
**Sugerencia Tabla:** `fi_account_journal_period`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| name | char | Journal-Period Name |  |
| state | selection | State | When journal period is created. The state is 'Draft'. If a report is printed it comes to 'Printed' state. When all transactions are done, it comes in 'Done' state. |
| journal_id | many2one | Journal |  |
| company_id | many2one | Company |  |
| fiscalyear_id | many2one | Fiscal Year |  |
| period_id | many2one | Period |  |
| active | boolean | Active | If the active field is set to False, it will allow you to hide the journal period without removing it. |
| icon | char | Icon |  |

---
## Módulo: Account Journal Select (`account.journal.select`)
**Sugerencia Tabla:** `fi_account_journal_select`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|

---
## Módulo: Journal View (`account.journal.view`)
**Sugerencia Tabla:** `fi_account_journal_view`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| columns_id | one2many | Columns |  |
| name | char | Journal View |  |

---
## Módulo: Account Model (`account.model`)
**Sugerencia Tabla:** `fi_account_model`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| legend | text | Legend |  |
| lines_id | one2many | Model Entries |  |
| journal_id | many2one | Journal |  |
| name | char | Model Name | This is a model for recurring accounting entries |
| company_id | many2one | Company |  |

---
## Módulo: Account Model Entries (`account.model.line`)
**Sugerencia Tabla:** `fi_account_model_line`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| analytic_account_id | many2one | Analytic Account |  |
| model_id | many2one | Model |  |
| account_id | many2one | Account |  |
| sequence | integer | Sequence | The sequence field is used to order the resources from lower sequences to higher ones. |
| name | char | Name |  |
| currency_id | many2one | Currency |  |
| credit | float | Credit |  |
| date_maturity | selection | Maturity Date | The maturity date of the generated entries for this model. You can choose between the creation date or the creation date of the entries plus the partner payment terms. |
| debit | float | Debit |  |
| amount_currency | float | Amount Currency | The amount expressed in an optional other currency. |
| partner_id | many2one | Partner |  |
| quantity | float | Quantity | The optional quantity on entries. |

---
## Módulo: Account Entry (`account.move`)
**Sugerencia Tabla:** `fi_account_move`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| total_banco | float | Total Banco |  |
| iva | selection | IVA APLICA |  |
| iva_id | many2one | Iva Fisco Bien |  |
| numero_aux | integer | Num. Aux |  |
| narration | text | Internal Note |  |
| journal_id | many2one | Journal |  |
| afectacion | boolean | Afectacion |  |
| fiscalyear_id | many2one | A. Fiscal |  |
| archivo | binary | Archivo |  |
| partner_id | many2one | Empresa |  |
| iva_id2 | many2one | Iva Fisco Srv. |  |
| type2_id | selection | Tipo Transaccion |  |
| migrado2 | boolean | Migrado Ant |  |
| archivado | boolean | Archivado |  |
| no_cp | boolean | NO CP |  |
| company_id | many2one | Company |  |
| contabilizado_id | many2one | Contabilizado por |  |
| state | selection | State |  |
| ref | char | Reference |  |
| is_start | boolean | Es Inicial |  |
| to_unlink | boolean | Borrar |  |
| validar_cp | boolean | Validar CP |  |
| varios_id | many2one | Pagos Varios TTHH |  |
| certificate_id | many2one | Compromiso Presupuestario |  |
| budget_post_id | many2one | Partida |  |
| aux_update | char | aux gob_implementation |  |
| renta_id2 | many2one | Retencion Renta Srv. |  |
| numero | integer | NUMERO COMPROBANTE |  |
| line_id | one2many | Entries |  |
| period_id | many2one | Period |  |
| is_pay | boolean | Es pago |  |
| cta_inventario | many2one | Cuenta de Inventario |  |
| date | date | Date |  |
| renta_id | many2one | Retencion Renta Bien |  |
| active | boolean | Activo |  |
| reposition | char | Reposicion |  |
| name | char | Number |  |
| beneficiario_ids | one2many | Detalle Beneficiarios |  |
| type | selection | Tipo Asiento |  |
| pago_id | many2one | Orden Pago |  |
| migrado | boolean | Es migrado |  |
| amount | float | Amount |  |
| balance | float | balance | This is a field only used for internal purpose and shouldn't be displayed |
| to_check | boolean | To Review | Check this box if you are unsure of that journal entry and if you want to note it as 'to be reviewed' by an accounting expert. |

---
## Módulo: Move bank reconcile (`account.move.bank.reconcile`)
**Sugerencia Tabla:** `fi_account_move_bank_reconcile`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| journal_id | many2one | Journal |  |

---
## Módulo: Move journal (`account.move.journal`)
**Sugerencia Tabla:** `fi_account_move_journal`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| target_move | selection | Target Moves |  |

---
## Módulo: Journal Items (`account.move.line`)
**Sugerencia Tabla:** `fi_account_move_line`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| bank_c_id | many2one | Linea Asiento |  |
| analytic_lines | one2many | Analytic lines |  |
| budget_certificate_id | many2one | Certificacion |  |
| statement_id | many2one | Statement | The bank statement used for bank reconciliation |
| seq | integer | Seq Impreso |  |
| wcxp_id | many2one | Detalle |  |
| monto | float | Monto a Pagar |  |
| date_transfer | date | Fecha Transferencia |  |
| debit | float | Debit |  |
| is_anticipo | boolean | Es anticipo |  |
| currency_id | many2one | Currency | The optional other currency if it is a multi-currency entry. |
| monto_pagado | float | Pagado |  |
| date_maturity | date | Due date | This field is used for payable and receivable journal entries. You can put the limit date for the payment of this line. |
| account_id2 | many2one | Cuenta por pagar tercero |  |
| entry_ids | one2many | Entries |  |
| invoice | many2one | Invoice |  |
| narration | text | Internal Note |  |
| tax_aux_id | many2one | Impuesto factura |  |
| partner_id | many2one | Partner |  |
| reconcile_partial_id | many2one | Partial Reconcile |  |
| concilied_ok | boolean | Conciliado |  |
| analytic_account_id | many2one | Analytic Account |  |
| num_referencia | integer | Num. Transferencia |  |
| tax_computed | float | Impuestos |  |
| reposition | char | Reposicion |  |
| migrado2 | boolean | Migra Inicial |  |
| credit | float | Credit |  |
| hoja | integer | Num. Hoja Estado Cuenta |  |
| cuenta_aux | char | Cuenta Aux |  |
| num_concilied | char | Numero Transferencia |  |
| is_ingreso_gad | boolean | Es ingreso GAD |  |
| company_id | many2one | Company |  |
| judicial_decimo | float | Desc. Judicial (DECIMOS) |  |
| tax_code_id | many2one | Tax Account | The Account can either be a base tax code or a tax code account. |
| state | selection | State |  |
| amount_residual_currency | float | Residual Amount | The residual amount on a receivable or payable of a journal entry expressed in its currency (maybe different of the company currency). |
| amount_residual | float | Residual Amount | The residual amount on a receivable or payable of a journal entry expressed in the company currency. |
| journal_id | many2one | Journal |  |
| partner2_id | many2one | Beneficiario |  |
| ref | char | Referencia |  |
| is_start | boolean | Inicial |  |
| num_comp | char | Comprobante |  |
| budget_post | many2one | Partida Catalogo |  |
| asset_id | many2one | Asset |  |
| updated | boolean | AuxUpdt |  |
| account_id | many2one | Account |  |
| partida_aux | char | Partida Aux |  |
| is_ingreso_anticipo | boolean | Es anticipo ingreso(vacaciones) |  |
| date_concilied | date | Fecha Conciliacion |  |
| move_line_cxp | many2one | Cta. por pagar |  |
| saldo | float | Saldo |  |
| budget_id_cert | many2one | Partida Prespuestaria |  |
| period_id | many2one | Period |  |
| financia_id | many2one | Cta. Financiera |  |
| amount_currency | float | Amount Currency | The amount expressed in an optional other currency if it is a multi-currency entry. |
| date | date | Fecha |  |
| pay_ids | one2many | Pagos |  |
| product_uom_id | many2one | UoM |  |
| tipo_conciliacion | many2one | Tipo Movimiento |  |
| move_id | many2one | Move | The move of this entry line. |
| product_id | many2one | Product |  |
| reconcile_id | many2one | Reconcile |  |
| centralisation | selection | Centralisation |  |
| tax_amount | float | Tax/Base Amount | If the Tax account is a tax code account, this field will contain the taxed amount.If the tax account is base tax code, this field will contain the basic amount(without tax). |
| name | char | Name |  |
| account_tax_id | many2one | Tax |  |
| pay_id | many2one | Pago |  |
| to_pay | boolean | Pagar |  |
| p_id | many2one | Impuestos |  |
| budget_accrued | boolean | Presupuesto Devengado ? |  |
| to_pay2 | boolean | Pagar |  |
| migrado | boolean | Es migrado |  |
| budget_paid | boolean | Presupuesto Pagado/Recaudado ? |  |
| budget_id | many2one | Partida |  |
| spi_numero | integer | Num.SPI |  |
| blocked | boolean | Litigation | You can check this box to mark this journal item as a litigation with the associated partner |
| date_created | date | Creation date |  |
| balance | float | Balance |  |
| quantity | float | Quantity | The optional quantity expressed by this line, eg: number of product sold. The quantity is not a legal requirement but is very useful for some reports. |

---
## Módulo: Account move line reconcile (`account.move.line.reconcile`)
**Sugerencia Tabla:** `fi_account_move_line_reconcile`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| trans_nbr | integer | # of Transaction |  |
| credit | float | Credit amount |  |
| writeoff | float | Write-Off amount |  |
| debit | float | Debit amount |  |

---
## Módulo: Move line reconcile select (`account.move.line.reconcile.select`)
**Sugerencia Tabla:** `fi_account_move_line_reconcile_select`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| account_id | many2one | Account |  |

---
## Módulo: Account move line reconcile (writeoff) (`account.move.line.reconcile.writeoff`)
**Sugerencia Tabla:** `fi_account_move_line_reconcile_writeoff`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| comment | char | Comment |  |
| analytic_id | many2one | Analytic Account |  |
| date_p | date | Date |  |
| writeoff_acc_id | many2one | Write-Off account |  |
| journal_id | many2one | Write-Off Journal |  |

---
## Módulo: Unreconciliation (`account.move.line.unreconcile.select`)
**Sugerencia Tabla:** `fi_account_move_line_unreconcile_select`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| account_id | many2one | Account |  |

---
## Módulo: Account Reconciliation (`account.move.reconcile`)
**Sugerencia Tabla:** `fi_account_move_reconcile`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| line_id | one2many | Entry Lines |  |
| type | char | Type |  |
| create_date | date | Creation date |  |
| name | char | Name |  |
| line_partial_ids | one2many | Partial Entry lines |  |

---
## Módulo: Choose Fiscal Year (`account.open.closed.fiscalyear`)
**Sugerencia Tabla:** `fi_account_open_closed_fiscalyear`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| fyear_id | many2one | Fiscal Year to Open | Select Fiscal Year which you want to remove entries for its End of year entries journal |

---
## Módulo: Print Account Partner Balance (`account.partner.balance`)
**Sugerencia Tabla:** `fi_account_partner_balance`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| display_partner | selection | Display Partners |  |
| chart_account_id | many2one | Chart of Account | Select Charts of Accounts |
| result_selection | selection | Partner's |  |
| date_from | date | Start Date |  |
| period_to | many2one | End Period |  |
| company_id | many2one | Company |  |
| journal_ids | many2many | Journals |  |
| filter | selection | Filter by |  |
| period_from | many2one | Start Period |  |
| fiscalyear_id | many2one | Fiscal Year | Keep empty for all open fiscal year |
| date_to | date | End Date |  |
| target_move | selection | Target Moves |  |

---
## Módulo: Account Partner Ledger (`account.partner.ledger`)
**Sugerencia Tabla:** `fi_account_partner_ledger`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| initial_balance | boolean | Include Initial Balances | If you selected to filter by date or period, this field allow you to add a row to display the amount of debit/credit/balance that precedes the filter you've set. |
| chart_account_id | many2one | Chart of Account | Select Charts of Accounts |
| result_selection | selection | Partner's |  |
| date_from | date | Start Date |  |
| period_to | many2one | End Period |  |
| company_id | many2one | Company |  |
| journal_ids | many2many | Journals |  |
| filter | selection | Filter by |  |
| period_from | many2one | Start Period |  |
| fiscalyear_id | many2one | Fiscal Year | Keep empty for all open fiscal year |
| page_split | boolean | One Partner Per Page | Display Ledger Report with One partner per page |
| date_to | date | End Date |  |
| amount_currency | boolean | With Currency | It adds the currency column if the currency is different from the company currency |
| target_move | selection | Target Moves |  |

---
## Módulo: Reconcilation Process partner by partner (`account.partner.reconcile.process`)
**Sugerencia Tabla:** `fi_account_partner_reconcile_process`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| progress | float | Progress | Shows you the progress made today on the reconciliation process. Given by  Partners Reconciled Today \ (Remaining Partners + Partners Reconciled Today) |
| today_reconciled | float | Partners Reconciled Today | This figure depicts the total number of partners that have gone throught the reconciliation process today. The current partner is counted as already processed. |
| next_partner_id | many2one | Next Partner to Reconcile | This field shows you the next partner that will be automatically chosen by the system to go through the reconciliation process, based on the latest day it have been reconciled. |
| to_reconcile | float | Remaining Partners | This is the remaining partners for who you should check if there is something to reconcile or not. This figure already count the current partner as reconciled. |

---
## Módulo: account.payment.sri (`account.payment.sri`)
**Sugerencia Tabla:** `fi_account_payment_sri`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| name | char | Descripcion |  |
| certificate_id | many2one | Cert |  |
| date_end | date | Fecha Hasta |  |
| date_start | date | Fecha Desde |  |
| state | selection | Estado |  |
| period_id | many2one | Periodo |  |
| account_ids | many2many | Ctas. Impuestos Retenidos |  |
| line_ids | one2many | Detalle |  |
| partner_id | many2one | SRI |  |
| move_id | many2one | Diario de Pago |  |

---
## Módulo: Payment Term (`account.payment.term`)
**Sugerencia Tabla:** `fi_account_payment_term`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| active | boolean | Active | If the active field is set to False, it will allow you to hide the payment term without removing it. |
| note | text | Description |  |
| name | char | Payment Term |  |
| line_ids | one2many | Terms |  |

---
## Módulo: Payment Term Line (`account.payment.term.line`)
**Sugerencia Tabla:** `fi_account_payment_term_line`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| payment_id | many2one | Payment Term |  |
| name | char | Line Name |  |
| sequence | integer | Sequence | The sequence field is used to order the payment term lines from the lowest sequences to the higher ones |
| days2 | integer | Day of the Month | Day of the month, set -1 for the last day of the current month. If it's positive, it gives the day of the next month. Set 0 for net days (otherwise it's based on the beginning of the month). |
| days | integer | Number of Days | Number of days to add before computation of the day of month.If Date=15/01, Number of Days=22, Day of Month=-1, then the due date is 28/02. |
| value | selection | Valuation | Select here the kind of valuation related to this payment term line. Note that you should have your last line with the type 'Balance' to ensure that the whole amount will be threated. |
| value_amount | float | Amount To Pay | For percent enter a ratio between 0-1. |

---
## Módulo: Account period (`account.period`)
**Sugerencia Tabla:** `fi_account_period`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| data_transferencias | binary | Archivo de Transferencias |  |
| date_stop | date | End of Period |  |
| code | char | Code |  |
| name | char | Period Name |  |
| state | selection | State | When monthly periods are created. The state is 'Draft'. At the end of monthly period it is in 'Done' state. |
| date_start | date | Start of Period |  |
| company_id | many2one | Company |  |
| fiscalyear_id | many2one | Fiscal Year |  |
| total_cierre | integer | Total Cierres |  |
| data_balance | binary | Archivo de Balance |  |
| data_cedulas | binary | Archivo de Cedulas |  |
| special | boolean | Opening/Closing Period | These periods can overlap. |

---
## Módulo: period close (`account.period.close`)
**Sugerencia Tabla:** `fi_account_period_close`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| data_transferencias | binary | Archivo de Transferencias |  |
| sure | boolean | Check this box |  |
| data_balance | binary | Archivo de Balance |  |
| data_cedulas | binary | Archivo de Cedulas |  |

---
## Módulo: Account Print Journal (`account.print.journal`)
**Sugerencia Tabla:** `fi_account_print_journal`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| chart_account_id | many2one | Chart of Account | Select Charts of Accounts |
| sort_selection | selection | Entries Sorted by |  |
| date_from | date | Start Date |  |
| period_to | many2one | End Period |  |
| journal_ids | many2many | Journals |  |
| company_id | many2one | Company |  |
| filter | selection | Filter by |  |
| period_from | many2one | Start Period |  |
| fiscalyear_id | many2one | Fiscal Year | Keep empty for all open fiscal year |
| date_to | date | End Date |  |
| amount_currency | boolean | With Currency | Print Report with the currency column if the currency is different from the company currency |
| target_move | selection | Target Moves |  |

---
## Módulo: account.recaudacion (`account.recaudacion`)
**Sugerencia Tabla:** `fi_account_recaudacion`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| simultaneo_id | many2one | Asiento Simultaneo |  |
| partida_anterior | many2one | Partida de cuentas por cobrar anterior |  |
| date_end | date | Fecha Hasta |  |
| valor_detalle | float | Valor detalle |  |
| archivo | binary | Archivo |  |
| acc_ant_id | many2one | Cuenta Anio Anterior |  |
| tipo | selection | Tipo |  |
| journal_id | many2one | Diario |  |
| formapago_ids | one2many | Forma de pago |  |
| move_ids | one2many | Detalle asiento |  |
| state | selection | Estado |  |
| valor_resumen | float | Valor resumen |  |
| recaudacion_ids_depurado | one2many | Detalle Resumen Recaudado Depurado |  |
| archivoxls | binary | Archivo Anios Anteriores xls |  |
| valor_dinero | float | Valor dinero |  |
| recaudacion_ids | one2many | Detalle Resumen Recaudado |  |
| tercero_ids | one2many | Fondos Ajenos Detalle |  |
| date | date | Fecha |  |
| move_id | many2one | Asiento Contable |  |
| line_det_ids | one2many | Detalle |  |
| name | char | Codigo Documento |  |
| recaudacion_ids_2 | one2many | Detalle Resumen Recaudado Anio |  |
| file_namexls | char | N. archivo xls |  |

---
## Módulo: account.recaudacion.line (`account.recaudacion.line`)
**Sugerencia Tabla:** `fi_account_recaudacion_line`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| account_id | char | Cuenta Contable |  |
| recargo | float | Recargo |  |
| descuento | float | Descuento |  |
| rec_id | many2one | Recaudacion |  |
| anterior_value | float | Anterior |  |
| actual_value | float | Actual |  |
| valor | float | Valor Total |  |
| partida_id | char | Partida |  |
| desc | char | Descripcion |  |

---
## Módulo: Detalle forma de pago recaudacion (`account.recaudacion.pago`)
**Sugerencia Tabla:** `fi_account_recaudacion_pago`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| monto | float | Monto |  |
| rec_id | many2one | Recaudacion |  |
| account_id | many2one | Cuenta Contable |  |
| journal_id | many2one | Forma Pago |  |

---
## Módulo: General Ledger Report (`account.report.general.ledger`)
**Sugerencia Tabla:** `fi_account_report_general_ledger`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| initial_balance | boolean | Include Initial Balances | If you selected to filter by date or period, this field allow you to add a row to display the amount of debit/credit/balance that precedes the filter you've set. |
| chart_account_id | many2one | Chart of Account | Select Charts of Accounts |
| date_from | date | Start Date |  |
| landscape | boolean | Landscape Mode |  |
| period_to | many2one | End Period |  |
| journal_ids | many2many | Journals |  |
| company_id | many2one | Company |  |
| filter | selection | Filter by |  |
| period_from | many2one | Start Period |  |
| fiscalyear_id | many2one | Fiscal Year | Keep empty for all open fiscal year |
| sortby | selection | Sort by |  |
| date_to | date | End Date |  |
| amount_currency | boolean | With Currency | It adds the currency column if the currency is different from the company currency |
| display_account | selection | Display Accounts |  |
| target_move | selection | Target Moves |  |

---
## Módulo: Documentos de Retención (`account.retention`)
**Sugerencia Tabla:** `fi_account_retention`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| address_id | many2one | Direccion |  |
| digital_id | many2one | Retencion Digital |  |
| type | selection | Tipo Comprobante |  |
| name | char | Número |  |
| invoice_id | many2one | Documento |  |
| tax_ids | one2many | Detalle de Impuestos |  |
| manual | boolean | Numeración Manual |  |
| number | char | Número |  |
| date | date | Fecha Emision |  |
| state | selection | Estado |  |
| auth_id2 | char | Autorizacion Retencion Electronica |  |
| to_cancel | boolean | Para anulación |  |
| num_document | char | Num. Comprobante |  |
| move_cancel_id | many2one | Asiento de Cancelacion |  |
| in_type | selection | Tipo |  |
| partner_id | many2one | Empresa |  |
| auth_id | many2one | Autorización |  |
| move_id | many2one | Asiento Contable |  |
| amount_total | float | Total |  |

---
## Módulo: account.retention.cache (`account.retention.cache`)
**Sugerencia Tabla:** `fi_account_retention_cache`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| active | boolean | Activo |  |
| name | char | Numero a Reservar |  |

---
## Módulo: account.sequence.fiscalyear (`account.sequence.fiscalyear`)
**Sugerencia Tabla:** `fi_account_sequence_fiscalyear`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| sequence_id | many2one | Sequence |  |
| fiscalyear_id | many2one | Fiscal Year |  |
| sequence_main_id | many2one | Main Sequence |  |

---
## ⚠️ ERROR EN MÓDULO: account.spi.voucher
> El sistema reportó: <Fault warning -- Object Error

Object account.spi.voucher doesn't exist: ''>

---
## Módulo: Entries by Statement from Invoices (`account.statement.from.invoice`)
**Sugerencia Tabla:** `fi_account_statement_from_invoice`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| date | date | Date payment |  |
| line_ids | many2many | Invoices |  |
| journal_ids | many2many | Journal |  |

---
## Módulo: Entries by Statement from Invoices (`account.statement.from.invoice.lines`)
**Sugerencia Tabla:** `fi_account_statement_from_invoice_lines`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| line_ids | many2many | Invoices |  |

---
## Módulo: Account State Open (`account.state.open`)
**Sugerencia Tabla:** `fi_account_state_open`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|

---
## Módulo: Account Subscription (`account.subscription`)
**Sugerencia Tabla:** `fi_account_subscription`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| model_id | many2one | Model |  |
| period_nbr | integer | Period |  |
| lines_id | one2many | Subscription Lines |  |
| name | char | Name |  |
| date_start | date | Start Date |  |
| period_total | integer | Number of Periods |  |
| state | selection | State |  |
| period_type | selection | Period Type |  |
| ref | char | Reference |  |

---
## Módulo: Subscription Compute (`account.subscription.generate`)
**Sugerencia Tabla:** `fi_account_subscription_generate`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| date | date | Date |  |

---
## Módulo: Account Subscription Line (`account.subscription.line`)
**Sugerencia Tabla:** `fi_account_subscription_line`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| date | date | Date |  |
| subscription_id | many2one | Subscription |  |
| move_id | many2one | Entry |  |

---
## Módulo: account.tax (`account.tax`)
**Sugerencia Tabla:** `fi_account_tax`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| domain | char | Domain | This field is only used if you develop your own module allowing developers to create specific taxes in a custom domain. |
| ref_tax_code_id | many2one | Refund Tax Code | Use this code for the VAT declaration. |
| sequence | integer | Sequence | The sequence field is used to order the tax lines from the lowest sequences to the higher ones. The order is important if you have a tax with several tax children. In this case, the evaluation order is important. |
| account_paid_id | many2one | Refund Tax Account |  |
| base_sign | float | Base Code Sign | Usually 1 or -1. |
| apply_budget | boolean | Afectar Presupuesto? |  |
| child_depend | boolean | Tax on Children | Set if the tax computation is based on the computation of child taxes rather than on the total amount. |
| include_base_amount | boolean | Included in base amount | Indicates if the amount of tax must be included in the base amount for the computation of the next taxes |
| account_id | many2one | Cta. por Pagar Fondo Tercero |  |
| ref_base_code_id | many2one | Refund Base Code | Use this code for the VAT declaration. |
| company_id | many2one | Company |  |
| tax_code_id | many2one | Account Tax Code | Use this code for the VAT declaration. |
| parent_id | many2one | Parent Tax Account |  |
| tax_company_id | many2one | SRI Partner | Este partner se aplicará en asiento contables de facturas |
| python_compute_inv | text | Python Code (reverse) |  |
| ref_tax_sign | float | Tax Code Sign | Usually 1 or -1. |
| type | selection | Tax Type | The computation method for the tax amount. |
| ref_base_sign | float | Base Code Sign | Usually 1 or -1. |
| description | char | Tax Code |  |
| tax_group | selection | Grupo |  |
| child_ids | one2many | Child Tax Accounts |  |
| type_tax_use | selection | Tax Application |  |
| base_code_id | many2one | Account Base Code | Use this code for the VAT declaration. |
| python_compute | text | Python Code |  |
| porcentaje | char | Porcentaje |  |
| active | boolean | Active | If the active field is set to False, it will allow you to hide the tax without removing it. |
| applicable_type | selection | Applicability | If not applicable (computed through a Python code), the tax won't appear on the invoice. |
| tax_map_ids | one2many | Cuentas Contables |  |
| name | char | Tax Name | This name will be displayed on reports |
| account_collected_id | many2one | Invoice Tax Account |  |
| budget | selection | Aplicacion Presupuestaria. |  |
| amount | float | Amount | For taxes of type percentage, enter % ratio between 0-1. |
| python_applicable | text | Python Code |  |
| tax_sign | float | Tax Code Sign | Usually 1 or -1. |
| price_include | boolean | Tax Included in Price | Check this if the price you use on the product and invoices includes this tax. |

---
## Módulo: Tax Code (`account.tax.code`)
**Sugerencia Tabla:** `fi_account_tax_code`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| info | text | Description |  |
| code | char | Case Code |  |
| name | char | Tax Case Name |  |
| sequence | integer | Sequence | Determine the display order in the report 'Accounting \ Reporting \ Generic Reporting \ Taxes \ Taxes Report' |
| sum | float | Year Sum |  |
| child_ids | one2many | Child Codes |  |
| company_id | many2one | Company |  |
| sign | float | Coefficent for parent | You can specify here the coefficient that will be used when consolidating the amount of this case into its parent. For example, set 1/-1 if you want to add/substract it. |
| notprintable | boolean | Not Printable in Invoice | Check this box if you don't want any VAT related to this Tax Code to appear on invoices |
| parent_id | many2one | Parent Code |  |
| line_ids | one2many | Lines |  |
| sum_period | float | Period Sum |  |

---
## Módulo: Tax Code Template (`account.tax.code.template`)
**Sugerencia Tabla:** `fi_account_tax_code_template`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| info | text | Description |  |
| code | char | Case Code |  |
| name | char | Tax Case Name |  |
| child_ids | one2many | Child Codes |  |
| sign | float | Sign For Parent |  |
| notprintable | boolean | Not Printable in Invoice | Check this box if you don't want any VAT related to this Tax Code to appear on invoices |
| parent_id | many2one | Parent Code |  |

---
## Módulo: Account tax chart (`account.tax.chart`)
**Sugerencia Tabla:** `fi_account_tax_chart`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| period_id | many2one | Period |  |
| target_move | selection | Target Moves |  |

---
## Módulo: account.tax.map (`account.tax.map`)
**Sugerencia Tabla:** `fi_account_tax_map`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| account_id2 | many2one | Cta. Fondo Teceros |  |
| budget | char | Partida |  |
| account_id | many2one | Cta. x Pagar |  |
| tax_id | many2one | Impuesto |  |

---
## Módulo: account.tax.template (`account.tax.template`)
**Sugerencia Tabla:** `fi_account_tax_template`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| domain | char | Domain | This field is only used if you develop your own module allowing developers to create specific taxes in a custom domain. |
| ref_tax_code_id | many2one | Refund Tax Code | Use this code for the VAT declaration. |
| sequence | integer | Sequence | The sequence field is used to order the taxes lines from lower sequences to higher ones. The order is important if you have a tax that has several tax children. In this case, the evaluation order is important. |
| base_sign | float | Base Code Sign | Usually 1 or -1. |
| child_depend | boolean | Tax on Children | Set if the tax computation is based on the computation of child taxes rather than on the total amount. |
| include_base_amount | boolean | Include in Base Amount | Set if the amount of tax must be included in the base amount before computing the next taxes. |
| ref_tax_sign | float | Tax Code Sign | Usually 1 or -1. |
| ref_base_code_id | many2one | Refund Base Code | Use this code for the VAT declaration. |
| name | char | Tax Name |  |
| tax_code_id | many2one | Tax Code | Use this code for the VAT declaration. |
| parent_id | many2one | Parent Tax Account |  |
| python_compute_inv | text | Python Code (reverse) |  |
| python_applicable | text | Python Code |  |
| type | selection | Tax Type |  |
| ref_base_sign | float | Base Code Sign | Usually 1 or -1. |
| description | char | Internal Name |  |
| tax_group | selection | Grupo |  |
| type_tax_use | selection | Tax Use In |  |
| base_code_id | many2one | Base Code | Use this code for the VAT declaration. |
| applicable_type | selection | Applicable Type | If not applicable (computed through a Python code), the tax won't appear on the invoice. |
| account_paid_id | many2one | Refund Tax Account |  |
| account_collected_id | many2one | Invoice Tax Account |  |
| chart_template_id | many2one | Chart Template |  |
| amount | float | Amount | For Tax Type percent enter % ratio between 0-1. |
| python_compute | text | Python Code |  |
| tax_sign | float | Tax Code Sign | Usually 1 or -1. |
| price_include | boolean | Tax Included in Price | Check this if the price you use on the product and invoices includes this tax. |

---
## Módulo: Treasury Analysis (`account.treasury.report`)
**Sugerencia Tabla:** `fi_account_treasury_report`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| company_id | many2one | Company |  |
| ending_balance | float | Ending Balance |  |
| credit | float | Credit |  |
| fiscalyear_id | many2one | Fiscalyear |  |
| period_id | many2one | Period |  |
| starting_balance | float | Starting Balance |  |
| debit | float | Debit |  |
| date | date | Beginning of Period Date |  |
| balance | float | Balance |  |

---
## Módulo: Account Unreconcile (`account.unreconcile`)
**Sugerencia Tabla:** `fi_account_unreconcile`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|

---
## Módulo: Account Unreconcile Reconcile (`account.unreconcile.reconcile`)
**Sugerencia Tabla:** `fi_account_unreconcile_reconcile`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|

---
## Módulo: Use model (`account.use.model`)
**Sugerencia Tabla:** `fi_account_use_model`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| model | many2many | Account Model |  |

---
## Módulo: Account Vat Declaration (`account.vat.declaration`)
**Sugerencia Tabla:** `fi_account_vat_declaration`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| chart_account_id | many2one | Chart of Account | Select Charts of Accounts |
| date_from | date | Start Date |  |
| based_on | selection | Based on |  |
| period_to | many2one | End Period |  |
| journal_ids | many2many | Journals |  |
| company_id | many2one | Company |  |
| filter | selection | Filter by |  |
| period_from | many2one | Start Period |  |
| fiscalyear_id | many2one | Fiscal Year | Keep empty for all open fiscal year |
| date_to | date | End Date |  |
| display_detail | boolean | Display Detail |  |
| chart_tax_id | many2one | Chart of Tax | Select Charts of Taxes |
| target_move | selection | Target Moves |  |

---
## Módulo: Accounting Voucher (`account.voucher`)
**Sugerencia Tabla:** `fi_account_voucher`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| comment | char | Counterpart Comment |  |
| line_cr_ids | one2many | Credits |  |
| date_due | date | Due Date |  |
| is_multi_currency | boolean | Multi Currency Voucher | Fields with internal purpose only that depicts if the voucher is a multi currency one or not |
| reference | char | Ref # | Transaction reference number. |
| line_dr_ids | one2many | Debits |  |
| number | char | Number |  |
| company_id | many2one | Company |  |
| currency_id | many2one | Currency |  |
| internal_type | selection | Tipo Interno |  |
| doc_reference | char | Doc. Referencia |  |
| narration | text | Notes |  |
| extra_type | char | Tipo Anticipos |  |
| partner_id | many2one | Partner |  |
| payment_rate | float | Exchange Rate | The specific rate that will be used, in this voucher, between the selected currency (in 'Payment Rate Currency' field)  and the voucher currency. |
| payment_rate_currency_id | many2one | Payment Rate Currency |  |
| paid_amount_in_company_currency | float | Paid Amount in Company Currency |  |
| pay_now | selection | Payment |  |
| writeoff_acc_id | many2one | Counterpart Account |  |
| move_ids | one2many | Journal Items |  |
| state | selection | State |  * The 'Draft' state is used when a user is encoding a new and unconfirmed Voucher.                          * The 'Pro-forma' when voucher is in Pro-forma state,voucher does not have an voucher number.                          * The 'Posted' state is used when user create voucher,a voucher number is generated and voucher entries are created in account                          * The 'Cancelled' state is used when user cancel voucher. |
| pre_line | boolean | Previous Payments ? |  |
| type | selection | Default Type |  |
| thirdparty_name | char | A nombre de |  |
| thirdparty | boolean | Girado a otra persona ? |  |
| payment_option | selection | Payment Difference | This field helps you to choose what you want to do with the eventual difference between the paid amount and the sum of allocated amounts. You can either choose to keep open this difference on the partner's account, or reconcile it with the payment(s) |
| account_id | many2one | Account |  |
| certificate_id | many2one | Compromiso presupuestario |  |
| paid | boolean | Paid | The Voucher has been totally paid. |
| pay_states | boolean | Pagado |  |
| ind_pay_doc | boolean | Tipo doc |  |
| period_id | many2one | Period |  |
| date_ind | boolean | Fecha Generacion |  |
| date | date | Date | Effective date for accounting entries |
| move_id | many2one | Account Entry |  |
| tax_id | many2one | Tax | Only for tax excluded from price |
| audit | boolean | To Review | Check this box if you are unsure of that journal entry and if you want to note it as 'to be reviewed' by an accounting expert. |
| tax_amount | float | Tax Amount |  |
| name | char | Memo |  |
| writeoff_amount | float | Difference Amount | Computed as the difference between the amount stated in the voucher and the sum of allocation on the voucher lines. |
| analytic_id | many2one | Write-Off Analytic Account |  |
| journal_id | many2one | Journal |  |
| amount | float | Total |  |
| line_ids | one2many | Voucher Lines |  |
| rule_id | many2one | Regla Salarial |  |

---
## Módulo: Voucher Lines (`account.voucher.line`)
**Sugerencia Tabla:** `fi_account_voucher_line`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| date_due | date | Due Date |  |
| reconcile | boolean | Full Reconcile |  |
| date_original | date | Date |  |
| move_line_id | many2one | Journal Item |  |
| type | selection | Dr/Cr |  |
| untax_amount | float | Untax Amount |  |
| company_id | many2one | Company |  |
| name | char | Description |  |
| currency_id | many2one | Currency |  |
| account_analytic_id | many2one | Analytic Account |  |
| amount | float | Amount |  |
| budget_id | many2one | Partida Presupuestaria |  |
| type_move | char | Tipo Movimiento |  |
| amount_original | float | Original Amount |  |
| voucher_id | many2one | Voucher |  |
| partner_id | many2one | Partner |  |
| amount_unreconciled | float | Open Balance |  |
| account_id | many2one | Account |  |

---
## Módulo: Account voucher unreconcile (`account.voucher.unreconcile`)
**Sugerencia Tabla:** `fi_account_voucher_unreconcile`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| remove | boolean | Want to remove accounting entries too ? |  |

---
## Módulo: ajeno.budget (`ajeno.budget`)
**Sugerencia Tabla:** `fi_ajeno_budget`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| line_ids | one2many | Detalle |  |
| name | many2one | Presupuesto |  |
| porcentaje | integer | Porcentaje Comision |  |

---
## Módulo: ajeno.budget.line (`ajeno.budget.line`)
**Sugerencia Tabla:** `fi_ajeno_budget_line`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| beneficiario | float | Entrega % Beneficiario |  |
| total | float | Total |  |
| name | many2one | Cuenta |  |
| a_id | many2one | Fondo Ajeno |  |
| prevista | float | Recaudacion Prevista |  |
| comision | float | Comision % por recaudacion |  |
| porcentaje | integer | Porcentaje Comision |  |
| total_2 | float | Total |  |
| inicial_caja | float | Saldo Inicial Caja |  |

---
## ⚠️ ERROR EN MÓDULO: ajusta.budget
> El sistema reportó: <Fault warning -- Object Error

Object ajusta.budget doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: asset.actividad
> El sistema reportó: <Fault warning -- Object Error

Object asset.actividad doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: asset.area
> El sistema reportó: <Fault warning -- Object Error

Object asset.area doesn't exist: ''>

---
## Módulo: Assets Analysis (`asset.asset.report`)
**Sugerencia Tabla:** `fi_asset_asset_report`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| asset_id | many2one | Asset |  |
| asset_category_id | many2one | Asset category |  |
| name | char | Year |  |
| move_check | boolean | Posted |  |
| gross_value | float | Gross Amount |  |
| depreciation_date | date | Depreciation Date |  |
| unposted_value | float | Unposted Amount |  |
| company_id | many2one | Company |  |
| state | selection | State |  |
| depreciation_value | float | Amount of Depreciation Lines |  |
| purchase_date | date | Purchase Date |  |
| nbr | integer | # of Depreciation Lines |  |
| posted_value | float | Posted Amount |  |
| partner_id | many2one | Partner |  |

---
## ⚠️ ERROR EN MÓDULO: asset.asset.subcateg
> El sistema reportó: <Fault warning -- Object Error

Object asset.asset.subcateg doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: asset.deprecia
> El sistema reportó: <Fault warning -- Object Error

Object asset.deprecia doesn't exist: ''>

---
## Módulo: asset.depreciation.confirmation.wizard (`asset.depreciation.confirmation.wizard`)
**Sugerencia Tabla:** `fi_asset_depreciation_confirmation_wizard`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| period_id | many2one | Period | Choose the period for which you want to automatically post the depreciation lines of running assets |

---
## ⚠️ ERROR EN MÓDULO: asset.destino
> El sistema reportó: <Fault warning -- Object Error

Object asset.destino doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: asset.direccion
> El sistema reportó: <Fault warning -- Object Error

Object asset.direccion doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: asset.estructura
> El sistema reportó: <Fault warning -- Object Error

Object asset.estructura doesn't exist: ''>

---
## Módulo: Modify Asset (`asset.modify`)
**Sugerencia Tabla:** `fi_asset_modify`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| method_number | integer | Number of Depreciations |  |
| note | text | Notes |  |
| method_period | integer | Period Length |  |
| name | char | Reason |  |
| method_end | date | Ending date |  |

---
## ⚠️ ERROR EN MÓDULO: asset.motivo
> El sistema reportó: <Fault warning -- Object Error

Object asset.motivo doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: asset.no.bienes
> El sistema reportó: <Fault warning -- Object Error

Object asset.no.bienes doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: asset.seccion
> El sistema reportó: <Fault warning -- Object Error

Object asset.seccion doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: asset.subseccion
> El sistema reportó: <Fault warning -- Object Error

Object asset.subseccion doesn't exist: ''>

---
## Módulo: budget.budget (`budget.budget`)
**Sugerencia Tabla:** `fi_budget_budget`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| code | char | Código |  |
| name | char | Presupuesto |  |
| budget_lines | one2many | Detalle de Presupuesto |  |
| date_end | date | Fecha Fin |  |
| date_start | date | Fecha Inicio |  |
| state | selection | Estado |  |
| poa_id | many2one | POA |  |
| department_id | many2one | Departamento |  |

---
## Módulo: Certificados Presupuestarios (`budget.certificate`)
**Sugerencia Tabla:** `fi_budget_certificate`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| iva | float | Total Iva | Este valor es unicamente informativo, se utiliza para el registro contable del IVA |
| number | char | Número de Compromiso |  |
| date | date | Fecha de Emisión |  |
| fiscalyear_id | many2one | Anio Fiscal |  |
| amount_commited | float | Total Comprometido |  |
| partner_id | many2one | Proveedor |  |
| message_ids | one2many | Messages |  |
| ref_doc | char | Ref. Docmto |  |
| user_id | many2one | Creado por: |  |
| solicitant_id | many2one | Solicitado por: |  |
| state | selection | Estado |  |
| project_id | many2one | Proyecto |  |
| department_id | many2one | Dirección / Coordinación |  |
| amount_certified | float | Total Certificado |  |
| period_id | many2one | Periodo |  |
| budget_type | selection | Aplicacion Presupuestaria. |  |
| revisado | boolean | Revisado?? |  |
| active | boolean | Activo |  |
| amount_total | float | Total Solicitado |  |
| payment_id | many2one | Orden de pago |  |
| name | char | Nro. de certificado |  |
| task_id | many2one | Tarea |  |
| date_confirmed | date | Fecha de Certificación |  |
| notes | text | Notas |  |
| date_commited | date | Fecha de Compromiso |  |
| item2_ids | one2many | Detalle Reajuste |  |
| tipo_aux | selection | Tipo Interno |  |
| migrado | boolean | Migrado |  |
| log_repetido | char | Log Partidas Repetidas |  |
| line_ids | one2many | Detalle |  |

---
## Módulo: budget.certificate.line (`budget.certificate.line`)
**Sugerencia Tabla:** `fi_budget_certificate_line`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| code | char | Codigo |  |
| amount_commited | float | Monto Comprometido |  |
| tipo_invoice | selection | Tipo |  |
| budget_disponible | float | Saldo Por Comprometer |  |
| partner_id | many2one | Proveedor |  |
| budget_disponible_certificado | float | Saldo Por Certificar |  |
| name_aux | char | Documento |  |
| state | char | Estado |  |
| project_id | many2one | Proyecto |  |
| agrega_iva | boolean | Agrega Iva | Si marca este campo el sistema automaticamente agregara el valor del iva |
| budget_post | many2one | Partida Catalogo |  |
| amount_certified | float | Monto Certificado |  |
| certificate_id | many2one | Certificado |  |
| amount_paid | float | Monto Pagado |  |
| program_id | many2one | Programa |  |
| budget_id_aux | many2one | Partida Mayor |  |
| budget_accrued | float | Devengado |  |
| period_id | many2one | Periodo Compromiso |  |
| financia_id | many2one | Cuenta Financiera |  |
| active | boolean | Activo |  |
| name | char | Partida |  |
| task_id | many2one | Actividad |  |
| amount | float | Monto Solicitado |  |
| date_commited | date | Fecha |  |
| migrado | boolean | Migrado |  |
| budget_paid | float | Pagado |  |
| budget_id | many2one | Partida |  |

---
## Módulo: Cierre Presupuestario (`budget.cierre`)
**Sugerencia Tabla:** `fi_budget_cierre`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| year_ant_id | many2one | Periodo Cerrar |  |
| year_id | many2one | Periodo Planificacion |  |
| valor | selection | Pasar valores |  |
| line_ids | one2many | Detalle Apertura |  |
| poa_id | many2one | Presupuesto |  |
| poa_ant_id | many2one | Presupuesto Cerrar |  |

---
## Módulo: budget.cierre.line (`budget.cierre.line`)
**Sugerencia Tabla:** `fi_budget_cierre_line`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| opcion | selection | Pasar valores |  |
| c_id | many2one | Cierre Presupuestos |  |
| project_id | many2one | Proyecto |  |

---
## ⚠️ ERROR EN MÓDULO: budget.concejo
> El sistema reportó: <Fault warning -- Object Error

Object budget.concejo doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: budget.concejo.line
> El sistema reportó: <Fault warning -- Object Error

Object budget.concejo.line doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: budget.distributivo
> El sistema reportó: <Fault warning -- Object Error

Object budget.distributivo doesn't exist: ''>

---
## Módulo: budget.estrategy (`budget.estrategy`)
**Sugerencia Tabla:** `fi_budget_estrategy`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| name | float | Partida |  |
| tipo | many2one | Tipo de Politica |  |
| p_id | many2one | Anual |  |
| program_id | many2one | Programa |  |
| estrategy_id | many2one | Politica Aplica |  |
| budget_id | many2one | Partida |  |
| poa_id | many2one | Presupuesto |  |

---
## Módulo: budget.financiamiento (`budget.financiamiento`)
**Sugerencia Tabla:** `fi_budget_financiamiento`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| code | char | Codigo |  |
| name | char | Codigo |  |
| tipo | selection | Tipo |  |
| sc | char | Desc Corta |  |
| desc_report | char | Descripcion Aplicacion del Gasto |  |
| desc | char | Descripcion |  |

---
## Módulo: Instancia de Partida presupuestaria (`budget.item`)
**Sugerencia Tabla:** `fi_budget_item`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| code | char | Código |  |
| reform_amount | float | Reformado |  |
| date_end | date | Fecha Fin |  |
| aux_tipo | char | Tipo Aplicacion |  |
| type_budget | char | Tipo presupuesto |  |
| traspaso_disminucion | float | Traspaso disminucion |  |
| request_amount | float | Solicitado |  |
| reserved_balance | float | Saldo x Certificar |  |
| paid_amount | float | Pagado |  |
| code_aux | char | Codigo Aux |  |
| date_start | date | Fecha inicio |  |
| code_report | char | Codigo reportes |  |
| suplemento | float | Suplemento |  |
| state | selection | Estado |  |
| project_id | many2one | Proyecto |  |
| commited_balance | float | Saldo x Comprometer |  |
| log_ids | one2many | Detalle Aplicacion |  |
| reduccion | float | Reduccion |  |
| avai_amount | float | Disponible |  |
| reforma_to_ids | one2many | Reforma para transferencias |  |
| budget_post_id | many2one | Partida |  |
| planned_amount | float | Asignación Inicial |  |
| program_id | many2one | Programa |  |
| request_ids | one2many | Documentos |  |
| reserved_amount | float | Certificado |  |
| devengado_amount | float | Devengado |  |
| financia_id | many2one | Cuenta Financiera |  |
| codif_amount | float | Codificado |  |
| traspaso_aumento | float | Traspaso aumento |  |
| name | char | Detalle |  |
| task_id | many2one | Actividad |  |
| devengado_balance | float | Saldo x Devengar |  |
| commited_amount | float | Comprometido |  |
| year_id | many2one | Anio Fiscal |  |
| devengado_sobregiro | boolean | Sobregirada devengado |  |
| budget_id | many2one | Presupuesto |  |
| reforma_ids | one2many | Reformas Aplicadas |  |
| poa_id | many2one | POA |  |
| department_id | many2one | Departamento |  |
| commited_sobregiro | boolean | Sobregirada codificado |  |

---
## Módulo: budget.item.log (`budget.item.log`)
**Sugerencia Tabla:** `fi_budget_item_log`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| monto | float | Monto |  |
| date | date | Fecha |  |
| aplicacion | char | Aplicacion |  |
| budget_log_id | many2one | Presupuesto |  |

---
## Módulo: Instancia de Partida presupuestaria migrada (`budget.item.migrated`)
**Sugerencia Tabla:** `fi_budget_item_migrated`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| code | char | Cod. Partida |  |
| reform_amount | float | Reforma |  |
| budget_item_id | many2one | Budget item |  |
| paid_amount | float | Devengado |  |
| elimina | boolean | Permitir Eliminar |  |
| program_code | char | codigo programa |  |
| commited_balance | float | Saldo x Comprometer |  |
| avai_amount | float | Saldo Disponible |  |
| certificate_id | many2one | Certificado |  |
| budget_post_id | many2one | Partida |  |
| planned_amount | float | Asignación Inicial |  |
| devengado_amount | float | Devengado |  |
| is_pronto | boolean | Pronto Pago |  |
| financia_id | many2one | Cta. Financiera |  |
| date | date | Fecha |  |
| move_id | many2one | Comprobante |  |
| desc | char | Descripcion |  |
| name | char | Denominación |  |
| move_line_id | many2one | Linea Comprobante |  |
| devengado_balance | float | Saldo x Devengar |  |
| commited_amount | float | Comprometido |  |
| type_budget | char | Tipo |  |
| codif_amount | float | Codificado |  |

---
## ⚠️ ERROR EN MÓDULO: budget.lotaip
> El sistema reportó: <Fault warning -- Object Error

Object budget.lotaip doesn't exist: ''>

---
## Módulo: budget.move (`budget.move`)
**Sugerencia Tabla:** `fi_budget_move`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| saldo_pay | float | Saldo por pagar |  |
| devengado | float | Devengado |  |
| saldo_comp | float | Saldo por comprometer |  |
| date_end | date | Fecha Hasta |  |
| date_start | date | Fecha desde |  |
| program_id | many2one | Programa |  |
| reformas | float | Reformas |  |
| pagado | float | Pagado |  |
| all_post | boolean | Todas las partidas |  |
| is_commited | boolean | Incluye Compromisos |  |
| datas | binary | Archivo |  |
| inicial | float | Inicial |  |
| line_ids | one2many | Detalle |  |
| comprometido | float | Comprometido |  |
| budget_id | many2one | Partida |  |
| poa_id | many2one | Presupuesto |  |
| project_id | many2one | Proyecto |  |
| partner_id | many2one | Beneficiario |  |
| codificado | float | Codificado |  |
| datas_fname | char | Nombre archivo |  |
| disponible | float | Disponible |  |

---
## Módulo: budget.move.line (`budget.move.line`)
**Sugerencia Tabla:** `fi_budget_move_line`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| seq | integer | Num. |  |
| b_id | many2one | Movimiento |  |
| certificate_id | many2one | Certificado |  |
| pagado | float | Pagado |  |
| comprometido | float | Comprometido |  |
| move_id | char | # Comprobante Contable |  |
| devengado | float | Devengado |  |
| date | date | Fecha Compromiso |  |
| partner_id | many2one | Beneficiario |  |
| cp_id | char | # Compromiso |  |
| desc | text | Concepto |  |

---
## ⚠️ ERROR EN MÓDULO: budget.pac
> El sistema reportó: <Fault warning -- Object Error

Object budget.pac doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: budget.pac.line
> El sistema reportó: <Fault warning -- Object Error

Object budget.pac.line doesn't exist: ''>

---
## Módulo: budget.poa (`budget.poa`)
**Sugerencia Tabla:** `fi_budget_poa`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| date_start | date | Fecha Inicio |  |
| name | char | Descripcion |  |
| date_end | date | Fecha Fin |  |
| total_presupuesto | float | Total Presupuesto |  |
| budget_ids | one2many | Detalle |  |
| state | selection | Estado |  |
| funcion_ids | one2many | Detalle Funciones |  |
| programa_ids | one2many | Programas |  |

---
## Módulo: budget.poa.funcion (`budget.poa.funcion`)
**Sugerencia Tabla:** `fi_budget_poa_funcion`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| total | float | Total |  |
| p_id | many2one | Presupuesto |  |
| funcion | char | Funcion |  |

---
## Módulo: budget.politica.anual (`budget.politica.anual`)
**Sugerencia Tabla:** `fi_budget_politica_anual`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| line_ids | one2many | Detalle |  |
| poa_id | many2one | Presupuesto |  |
| project_id | many2one | Proyecto |  |
| program_id | many2one | Programa |  |

---
## Módulo: budget.post (`budget.post`)
**Sugerencia Tabla:** `fi_budget_post`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| nivel | integer | Nivel |  |
| aux_recaudacion | boolean | Auxiliar para recaudacion? |  |
| internal_type | selection | Tipo |  |
| name | char | Partida |  |
| tipo | selection | Tipo |  |
| codigo_catalogo | char | Cod. Catalogo |  |
| code_aux | char | Código |  |
| venta | boolean | Venta |  |
| child_ids | one2many | Hijos |  |
| year_id | many2one | Anio |  |
| is_pac | boolean | Reporte PAC |  |
| cingreso | many2one | Cuenta de ingreso |  |
| parent_id | many2one | Partida Mayor/padre |  |
| activo | boolean | Activo |  |
| code | char | Código |  |
| budget_type_id | many2one | Tipo de Aplicación |  |
| publicado | boolean | Publicado PAC? |  |
| is_emision | boolean | Con Emision | Si marca este campo el sistema hara devengado y pago |
| cxc | many2one | Cuenta por cobrar |  |
| tipo_pac | selection | Tipo |  |

---
## Módulo: budget.reajuste (`budget.reajuste`)
**Sugerencia Tabla:** `fi_budget_reajuste`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| monto | float | Monto Extra | Ingrese aqui el valor adicional |
| date | date | Fecha |  |
| name | many2one | Partida |  |
| certificate_id | many2one | Certificado |  |

---
## Módulo: Reformas Presupuestarias (`budget.reform`)
**Sugerencia Tabla:** `fi_budget_reform`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| type_transaction | selection | Tipo de Reforma |  |
| justification | text | Justificación Legal |  |
| request_date | date | Fecha de Solicitud |  |
| date_done | date | Fecha de Aplicación |  |
| task2_id | many2one | Actividad Destino |  |
| state | selection | Estado |  |
| program_id | many2one | Programa |  |
| name | char | Código |  |
| amount | float | Valor de Reforma | Valor de reforma a la partida presupuestaria, considerar el tipo de reforma. |
| type_budget | char | Tipo |  |
| budget_id | many2one | Partida Origen |  |
| amount_b2 | float | Disponible (Partida destino) |  |
| amount_b1 | float | Disponible (Partida origen) |  |
| project2_id | many2one | Proyecto Destino |  |
| project_id | many2one | Proyecto |  |
| task_id | many2one | Actividad |  |
| budget2_id | many2one | Partida Destino |  |

---
## Módulo: budget.reform.container (`budget.reform.container`)
**Sugerencia Tabla:** `fi_budget_reform_container`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| date | date | Fecha |  |
| line_ids | many2many | Detalle de reforma |  |
| name | char | Código |  |

---
## Módulo: Techos Presupuestarios (`budget.roof`)
**Sugerencia Tabla:** `fi_budget_roof`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| fy_id | many2one | Ejercicio Fiscal |  |
| date | date | Fecha de Aprobación |  |
| state | selection | Estado |  |
| detail_ids | one2many | Detalle de Techo Presupuestario |  |
| amount_total | float | Presupuesto Total |  |

---
## Módulo: Limites presupuestarios por departamento (`budget.roof.line`)
**Sugerencia Tabla:** `fi_budget_roof_line`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| fy_id | float | Ejercicio Fiscal |  |
| state | selection | Estado |  |
| limit_amount | float | Límite |  |
| roof_id | many2one | Techo Presupuestario |  |
| department_id | many2one | Dirección Coordinación |  |

---
## Módulo: budget.sobregiro (`budget.sobregiro`)
**Sugerencia Tabla:** `fi_budget_sobregiro`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| line_ids | one2many | Detalle |  |
| poa_id | many2one | Presupuesto |  |
| date_to | date | Fecha Hasta |  |

---
## Módulo: budget.sobregiro.line (`budget.sobregiro.line`)
**Sugerencia Tabla:** `fi_budget_sobregiro_line`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| code | char | Codigo |  |
| reform_amount | float | Reforma |  |
| sobregiro_devengado | float | Sobregiro Devengado |  |
| planned_amount | float | Asignacion Inicial |  |
| devengado_amount | float | Devengado |  |
| sobregiro_commited | float | Sobregiro Comprometido |  |
| commited_amount | float | Comprometido |  |
| s_id | many2one | Sobregiro |  |
| budget_id | many2one | Partida |  |
| codificado_amount | float | Codificado |  |
| name | char | Descripcion |  |

---
## Módulo: budget.user.type (`budget.user.type`)
**Sugerencia Tabla:** `fi_budget_user_type`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| code | char | Código |  |
| name | char | Aplicación Presupuestaria |  |

---
## ⚠️ ERROR EN MÓDULO: distributivo.budget
> El sistema reportó: <Fault warning -- Object Error

Object distributivo.budget doesn't exist: ''>

---
## Módulo: distributivo.budget.tthh (`distributivo.budget.tthh`)
**Sugerencia Tabla:** `fi_distributivo_budget_tthh`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| line_ids | one2many | Detalle Programa |  |
| poa_id | many2one | POA |  |
| name | many2one | Programa |  |

---
## Módulo: ejec.budget (`ejec.budget`)
**Sugerencia Tabla:** `fi_ejec_budget`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| devengado | float | Devengado |  |
| disponible | float | Disponible |  |
| date_end | date | Hasta |  |
| date_start | date | Desde |  |
| reformas | float | Reformas |  |
| pagado | float | Pagado |  |
| budget_id | many2one | Partida |  |
| inicial | float | Inicial |  |
| comprometido | float | Comprometido |  |
| line_ids | one2many | Detalle |  |
| poa_id | many2one | Presupuesto |  |
| codificado | float | Codificado |  |

---
## Módulo: ejec.budget.line (`ejec.budget.line`)
**Sugerencia Tabla:** `fi_ejec_budget_line`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| e_id | many2one | Partida |  |
| comprometido | float | Comprometido |  |
| pagado | float | Pagado |  |
| comprobante | char | Num. Comprobante |  |
| budget_id | char | Partida |  |
| date | date | Fecha |  |
| detalle | char | Detalle |  |

---
## Módulo: evaluacion.budget (`evaluacion.budget`)
**Sugerencia Tabla:** `fi_evaluacion_budget`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| nivel | integer | Nivel |  |
| date_from | date | Fecha Desde |  |
| datas_fname | char | Nombre archivo |  |
| date_to | date | Fecha Hasta |  |
| poa_id | many2one | Presupuesto |  |
| datas | binary | Archivo |  |

---
## Módulo: evaluacion.budgeti (`evaluacion.budgeti`)
**Sugerencia Tabla:** `fi_evaluacion_budgeti`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| nivel | integer | Nivel |  |
| date_from | date | Fecha Desde |  |
| datas_fname | char | Nombre archivo |  |
| date_to | date | Fecha Hasta |  |
| poa_id | many2one | Presupuesto |  |
| datas | binary | Archivo |  |

---
## ⚠️ ERROR EN MÓDULO: gt.account.asset.acta
> El sistema reportó: <Fault warning -- Object Error

Object gt.account.asset.acta doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: gt.account.asset.baja.masiva
> El sistema reportó: <Fault warning -- Object Error

Object gt.account.asset.baja.masiva doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: gt.account.asset.baja.masiva.det
> El sistema reportó: <Fault warning -- Object Error

Object gt.account.asset.baja.masiva.det doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: gt.account.asset.componente
> El sistema reportó: <Fault warning -- Object Error

Object gt.account.asset.componente doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: gt.account.asset.duplicar
> El sistema reportó: <Fault warning -- Object Error

Object gt.account.asset.duplicar doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: gt.account.asset.income
> El sistema reportó: <Fault warning -- Object Error

Object gt.account.asset.income doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: gt.account.asset.justificacion
> El sistema reportó: <Fault warning -- Object Error

Object gt.account.asset.justificacion doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: gt.account.asset.moves
> El sistema reportó: <Fault warning -- Object Error

Object gt.account.asset.moves doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: gt.account.asset.moves.relation
> El sistema reportó: <Fault warning -- Object Error

Object gt.account.asset.moves.relation doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: gt.account.asset.rbodega
> El sistema reportó: <Fault warning -- Object Error

Object gt.account.asset.rbodega doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: gt.account.asset.tipo.acta
> El sistema reportó: <Fault warning -- Object Error

Object gt.account.asset.tipo.acta doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: gt.account.asset.transaction
> El sistema reportó: <Fault warning -- Object Error

Object gt.account.asset.transaction doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.accion.personal
> El sistema reportó: <Fault warning -- Object Error

Object hr.accion.personal doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.accion.personal.nivel
> El sistema reportó: <Fault warning -- Object Error

Object hr.accion.personal.nivel doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.account.configuration
> El sistema reportó: <Fault warning -- Object Error

Object hr.account.configuration doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.advance.config
> El sistema reportó: <Fault warning -- Object Error

Object hr.advance.config doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.anual.projection
> El sistema reportó: <Fault warning -- Object Error

Object hr.anual.projection doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.anual.rent.tax
> El sistema reportó: <Fault warning -- Object Error

Object hr.anual.rent.tax doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.applicant
> El sistema reportó: <Fault warning -- Object Error

Object hr.applicant doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.base.configuration
> El sistema reportó: <Fault warning -- Object Error

Object hr.base.configuration doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.base.retention
> El sistema reportó: <Fault warning -- Object Error

Object hr.base.retention doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.base.retention.line
> El sistema reportó: <Fault warning -- Object Error

Object hr.base.retention.line doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.calendar.line
> El sistema reportó: <Fault warning -- Object Error

Object hr.calendar.line doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.capacitacion
> El sistema reportó: <Fault warning -- Object Error

Object hr.capacitacion doesn't exist: ''>

---
## Módulo: Contract (`hr.contract`)
**Sugerencia Tabla:** `fi_hr_contract`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| visa_expire | date | Visa Expire Date |  |
| wage | float | Wage | Basic Salary of the employee |
| employee_id | many2one | Employee |  |
| working_hours | many2one | Working Schedule |  |
| job_id | many2one | Job Title |  |
| type_id | many2one | Contract Type |  |
| visa_no | char | Visa No |  |
| date_end | date | End Date |  |
| trial_date_end | date | Trial End Date |  |
| date_start | date | Start Date |  |
| advantages | text | Advantages |  |
| permit_no | char | Work Permit No |  |
| trial_date_start | date | Trial Start Date |  |
| department_id | many2one | Department |  |
| notes | text | Notes |  |
| name | char | Contract Reference |  |

---
## ⚠️ ERROR EN MÓDULO: hr.contract.encargo
> El sistema reportó: <Fault warning -- Object Error

Object hr.contract.encargo doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.contract.nivel
> El sistema reportó: <Fault warning -- Object Error

Object hr.contract.nivel doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.contract.projection
> El sistema reportó: <Fault warning -- Object Error

Object hr.contract.projection doesn't exist: ''>

---
## Módulo: Contract Type (`hr.contract.type`)
**Sugerencia Tabla:** `fi_hr_contract_type`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| name | char | Contract Type |  |

---
## ⚠️ ERROR EN MÓDULO: hr.contract.type.type
> El sistema reportó: <Fault warning -- Object Error

Object hr.contract.type.type doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.contribution.register
> El sistema reportó: <Fault warning -- Object Error

Object hr.contribution.register doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.change.job
> El sistema reportó: <Fault warning -- Object Error

Object hr.change.job doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.dec4.export
> El sistema reportó: <Fault warning -- Object Error

Object hr.dec4.export doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.decimo.cuarto
> El sistema reportó: <Fault warning -- Object Error

Object hr.decimo.cuarto doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.decimo.cuarto.line
> El sistema reportó: <Fault warning -- Object Error

Object hr.decimo.cuarto.line doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.decimo.tercero
> El sistema reportó: <Fault warning -- Object Error

Object hr.decimo.tercero doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.decimo.tercero.line
> El sistema reportó: <Fault warning -- Object Error

Object hr.decimo.tercero.line doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.deduction
> El sistema reportó: <Fault warning -- Object Error

Object hr.deduction doesn't exist: ''>

---
## Módulo: hr.department (`hr.department`)
**Sugerencia Tabla:** `fi_hr_department`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| member_ids | one2many | Members |  |
| name | char | Department Name |  |
| child_ids | one2many | Child Departments |  |
| company_id | many2one | Company |  |
| note | text | Note |  |
| parent_id | many2one | Parent Department |  |
| complete_name | char | Name |  |
| manager_id | many2one | Manager |  |

---
## ⚠️ ERROR EN MÓDULO: hr.dept.line
> El sistema reportó: <Fault warning -- Object Error

Object hr.dept.line doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.doc.holidays
> El sistema reportó: <Fault warning -- Object Error

Object hr.doc.holidays doesn't exist: ''>

---
## Módulo: Employee (`hr.employee`)
**Sugerencia Tabla:** `fi_hr_employee`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| address_id | many2one | Working Address |  |
| code | char | Code |  |
| coach_id | many2one | Coach |  |
| resource_id | many2one | Resource |  |
| color | integer | Color Index |  |
| photo | binary | Photo |  |
| marital | selection | Marital Status |  |
| sinid | char | SIN No | Social Insurance Number |
| manager | boolean | Is a Manager |  |
| identification_id | char | Identification No |  |
| partner_id | many2one | unknown | Partner that is related to the current employee. Accounting transaction will be written on this partner belongs to employee. |
| children | integer | Number of Children |  |
| city | char | City |  |
| time_efficiency | float | Efficiency factor | This field depict the efficiency of the resource to complete tasks. e.g  resource put alone on a phase of 5 days with 5 tasks assigned to him, will show a load of 100% for this phase by default, but if we put a efficency of 200%, then his load will only be 50%. |
| user_id | many2one | User | Related user name for the resource to manage its access. |
| contract_id | many2one | Contract | Latest contract of the employee |
| work_phone | char | Work Phone |  |
| country_id | many2one | Nationality |  |
| company_id | many2one | Company |  |
| medic_exam | date | Medical Examination Date |  |
| bank_account_id | many2one | Bank Account Number | Employee bank salary account |
| parent_id | many2one | Manager |  |
| category_ids | many2many | Categories |  |
| vehicle | char | Company Vehicle |  |
| department_id | many2one | Department |  |
| otherid | char | Other Id |  |
| mobile_phone | char | Work Mobile |  |
| vehicle_distance | integer | Home-Work Distance | In kilometers |
| child_ids | one2many | Subordinates |  |
| birthday | date | Date of Birth |  |
| active | boolean | Active | If the active field is set to False, it will allow you to hide the resource record without removing it. |
| calendar_id | many2one | Working Time | Define the schedule of resource |
| work_email | char | Work E-mail |  |
| job_id | many2one | Job |  |
| work_location | char | Office Location |  |
| name | char | Name |  |
| gender | selection | Gender |  |
| notes | text | Notes |  |
| address_home_id | many2one | Home Address |  |
| passport_id | char | Passport No |  |
| contract_ids | one2many | Contracts |  |
| place_of_birth | char | Place of Birth |  |
| login | char | Login |  |
| ssnid | char | SSN No | Social Security Number |
| resource_type | selection | Resource Type |  |

---
## Módulo: Employee Category (`hr.employee.category`)
**Sugerencia Tabla:** `fi_hr_employee_category`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| child_ids | one2many | Child Categories |  |
| parent_id | many2one | Parent Category |  |
| complete_name | char | Name |  |
| name | char | Category |  |
| employee_ids | many2many | Employees |  |

---
## ⚠️ ERROR EN MÓDULO: hr.employee.course
> El sistema reportó: <Fault warning -- Object Error

Object hr.employee.course doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.employee.title
> El sistema reportó: <Fault warning -- Object Error

Object hr.employee.title doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.family.item
> El sistema reportó: <Fault warning -- Object Error

Object hr.family.item doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.he.register
> El sistema reportó: <Fault warning -- Object Error

Object hr.he.register doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.he.register.alone
> El sistema reportó: <Fault warning -- Object Error

Object hr.he.register.alone doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.he.register.alone.line
> El sistema reportó: <Fault warning -- Object Error

Object hr.he.register.alone.line doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.he.register.line
> El sistema reportó: <Fault warning -- Object Error

Object hr.he.register.line doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.hist.job
> El sistema reportó: <Fault warning -- Object Error

Object hr.hist.job doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.hist.wage
> El sistema reportó: <Fault warning -- Object Error

Object hr.hist.wage doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.holidays
> El sistema reportó: <Fault warning -- Object Error

Object hr.holidays doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.holidays.remaining.leaves.user
> El sistema reportó: <Fault warning -- Object Error

Object hr.holidays.remaining.leaves.user doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.holidays.status
> El sistema reportó: <Fault warning -- Object Error

Object hr.holidays.status doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.holidays.summary.dept
> El sistema reportó: <Fault warning -- Object Error

Object hr.holidays.summary.dept doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.holidays.summary.employee
> El sistema reportó: <Fault warning -- Object Error

Object hr.holidays.summary.employee doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.ie.head
> El sistema reportó: <Fault warning -- Object Error

Object hr.ie.head doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.ie.line
> El sistema reportó: <Fault warning -- Object Error

Object hr.ie.line doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.ir.head
> El sistema reportó: <Fault warning -- Object Error

Object hr.ir.head doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.ir.line
> El sistema reportó: <Fault warning -- Object Error

Object hr.ir.line doesn't exist: ''>

---
## Módulo: Job Description (`hr.job`)
**Sugerencia Tabla:** `fi_hr_job`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| requirements | text | Requirements |  |
| name | char | Job Name |  |
| employee_ids | one2many | Employees |  |
| description | text | Job Description |  |
| company_id | many2one | Company |  |
| state | selection | State |  |
| no_of_recruitment | float | Expected in Recruitment |  |
| expected_employees | float | Expected Employees | Required number of employees in total for that job. |
| no_of_employee | float | Number of Employees | Number of employees with that job. |
| department_id | many2one | Department |  |

---
## ⚠️ ERROR EN MÓDULO: hr.job.line
> El sistema reportó: <Fault warning -- Object Error

Object hr.job.line doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.last.job
> El sistema reportó: <Fault warning -- Object Error

Object hr.last.job doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.last.work
> El sistema reportó: <Fault warning -- Object Error

Object hr.last.work doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.liquidation.compute
> El sistema reportó: <Fault warning -- Object Error

Object hr.liquidation.compute doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.liquidation.line
> El sistema reportó: <Fault warning -- Object Error

Object hr.liquidation.line doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.marital.status
> El sistema reportó: <Fault warning -- Object Error

Object hr.marital.status doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.no.cobro
> El sistema reportó: <Fault warning -- Object Error

Object hr.no.cobro doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.novedad
> El sistema reportó: <Fault warning -- Object Error

Object hr.novedad doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.pago.rol
> El sistema reportó: <Fault warning -- Object Error

Object hr.pago.rol doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.pago.rol.line
> El sistema reportó: <Fault warning -- Object Error

Object hr.pago.rol.line doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.pago.terceros
> El sistema reportó: <Fault warning -- Object Error

Object hr.pago.terceros doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.pago.terceros.line
> El sistema reportó: <Fault warning -- Object Error

Object hr.pago.terceros.line doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.payroll.advance
> El sistema reportó: <Fault warning -- Object Error

Object hr.payroll.advance doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.payroll.advance.line
> El sistema reportó: <Fault warning -- Object Error

Object hr.payroll.advance.line doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.payroll.export
> El sistema reportó: <Fault warning -- Object Error

Object hr.payroll.export doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.payroll.structure
> El sistema reportó: <Fault warning -- Object Error

Object hr.payroll.structure doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.payroll.update.masive.wage
> El sistema reportó: <Fault warning -- Object Error

Object hr.payroll.update.masive.wage doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.payroll.update.wage
> El sistema reportó: <Fault warning -- Object Error

Object hr.payroll.update.wage doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.payslip
> El sistema reportó: <Fault warning -- Object Error

Object hr.payslip doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.payslip.account
> El sistema reportó: <Fault warning -- Object Error

Object hr.payslip.account doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.payslip.account.budget
> El sistema reportó: <Fault warning -- Object Error

Object hr.payslip.account.budget doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.payslip.account.direct
> El sistema reportó: <Fault warning -- Object Error

Object hr.payslip.account.direct doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.payslip.employees
> El sistema reportó: <Fault warning -- Object Error

Object hr.payslip.employees doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.payslip.input
> El sistema reportó: <Fault warning -- Object Error

Object hr.payslip.input doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.payslip.line
> El sistema reportó: <Fault warning -- Object Error

Object hr.payslip.line doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.payslip.run
> El sistema reportó: <Fault warning -- Object Error

Object hr.payslip.run doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.payslip.worked_days
> El sistema reportó: <Fault warning -- Object Error

Object hr.payslip.worked_days doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.projection.line
> El sistema reportó: <Fault warning -- Object Error

Object hr.projection.line doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.projection.max
> El sistema reportó: <Fault warning -- Object Error

Object hr.projection.max doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.quincena
> El sistema reportó: <Fault warning -- Object Error

Object hr.quincena doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.quincena.line
> El sistema reportó: <Fault warning -- Object Error

Object hr.quincena.line doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.quincena.line.line
> El sistema reportó: <Fault warning -- Object Error

Object hr.quincena.line.line doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.recruitment.degree
> El sistema reportó: <Fault warning -- Object Error

Object hr.recruitment.degree doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.recruitment.job2phonecall
> El sistema reportó: <Fault warning -- Object Error

Object hr.recruitment.job2phonecall doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.recruitment.partner.create
> El sistema reportó: <Fault warning -- Object Error

Object hr.recruitment.partner.create doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.recruitment.report
> El sistema reportó: <Fault warning -- Object Error

Object hr.recruitment.report doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.recruitment.source
> El sistema reportó: <Fault warning -- Object Error

Object hr.recruitment.source doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.recruitment.stage
> El sistema reportó: <Fault warning -- Object Error

Object hr.recruitment.stage doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.rent.tax
> El sistema reportó: <Fault warning -- Object Error

Object hr.rent.tax doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.rubro
> El sistema reportó: <Fault warning -- Object Error

Object hr.rubro doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.rule.input
> El sistema reportó: <Fault warning -- Object Error

Object hr.rule.input doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.salary.rule
> El sistema reportó: <Fault warning -- Object Error

Object hr.salary.rule doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.salary.rule.category
> El sistema reportó: <Fault warning -- Object Error

Object hr.salary.rule.category doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.sectorial.table
> El sistema reportó: <Fault warning -- Object Error

Object hr.sectorial.table doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.sectorial.table.line
> El sistema reportó: <Fault warning -- Object Error

Object hr.sectorial.table.line doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.sol.personal
> El sistema reportó: <Fault warning -- Object Error

Object hr.sol.personal doesn't exist: ''>

---
## Módulo: Pagos Varios (`hr.varios`)
**Sugerencia Tabla:** `fi_hr_varios`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| name | text | Descripcion |  |
| observaciones | char | Observaciones |  |
| state | selection | Estado |  |
| period_id | many2one | Periodo |  |
| archivo | binary | Archivo |  |
| line_ids | one2many | Detalle |  |
| total | float | Total |  |

---
## Módulo: Detalle Pagos Varios (`hr.varios.line`)
**Sugerencia Tabla:** `fi_hr_varios_line`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| name | many2one | Beneficiario |  |
| name_partner | char | unknown |  |
| varios_id | many2one | Pagos varios |  |
| monto | float | Valor |  |
| monto_anticipo | float | Monto Anticipo |  |
| descuento | float | Descuento |  |
| descontado_id | many2one | Empleado Descontado |  |
| period_id | many2one | Periodo |  |
| valor | float | Valor Total |  |

---
## ⚠️ ERROR EN MÓDULO: hr.vinculation
> El sistema reportó: <Fault warning -- Object Error

Object hr.vinculation doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.work.period
> El sistema reportó: <Fault warning -- Object Error

Object hr.work.period doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: hr.work.period.line
> El sistema reportó: <Fault warning -- Object Error

Object hr.work.period.line doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: import.asset
> El sistema reportó: <Fault warning -- Object Error

Object import.asset doesn't exist: ''>

---
## Módulo: Email Thread (`mail.thread`)
**Sugerencia Tabla:** `fi_mail_thread`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| message_ids | one2many | Messages |  |

---
## Módulo: nivel.budget (`nivel.budget`)
**Sugerencia Tabla:** `fi_nivel_budget`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| name | integer | Nivel |  |

---
## Módulo: pagar.sri (`pagar.sri`)
**Sugerencia Tabla:** `fi_pagar_sri`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| partner_id | many2one | Beneficiario |  |
| date_start | date | Fecha Inicio |  |
| bank_id | many2one | Banco |  |
| move_id | many2one | Comprobante Contable |  |
| opc | selection | Opcion |  |
| date | date | Fecha Corte |  |
| line_ids | one2many | Detalle |  |
| total_pago | float | Total A Pagar |  |
| cp_id | many2one | Documento presupuestario |  |

---
## Módulo: pagar.sri.line (`pagar.sri.line`)
**Sugerencia Tabla:** `fi_pagar_sri_line`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| pagar | boolean | Pagar |  |
| code | char | Code |  |
| account_id | many2one | Cuenta |  |
| move_line_id | many2one | Cuenta por pagar |  |
| ref | char | Referencia |  |
| i_id | many2one | Pagar |  |
| monto_pago | float | Monto a pagar |  |
| saldo | float | Saldo |  |
| budget_id | many2one | Partida |  |
| monto | float | Monto |  |
| desc | char | Descripcion |  |
| partner_id | many2one | Beneficiario |  |
| certificate_line_id | many2one | Certificado linea |  |
| move_id | many2one | Comprobante |  |
| name | char | Desc |  |

---
## Módulo: partner.account (`partner.account`)
**Sugerencia Tabla:** `fi_partner_account`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| p_id | many2one | Proveedor |  |
| account_id | many2one | Cuenta |  |
| name | char | Partida |  |

---
## Módulo: pay.fondo.sri (`pay.fondo.sri`)
**Sugerencia Tabla:** `fi_pay_fondo_sri`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| account_id2 | char | Cuenta Fondo Tercero/SRI |  |
| account_id | char | Cuenta por pagar |  |

---
## Módulo: Solicitud de Pago (`payment.request`)
**Sugerencia Tabla:** `fi_payment_request`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| user_id | many2one | Elaborado por |  |
| name | char | Solicitud de Pago No. |  |
| certificate_id | many2one | Certificacion Presupuestaria |  |
| amount_invoice | float | Monto (inc. IVA) |  |
| concepto | text | Concepto |  |
| date_request | datetime | Fecha Solicitud |  |
| type_doc | selection | Proceso |  |
| state | selection | Estado |  |
| observaciones | text | Observaciones |  |
| otra_fecha | boolean | Otra fecha |  |
| type_num | char | Convenio/Contrato No. |  |
| partner_id | many2one | Proveedor |  |
| emp_solicitante | many2one | Solicitante |  |

---
## Módulo: Analytic Entries by line (`project.account.analytic.line`)
**Sugerencia Tabla:** `fi_project_account_analytic_line`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| from_date | date | From |  |
| to_date | date | To |  |

---
## Módulo: project.budget.plan.wiz (`project.budget.plan.wiz`)
**Sugerencia Tabla:** `fi_project_budget_plan_wiz`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| wiz_id | many2one | Asistente |  |
| planned_amount | float | Monto |  |
| budget_id | many2one | Linea de Presupuesto planificado |  |
| name | char | Descripción |  |
| acc_budget_id | many2one | Partida Presupuestaria |  |

---
## Módulo: Trasferencia de valores entre partidas (`project.budget.transfer`)
**Sugerencia Tabla:** `fi_project_budget_transfer`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| budget_to_id | many2one | Partida Destino |  |
| budget_from_id | many2one | Partida Origen |  |
| name | char | Número |  |
| state | selection | Estado |  |
| amount | float | Valor a transferir |  |
| activity_from_id | many2one | Actividad Origen |  |
| project_from_id | many2one | Proyecto Origen |  |
| project_to_id | many2one | Proyecto Destino |  |
| activity_to_id | many2one | Actividad Destino |  |

---
## ⚠️ ERROR EN MÓDULO: purchase.config.infima
> El sistema reportó: <Fault warning -- Object Error

Object purchase.config.infima doesn't exist: ''>

---
## Módulo: purchase.config.wizard (`purchase.config.wizard`)
**Sugerencia Tabla:** `fi_purchase_config_wizard`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| default_method | selection | Default Invoicing Control Method |  |
| config_logo | binary | Image |  |

---
## Módulo: Purchase Order (`purchase.order`)
**Sugerencia Tabla:** `fi_purchase_order`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| origin | char | Source Document | Reference of the document that generated this purchase order request. |
| order_line | one2many | Order Lines |  |
| invoiced_rate | float | Invoiced |  |
| partner_address_id | many2one | Address |  |
| amount_net | float | Base Imponible - Desc | The amount after additional discount. |
| invoice_ids | many2many | Invoices | Invoices generated for a purchase order |
| date_order | date | Order Date | Date on which this document has been created. |
| partner_id | many2one | Supplier |  |
| invoiced | boolean | Invoiced & Paid | It indicates that an invoice has been paid |
| dest_address_id | many2one | Destination Address | Put an address if you want to deliver directly from the supplier to the customer.In this case, it will remove the warehouse link and set the customer location. |
| create_uid | many2one | Responsible |  |
| fiscal_position | many2one | Fiscal Position |  |
| amount_untaxed | float | Untaxed Amount | The amount without tax |
| location_id | many2one | Destination |  |
| company_id | many2one | Company |  |
| amount_tax | float | Taxes | The tax amount |
| state | selection | State | The state of the purchase order or the quotation request. A quotation is a purchase order in a 'Draft' state. Then the order has to be confirmed by the user, the state switch to 'Confirmed'. Then the supplier must confirm the order to change the state to 'Approved'. When the purchase order is paid and received, the state becomes 'Done'. If a cancel action occurs in the invoice or in the reception of goods, the state becomes in exception. |
| add_disc | float | Descuento(%) |  |
| pricelist_id | many2one | Pricelist | The pricelist sets the currency used for this purchase order. It also computes the supplier price for the selected products/quantities. |
| add_disc_amt | float | Descuento($) | The additional discount on untaxed amount. |
| warehouse_id | many2one | Warehouse |  |
| shipped_rate | float | Received |  |
| partner_ref | char | Supplier Reference |  |
| picking_ids | one2many | Picking List | This is the list of picking list that have been generated for this purchase |
| date_approve | date | Date Approved | Date on which purchase order has been approved |
| amount_total | float | Total | The total amount |
| name | char | Order Reference | unique number of the purchase order,computed automatically when the purchase order is created |
| notes | text | Notes |  |
| invoice_method | selection | Invoicing Control | Based on Purchase Order lines: place individual lines in 'Invoice Control > Based on P.O. lines' from where you can selectively create an invoice. Based on generated invoice: create a draft invoice you can validate later. Based on receptions: let you create an invoice when receptions are validated. |
| shipped | boolean | Received | It indicates that a picking has been done |
| validator | many2one | Validated by |  |
| minimum_planned_date | date | Expected Date | This is computed as the minimum scheduled date of all purchase order lines' products. |
| product_id | many2one | Product |  |

---
## Módulo: Purchase Order Merge (`purchase.order.group`)
**Sugerencia Tabla:** `fi_purchase_order_group`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|

---
## Módulo: Purchase Order Line (`purchase.order.line`)
**Sugerencia Tabla:** `fi_purchase_order_line`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| name | char | Description |  |
| product_uom | many2one | Product UOM |  |
| date_planned | date | Scheduled Date |  |
| order_id | many2one | Order Reference |  |
| price_unit | float | Unit Price |  |
| price_subtotal | float | Subtotal |  |
| company_id | many2one | Company |  |
| move_ids | one2many | Reservation |  |
| invoice_lines | many2many | Invoice Lines |  |
| state | selection | State |  * The 'Draft' state is set automatically when purchase order in draft state.                                         * The 'Confirmed' state is set automatically as confirm when purchase order in confirm state.                                         * The 'Done' state is set automatically when purchase order is set as done.                                         * The 'Cancelled' state is set automatically when user cancel purchase order. |
| product_id | many2one | Product |  |
| taxes_id | many2many | Taxes |  |
| move_dest_id | many2one | Reservation Destination |  |
| product_qty | float | Quantity |  |
| account_analytic_id | many2one | Analytic Account |  |
| date_order | date | Order Date |  |
| partner_id | many2one | Partner |  |
| notes | text | Notes |  |
| invoiced | boolean | Invoiced |  |

---
## Módulo: Purchase Order Line Make Invoice (`purchase.order.line_invoice`)
**Sugerencia Tabla:** `fi_purchase_order_line_invoice`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|

---
## ⚠️ ERROR EN MÓDULO: purchase.pac
> El sistema reportó: <Fault warning -- Object Error

Object purchase.pac doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: purchase.pac.line
> El sistema reportó: <Fault warning -- Object Error

Object purchase.pac.line doesn't exist: ''>

---
## Módulo: Purchases Orders (`purchase.report`)
**Sugerencia Tabla:** `fi_purchase_report`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| product_uom | many2one | Reference UoM |  |
| nbr | integer | # of Lines |  |
| partner_address_id | many2one | Address Contact Name |  |
| month | selection | Month |  |
| delay_pass | float | Days to Deliver |  |
| location_id | many2one | Destination |  |
| dest_address_id | many2one | Dest. Address Contact Name |  |
| price_standard | float | Products Value |  |
| user_id | many2one | Responsible |  |
| expected_date | date | Expected Date |  |
| partner_id | many2one | Supplier |  |
| company_id | many2one | Company |  |
| delay | float | Days to Validate |  |
| state | selection | Order State |  |
| pricelist_id | many2one | Pricelist |  |
| negociation | float | Purchase-Standard Price |  |
| price_average | float | Average Price |  |
| warehouse_id | many2one | Warehouse |  |
| date | date | Order Date | Date on which this document has been created |
| day | char | Day |  |
| date_approve | date | Date Approved |  |
| product_id | many2one | Product |  |
| price_total | float | Total Price |  |
| name | char | Year |  |
| validator | many2one | Validated By |  |
| category_id | many2one | Category |  |
| quantity | float | Quantity |  |

---
## ⚠️ ERROR EN MÓDULO: purchase.requisition
> El sistema reportó: <Fault warning -- Object Error

Object purchase.requisition doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: purchase.requisition.cancel
> El sistema reportó: <Fault warning -- Object Error

Object purchase.requisition.cancel doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: purchase.requisition.line
> El sistema reportó: <Fault warning -- Object Error

Object purchase.requisition.line doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: purchase.requisition.partner
> El sistema reportó: <Fault warning -- Object Error

Object purchase.requisition.partner doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: relate.invoice.asset
> El sistema reportó: <Fault warning -- Object Error

Object relate.invoice.asset doesn't exist: ''>

---
## Módulo: Receivable accounts (`report.account.receivable`)
**Sugerencia Tabla:** `fi_report_account_receivable`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| credit | float | Credit |  |
| balance | float | Balance |  |
| type | selection | Account Type |  |
| name | char | Week of Year |  |
| debit | float | Debit |  |

---
## Módulo: Report of the Sales by Account (`report.account.sales`)
**Sugerencia Tabla:** `fi_report_account_sales`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| product_id | many2one | Product |  |
| account_id | many2one | Account |  |
| month | selection | Month |  |
| currency_id | many2one | Currency |  |
| period_id | many2one | Force Period |  |
| amount_total | float | Total |  |
| quantity | float | Quantity |  |
| name | char | Year |  |

---
## Módulo: Report of the Sales by Account Type (`report.account_type.sales`)
**Sugerencia Tabla:** `fi_report_account_type_sales`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| product_id | many2one | Product |  |
| user_type | many2one | Account Type |  |
| month | selection | Month |  |
| currency_id | many2one | Currency |  |
| period_id | many2one | Force Period |  |
| amount_total | float | Total |  |
| quantity | float | Quantity |  |
| name | char | Year |  |

---
## Módulo: Cédula Presupuestaria (`report.budget.card`)
**Sugerencia Tabla:** `fi_report_budget_card`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| nivel | integer | Nivel |  |
| date_from | date | Fecha incicial |  |
| proy | boolean | Por Proyecto |  |
| nivel_aux | many2one | Nivel |  |
| mensajes | text | Mensajes |  |
| filename | char | Nombre |  |
| project | boolean | Por programa? |  |
| fiscalyear | many2one | Fiscal year |  |
| asig_inicial | boolean | Solo asignacion inicial? |  |
| datas | binary | Archivo |  |
| date_to | date | Fecha final |  |
| program_ids | many2many | Programas |  |
| poa_id | many2one | Presupuesto |  |
| project_id | many2one | Proyecto |  |
| data | binary | Archivo de Texto |  |
| tipo_nivel | selection | Tipo Nivel |  |
| datas_fname | char | Nombre archivo |  |
| tipo | char | Tipo |  |

---
## ⚠️ ERROR EN MÓDULO: rule.account
> El sistema reportó: <Fault warning -- Object Error

Object rule.account doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: sri.107
> El sistema reportó: <Fault warning -- Object Error

Object sri.107 doesn't exist: ''>

---
## ⚠️ ERROR EN MÓDULO: stock.account.move
> El sistema reportó: <Fault warning -- Object Error

Object stock.account.move doesn't exist: ''>

---
## Módulo: Validate Account Move (`validate.account.move`)
**Sugerencia Tabla:** `fi_validate_account_move`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| period_id | many2one | Period |  |
| journal_id | many2one | Journal |  |

---
## Módulo: Validate Account Move Lines (`validate.account.move.lines`)
**Sugerencia Tabla:** `fi_validate_account_move_lines`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|

---
## Módulo: wizard.budget.query (`wizard.budget.query`)
**Sugerencia Tabla:** `fi_wizard_budget_query`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| budget_id | many2one | Presupuesto |  |

---
## Módulo: wizard.budget.update (`wizard.budget.update`)
**Sugerencia Tabla:** `fi_wizard_budget_update`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| amount | float | Monto |  |

---
## Módulo: wizard.multi.charts.accounts (`wizard.multi.charts.accounts`)
**Sugerencia Tabla:** `fi_wizard_multi_charts_accounts`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| purchase_tax_rate | float | Purchase Tax(%) |  |
| complete_tax_set | boolean | Complete Set of Taxes | This boolean helps you to choose if you want to propose to the user to encode the sales and purchase rates or use the usual m2o fields. This last choice assumes that the set of tax defined for the chosen template is complete |
| code_digits | integer | # of Digits | No. of Digits to use for account code |
| chart_template_id | many2one | Chart Template |  |
| sale_tax | many2one | Default Sale Tax |  |
| company_id | many2one | Company |  |
| purchase_tax | many2one | Default Purchase Tax |  |
| seq_journal | boolean | Separated Journal Sequences | Check this box if you want to use a different sequence for each created journal. Otherwise, all will use the same sequence. |
| config_logo | binary | Image |  |
| sale_tax_rate | float | Sales Tax(%) |  |
| bank_accounts_id | one2many | Cash and Banks |  |

---
## Módulo: wizard.payment.sri (`wizard.payment.sri`)
**Sugerencia Tabla:** `fi_wizard_payment_sri`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| total | float | Total |  |
| period_id | many2one | Mes |  |
| total_marcado | float | Total A Pagar |  |
| date_payment | date | Fecha de Pago |  |
| journal_id | many2one | Banco |  |

---
## Módulo: Asistente para Pago de Impuestos (`wizard.payment.taxes`)
**Sugerencia Tabla:** `fi_wizard_payment_taxes`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| chart_account_id | many2one | Chart of Account | Select Charts of Accounts |
| certificate_id | many2one | Compromiso Presupuestario |  |
| date_from | date | Start Date |  |
| period_to | many2one | End Period |  |
| journal_id | many2one | Banco |  |
| company_id | many2one | Company |  |
| filter | selection | Filter by |  |
| period_from | many2one | Start Period |  |
| fiscalyear_id | many2one | Fiscal Year | Keep empty for all open fiscal year |
| date_to | date | End Date |  |
| date | date | Fecha de Pago |  |
| journal_ids | many2many | Journals |  |
| partner_id | many2one | Servicio de Rentas Internas |  |
| target_move | selection | Target Moves |  |

---
## Módulo: wizard.project.budget.task (`wizard.project.budget.task`)
**Sugerencia Tabla:** `fi_wizard_project_budget_task`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| available | float | Disponible |  |
| task_id | many2one | Actividad |  |
| expense_planned_ids | one2many | Detalle de Gasto |  |
| amount_projects | float | Presupuesto en Otros Proyectos |  |
| budget_planned_ids | one2many | Presupuestación |  |
| budget_project | float | Presupuestado Actual de Proyecto |  |
| fy_id | many2one | Ejercicio Fiscal |  |
| amount_total | float | Límite Presupuestario de Coordinación |  |
| task_amount | float | Presupuesto de Actividad |  |
| department_id | many2one | Coordinación Dirección |  |

---
## Módulo: wizard.update.budget.post (`wizard.update.budget.post`)
**Sugerencia Tabla:** `fi_wizard_update_budget_post`
| Campo | Tipo | Etiqueta | Ayuda |
|---|---|---|---|
| data | binary | Archivo CSV |  |

---
