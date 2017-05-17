
import math

# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Calcula parametros de um portfolio
# Parametros
# 	dt_start - data inicial
# 	dt_end - data final
# 	ls_symbols - lista de simbolos
# 	ls_allocs - lista com o percentual de cada simbolo no portfolio (deve somar 1)
# Retornos
#	vol - volatilidade do portfolio
#	daily_ret - media do retorno diariodo portfolio
#	sharpe - sharpe ratio do portfolio
#	cum_ret - retorno acumulado do portfolio
def simulate(dt_start, dt_end, ls_symbols, ls_allocs):
	if sum(ls_allocs) != 1:
		return 0, 0, 0, 0

	dt_timeofday = dt.timedelta(hours=16)
	ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
	days = len(ldt_timestamps)
	c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)
	ls_keys = ['close']
	ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
	d_data = dict(zip(ls_keys, ldf_data))
	
	for s_key in ls_keys:
		d_data[s_key] = d_data[s_key].fillna(method='ffill')
		d_data[s_key] = d_data[s_key].fillna(method='bfill')
		d_data[s_key] = d_data[s_key].fillna(1.0)

	na_price = d_data['close'].values

	na_normalized_price = na_price / na_price[0, :]

	na_normalized_price_port = np.dot(na_normalized_price, ls_allocs)
	cum_ret = na_normalized_price_port[-1]

	na_rets = na_normalized_price_port.copy()
	tsu.returnize0(na_rets)
	vol = np.std(na_rets)
	daily_ret = np.mean(na_rets)

	sharpe = math.sqrt(days) * daily_ret / vol

	return vol, daily_ret, sharpe, cum_ret

def main():
	''' Main Function'''

	# List of symbols and allocations
	ls_symbols = ["AXP", "HPQ", "IBM", "HNZ"]
	ls_allocs = [0.0, 0.0, 0.0, 1.0]

	# Start and End date of the charts
	dt_start = dt.datetime(2010, 1, 1)
	dt_end = dt.datetime(2010, 12, 31)

	vol, daily_ret, sharpe, cum_ret = simulate(dt_start, dt_end, ls_symbols, ls_allocs)

	print "Volatility: " + str(vol)
	print "Avg Daily Returns: " + str(daily_ret)
	print "Sharpe Ratio: " + str(sharpe)
	print "Cumulative Returns: " + str(cum_ret)


if __name__ == '__main__':
	main()
