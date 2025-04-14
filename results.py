import json
import plot
import sys
import csv

def printPretty(fstline,nbTypes,resS,respS,filename):
    for i in range(len(fstline)):
        fstline[i] = fstline[i].ljust(14)
    fstline = "".join(fstline)
    with open(f"tables/{filename}",'w') as f:
        f.write(fstline)
        for t in range(len(nbTypes)):
            for i in range(len(resS[t])):
                resS[t][i] = str(resS[t][i]).ljust(13)
                respS[t][i] = str(respS[t][i]).ljust(13)
            f.write(labels[t].ljust(14)+" "+str(nbTypes[t]).ljust(14)+"  ".join(resS[t]))
            f.write("  %".ljust(14)+" ".ljust(15)+"  ".join(respS[t]))

def printExcel(rowsName,nbTypes,resS,respS):
    res = []
    for t in range(len(nbTypes)):
        res.append([labels[t],nbTypes[t]]+resS[t])
        res.append(["%",""]+respS[t])
    res.append([])
    with open("tables.csv", 'a') as csvfile: 
        # creating a csv writer object 
        csvwriter = csv.writer(csvfile) 
        # writing the fields 
        csvwriter.writerow(rowsName) 
        # writing the data rows 
        csvwriter.writerows(res)

def printLatex(fstline,nbTypes,resS,respS):
    print(fstline)
    # print("Type lemmas & Nb lemmas & Develop & Escape & Backtracking & Blacklisting & Probabilistic & SmartTamarin & All strats & All strats+tact\\\\")
    for t in range(len(nbTypes)):
        print(labels[t]+" & "+str(nbTypes[t])+" & "+" & ".join(resS[t])+"\\\\")
        # print("    & %    & "+" & ".join(respS[t])+" \\\\")

def printStratResults(resp,noBaseLine):
    if noBaseLine:
        printableData = [[] for i in resp[0][:-1]]
        for i in range(len(printableData)):
            for j in range(len(resp)):
                printableData[i].append(resp[j][i])
        strats = ["Escape","Backtracking","Blacklisting","Probabilistic","SmartTamarin","Combined\n strategies"]
        # plot.generatePlotNoBaseline(printableData,strats,labels,saveFile="graphs/resByTypeNoBaseline.png")
    else:
        printableData = [[] for i in resp[0][:-1]]
        for i in range(len(printableData)):
            for j in range(len(resp)):
                printableData[i].append(resp[j][i])
        strats = ["Baseline","Escape","Backtracking","Blacklisting","Probabilistic","SmartTamarin","Combined\n strategies"]
        plot.generatePlotGeneral(printableData,strats,labels,saveFile="graphs/resByType.png")

def printTacticResults(resp):
    printableData = [[] for i in resp[0][:-1]]
    for i in range(len(printableData)):
        for j in range(len(resp)):
            printableData[i].append(resp[j][i])
    strats = ["Baseline","Combined strategies","Combined strategies\nwith tactic generation"]
    # plot.generatePlotGeneral(printableData,strats,labels,saveFile="graphs/resTacticGen.png")

