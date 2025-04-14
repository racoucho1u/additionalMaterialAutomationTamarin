import re
import manipulateFile as mf

def generateInputFile(filename, diff, lemmaFile, diir, benchmarkcase, constructedInput,log):
	inputs = []
	lemmas = []

	fi = f"files_to_benchmark/input_lemmas_tacticGen/{lemmaFile}"

	with open(fi) as f:
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

if __name__ == "__main__":

    benchmarkCase = "tacticGeneration/tamarin-prover"
    file = "files_to_benchmark/input_lemmas_tacticGen.txt"
    constructedInput = "files_to_benchmark/currentLemmaInput"
    log = "files_to_benchmark/log"

    parallel_input=[]
    with open(file) as f:
        lines = f.readlines()
        inputsRough,inputs = [],[]
        for line in lines:
            if line[0] != "#":
				#params = filename,setDiff,lemma,caseStudy,benchmarkCase,log
                params = re.split(r'\t',line)
                print(params)
                #print(parseAndRun((params[1], params[0], params[2][:-1], benchmarkCase, recapFile)))
                inputsRough.append((params[1], params[0], params[2], params[3][:-1], benchmarkCase))
                inputs = generateInputFile(params[1], params[0], params[2], params[3][:-1], benchmarkCase, constructedInput, log)
				
                for i in inputs:
                    diff = False
                    filename,setDiff,lemma,caseStudy,benchmarkCase,log = i
                    theoryfile = f"files_to_benchmark/{caseStudy}/{filename}"
                    if setDiff == "TRUE":
                        diff = True
                    print(diff)
                    parallel_input.append([theoryfile,lemma,f"diff={diff}"])
                    # print(theoryfile,lemma,bool(setDiff))
    mf.parallelProving(parallel_input,2)
                    # mf.proveUntil(theoryfile,lemma,diff=bool(setDiff))
				
