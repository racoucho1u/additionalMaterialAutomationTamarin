import subprocess
import sys
import argparse
import tacticExportPoC as te
import multiprocessing

WRAPPER_PATH = "tamarin_wrapper.py"
# original_file = "SourceOfUniqueness.spthy"
original_file = "examples/ccs18-5G/5G-AKA-bindingChannel/5G_AKA.spthy"
TIMEOUT_FACTOR = 5
# mininum timeout in seconds
MIN_TIMEOUT = 10

# tactic = "tactic: sqn_ue_nodecrease\ndeprio:\n\tallGoal \"ActionG#vk(Fact{factTag=KUFact factAnnotations=fromList[] factTerms=[f1(~k pair(SqnHSS RAND))]}\"\ndeprio:\n\tallGoal \"ActionG#vk(Fact{factTag=KUFact factAnnotations=fromList[] factTerms=[f1(~k pair(Union(SqnUE dif) RAND))]}\"\ndeprio:\n\tallGoal \"ActionG#vk(Fact{factTag=KUFact factAnnotations=fromList[] factTerms=[Xor(f5(~k RAND) Union(SqnUE dif))]}\"\n\n"

def add_tactic_to_file(filename,tactic):
    with open(filename, "r") as f:
        contents = f.readlines()

    last_line = len(contents)-1
    while (not 'end' in contents[last_line]) and (last_line>0):
        last_line -= 1
        
    contents.insert(last_line-1, tactic)

    with open(filename, "w") as f:
        contents = "".join(contents)
        f.write(contents)

    # print(contents)