def analysisGen(noBaseLine):
    res, resp = [[],[],[],[],[],[]], [[],[],[],[],[],[]]
    resS, respS = [[],[],[],[],[],[]], [[],[],[],[],[],[]]

    strategies = strat[:-1]
    if noBaseLine:
        strategies = strat[1:-1]
    for s in strategies:
        nbTypes = []
        for i in range(len(types)):
            f, tp = 0, 0
            for lm in lemma[s]['lemmas']:
                st = lemma[s]['lemmas'][lm]['status']
                t = lemma[s]['lemmas'][lm]['lemma_type']
                if (types[i] in t and selectLemma(noBaseLine,s,lm)):
                    tp += 1
                    if (st == "finito"):
                        f += 1
            p = f*100/tp
            nbTypes.append(tp)
            res[i].append(f)
            resp[i].append(round(p,2))
            resS[i].append(str(f)+" ["+str(round(p,2))+"]")
            respS[i].append(str(round(p,2)))
                    
    #Combined results 
    counterByTypeStrat,counterByTypeStratAndTacticGen = byCaseStudyAllTactic()
    resDvp = []
    for t in range(len(types)):
        p = counterByTypeStrat[t]*100/nbTypes[t]
        res[t].append(counterByTypeStrat[t])
        resp[t].append(round(p,2))
        resS[t].append(str(counterByTypeStrat[t])+" ["+str(round(p,2))+"]")
        respS[t].append(str(round(p,2)))

        p = counterByTypeStratAndTacticGen[t]*100/nbTypes[t]
        res[t].append(counterByTypeStratAndTacticGen[t])
        resp[t].append(round(p,2))
        resS[t].append(str(counterByTypeStratAndTacticGen[t])+" ["+str(round(p,2))+"]")
        respS[t].append(str(round(p,2)))

        resDvp.append(res[t][0])

    if noBaseLine:
        #Printing general results
        fstline = ["Type lemmas","Nb lemmas","Escape","Backtracking","Blacklisting","Probabilistic","SmartTamarin","All strats"] #,"All strats+tact"]
        printPretty(fstline,nbTypes,resS,respS,"table2_strategiesresults")
        # printExcel(fstline,nbTypes,resS,respS)
        #printLatex(fstline,nbTypes,resS,respS)
                
        #Ploting results
        printStratResults(resp,noBaseLine)

    

    else:
        #Printing general results
        fstline = ["Type lemmas","Nb lemmas", "Develop","Escape","Backtracking","Blacklisting","Probabilistic","SmartTamarin","All strats","All strats+tact"]
        printPretty(fstline,nbTypes,resS,respS,"appendix_strategiesComparedToBaseline")
        # printExcel(fstline,nbTypes,resS,respS)
        #printLatex(fstline,nbTypes,resS,respS)
                
        #Ploting results
        printStratResults(resp,noBaseLine)

        #Tactic generation analysis
        generalTable,generalTableProportion = [], []
        for i in range(len(nbTypes)):
            improvementProp = counterByTypeStratAndTacticGen[i]-resDvp[i]
            generalTable.append([str(resDvp[i])+" ["+str(round(resDvp[i]*100/nbTypes[i],2))+"]",str(counterByTypeStrat[i])+" ["+str(round(counterByTypeStrat[i]*100/nbTypes[i],2))+"]",str(counterByTypeStratAndTacticGen[i])+" ["+str(round(counterByTypeStratAndTacticGen[i]*100/nbTypes[i],2))+"]",str(improvementProp)+" [+"+str(round((counterByTypeStratAndTacticGen[i]-resDvp[i])/resDvp[i]*100,2))+"]"])
            generalTableProportion.append([str(round(resDvp[i]*100/nbTypes[i],2)),str(round(counterByTypeStrat[i]*100/nbTypes[i],2)),str(round(counterByTypeStratAndTacticGen[i]*100/nbTypes[i],2)),"-"])
        fstline = ["Type lemmas","Nb lemmas","All strats","All strats+tact","Improvement"]
        printPretty(fstline,nbTypes,generalTable,generalTableProportion,"table5_combinedResults")
        # printLatex(fstline,nbTypes,generalTable,generalTableProportion)
        printTacticResults(generalTableProportion[:][:])
        
	
def byCaseStudyAllTactic():
    #Results if we all my strats and tacticGeneration 
    counterByTypeStrat, counterByTypeStratAndTacticGen = [], []
    for i in range(len(types)):
        counterTypeStrat, counterTypeStratTactic = 0, 0
        for lm in lemmaNames:
            dir = lemma['develop']['lemmas'][lm]['theory_dir']	
            if not dir=="emv":
                ty = lemma['escapeFinal']['lemmas'][lm]['lemma_type']
                provedStrat, proveTactic = False,False
                for s in strat[1:6]:
                    if (types[i] in ty and selectLemma(False,s,lm)):
                        st = lemma[s]['lemmas'][lm]['status']
                        ta = lemma[s]['lemmas'][lm]['tactic']				
                        if (st == "finito"):
                            provedStrat = True
                        if (ta != ""):
                            proveTactic = True
                if provedStrat:
                    counterTypeStrat += 1
                if provedStrat or proveTactic:
                    counterTypeStratTactic +=1 
        counterByTypeStrat.append(counterTypeStrat)
        counterByTypeStratAndTacticGen.append(counterTypeStratTactic)
    return(counterByTypeStrat,counterByTypeStratAndTacticGen)

def onlyU(listStatus,idx):
	for j in range(len(listStatus)):
		if j != idx and listStatus[j] == "finito":
			return False
	return True


