import os
from enum import Enum
from dataclasses import dataclass, asdict
import json


def parse_folder(strats: dict[str, dict], lemma_types, folder: str):
    could_not_parse = []
    for dirpath, dirnames, filenames in os.walk(folder):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            # print(f"File: {full_path}")
            try:
                strategy_name = dirpath.split("/")[-2]
                theory_dir = "_".join(dirpath.split("/")[-1].split("_")[1:-1])
                (theory_file, lemma_name) = filename.split("__")
                lemma_name = (
                    lemma_name.replace("_total.spthy", "")
                    .replace("_time.spthy", "")
                    .replace("_recap.spthy", "")
                    .replace("_total_summary.spthy", "")
                )
                theory_and_lemma=f"{theory_file}__{theory_dir}__{lemma_name}"
                #print(theory_and_lemma)
                #print(f"strat: {strategy_name}")
                #print(filename)
                #print(f"lemma: {lemma_name}")
                strategy = strats.get(strategy_name)
                if strategy is None:
                    strategy = {"name": strategy_name, "lemmas": {}}
                    strats[strategy_name] = strategy
                lemma = strategy["lemmas"].get(theory_and_lemma)

                if lemma is None:
                    #print(lemma_name)
                    lemma = {
                        "name": lemma_name,
                        "theory_file": theory_file,
                        "theory_dir": theory_dir,
                        "lemma_type": get_lemma_type(theory_file, lemma_name,theory_dir, lemma_types),
                        "oracleStatus": get_oracle_status(theory_file, lemma_name,theory_dir, lemma_types),
                        "time": 0,
                        "status": "timeout",
                        "tactic": "",
                        "reason": ""
                    }
                    #print(strategy_name)
                    strategy["lemmas"][theory_and_lemma] = lemma
                    #print(strategy["lemmas"][theory_and_lemma])
                parse_file(strategy_name,filename,full_path, lemma)
                #if (strategy_name == "smartverif"):
                    #print()
                # print(f"lemma: {lemma}")
                # print("---")
            except:
                could_not_parse .append(full_path)
    # print(f"could not parse : {could_not_parse }")

def get_lemma_type(theory_file, lemma_name,theory_dir, lemma_types):
    fail, debug = 0, False
    #if lemma_name == "noninjectiveagreementREADER" or lemma_name == "noninjectiveagreementTAG":
        #debug = True
    for truc in lemma_types["dicts"]:
        if truc["filename"]==theory_file and truc["dirname"]==theory_dir:
            #fail =1
            #if debug:
                #print(theory_file)
                #print(truc)
            for lemma in truc["lemmas"]:
                if lemma["lemmaName"] == lemma_name:
                    #if debug:
                        #print(theory_file)
                        #print(lemma_name)
                        #print(lemma["type"])
                    type = str(lemma["type"])
                    if "3" in type and "5" in type:
                        type = type.replace("5",'')
                        print('changing?')
                    return type
    print(f"{theory_dir}A")
    print(f"{theory_file}A")
    print(lemma_name)
    print()
    return ""

def get_oracle_status(theory_file, lemma_name,theory_dir, lemma_types):
    for truc in lemma_types["dicts"]:
        if truc["filename"]==theory_file and truc["dirname"]==theory_dir:
            for lemma in truc["lemmas"]:
                if lemma["lemmaName"] == lemma_name:
                    return str(lemma["oracleStatus"])
    return ""


def parse_time(file_path: str, lemma: dict[str,str|float]):
    with open(file_path, "r") as f:
        content = f.read()
        time = float(content.strip())
        lemma["time"]=time

def parse_total(file_path: str, lemma: dict[str,str|float]):
    with open(file_path, 'rb') as file:
        file.seek(-2, os.SEEK_END)
        while file.read(1) != b'\n':
            file.seek(-2, os.SEEK_CUR)
        last_line = file.readline().decode().strip()
        if "Killed" in last_line:
            lemma["status"]="killed"

def parse_smart(file_path: str, lemma: dict[str,str|float]):
    with open(file_path, 'rb') as file:
        file.seek(-2, os.SEEK_END)
        while file.read(1) != b'\n':
            file.seek(-2, os.SEEK_CUR)
        last_line = file.readline().decode().strip()
        if "Verification Starts" in last_line:
            lemma["status"]="killed"
        # else:
        #     print(file_path)


def parse_file(strategy_name: str, filename: str, full_path: str, lemma: dict[str,str|float]):
    if strategy_name != "smartverif":
        if filename.endswith("total.spthy"):
            parse_total(full_path, lemma)
        elif filename.endswith("time.spthy"):
            parse_time(full_path, lemma)
        elif filename.endswith("recap.spthy") or filename.endswith("total_summary.spthy"):
            lemma["status"]="finito"
            lemma["reason"]="already proven"
    else:
        if filename.endswith("total.spthy"):
            parse_smart(full_path, lemma)
        elif filename.endswith("time.spthy"):
            parse_time(full_path, lemma)  

def parse_tactic_gen(strat_dict,strategy_name,folder):
    with open (folder+"/scriptResult") as tacGen:
        lines = tacGen.readlines()
        for l in lines:
            #Cases where a proof has been reached
            if l != '\n':
                if '{' in l:
                    splitLine = l.split(' ')
                    lemma_name = splitLine[2].split('\t')[0]
                    theory_file = splitLine[3].split('/')[-1].split('.')[0]
                    theory_dir	= splitLine[3].split('/')[-2]
                    tactic = splitLine[-1][1:-3]
                    reason = "proved"
                    # print(f"{lemma_name} {theory_file} {theory_dir} {tactic}")
                else:
                    splitLine = l.split(' ')
                    # print(splitLine)
                    lemma_name = splitLine[3].split('\t')[0]
                    theory_file = splitLine[4].split('/')[-1].split('.')[0]
                    # print(splitLine[4])
                    # print(l)
                    theory_dir	= splitLine[4].split('/')[-2]
                    tactic = ""
                    reason = ' '.join(splitLine[5:])[:-2]
                    # print(f"{lemma_name} {theory_file} {theory_dir} {tactic}")
            theory_and_lemma=f"{theory_file}__{theory_dir}__{lemma_name}"
            strat_dict[strategy_name]['lemmas'][theory_and_lemma]['tactic'] = tactic
            strat_dict[strategy_name]['lemmas'][theory_and_lemma]['reason'] = reason
        



strat_dict: dict[str, dict] = {}

with open('metaData.json', 'r') as file:
    lemma_types = json.load(file)

    parse_folder(strat_dict,lemma_types, "propre")
    parse_tactic_gen(strat_dict,"escapeFinal","propre/tacticGenEscape")
    
with open('oui.json', 'w') as f:
    json.dump(lemma_types, f,indent=4)

with open('data.json', 'w') as file:
    json.dump(strat_dict, file,indent=4)
















