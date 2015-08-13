# calculate_metrics.py
# Functions to calculate metrics
# Authored by Arthur J Delarue on 8/11/15

def getFreshmenAverageRankingScore(freshmenPrefs, results):
	"""
	Calculate freshmen average ranking score.

	Args:
		freshmenPrefs: list of lists, represents matrix of dimensions (nFreshmen, nEntries) where entry (i,j) is the ranking given by freshman i to entry j
		results: list of length nFreshmen, such that entry i is the entry that freshman i was assigned to (0:A, 1:B, etc.)

	Returns:
		(9 - average ranking given by freshmen to assigned entry)/8 * 100
	"""
	total_rankings = 0
	for (i,result) in enumerate(results):
		total_rankings += freshmenPrefs[i][result]
	average_ranking = float(total_rankings)/len(results)
	return (9-average_ranking)/8 * 100

def getPercentageFreshmenInTopThree(freshmenPrefs, results):
	"""
	Calculate percentage of freshmen placed in one of their top three entries.

	Args:
		freshmenPrefs: list of lists, represents matrix of dimensions (nFreshmen, nEntries) where entry (i,j) is the ranking given by freshman i to entry j
		results: list of length nFreshmen, such that entry i is the entry that freshman i was assigned to (0:A, 1:B, etc.)

	Returns:
		percentage of freshmen assigned to one of their top three entries
	"""
	numFreshmenInTopThree = 0
	for (i,result) in enumerate(results):
		if freshmenPrefs[i][result] < 4:
			numFreshmenInTopThree += 1
	return float(numFreshmenInTopThree)/len(results) * 100

def getFreshmenMaxRankingScore(freshmenPrefs, results):
	"""
	Calculate freshman maximum ranking score.

	Args:
		freshmenPrefs: list of lists, represents matrix of dimensions (nFreshmen, nEntries) where entry (i,j) is the ranking given by freshman i to entry j
		results: list of length nFreshmen, such that entry i is the entry that freshman i was assigned to (0:A, 1:B, etc.)

	Returns:
		(9 - maximum ranking given by a freshman to their assigned entry)/8 * 100
	"""
	max_ranking = 0
	for (i,result) in enumerate(results):
		if freshmenPrefs[i][result] > max_ranking:
			max_ranking = freshmenPrefs[i][result]
	return float(9-max_ranking)/8 * 100

def getEntryAverageRanking(entryPrefs, results):
	"""
	Calculate entry average ranking.

	Args:
		entryPrefs: list of lists, represents matrix of dimensions (nFreshmen, nEntries) where entry (i,j) is the rating given by entry j to freshman i
		results: list of length nFreshmen, such that entry i is the entry that freshman i was assigned to (0:A, 1:B, etc.)

	Returns:
		average rating given by entries to their assigned freshmen
	"""
	total_rankings = 0
	for (i,result) in enumerate(results):
		total_rankings += entryPrefs[i][result]
	average_ranking = float(total_rankings)/len(results)
	return average_ranking

def getEntryAverageRankingScore(entryPrefs, results):
	"""
	Turns entry average rating into a number between 0 and 100

	Args:
		entryPrefs: list of lists, represents matrix of dimensions (nFreshmen, nEntries) where entry (i,j) is the rating given by entry j to freshman i
		results: list of length nFreshmen, such that entry i is the entry that freshman i was assigned to (0:A, 1:B, etc.)

	Returns:
		average rating given by entries to their assigned freshmen/6 * 100
	"""
	average_ranking = getEntryAverageRanking(entryPrefs, results)
	return average_ranking/6 * 100