def compareN(consType,label,indexes):
    strt = []
    for i in indexes:
        strt.append(strat[i])
    timeComp = [0 for i in range(len(strt))]
    finished = [0 for i in range(len(strt))]
    times = [0 for i in range(len(strt))]
    only = [0 for i in range(len(strt))]
    totTime = [0 for i in range(len(strt))]
    casesConsidered = 0
    #consType = "0"
    for lm in lemmaNames:
        status, lemmaTimes = [], []
        if selectLemma(False,strt[0],lm):
            for s in strt: 
                status.append(lemma[s]['lemmas'][lm]['status'])
                lemmaTimes.append(lemma[s]['lemmas'][lm]['time'])
            t = lemma[strt[0]]['lemmas'][lm]['lemma_type']
            if consType in t:
                allFinished = True
                for st in status:
                    if st != "finito":
                        allFinished = False
                        break
                if allFinished:
                    casesConsidered += 1	
                    timeComp[min( (v, i) for i, v in enumerate(lemmaTimes) )[1]] += 1
                    for j in range(len(lemmaTimes)):
                        totTime[j] += lemmaTimes[j]
                for k in range(len(status)):
                    if status[k] == "finito":
                        finished[k] += 1
                        if onlyU(status,k):
                            only[k] += 1
    rtotTime = []
    for k in range(len(indexes)):
        # print(f"{strt[k]} faster in {timeComp[k]} cases")
        # print(f"{strt[k]} only in {only[k]} cases")
        # print(f"{strt[k]} total time: {round(totTime[k],2)}")
        rtotTime.append(str(round(totTime[k],2)))

    with open(f"tables/table3_timecomp",'a') as f:
        f.write(f"{label}\n")
        f.write("\\textbf{Only} & "+" & ".join(list(map(str,only)))+"\\\\\n")
        f.write("\\textbf{Faster} & "+" & ".join(list(map(str,timeComp)))+"\\\\\n")
        f.write("\\textbf{Total time (s)} & "+" & ".join(rtotTime)+"\\\\\n\n")

def compare(consType,i1,i2):
    s1, s2 = strat[i1], strat[i2]
    t1B, t2B = 0, 0
    pt1B, pt2B = [], []
    t1, t2 = 0, 0
    o1, o2 = 0, 0
    casesConsidered = 0
    #consType = "0"
    for lm in lemmaNames:
        if selectLemma(False,strat[0],lm):
            st1, st2 = lemma[s1]['lemmas'][lm]['status'],lemma[s2]['lemmas'][lm]['status']
            t = lemma[s1]['lemmas'][lm]['lemma_type']
            if consType in t:
                if (st1 == "finito") and (st2 == "finito"):
                    casesConsidered += 1
                    t1 = lemma[s1]['lemmas'][lm]['time']
                    t2 = lemma[s2]['lemmas'][lm]['time']	
                    if t1 < t2:
                        t1B += 1
                        pt1B.append(t2/t1)
                    else:
                        t2B += 1
                        pt2B.append(t1/t2)
                if (st1 == "finito") and (st2 != "finito"):
                    o1 += 1
                if (st1 != "finito") and (st2 == "finito"):
                    o2 += 1

    howmuch1,howmuch2 = "-","-"
    if len(pt1B) != 0:
       howmuch1 = round(sum(pt1B)/len(pt1B),2)
    if len(pt2B) != 0:
        howmuch2 = round(sum(pt2B)/len(pt2B),2)
    return(f"{o1} & {o2}",f"{t1B} & {t2B}",f"{howmuch1} & {howmuch2}",casesConsidered,round(t1B/casesConsidered*100,2),round(t2B/casesConsidered*100,2))

def compare2by2(t,stratToComp):
    only, faster, howmuch = [],[],[]
    for i in stratToComp:
        only2, faster2, howmuch2, casesConsidered, prop1faster,prop2faster = compare(t,i,0)
        only.append(only2)
        faster.append(faster2)
        howmuch.append(howmuch2)
        # print(i,casesConsidered,prop1faster,prop2faster)

    with open(f"tables/table3_timecomp",'a') as f:
        f.write("\\textbf{Only} & "+" & ".join(only)+" \\\\\n")
        f.write("\\textbf{Faster} & "+" & ".join(faster)+" \\\\\n")
        f.write("{\\small \\textbf{How much faster}} & "+" & ".join(howmuch)+" \\\\\n\n")

def sort_by_indexes(lst, indexes, reverse=False):
  return [val for (_, val) in sorted(zip(indexes, lst), key=lambda x: \
          x[0], reverse=reverse)]