def tamarin_wrapper_call(arg_list, time_out=6000):
    return subprocess.Popen(
        ["python3", WRAPPER_PATH]
        + arg_list
        + [
            "-t",
            str(time_out),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).communicate()

def prove_with_tactic(q,filename,lemma_name,macro,heuristic,tactic_nb,diff,timeout=6000):

    outputFile = filename.split("/")[-1]
    lemma_name_file = lemma_name.split(" ")[0]
    diffFlag = ""
    if diff != "False":
        diffFlag = "--diff"
    print(diff,diffFlag)
    out, err = tamarin_wrapper_call([filename, "-s", f"--lemma={lemma_name}",f"--tam=--heuristic={heuristic} {macro} {diffFlag} --output=results/{lemma_name_file}_{outputFile}  2>> tacticBatch/{lemma_name_file}_{outputFile}"],timeout)
    if err:
        print(
            "Sanity check failed for: "
            + filename
            + ", lemma name: "
            + lemma_name
            + "\nError: "
            + err.decode(),
            file=sys.stderr,
        )
        q.put("Sanity check failed for: "
            + filename
            + ", lemma name: "
            + lemma_name
            + "\nError: "
            + err.decode())
        sys.exit(1)

    for line in out.decode().rstrip().split("\n"):
        # Successful calls to the wrapper should produce a triple (data, status,time)
        # while timedout calls should produce the tuple (data, status,time,tactic)
        # not sure yet how the killed proofs are handled

        data = line.split(" ")
        # total_time += float(data[2])
        
        try:
            tactic = te.extractTacticsFile(f"tacticBatch/{lemma_name_file}_{outputFile}")
            if tactic != "":   
                tacticRough = tactic.split("tactic:")[1]
                deprios = tacticRough.replace("---","\n")
                tactic = "\ntactic: "+lemma_name_file+"_"+str(tactic_nb)+"\n"+deprios+"\n\n"
                # print(tactic)
                add_tactic_to_file(filename,tactic)
        except Exception:
            with open ("debugFile",'a') as df:
                df.write(f"Tactic generation error: {filename}\n")
            tactic = "Error in generation"

        return(data[:4],tactic)

    
    
def proveUntil(file_path, lemma, macro, q, bound=3, heuristic="s", timeout=15, diff=False):
    tactic,tactic_updated, heuristic_old = "","new","old"
    proof_attempt = 0
    proved = False
    while proof_attempt<bound and tactic_updated != "Error in generation":
        if tactic == tactic_updated and tactic != "":
            break 
        if tactic_updated == "":
            heuristic = heuristic_old
        if tactic == tactic_updated or tactic_updated == "":
            timeout *= 2
        print(f"Proving {lemma} ({file_path}) with heuristic: {heuristic}, timeout: {timeout}")
        tactic = tactic_updated
        status, tactic_updated = prove_with_tactic(q,file_path,lemma,macro,heuristic,proof_attempt,diff,timeout)
        if 'True' in status or 'False' in status:
            proved = True
            print(f"Prove lemma {lemma} (file:{file_path}) with heuristic: {heuristic}.\n")
            q.put(f"Prove lemma {lemma} (file:{file_path}) with heuristic: {heuristic}.\n")
            # with open('results/scriptResult', 'a') as r:
            #     r.write(f"Prove lemma {lemma} (file:{file_path}) with heuristic: {heuristic}.\n")
            break
        heuristic_old = heuristic
        heuristic = "{"+lemma+"_"+str(proof_attempt)+"}"
        proof_attempt += 1
    if not proved:
        if (proof_attempt==bound):
            print(f"Cannot prove lemma {lemma} (file:{file_path}) after {proof_attempt} attempts (timeout={timeout}s): attempts bound reached ({bound}).\n")
            q.put(f"Cannot prove lemma {lemma} (file:{file_path}) after {proof_attempt} attempts (timeout={timeout}s): attempts bound reached ({bound}).\n")
            # with open(f'results/scriptResult_{lemma}_{filepath}', 'a') as r:
            #     r.write(f"Cannot prove lemma {lemma} (file:{file_path}) after {proof_attempt} attempts (timeout={timeout}s): attempts bound reached ({bound}).\n")
        else:
            if tactic == tactic_updated:
                print(f"Cannot prove lemma {lemma} (file:{file_path}) after {proof_attempt} attempts (timeout={timeout}s): no tactic no longer changing.\n")
                q.put(f"Cannot prove lemma {lemma} (file:{file_path}) after {proof_attempt} attempts (timeout={timeout}s): no tactic no longer changing.\n")
                # with open(f'results/scriptResult_{lemma}_{filepath}', 'a') as r:
                #     r.write(f"Cannot prove lemma {lemma} (file:{file_path}) after {proof_attempt} attempts (timeout={timeout}s): no tactic no longer changing.\n")
            else:
                if (tactic == tactic_updated and not proved) or tactic_updated == "":
                    print(f"Cannot prove lemma {lemma} (file:{file_path}) after {proof_attempt} attempts (timeout={timeout}s): new tactic empty.\n")
                    q.put(f"Cannot prove lemma {lemma} (file:{file_path}) after {proof_attempt} attempts (timeout={timeout}s): new tactic empty.\n")
                    # with open(f'results/scriptResult_{lemma}_{filepath}', 'a') as r:
                    #     r.write(f"Cannot prove lemma {lemma} (file:{file_path}) after {proof_attempt} attempts (timeout={timeout}s): new tactic empty.\n")
                else:
                    if (tactic_updated == "Error in generation"):
                        print(f"Cannot prove lemma {lemma} (file:{file_path}) after {proof_attempt} attempts (timeout={timeout}s): problem in the tactic generation.\n")
                        q.put(f"Cannot prove lemma {lemma} (file:{file_path}) after {proof_attempt} attempts (timeout={timeout}s): problem in the tactic generation.\n")
                    else:
                        print(f"Cannot prove lemma {lemma} (file:{file_path}) after {proof_attempt} attempts (timeout={timeout}s): unclear reason.\n")
                        q.put(f"Cannot prove lemma {lemma} (file:{file_path}) after {proof_attempt} attempts (timeout={timeout}s): unclear reason.\n")
                    # with open(f'results/scriptResult_{lemma}_{filepath}', 'a') as r:
                    #     r.write(f"Cannot prove lemma {lemma} (file:{file_path}) after {proof_attempt} attempts (timeout={timeout}s): unclear reason.\nbound:{bound}, tactic={tactic}, tacticUpdated={tactic_updated}END")
        
def parallelInput(inputs,q):
    file_path = inputs[0]
    lemma = inputs[1]
    macro = ""
    bound=4
    heuristic="s"
    timeout=10
    diff=False

    splitLemma = lemma.split(" ")
    if len(splitLemma)>1:
        lemma = splitLemma[0]
        macro = splitLemma[1]


    for i in range(2,len(inputs)):
        if "bound" in inputs[i]:
            bound=inputs[i].split('=')[1]
        if "heuristic" in inputs[i]:
            heuristic=inputs[i].split('=')[1]
        if "timeout" in inputs[i]:
            timeout=inputs[i].split('=')[1]
        if "diff" in inputs[i]:
            diff=inputs[i].split('=')[1]
    #print(file_path, lemma, bound, heuristic, timeout, diff)
    proveUntil(file_path, lemma, macro, q, bound, heuristic, timeout, diff)

def listener(q):
    '''listens for messages on the q, writes to file. '''

    with open('results/scriptResult', 'a') as f:
        while 1:
            m = q.get()
            if m == 'kill':
                f.write('Finished\n')
                break
            f.write(str(m) + '\n')
            f.flush()

def parallelProving(inputs_parallel,N=5):
    #https://stackoverflow.com/questions/13446445/python-multiprocessing-safely-writing-to-a-file
    manager = multiprocessing.Manager()
    q = manager.Queue()
    pool = multiprocessing.Pool(N)

    #put listener to work first
    watcher = pool.apply_async(listener, (q,))

    #fire off workers
    jobs = []
    for i in inputs_parallel:
        job = pool.apply_async(parallelInput, (i, q))
        jobs.append(job)

    # collect results from the workers through the pool result queue
    for job in jobs: 
        job.get()

    #now we are done, kill the listener
    q.put('kill')
    pool.close()
    pool.join()


# Idea: we try to prove the lemma until 1)we have a proof, 2)we meet the user defined bound for the number of proof, 3)the exported tactic does not change anymore
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Tries to prove a lemma given a heuristic, \
                                        if proof fails, generate a tactic and tries again with it."
    )
    parser.add_argument("spthy_file", help="path to target spthy file")
    parser.add_argument("lemma", help="lemma that need to be proven",)
    parser.add_argument("-b", "--bound", type=int, default=3, help="max number of proof attempt")
    parser.add_argument("--heuristic", type=str, default="s", help="heuristic to use as the default for first attempt")
    parser.add_argument("--timeout", type=int, default=6000, help="timeout in s, default:6000")
    parser.add_argument("--diff", action='store_true', help="set if diff protocol")

    args = parser.parse_args()
    file_path = args.spthy_file
    lemma = args.lemma
    bound = int(args.bound)
    heuristic = args.heuristic
    
    timeout = args.timeout
    diff = args.diff
    
    parallelProving([[file_path, lemma]])
