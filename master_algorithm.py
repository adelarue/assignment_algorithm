# master_algorithm.py
# Runs all algorithm versions, computes score for each one, chooses best and outputs results

import calculate_metrics as metrics
import marriage_algorithm as marriage
import os

ENTRIES = ["A","B","C","D","E","F","G","H","J"]

######################
# Input to algorithm #
######################
# 1. name of file with freshmen preferences and genders
FRESHMEN_PREFERENCES = "finalfroshprefsGen.csv"
# 2. name of file with entry preferences
ENTRY_PREFERENCES = "entryprefs.csv"
# 3. name of file with vacancy numbers for each entry
ROOM_NUMBERS = "entryVacancies.csv"
######################

def read_input_and_results(resultFileName, froshPreferenceFileName, entryPreferenceFileName):
	"""
	Fetch results and inputs and outputs them in nice matrix form.

	Args:
		resultFileName          : string, name of file with freshman assignments to entries
		froshPreferenceFileName : string, name of file with freshmen preferences and genders
		entryPreferenceFileName : string, name of file with entry preferences
	Returns:
		freshmenPrefs           : list of lists (m * n matrix where m is the number of freshmen and n the number of entries) with rankings assigned to each entry by freshmen
		entryPrefs              : list of lists (m * n matrix where m is the number of freshmen and n the number of entries) with ratings assigned to each freshman by entries
		results                 : list where element i is the assigned entry of freshman i
	"""
	resultsFile = open(resultFileName, "r")
	entryPrefsFile = open(entryPreferenceFileName, "r")
	freshmenPrefsFile = open(froshPreferenceFileName, "r")
	results = []
	entryPrefs = []
	freshmenPrefs = []
	for line in freshmenPrefsFile:
		row = line.split(",")
		freshmenPrefs.append([])
		for i in xrange(1,len(row)-1):
			freshmenPrefs[-1].append(int(row[i]))
	for line in resultsFile:
		row = line.split(",")
		results.append(ENTRIES.index(row[1][0]))
	for line in entryPrefsFile:
		row = line.split(",")
		entryPrefs.append([])
		for i in xrange(1, len(row)):
			entryPrefs[-1].append(int(row[i]))
	return freshmenPrefs, entryPrefs, results

def run_all_LP_solutions():
	"""
	Run LP.jl file from the command line. Return None.
	"""
	os.system("julia LP.jl")
	return None

def choose_all_algorithms():
	"""
	Automatically writes all outputFileNames to a text file. This allows the LP.jl file to know what it needs to do.
	"""
	f = open("outputFiles.txt", "w")
	weights = range(60,81)
	cost_functions = ["simple", "quad", "simplequad", "simplerquad", "minimax"]
	for weight in weights:
		for cf in cost_functions:
			filename = "output_%d_" % weight
			filename = filename + cf
			f.write(filename + "_noMaxRank.csv\n")
			f.write(filename + "_maxRank.csv\n")
	f.write("output_marriage_noGreasing.csv\n")
	f.write("output_marriage_greasing.csv\n")
	f.close()
	return "outputFiles.txt"

def calculate_score(resultFileName, entryPreferenceFileName, froshPreferenceFileName):
	"""
	Calculate score of a particular algorithm, out of 100

	Args:
		resultFileName : string, name of file with results of algorithm
		entryPreferenceFileName : string, name of file with entry preferences
		froshPreferenceFileName : string, name of file with freshmen preferences

	Returns:
		score of algorithm results between 0 and 100
	"""
	freshmenPrefs, entryPrefs, results = read_input_and_results(resultFileName, froshPreferenceFileName, entryPreferenceFileName)
	freshmanHappiness = metrics.getFreshmenAverageRankingScore(freshmenPrefs, results)
	freshmanFairness = metrics.getFreshmenMaxRankingScore(freshmenPrefs, results)
	entryHappiness = metrics.getPercentageTopRankedFreshmenAllEntries(entryPrefs, results)
	# getEntryAverageRankingScore(entryPrefs, results)
	entryFairness = metrics.getEntryAverageRankingVarianceScore(entryPrefs, results)
	score = 0.5 * freshmanHappiness + 0.1 * freshmanFairness + 0.2 * entryHappiness + 0.2 * entryFairness
	return score

def assignFreshmenToEntries():
	"""
	Master function. Calls all algorithms, picks one with best score, deletes all other outputs.
	"""
	# Create file where all algorithms are named
	algorithmFileName = choose_all_algorithms()
	# Call Julia
	run_all_LP_solutions()
	# Run marriage algorithms
	marriage.run_marriage_algorithm(ROOM_NUMBERS, False, 0.55, FRESHMEN_PREFERENCES, ENTRY_PREFERENCES, True, "Outputs/output_marriage_greasing.csv")
	marriage.run_marriage_algorithm(ROOM_NUMBERS, False, 0.55, FRESHMEN_PREFERENCES, ENTRY_PREFERENCES, False, "Outputs/output_marriage_noGreasing.csv")
	# Find best result
	algorithmFile = open(algorithmFileName, "r")
	algorithmScores = {}
	# For each algorithm, compute score and place in dictionary
	for line in algorithmFile:
		resultFileName = line.rstrip()
		resultFileName = "Outputs/" + resultFileName
		algorithmScores[resultFileName] = calculate_score(resultFileName, ENTRY_PREFERENCES, FRESHMEN_PREFERENCES)
	# Find best score
	maxScore = 0
	bestAlgorithm = ""
	for key in algorithmScores.keys():
		print key, "\t", algorithmScores[key]
		if algorithmScores[key] > maxScore:
			maxScore = algorithmScores[key]
			bestAlgorithm = key
	# Go through output files, save correct one, delete all others
	for key in algorithmScores.keys():
		if key != bestAlgorithm:
			cmd = "rm " + key
			os.system(cmd)
		else:
			cmd = "mv " + key + " " + "final_output.csv"
			os.system(cmd)
	print maxScore
	print bestAlgorithm

if __name__ == "__main__":
	assignFreshmenToEntries()