def tieBreaker(consType,indexes):
    # print("tiebreaking",consType,indexes)
    strt = []
    for i in indexes:
        strt.append(strat[i])
    timeComp = [0 for i in range(len(strt))]
    for lm in lemmaNames:
        if selectLemma(False,strat[0],lm):
            status, lemmaTimes = [], []
            for s in strt:
                status.append(lemma[s]['lemmas'][lm]['status'])
                lemmaTimes.append(lemma[s]['lemmas'][lm]['time'])
            t = lemma[strt[0]]['lemmas'][lm]['lemma_type']
            if consType in t:
                allFinished = True
                for st in status:
                    if st != "finito":
                        allFinished = False
                        break
                if allFinished:	
                    timeComp[min( (v, i) for i, v in enumerate(lemmaTimes) )[1]] += 1
    # print(indexes)
    # print(timeComp)
    return(sort_by_indexes(indexes,timeComp,True))  

def untieRanking(type,scores,ranking):
    sortedScores = sorted(scores,reverse=True)
    if len(sortedScores)>1 and sortedScores[0]>0:
        i = 0
        while (i+1) < len(sortedScores) and sortedScores[i+1] == sortedScores[0]:
            i += 1
        if i > 0:
            ranking[0:i+1] = tieBreaker(type,ranking[0:i+1])
    return(ranking)

def generalRanking(type,stratsIdx):
    strtScore = [0 for i in range(len(stratsIdx))]
    for lm in lemmaNames:
        if selectLemma(False,strat[0],lm):
            for si in range(len(stratsIdx)): 
                s = strat[stratsIdx[si]]
                st = lemma[s]['lemmas'][lm]['status']
                t = lemma[s]['lemmas'][lm]['lemma_type']
                if type in t and st == "finito":
                    strtScore[si] += 1
    ranking = sort_by_indexes(stratsIdx,strtScore,True)
    return(untieRanking(type,strtScore,ranking))



def proveUnique(type,stratTested,ref):
    score = 0
    for lm in lemmaNames:
        if selectLemma(False,strat[0],lm):
            unique = False
            st = lemma[strat[stratTested]]['lemmas'][lm]['status']
            t = lemma[strat[stratTested]]['lemmas'][lm]['lemma_type']
            if type in t: 
                if st == "finito":
                    unique = True
                    for s in ref:
                        if (lemma[strat[s]]['lemmas'][lm]['status'] == "finito"):
                            unique = False
            if unique:
                score += 1
    return(score)
                    
def uniquenessRanking(type,toberanked,ref):
    uniquenessScore, uranking = [], []
    for s in toberanked:
        uniquenessScore.append(proveUnique(type,s,ref))
    uranking = sort_by_indexes(toberanked,uniquenessScore,True)
    uranking = untieRanking(type,uniquenessScore,uranking)
    return(uranking,sorted(uniquenessScore,reverse=True))

def fastest(consType,ranking):
    return(tieBreaker(consType,ranking)[0])

def workflowEfficience(type,ranking):
    score, casesConsidered = 0, 0
    for lm in lemmaNames:
        if selectLemma(False,strat[0],lm):
            proved = False
            t = lemma[strat[0]]['lemmas'][lm]['lemma_type']
            if type in t:
                casesConsidered += 1
                for si in ranking:
                    s = strat[si]
                    st = lemma[s]['lemmas'][lm]['status']
                    if (st == "finito"):
                        proved = True
                if proved:
                    score += 1
    return(casesConsidered,score)

def resultApproach(type,s):
    score = 0
    for lm in lemmaNames:
        if selectLemma(False,strat[0],lm):
            t = lemma[strat[0]]['lemmas'][lm]['lemma_type']
            if type in t:
                if (lemma[strat[s]]['lemmas'][lm]['status'] == "finito"):
                    score += 1
    return(score)

def printLatexWorkflow(ref,score,terminationRate,compareBase,compareBest):
    strat = ["Develop","Escape","Backtracking","Blacklisting","Proba","SmartTamarin","SmartVerif"]
    lines = [" & \\textbf{All} & \\textbf{Classic} & \\textbf{Exists} & \\textbf{Source} & \\textbf{Reuse} & \\textbf{Induction} \\\\"]
    resLen0 = len(ref[0])
    fstCol = [f"{i}. &" for i in range(1,resLen0+1)]+["\\begin{tabular}{l} \\textbf{Workflow} \\\\ \\textbf{success}\\end{tabular} & ","\\begin{tabular}{c} \\textbf{Termination rate} \\\\ \\textbf{in \\%}\\end{tabular} & ","\\begin{tabular}{c} \\textbf{Improvement in \\%} \\\\ \\textbf{(/baseline)}\\end{tabular} & ","\\begin{tabular}{c} \\textbf{Improvement in \\%} \\\\ \\textbf{(/best approach)}\\end{tabular}& "]
    prettyStrat = [[] for _ in range(len(ref))]
    for i in range(len(ref)):
        # print(ref[i])
        for j in range(len(ref[i])):
            if ref[i][j] == -1:
                s = "-"
            else:
                s = strat[ref[i][j]]
            prettyStrat[j].append(s)
    for k in range(resLen0):
        lines.append(fstCol[k]+" & ".join(prettyStrat[k])+"\\\\\n")
    lines.append(fstCol[resLen0]+" & ".join(score)+"\\\\\n")
    lines.append(fstCol[resLen0+1]+" & ".join(terminationRate)+"\\\\\n")
    lines.append(fstCol[resLen0+2]+" & ".join(compareBase)+"\\\\\n")
    lines.append(fstCol[resLen0+3]+" & ".join(compareBest)+"\\\\\n")
    with open("tables/table5_workflow",'w') as f:
        for l in lines: 
            f.write(l)


