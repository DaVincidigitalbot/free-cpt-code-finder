# Payment Engine Reconciliation

Single source of truth: cpt_database.json estimated_medicare_payment, computed as total_rvu * CMS conversion factor 33.4009 when total_rvu is present

## Browser Harness Results
- 43632: Case Builder $1875.46 | wRVU 34.26 | lines [{'cpt': '43632', 'basePayment': 1875.46, 'totalRvu': 56.15, 'pay': 1875.46, 'effWrvu': 34.26}]
- 43633: Case Builder $1775.93 | wRVU 32.31 | lines [{'cpt': '43633', 'basePayment': 1775.93, 'totalRvu': 53.17, 'pay': 1775.93, 'effWrvu': 32.31}]
- 43621: Case Builder $2091.56 | wRVU 38.54 | lines [{'cpt': '43621', 'basePayment': 2091.56, 'totalRvu': 62.62, 'pay': 2091.56, 'effWrvu': 38.54}]
- 43870: Case Builder $673.70 | wRVU 11.15 | lines [{'cpt': '43870', 'basePayment': 673.7, 'totalRvu': 20.17, 'pay': 673.7, 'effWrvu': 11.15}]
- 44140: Case Builder $1250.20 | wRVU 22.03 | lines [{'cpt': '44140', 'basePayment': 1250.2, 'totalRvu': 37.43, 'pay': 1250.2, 'effWrvu': 22.03}]
- 43632+43870: Case Builder $2212.31 · MPPR applied | wRVU 45.41 | lines [{'cpt': '43632', 'basePayment': 1875.46, 'totalRvu': 56.15, 'pay': 1875.46, 'effWrvu': 34.26}, {'cpt': '43870', 'basePayment': 673.7, 'totalRvu': 20.17, 'pay': 336.85, 'effWrvu': 11.15}]