def getEntryAverageRankingPerEntry(entryPrefs, results):
	"""
	Calculate entry average rating, for each entry

	Args:
		entryPrefs: list of lists, represents matrix of dimensions (nFreshmen, nEntries) where entry (i,j) is the rating given by entry j to freshman i
		results: list of length nFreshmen, such that entry i is the entry that freshman i was assigned to (0:A, 1:B, etc.)

	Returns:
		list of length nEntries with element i being the average rating given by entry i to their assigned freshmen
	"""
	average_rankings = [0. for i in xrange(9)]
	numFreshmenPerEntry = [0 for i in xrange(9)]
	for (i,result) in enumerate(results):
		average_rankings[result] = float(numFreshmenPerEntry[result] * average_rankings[result] + entryPrefs[i][result])/(numFreshmenPerEntry[result] + 1)
		numFreshmenPerEntry[result] += 1
	return average_rankings

def getEntryAverageRankingVariance(entryPrefs, results):
	"""
	Calculate variance between average ratings between entries.

	Args:
		entryPrefs: list of lists, represents matrix of dimensions (nFreshmen, nEntries) where entry (i,j) is the rating given by entry j to freshman i
		results: list of length nFreshmen, such that entry i is the entry that freshman i was assigned to (0:A, 1:B, etc.)

	Returns:
		variance of average ratings given by each entry to their assigned freshmen, with each entry having equal weight (i.e. not weighted by population)	
	"""
	average_rankings = getEntryAverageRankingPerEntry(entryPrefs, results)
	global_average = getEntryAverageRanking(entryPrefs, results)
	variance = 0.
	for val in average_rankings:
		variance += (val - global_average) ** 2
	variance = variance/len(average_rankings)
	return variance

def getEntryAverageRankingVarianceScore(entryPrefs, results):
	"""
	Turn variance of average ratings given by each entry into a score out of 100.

	Args:
		entryPrefs: list of lists, represents matrix of dimensions (nFreshmen, nEntries) where entry (i,j) is the rating given by entry j to freshman i
		results: list of length nFreshmen, such that entry i is the entry that freshman i was assigned to (0:A, 1:B, etc.)

	Returns:
		(1 - min(variance, 0.4)/0.4) * 100
	"""
	maxVariance = 0.4
	variance = min(getEntryAverageRankingVariance(entryPrefs, results), maxVariance)
	return (1 - variance/maxVariance) * 100

def getPercentageTopRankedFreshmenPerEntry(entryPrefs, results):
	"""
	Get percentage of freshmen in each entry that got a 4, 5 or 6

	Args:
		entryPrefs: list of lists, represents matrix of dimensions (nFreshmen, nEntries) where entry (i,j) is the rating given by entry j to freshman i
		results: list of length nFreshmen, such that entry i is the entry that freshman i was assigned to (0:A, 1:B, etc.)

	Returns:
		list of length nEntries where element i is the percentage of freshmen in entry i that got a 4, 5 or 6	
	"""
	percentage_topranked = [0. for i in xrange(9)]
	total_freshmen = [0 for i in xrange(9)]
	for (i,result) in enumerate(results):
		if entryPrefs[i][result] > 3:
			percentage_topranked[result] += 1
		total_freshmen[result] += 1
	for (i, entryTotal) in enumerate(total_freshmen):
		if entryTotal != 0:
			percentage_topranked[i] = float(percentage_topranked[i])/entryTotal * 100
	return percentage_topranked

def getPercentageTopRankedFreshmenAllEntries(entryPrefs, results):
	"""
	Get percentage of freshmen overall that got a 4, 5 or 6 from their assigned entry

	Args:
		entryPrefs: list of lists, represents matrix of dimensions (nFreshmen, nEntries) where entry (i,j) is the rating given by entry j to freshman i
		results: list of length nFreshmen, such that entry i is the entry that freshman i was assigned to (0:A, 1:B, etc.)

	Returns:
		percentage of freshmen overall that got a 4, 5 or 6	from their assigned entry
	"""
	percentage_topranked = 0.
	for (i,result) in enumerate(results):
		if entryPrefs[i][result] > 3:
			percentage_topranked += 1
	percentage_topranked = percentage_topranked/float(len(results))
	return percentage_topranked