def workflow(stratsIdx):
    rankings, scores, terminationRates = [],[],[]
    scoresDvp, terminationsRateDvp, terminationsRateBest = [], [],[]
    for t in types:
        #Defining the ranking
        ranking = generalRanking(t,stratsIdx)

        increasingCoverage = True
        toberanked, ref = ranking[1:], ranking[:1]
        while increasingCoverage and toberanked != []:
            # toberanked = generalRanking(type,toberanked)
            uranking,uscore = uniquenessRanking(t,toberanked,ref)
            if max(uscore) == 0:
                increasingCoverage = False
            else:
                toberanked = uranking[1:]
                ref.append(uranking[0])
        fastst = fastest(t,ref)

        #Informations about the ranking
        casesConsidered,score =workflowEfficience(t,ref)
        terminationRate = round(score*100/casesConsidered)
        scoreDvp = resultApproach(t,0)
        terminationRateDvp = round(scoreDvp*100/casesConsidered)
        scoreBest = resultApproach(t,ref[0])
        terminationRateBest = round(scoreBest*100/casesConsidered)
        rankings.append(ref)
        scores.append(score)
        terminationRates.append(terminationRate)
        scoresDvp.append(scoreDvp)
        terminationsRateDvp.append(terminationRateDvp)
        terminationsRateBest.append(terminationRateBest)

        # print(f"Strat {t}, fastest: {fastst}")

    #Printing
    maxLen = max([len(i) for i in rankings])
    rankings = [(r+ maxLen * [-1])[:maxLen] for r in rankings]

    printingScores = [f"{scores[i]} ({scoresDvp[i]})" for i in range(len(scores))]
    printingTerm = [f"{terminationRates[i]} ({terminationsRateDvp[i]})" for i in range(len(scores))]
    compareBase = [f"+{terminationRates[i]-terminationsRateDvp[i]}" for i in range(len(scores))]
    compareBest = [f"+{terminationRates[i]-terminationsRateBest[i]}" for i in range(len(scores))]

    printLatexWorkflow(rankings,printingScores,printingTerm,compareBase,compareBest)

    
       
	
def oracled(oracleStatus):
	return(oracleStatus == "1.0" or oracleStatus == "0.0")

def selectLemma(noBaseLine,strategy,lem):
    n = lemma[strategy]['lemmas'][lem]['name']
    os = lemma[strategy]['lemmas'][lem]['oracleStatus']
    dir = lemma[strategy]['lemmas'][lem]['theory_dir']
	
    oracledS = oracled(os)

    if noBaseLine:
        # and not lemma['develop']['lemmas'][lem]['status'] == "finito"
        return(not dir=="emv" and not dir=="smartverif" and not n=="Observational_equivalence" and not lemma['develop']['lemmas'][lem]['status'] == "finito")	
    else:
        return(not dir=="emv" and not dir=="smartverif" and not n=="Observational_equivalence")
    
if __name__ == "__main__":
	
    with open('data.json','r') as file:
        lemma =json.load(file)
		
    strat = ["develop","escapeFinal","backtracking","blacklisting","proba","smartmarin","smartverif"]
    # labels = ["All","Classic","Exists","Diff","Source","Reuse","Induction"]
    # types = ["","0","1","2","3","4","5"]
    labels = ["All","Classic","Exists","Source","Reuse","Induction"]
    types = ["","0","1","3","4","5"]
    lemmaNames = []
    for lm in lemma[strat[0]]['lemmas']:
        lemmaNames.append(lm)

    noBaseLine = True
    analysisGen(noBaseLine)
    #Appendix
    analysisGen(not noBaseLine)

    for t in range(len(types)):
        compareN(types[t],labels[t],[0,1,2,3,4,5])
        compare2by2(types[t],[1,2,3,4,5])
    workflow([0,1,2,3,4,5])
        