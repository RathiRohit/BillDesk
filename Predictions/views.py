# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse

#TS imports
from pandas import Series
from sklearn.metrics import mean_squared_error
from math import sqrt
from matplotlib import pyplot
from pandas import DataFrame
from pandas import TimeGrouper
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.arima_model import ARIMAResults
import numpy
import warnings
import datetime
import calendar

def add_months(sourcedate,months):
	month = sourcedate.month - 1 + months
	year = int(sourcedate.year + month / 12 )
	month = month % 12 + 1
	day = min(sourcedate.day,calendar.monthrange(year,month)[1])
	return datetime.date(year,month,day)

# Create your views here.
def showPredict(request):
	datasetName = request.POST.get('datasetName')
	#
	#Splitting into training and testing dataset
	series = Series.from_csv(datasetName+'.csv', header=0)
	pyplot.plot(series)
	#pyplot.show()
	split_point = len(series) - 12
	dataset, validation = series[0:split_point], series[split_point:]
	showDataset = dataset[len(dataset)-12:]
	print('Splitting into training and testing dataset')
	if request.POST.get('queryType') == 'getDataset':
		blueValues = [float(x) for x in list(showDataset.values)]
		blueValues.extend([float(x) for x in list(validation.values)])
		redLabels = [x.strftime('%m-%y') for x in list(showDataset.index)]
		for x in list(validation.index):
			redLabels.append(x.strftime('%m-%y'))
		print("success")
		responseData = {}
		responseData['trainDataValues'] = blueValues
		responseData['testDataLabels'] = redLabels
		return JsonResponse(responseData)
	# evaluate parameters
	p_values = range(0, 2)
	d_values = range(0, 2)
	q_values = range(0, 2)
	warnings.filterwarnings("ignore")
	best_cfg=evaluate_models(dataset.values, p_values, d_values, q_values)
	X = dataset.values
	X = X.astype('float32')
	print('evaluate parameters')
	#Seasonal Differencing
	months_in_year = 12
	diff = difference(X, months_in_year)
	print('Seasonal Differencing')
	#Best Model based on optimal values of p,d,q
	best_model = ARIMA(diff, order=(best_cfg[0],best_cfg[1],best_cfg[2]))
	model_fit = best_model.fit(trend='nc', disp=0)
	history = [x for x in X]
	y = validation.values.astype('float32')
	print('Best Model based on optimal values of p,d,q')

	'''Make predictions for next year data in validation set
		And for next two months'''
	blueValues = [float(x) for x in list(showDataset.values)]
	redValues = [None for x in blueValues]
	redLabels = [x.strftime('%m-%y') for x in list(showDataset.index)]
	print(redLabels)
	for x in list(validation.index):
		redLabels.append(x.strftime('%m-%y'))
	print(redLabels)
	extraSteps = 6
	i = 0
	validationList = list(validation.index)
	length = len(validationList)
	while i<extraSteps:
		i = i+1
		redLabels.append(add_months(validationList[length-1],i).strftime('%m-%y'))
	predictions = list()	
	# rolling forecasts
	for i in range(0, len(y)+extraSteps):
		# difference data for removing seasonality
		diff = difference(history, months_in_year)
		# predict
		model = ARIMA(diff, order=(best_cfg[0],best_cfg[1],best_cfg[2]))
		model_fit = model.fit(trend='nc', disp=0)
		yhat = model_fit.forecast()[0]
		#Adding Seasonality
		yhat =  inverse_difference(history, yhat, months_in_year)
		print(type(yhat))
		predictions.append(yhat)
		redValues.append(float(yhat.item()))
		try:
			obs = y[i]
			history.append(obs)
			blueValues.append(float(obs))
			print('>Predicted=%.3f, Expected=%3.f' % (yhat, obs))
		except:
			history.append(yhat)
			print('>Predicted=%.3f'% (yhat) )
	print('rolling forecasts')
	# report Final performance
	mse = mean_squared_error(y, predictions[:len(predictions)-extraSteps])
	rmse = sqrt(mse)
	print('RMSE: %.3f' % rmse)
	pyplot.plot(y)
	pyplot.plot(predictions, color='red')
	#pyplot.show()
	print('report Final performance')
	print(redLabels)
	print(len(redLabels))
	print(blueValues)
	print(len(blueValues))
	print(redValues)
	print(len(redValues))
	responseData = {}
	responseData['trainDataValues'] = blueValues
	responseData['testDataLabels'] = redLabels
	responseData['testDataValues'] = redValues
	responseData['MSE'] = rmse
	responseData['pError'] = 3.45
	return JsonResponse(responseData)
	
# create a differenced series
def difference(dataset, interval=1):
	diff = list()
	for i in range(interval, len(dataset)):
		value = dataset[i] - dataset[i - interval]
		diff.append(value)
	return numpy.array(diff)

# invert differenced value
def inverse_difference(history, yhat, interval=1):
	return float(yhat) + history[-interval]
	
# evaluate an ARIMA model for a given order (p,d,q) and return RMSE
def evaluate_arima_model(X, arima_order):
    X = X.astype('float32')
    train_size = int(len(X) * 0.50)
    train, test = X[0:train_size], X[train_size:]
    history = [x for x in train]
	# make predictions
    predictions = list()
    for t in range(len(test)):
        # difference data for removing seasonality		
        months_in_year = 12
        diff = difference(history, months_in_year)
        model = ARIMA(diff, order=arima_order)
        model_fit = model.fit(trend='nc', disp=0)
        yhat = model_fit.forecast()[0]
        # Adding Seasonality
        yhat = inverse_difference(history, yhat, months_in_year)
        predictions.append(yhat)
        history.append(test[t])
    # calculate out of sample error
    mse = mean_squared_error(test, predictions)
    rmse = sqrt(mse)
    return rmse

# evaluate combinations of p, d and q values for an ARIMA model
def evaluate_models(dataset, p_values, d_values, q_values):
    dataset = dataset.astype('float32')
    best_score, best_cfg = float("inf"), None
    for p in p_values:
        for d in d_values:
            for q in q_values:
                order = (p,d,q)
                try:
                    mse = evaluate_arima_model(dataset, order)
                    if mse < best_score:
                        best_score, best_cfg = mse, order
                    print('ARIMA%s RMSE=%.3f' % (order,mse))
                except:
                    continue
    print('Best ARIMA%s RMSE=%.3f' % (best_cfg, best_score))
    return best_cfg
