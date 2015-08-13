# marriage_algorithm.py
# Python 2.7 version of the marriage algorithm
# Translation of the IPython notebook of the same name
# Authored by Elena de La Paz (6/15)

import csv
import copy
import collections
from random import shuffle
GENDERMAP = {'0':'M', '1':'F'}
OPPOSITE_GENDER = {'M':'F','F':'M'}

def run_marriage_algorithm(entryVacancyFileName, gendersProvided, maxGenderProportion, froshPreferenceFileName, entryPreferenceFileName, allowGreasing, outputFileName):
	"""
	Run marriage algorithm on provided situation.

	Args:
		entryVacancyFileName    : name of file where entry vacancies are listed
		gendersProvided         : boolean, true if gender preferences have been provided, false otherwise
		maxGenderProportion     : float, maximal proportion of freshmen of the same gender
		froshPreferenceFileName : string, name of file with freshmen preferences and genders
		entryPreferenceFileName : string, name of file with entry preferences
		allowGreasing           : boolean, true if greasing is allowed
		outputFileName          : string, name of outputfile
	Returns:
		None
	"""

	# Define relevant classes
	class Entry:
	    def __init__(self, name, rooms):
	        self.name = name.upper()
	        self.rooms = rooms
	        self.ratings = {}
	        self.taken = set()

	    def __str__(self):
	        return '<{0} Entry>'.format(self.name)

	    def __repr__(self):
	        return self.__str__()

	    def add_rating(self, freshman, rating):
	        self.ratings[freshman.name] = rating

	    def can_take(self, freshman):
	    	return self.rooms[freshman.gender] > 0 or (sum([entry.rooms[freshman.gender] for entry in Entries.values()]) == 0 and sum([entry.rooms[OPPOSITE_GENDER[freshman.gender]] for entry in Entries.values()]) == 0 and self.rooms['U'] > 0)
	        # return self.rooms[freshman.gender] + self.rooms['U'] > 0

	    def take(self, freshman):
	        self.taken.add(freshman)
	        if self.rooms[freshman.gender] > 0:
	            self.rooms[freshman.gender] -= 1
	        else:
	            self.rooms['U'] -= 1

	    def add_to_round(self, freshman):
	        self.current_round.add(freshman)

	    def process_round(self):
	        frosh = sorted(self.current_round, key=lambda f: (-self.ratings[f.name], len(Entries)))
	        taken, dropped = set(), set()
	        for freshman in frosh:
	            if self.can_take(freshman):
	                self.take(freshman)
	                taken.add(freshman)
	            else:
	                dropped.add(freshman)

	        return taken, dropped

	class Freshman:
		def __init__(self, name, gender, rankings):
			self.name = name
			self.gender = gender
			self.rankings = rankings
			self.savedRankings = copy.deepcopy(self.rankings)

		def __str__(self):
			return '<Freshman: {0}>'.format(self.name)

		def __repr__(self):
			return self.__str__()

		def favorite_entry(self):
			if min(self.rankings.values()) == float('inf'):
				self.rankings = copy.deepcopy(self.savedRankings)
			Min = 10000
			Entry = None 
			for key in self.rankings:
				if self.rankings[key] < Min: 
					Min = self.rankings[key]
					Entry = key 
			return Entry

		def rejected_by(self, entry):
			self.rankings[entry.name] = float('inf')

	# Import functions
	def add_entries(entry_csv, gendersProvided, maxGenderProportion):
		"""
		For each entry, create an instance of Entry and put it in Entries
		"""
		if gendersProvided:
		    with open(entry_csv) as f:
		        for line in csv.reader(f):
		            name = line[0].strip()
		            m, f, u = map(int, line[1:])
		            rooms = {
		                'M': m,
		                'F': f,
		                'U': u,
		            }
		            entry = Entry(name, rooms)
		            Entries[name] = entry
		else:
			with open(entry_csv) as f:
				for line in csv.reader(f):
					name = line[0].strip()
					m, f, u = map(int, line[1:])
					m = int(round((1 - 4.0/3 * maxGenderProportion) * u))
					f = int(round((1 - 4.0/3 * maxGenderProportion) * u))
					u = u - m - f
					rooms = {
						'M': m,
						'F': f,
						'U': u,
					}
					entry = Entry(name, rooms)
					Entries[name] = entry

	def frosh_prefs(frosh_prefs):
		"""
		For each freshman, create an instance of Freshman and put it in Frosh
		"""
		with open(frosh_prefs) as f:
			for line in csv.reader(f):
				name = line[0].strip()
				gender = GENDERMAP[line[10].strip()]
				a, b, c, d, e, f, g, h, j = map(int, line[1:10])
				rankings = dict(zip(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J'], [a, b, c, d, e, f, g, h, j]))
				if set(rankings.values()) != set(range(1, 10)):
				    raise Exception('Unusable preferences: {0}'.format(name))
				freshman = Freshman(name, gender, rankings)
				Frosh[name] = freshman

	def entry_prefs(entry_prefs):
		"""
		For each frosh, add entry ratings. If improperly formatted, will return infinity
		"""
		with open(entry_prefs) as f:
			for line in csv.reader(f):
				name = line[0].strip()
				freshman = Frosh[name]
				if len(line[1:]) == 9:
					a, b, c, d, e, f, g, h, j = map(int, line[1:])
					for entry_name, rating in zip(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J'], [a, b, c, d, e, f, g, h, j]):
						entry = Entries[entry_name]
						entry.add_rating(freshman, rating)
				else: 
					del Frosh[freshman.name]

	# If entry gave a 6 and frosh put them in top 3, place automatically
	def greasing(Entries, Frosh):
	    greasing = {}
	    for entry in Entries.values():
	        for f_name, rating in entry.ratings.items():
	            freshman = Frosh[f_name]
	            ranking = freshman.rankings[entry.name]
	            if rating == 6 and ranking <= 3:
	                if freshman in greasing:
	                    greasy_entry = greasing[freshman]
	                    if freshman.rankings[greasy_entry.name] < ranking: # frosh likes greasy better
	                        greasing[freshman] = entry
	                else:
	                    greasing[freshman] = entry
	    return greasing

	def grease_placement(greasing, Entries, Frosh):
	    for freshman, entry in greasing.items():
	        if entry.can_take(freshman):
	            entry.take(freshman)
	            del Frosh[freshman.name]

	# Marriage algorithm
	def getMarried(Entries, Frosh):
		while len(Frosh) > 0:
			# print "here"
			for entry in Entries.values(): 
				entry.current_round = set()
			for freshman in Frosh.values(): 
				if min(freshman.rankings) == float('inf'):
					print freshman.name
				else:
					favorite_entry = freshman.favorite_entry()
					Entries[favorite_entry].current_round.add(freshman)
			for entry in Entries.values():
				taken, dropped = entry.process_round()
				for freshman in taken: 
					del Frosh[freshman.name]
				for freshman in dropped: 
					freshman.rejected_by(entry)
	        
		## CHECK 1: ALL FROSH TAKEN 
		print "CHECK 1: ", len(Frosh) == 0
		# CHeck 2: No FROSH PLACED TWICE
		froshies = []
		for entry in Entries.values():
			for frosh in entry.taken:
				if frosh not in froshies: 
					froshies.append(frosh)
				else:
					print "CHECK 2: ", False
			print "CHECK 2: ",True
			output = []
			for entry in Entries.values(): 
				for frosh in entry.taken: 
					output.append((frosh.name, entry.name) )
			return output

	def distribute_entries(Entries, Frosh, maxGenderProportion): 
		to_dist = int(sum([sum(entry.rooms.values()) for entry in Entries.values()]) - len(Frosh))
		extras = to_dist/len(Entries)
		mod = to_dist % len(Entries)
		for entry in Entries.values(): 
			for i in range(extras): 
				entry.rooms['U'] -= 1
		queue = ['A','B','C','D','E','F','G','H','J']
		shuffle(queue)
		j = 0
		while mod > 0: 
			Entries[queue[j]].rooms['U'] -=1
			mod -=1
			j +=1
		for entry in Entries.values():
			u = entry.rooms['U'] + entry.rooms['M'] + entry.rooms['F']
			m = int(round((1 - 4.0/3 * maxGenderProportion) * u))
			f = int(round((1 - 4.0/3 * maxGenderProportion) * u))
			u = u - m - f
			entry.rooms['U'] = u
			entry.rooms['M'] = m
			entry.rooms['F'] = f

	def write_pairing(pairing, fileName): 
		froshToEntry = {}
		for freshman, entry in pairing:
			froshToEntry[freshman] = entry
		with open(fileName, 'wb') as csvfile:
			writer = csv.writer(csvfile, delimiter = ',', quotechar = '|')
			for freshman in sorted(froshToEntry.keys()):
				writer.writerow([freshman, froshToEntry[freshman]])

	Entries = {}
	Frosh = {}
	add_entries(entryVacancyFileName, gendersProvided, maxGenderProportion)
	frosh_prefs(froshPreferenceFileName)
	entry_prefs(entryPreferenceFileName)
	distribute_entries(Entries, Frosh, maxGenderProportion)
	if allowGreasing:
		g = greasing(Entries, Frosh)
		grease_placement(g, Entries, Frosh)
	results = getMarried(Entries, Frosh)
	write_pairing(results, outputFileName)
	return None
	
# if __name__ == "__main__":
# 	Entries = {}
# 	Frosh = {}
# 	add_entries('entryVacancies.csv', False, 0.55)
# 	frosh_prefs('finalfroshprefsGen_anon.csv')
# 	entry_prefs('entryprefs_anon.csv')
# 	distribute_entries(Entries, Frosh, 0.55)
# 	# print sum([sum(entry.rooms.values()) for entry in Entries.values()])
# 	# Comment out next two lines if no special treatment of 6s
# 	g = greasing(Entries, Frosh)
# 	grease_placement(g, Entries, Frosh)
# 	results = getMarried(Entries, Frosh)
# 	# write_pairing(results, 'Outputs/output_sp.csv')