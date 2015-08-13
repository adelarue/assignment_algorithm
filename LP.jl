# LP.jl
# read from file and build linear program, then solve it using Gurobi
# Authored on 6/17/15 by Arthur J Delarue

using JuMP, Gurobi

# Default parameters... ignore
COST_FUNCTION = "simplerquad"
MAX_RANKING = true
gendersProvided = false

# cd("/Users/arthurdelarue/Documents/MIT/President/algorithm")
ENTRIES = ["A","B","C","D","E","F","G","H","J"]
ENTRY_TOTAL_ROOMS = [32,32,32,32,30,42,40,48,30]

FILENAME = "output100_quad.csv"
FRESHMEN_WEIGHT = 1.0
# end of default parameters

function run_LP(;outputFileName::String = FILENAME, freshmenWeight = FRESHMEN_WEIGHT, costFunction = COST_FUNCTION, maxRanking = MAX_RANKING)
	"""
	Run LP formulation for matching.

	Args:
		outputFileName   : string, name of file where output is saved
		freshmenWeight   : float between 0 and 1, relative importance of freshman and entry preferences. 0 is 0% freshman preference, 1 is 100% freshman preference
		costFunction     : string, describes cost function to be minimized. Possibles values include simple, quad, simplequad, simplerquad and minimax
		maxRanking       : boolean, true if minimax algorithm is run first to try and enforce freshman fairness. Default value is false
	"""

	# Read in freshmen and entry preferences
	freshmenPrefs = readcsv("finalfroshprefsGen_anon.csv")
	entryprefs = readcsv("entryprefs_anon.csv")
	# Read in number of vacancies
	rooms = readcsv("entryVacancies.csv")
	names = freshmenPrefs[:,1]
	entries = rooms[:,1]

	# Create matrix of costs
	freshmenCosts = zeros(length(names), length(entries))
	entryCosts = zeros(length(names), length(entries))
	# Add freshmen and entry numbers
	for i=1:length(names), j=1:length(entries)
		freshmenCosts[i,j] = freshmenPrefs[i,j+1]
		entryCosts[i,j] = entryprefs[i,j+1]
	end
	# Create total matrix
	costMatrix = zeros(length(names), length(entries))
	costMatrix2 = zeros(length(names), length(entries))
	for i=1:length(names), j=1:length(entries)
		costMatrix[i,j] = freshmenWeight * (freshmenCosts[i,j]-1)/8 + (1 - freshmenWeight) * (6 - entryCosts[i,j])/6
		costMatrix2[i,j] = freshmenWeight * (freshmenCosts[i,j]-1)/8 * (freshmenCosts[i,j]-1)/8 + (1 - freshmenWeight) * (6 - entryCosts[i,j])/6 * (6 - entryCosts[i,j])/6
	end

	# Create arrays of boys and girls
	boys = Int[]
	girls = Int[]
	for i=1:length(names)
		if freshmenPrefs[i,11] == 0
			push!(boys, i)
		elseif freshmenPrefs[i,11] == 1
			push!(girls, i)
		end
	end

	# Find most prevalent gender
	maxGender = max(length(boys)/length(names), length(girls)/length(names))

	# Split vacancies by gender
	totalRoomsPerEntry = rooms[:,2] + rooms[:,3] + rooms[:,4]
	if gendersProvided
		maxBoysPerEntry = rooms[:,2] + rooms[:,4]
		maxGirlsPerEntry = rooms[:,3] + rooms[:,4]
	else
		maxBoysPerEntry = 4/3 * maxGender * totalRoomsPerEntry
		maxGirlsPerEntry = 4/3 * maxGender * totalRoomsPerEntry
	end

	# Find number of rooms that will remain empty, and max per entry
	numEmptyRooms = sum(totalRoomsPerEntry) - length(names)
	if numEmptyRooms < 0
		println("!!!! WARNING : more freshmen than rooms !!!!")
	end
	numEmptyRoomsPerEntry = int(ceil(numEmptyRooms/sum(ENTRY_TOTAL_ROOMS) .* ENTRY_TOTAL_ROOMS))

	# Create JuMP model (linear program)
	m = Model(solver=GurobiSolver(TimeLimit=200, OutputFlag=0))

	# Define binary variables: true if freshman i assigned to entry j
	@defVar(m, x[i=1:length(names),j=1:length(entries)], Bin)
	# Define extra variable for minimax cost function
	if costFunction == "minimax"
		@defVar(m, maximum >= 0)
	end

	# One entry per freshman
	@addConstraint(m, oneEntryPerFreshman[i=1:length(names)], sum{x[i,j], j=1:length(entries)} == 1)

	# No more freshmen per entry than vacancies, and no more than a set number of vacancies per entry
	@addConstraint(m, freshmenPerEntryMax[j=1:length(entries)], sum{x[i,j], i=1:length(names)} <= totalRoomsPerEntry[j])
	@addConstraint(m, freshmenPerEntryMin[j=1:length(entries)], sum{x[i,j], i=1:length(names)} >= totalRoomsPerEntry[j] - numEmptyRoomsPerEntry[j])

	# Not too many boys
	@addConstraint(m, boyLimit[j=1:length(entries)], sum{x[i,j], i=boys} <= maxBoysPerEntry[j])

	# Not too many girls
	@addConstraint(m, girlLimit[j=1:length(entries)], sum{x[i,j], i=girls} <= maxGirlsPerEntry[j])

	# Max Ranking
	if maxRanking
		maximumRanking = run_LP(outputFileName="tmp.csv", freshmenWeight=freshmenWeight, costFunction="minimax", maxRanking=false)
		@addConstraint(m, maxRanking[i=1:length(names)], sum{x[i,j] * freshmenCosts[i,j], j = 1:length(entries)} <= int(maximumRanking) + 0.001)
	end

	# Set objective function
	if costFunction == "simple"
		@setObjective(m, Min, sum{costMatrix[i,j] * x[i,j], i=1:length(names), j = 1:length(entries)})
	elseif costFunction == "quad"
		@defExpr(sc[j=1:length(entries)], sum{costMatrix[i,j] * x[i,j], i = 1:length(names)})
		@setObjective(m, Min, sum{sc[j] * sc[j], j = 1:length(entries)})
	elseif costFunction == "simplequad"
		@setObjective(m, Min, sum{costMatrix[i,j] * costMatrix[i,j] * x[i,j], i=1:length(names), j = 1:length(entries)})
	elseif costFunction == "simplerquad"
		@setObjective(m, Min, sum{costMatrix2[i,j] * x[i,j], i=1:length(names), j=1:length(entries)})
	elseif costFunction == "minimax"
		@defExpr(weightedSum[i=1:length(names)], sum{ costMatrix[i,j] * x[i,j], j=1:length(entries)})
		@addConstraint(m, maximumConstr[i=1:length(names)], weightedSum[i] - maximum <= 0)
		@setObjective(m, Min, maximum)
	end

	# Solve problem
	status = solve(m)

	# Check if infeasible, debug if necessary
	if status == :Infeasible
		buildInternalModel(m)
		print_iis_gurobi(m)
	end
	# Write output to file
	if status == :Optimal
		println(string(outputFileName, "\t: optimal solution found"))
		x_opt = getValue(x)
		outputFile = open(string("Outputs/",outputFileName), "w")
		for i=1:length(names)
			entry = indmax(x_opt[i,:])
			write(outputFile, string(names[i],",",ENTRIES[entry],"\n"))
		end
		close(outputFile)
		# Special case for minimax cost function (because this is used for maxRanking variation)
		if costFunction == "minimax"
			maximumRanking = 0
			for i = 1:length(names)
				entry = indmax(x_opt[i,:])
				if freshmenCosts[i,entry] > maximumRanking
					maximumRanking = freshmenCosts[i,entry]
				end
			end
			return maximumRanking
		end
	end
