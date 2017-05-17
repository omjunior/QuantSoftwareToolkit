
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

	na_price, days = read_closing(dt_start, dt_end, ls_symbols)

	na_normalized_price = na_price / na_price[0, :]

	return simulate_internal(na_normalized_price, ls_allocs, days)

# Optimize a portfolio by sharpe rate and return an allocation array
# along with all the statistics of simulate method
def optimize_sharpe(dt_start, dt_end, ls_symbols):

	na_price, days = read_closing(dt_start, dt_end, ls_symbols)

	na_normalized_price = na_price / na_price[0, :]

	max_sharpe = float('-inf')
	for i in range(11):
		for j in range(11-i):
			for k in range(11-i-j):
				alloc = [i/10.0, j/10.0, k/10.0, (10-i-j-k)/10.0]
				vol, daily_ret, sharpe, cum_ret = simulate_internal(na_normalized_price, alloc, 252)
				if (sharpe > max_sharpe):
					max_sharpe = sharpe
					opt_alloc = list(alloc)
					opt_vol = vol
					opt_daily_ret = daily_ret
					opt_cum_ret = cum_ret


	return opt_alloc, opt_vol, opt_daily_ret, max_sharpe, opt_cum_ret

# read closing values of ls_symbols and return a numpy array with the values
# and the number of market days
def read_closing(dt_start, dt_end, ls_symbols):
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

	return d_data['close'].values, days


# actually do the computations
def simulate_internal(na_normalized_price, ls_allocs, days):
	na_normalized_price_port = np.dot(na_normalized_price, ls_allocs)
	cum_ret = na_normalized_price_port[-1]

	na_rets = na_normalized_price_port.copy()
	tsu.returnize0(na_rets)

	vol = np.std(na_rets)
	daily_ret = np.mean(na_rets)
	sharpe = math.sqrt(days) * daily_ret / vol

	return vol, daily_ret, sharpe, cum_ret


# main
def main():
	''' Main Function'''

	# List of symbols and allocations
	ls_symbols = ["AAPL", "GLD", "GOOG", "XOM"]

	# Start and End date of the charts
	dt_start = dt.datetime(2011, 1, 1)
	dt_end = dt.datetime(2011, 12, 31)

	alloc, vol, daily_ret, sharpe, cum_ret = optimize_sharpe(dt_start, dt_end, ls_symbols)

	print "Allocation: " + str(alloc)
	print "Volatility: " + str(vol)
	print "Avg Daily Returns: " + str(daily_ret)
	print "Sharpe Ratio: " + str(sharpe)
	print "Cumulative Returns: " + str(cum_ret)


if __name__ == '__main__':
	main()
