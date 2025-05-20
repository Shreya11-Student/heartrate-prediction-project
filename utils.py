
import os
import string


def getTrainData():
	covid, non_covid, traindata = [], [], []
	for filename in os.listdir("train"):
	    if filename == "covid.txt":
		    with open('train/'+filename) as f:
			    covid = [(sym, 'Covid') for sym in f.readlines()]
	    if filename == "non_covid.txt":
		    with open('train/'+filename) as f:
			    non_covid = [(sym, 'Non Covid') for sym in f.readlines()]
	    

	for (words, category) in covid + non_covid:
		words_filtered = [e for e in words.split() if len(e) > 2]
		traindata.append((words_filtered, category))

	print(traindata)
	return traindata

def export(filename, data, p):
    with open(filename, p) as output:
    	for line in data:
        	output.write(line)