end

function run_all_LP_solutions(algorithmFileName)
	"""
	Run all LP solutions based on what is listed in the file provided.

	Args:
		algorithmFileName : string, name of file with listed algorithms to be used
	"""
	# Open algorithm file
	algorithmFile = open(algorithmFileName, "r")
	# Loop through lines of file
	for line in readlines(algorithmFile)
		# remove trailing newline
		fileName = strip(line, '\n')
		# extract relevant information from filename
		row = split(split(line, ".")[1], "_")
		if row[2] != "marriage"
			fWeight = float(row[2])/100
			cost_func = row[3]
			if row[4] == "noMaxRank"
				maxRank = false
			else
				maxRank = true
			end
			# Run LP based on parameters
			run_LP(outputFileName = fileName, freshmenWeight = fWeight, costFunction = cost_func, maxRanking = maxRank)
		end
	end
	return 0
end

function print_iis_gurobi(m::Model)
	"""
	Helper debugging function. Ignore.

	Taken from JuMP examples online. Given a LP instance, uses Gurobi to troubleshoot infeasibility.
	Outputs IIS to find "bad" constraints.
	"""
    grb = MathProgBase.getrawsolver(getInternalModel(m))
    Gurobi.computeIIS(grb)
    numconstr = Gurobi.num_constrs(grb)
    numvar = Gurobi.num_vars(grb)

    iisconstr = Gurobi.get_intattrarray(grb, "IISConstr", 1, numconstr)
    iislb = Gurobi.get_intattrarray(grb, "IISLB", 1, numvar)
    iisub = Gurobi.get_intattrarray(grb, "IISUB", 1, numvar)

    println("Irreducible Inconsistent Subsystem (IIS)")
    println("Variable bounds:")
    for i in 1:numvar
        v = Variable(m, i)
        if iislb[i] != 0 && iisub[i] != 0
            println(getLower(v), " <= ", getName(v), " <= ", getUpper(v))
        elseif iislb[i] != 0
            println(getName(v), " >= ", getLower(v))
        elseif iisub[i] != 0
            println(getName(v), " <= ", getUpper(v))
        end
    end

    println("Constraints:")
    for i in 1:numconstr
        if iisconstr[i] != 0
            println(m.linconstr[i])
        end
    end
    println("End of IIS")
end

# Run all algorithms and save their outputs
@time run_all_LP_solutions("outputFiles.txt")