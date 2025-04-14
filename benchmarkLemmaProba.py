import os
import re
import sys
from os.path import exists
import multiprocessing
from time import perf_counter
import csv


def parseBigFile(file):

	filename = os.path.splitext(file)[0]
	inSum = False
	incomplete=False

	summary=f"{filename}_summary.spthy"

	f = open(file,"r")
	for line in f.readlines():
		if inSum and (re.findall("incomplete", line) != []):
			with open(summary,"a") as s:
				s.write(line)
				incomplete = True
		elif inSum:
			with open(summary,"a") as s:
				s.write(line)
		elif (re.findall("summary of summaries", line) != []):
			inSum = True
	f.close()
	return incomplete

def parseAndRun(arg):

	filename,setDiff,lemma,caseStudy,benchmarkCase,log = arg
	filename = filename.split(".")[0]

	lemmaName = re.split("\t",lemma)[0]

	with open(log,'a') as l:
		l.write(f"BEGINNING: {caseStudy}\t{filename}\t{lemmaName}\n")
	print(f"{filename}\t{lemmaName}")

	resultDir = f"../../files_to_benchmark/res_{caseStudy}_{benchmarkCase}"
	#if not os.path.isdir(resultDir):
	#	os.makedirs(resultDir)

	#dirname = f"../../files_to_benchmark/{caseStudy}"
	dirname = f"../../files_to_benchmark/probaOnly/"
	proofFile = f"{resultDir}/{filename}_recap.spthy"
	bigfile = f"{resultDir}/{filename}_total.spthy"
	timefile= f"{resultDir}/{filename}_time.spthy"

	diff=""
	result=""


	if (setDiff=="TRUE"):
		diff = "--diff"

	proofFile = f"{resultDir}/{filename}__{lemmaName}_recap.spthy"
	bigfile = f"{resultDir}/{filename}__{lemmaName}_total.spthy"
	timefile= f"{resultDir}/{filename}__{lemmaName}_time.spthy"

	#cmd = f"timeout 12h tamarin-prover --prove={lemma} {dirname}/{filename}.spthy {diff} +RTS -N4 -RTS --output={proofFile} --derivcheck-timeout=0 > {bigfile} 2>&1"
	#print(cmd)
	start = perf_counter()
	#print(f"timeout 4h tamarin-prover --prove={lemma} {dirname}/{filename}.spthy {diff} +RTS -N4 -RTS --output={proofFile} --derivcheck-timeout=0 > {bigfile} 2>&1")
	os.system(f"timeout 2h tamarin-prover --prove={lemma} {dirname}/{filename}.spthy {diff} +RTS -N4 -RTS --output={proofFile} --derivcheck-timeout=0 > {bigfile} 2>&1")
	end = perf_counter()

	with open(f"{timefile}","a") as t:
		t.write(str(end-start)+"\n")


	with open(log,'a') as l:
		l.write(f"ENDING: {caseStudy}\t{filename}\t{lemmaName}\n")


	if (not exists(proofFile) or (os.stat(proofFile).st_size == 0)):
		with open(bigfile, 'r') as bf:
			lastline = bf.readlines()[-1]
		if (re.findall("Killed",lastline) == []):
			result = f"{filename},Killed\n"
		else:

			result = f"{filename},TimeOut\n"
		if (exists(proofFile)):
			os.remove(proofFile)
	else:
		status = parseBigFile(bigfile)
		if (status):
			result = f"{filename},Incomplete\n"
		else:
			t = ""
			with open(timefile) as tf :
				lines = tf.readlines()
			result = f"{filename},{lines[-1]}"
		#os.remove(bigfile)

	
	return(result)



def chooseVersion(version):
	#Determine what version of tamarin we are benchmarking
	benchmarkCase = ""
	tamarinDir = ""
	if (version == '0'):
		benchmarkCase = "develop"
		tamarinDir = "develop/tamarin-prover"
		version = 0
	elif (version == '1'):
		benchmarkCase = "escapeLoop"
		tamarinDir = "escape_new/tamarin-prover"
		version = 1
	elif (version == '2'):
		benchmarkCase = "backtracking"
		tamarinDir = "loopNoBlackList/tamarin-prover"
		version = 2
	elif (version == '3'):
		benchmarkCase = "blackListing"
		tamarinDir = "reinfLearning/tamarin-prover"
		version = 3
	elif (version == '4'):
		benchmarkCase = "smartverif"
		tamarinDir = "develop/tamarin-prover"
		version = 4
	elif (version == '5'):
		benchmarkCase = "backtrackingLight"
		tamarinDir = "backtrackingLight/tamarin-prover"
		version = 5
	elif (version == '6'):
		benchmarkCase = "h5i5"
		tamarinDir = "proba/tamarin-prover"
		version = 5
	else:
		print("Incorrect argument: choose among the following",
				"0: developp version of tamarin",
				"1: escaping the loop version",
				"2: backtracking version 'without blacklist",
				"3: blackListing version",
				"4: smartverif",
				"5: backtracking only when no more option",
				sep=os.linesep
			)
		quit()

	if (not os.path.isdir(tamarinDir)):
		print(f"The following version of tamarin does not exit: {tamarinDir}")
		quit()

	os.chdir(tamarinDir)
	print(os.getcwd())
	os.system("make")

	#In SmartVerif case we recompile the right version of tamarin before giving it to SmartVerif
	if (version == 4):
		print(os.getcwd())
		print(version)
		os.chdir("../smartverifD")

	return(benchmarkCase, version)

def generateInputFile(filename, diff, lemmaFile, diir, benchmarkcase, constructedInput,log):
	inputs = []
	lemmas = []
	with open(f"../../files_to_benchmark/lemmasProbaOnly/{lemmaFile}") as f:
			lines = f.readlines()
			for line in lines:
				if line[0] != "#":

					lemma = re.sub(r"\s+$", "", line, 0, re.MULTILINE)
					lemmas.append(lemma)
	with open(constructedInput,'a') as ci:
		for lemma in lemmas:
			ci.write(f"{diir}\t{filename}\t{lemma}\t{diff}\n")
			inputs.append((filename, diff, lemma, diir,benchmarkcase,log))
	return(inputs)


if (len(sys.argv) != 2):
	print("Choose the benchmark mode",
			"0: developp version of tamarin",
			"1: escaping the loop version",
			"2: backtracking version 'without blacklist",
			"3: blackListing version",
			"4: smartverif",
			"5: backtracking only when no more option",
            "6: proba",
            sep=os.linesep)
	benchmarkCase, version = chooseVersion(input(""))
else:
	benchmarkCase, version = chooseVersion(sys.argv[1])


N = 2
file = "../../files_to_benchmark/inputLemmasProbaOnly"
constructedInput = "../../files_to_benchmark/currentLemmaInput"
log = "../../files_to_benchmark/log"
recapFile = f"../../files_to_benchmark/recapfile_{benchmarkCase}.csv"

inputs=[]
inputs_parallel = []
if os.path.isfile(constructedInput):
	os.remove(constructedInput)
if os.path.isfile(log):
	os.remove(log)
with open(file) as f:
	lines = f.readlines()
	for line in lines:
		if line[0] != "#":
			params = re.split(r'\t',line)
			#print(parseAndRun((params[1], params[0], params[2][:-1], benchmarkCase, recapFile)))
			print(params[3][:-1])
			inputs.append((params[1], params[0], params[2], params[3][:-1], benchmarkCase))

			inputs_parallel = inputs_parallel + generateInputFile(params[1], params[0], params[2], params[3][:-1], benchmarkCase, constructedInput, log)

			resultDir = f"../../files_to_benchmark/res_{params[3][:-1]}_{benchmarkCase}"
			if not os.path.isdir(resultDir):
				os.makedirs(resultDir)

pool = multiprocessing.Pool(processes=N)
outputs = pool.map(parseAndRun, inputs_parallel)
pool.close()
pool.join()


#https://www.geeksforgeeks.org/writing-csv-files-in-python/
with open(recapFile,'a') as r:
	r.write(f"New try {benchmarkCase}\n")
	for res in outputs:
		r.write(res)

os.chdir("..")
