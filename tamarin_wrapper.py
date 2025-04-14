import argparse
import copy
import itertools
import json
import os
import signal
import subprocess
import pprint
from tabulate import tabulate
import numpy as np
import matplotlib.pyplot as plt
from datetime import date
import csv
import time

import tacticExportPoC as te

ignore = False


def create_commands(model, executable, ram, cores, lemmas, preprocess_flags, tam):
    finished_commands = []
    prefix = ''
    # if timeout:
    #    prefix += 'timeout %i ' % timeout
    prefix += executable + ' ' + model + ' '
    infix = ''
    if ram:  # does not work
        print("RAM is currently not supported")
        exit()
        infix += "+RTS -N%i -M%i -RTS " % (cores, ram * 1024)
    else:
        infix += "+RTS -N%i -RTS " % cores
    preprocess_flags_string = ''
    if preprocess_flags:
        for ffl in preprocess_flags:
            preprocess_flags_string += '-D=%s ' % ffl
    lemma_strings = []
    for lemma in lemmas:
        lemma_strings.append('--prove=%s ' % lemma)
    for lemma_s in lemma_strings:
        command = prefix + lemma_s + infix + preprocess_flags_string + tam
        finished_commands.append((model, command, lemma_s.split("=")[1]))
    return finished_commands


def run_tamarin(cmd, timeout, silent, log):
    process = subprocess.Popen(cmd, cwd=os.path.dirname(os.path.realpath(__file__)), stderr=subprocess.STDOUT,
                               stdout=subprocess.PIPE, start_new_session=True, shell=True)
    try:
        output, errors = process.communicate(timeout=timeout)
        if "Maude returned warning" in str(output):
            with open ("debugFile",'a') as df:
                df.write("maude error\n")
                df.write(str(time.localtime()))
                df.write(cmd+"\n")
                df.write(str(output)+"\n")
                df.write(str(proof_results)+"\n")
            return "AssociativeFailure", ''
        elif "CallStack" in str(output) or "internal error" in str(output):
            with open ("debugFile",'a') as df:
                df.write("Other error\n")
                df.write(str(time.localtime()))
                df.write(cmd+"\n")
                df.write(str(output)+"\n")
                df.write(str(proof_results)+"\n")
            return "TamarinError", ''

        proof_tactics = [line for line in str(
            output).split('\\n') if ("---" in line)]
        proof_results = [line for line in str(
            output).split('\\n') if ("steps" in line)]
        if len(proof_results) >= 1:
            for line in proof_results:
                if "verified" in line:
                    return line, True
                if "falsified" in line:
                    return line, False
        with open ("debugFile",'a') as df:
            df.write("Scripting error\n")
            df.write(str(time.localtime())+"\n")
            df.write(cmd+"\n")
            df.write(str(output)+"\n")
            df.write(str(proof_results)+"\n")
        return "killed?", proof_tactics

    except subprocess.TimeoutExpired as timeErr:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        outs, errs = process.communicate()
        proof_tactics = [line for line in str(
            outs).split('\\n') if ("---" in line)]
        return "timeout", proof_tactics #


def get_lemma(model, executable, preprocess_flags):
    command = "%s %s" % (executable, model)
    preprocess_flags_string = ''
    if preprocess_flags:
        for ffl in preprocess_flags:
            preprocess_flags_string += ' -D=%s' % ffl
    command += preprocess_flags_string
    process = subprocess.Popen(command.split(' '), cwd=os.path.dirname(os.path.realpath(__file__)),
                               stderr=subprocess.STDOUT,
                               stdout=subprocess.PIPE, start_new_session=True, shell=False)
    try:
        output, errors = process.communicate()
        if "Maude returned warning" in str(output):
            return "AssociativeFailure", ''
        elif "CallStack" in str(output) or "internal error" in str(output):
            return "TamarinError", ''

        proof_results = [line.split(' ')[2] for line in str(
            output).split('\\n') if ("steps" in line)]
        if len(proof_results) > 0:
            return "Success", proof_results
        else:
            return "NoLemmas", []
    except Exception:
        return "Error", []


def load_json(file):
    try:
        with open(file) as json_file:
            data = json.load(json_file)
            return data
    except Exception:
        print("Not a valid JSON format")
        exit()


def parse_arguments(parsed_args):
    model_dict = dict()
    model_dict[parsed_args.filename] = dict()
    ignore = parsed_args.ignore
    model_dict[parsed_args.filename]["executable"] = parsed_args.name
    model_dict[parsed_args.filename]["timeout"] = parsed_args.timeout
    model_dict[parsed_args.filename]["ram"] = parsed_args.ram
    model_dict[parsed_args.filename]["cores"] = parsed_args.cores
    model_dict[parsed_args.filename]["silent"] = parsed_args.silent
    model_dict[parsed_args.filename]["log"] = parsed_args.log
    model_dict[parsed_args.filename]["tamcommand"] = parsed_args.tam
    if parsed_args.preprocess:
        model_dict[parsed_args.filename]["preprocess_flags"] = [
            item for item in parsed_args.preprocess.split(',')]
    else:
        model_dict[parsed_args.filename]["preprocess_flags"] = []
    if parsed_args.lemmas:
        model_dict[parsed_args.filename]["lemmas"] = [
            item for item in parsed_args.lemmas.split(',')]
    else:
        executable = model_dict[parsed_args.filename]["executable"]
        preprocess_flags = model_dict[parsed_args.filename]["preprocess_flags"]
        is_lemmas = get_lemma(parsed_args.filename,
                              executable, preprocess_flags)
        if is_lemmas[0] == "Success":
            model_dict[parsed_args.filename]["lemmas"] = is_lemmas[1]
        else:
            print(parsed_args.filename + " has no lemmas")
            exit()
    # parsed later
    model_dict[parsed_args.filename]["flags"] = parsed_args.flags
    return model_dict


def get_implications(status, orders, nextvalue, restrictions):
    if status:
        new_cross_prod = []
        for i in range(len(nextvalue)):
            if nextvalue[i] == "":
                new_cross_prod.append([""])
            else:
                smaller = [nextvalue[i]]
                for order in orders:
                    if nextvalue[i] == order[0]:
                        smaller.append(order[1])
                smaller.append("")
                new_cross_prod.append(smaller)
        resultlist = list(itertools.product(*new_cross_prod))
    else:
        new_cross_prod = []
        for i in range(len(nextvalue)):
            if nextvalue[i] == "":
                new_cross_prod.append(restrictions[i] + [""])
            else:
                bigger = [nextvalue[i]]
                for order in orders:
                    if nextvalue[i] == order[1]:
                        bigger.append(order[0])
                new_cross_prod.append(bigger)
        resultlist = list(itertools.product(*new_cross_prod))
    resultlist.remove(nextvalue)
    if resultlist:
        return resultlist
    else:
        return []



def execute_model(model, commands, log, silent, timeout):
    results = []
    for (model, command, lemma) in commands:
        if not silent:
            print(model, lemma)
        # result_list = [["Protocol", "Lemma", "Verified", "#Steps", "List of Flags"]]
        # result should have the form (model, lemma, status, steps, [flags])
        start = time.time()
        res, status = run_tamarin(command, timeout, silent, log)
        finaltime = time.time() - start
        if res in ["TamarinError", "timeout", "AssociativeFailure","killed?"]:
            steps = -1
            tactic = te.extractTacticsParams(status)
            status = res
            results.append([lemma, status, finaltime, steps, tactic])
        else:
            tmplist = res.split()
            steps = tmplist[tmplist.index('steps)') - 1][1:]
            results.append([lemma, status, finaltime, steps, []])
    return results


def main(parsed_args):
    start_exec_time = time.time()
    if parsed_args.filename:
        query_dict = parse_arguments(parsed_args)

    fulltable = []
    if not os.path.exists('results'):
        os.makedirs('results')
    for model in query_dict.keys():
        flags = query_dict[model]["flags"]
        commands = create_commands(model,
                                   query_dict[model]["executable"],
                                   query_dict[model]["ram"],
                                   query_dict[model]["cores"],
                                   query_dict[model]["lemmas"],
                                   query_dict[model]["preprocess_flags"],
                                   query_dict[model]["tamcommand"])
        if not query_dict[model]["silent"]:
            print("Number of created commands: %i" % len(commands))
            for command in commands:
                print(command)
        start_full_exec = time.time()
        cleaned_results = execute_model(model,
                                        commands,
                                        query_dict[model]["log"],
                                        query_dict[model]["silent"],
                                        query_dict[model]["timeout"])
        finalprocesstime = time.time() - start_full_exec
        for l in cleaned_results:
            print(" ".join(str(x) for x in l))


def pre_process():
    '''
    Parse input
    '''

    parser = argparse.ArgumentParser(description='A cool wrapper for tamarin')
    parser.add_argument('-n', '--name', type=str, default='tamarin-prover',
                        help='name of the tamarin executable')  # WORKING
    parser.add_argument('-t', '--timeout', type=int, default=60000,
                        help='timeout in seconds per execution')  # WORKING
    parser.add_argument('-r', '--ram', type=int,
                        help='max RAM in Gb')  # TODO currently not working/supported
    parser.add_argument('-c', '--cores', type=int,
                        help='max cores', default=min(os.cpu_count(), 4))  # WORKING
    parser.add_argument('-s', '--silent', action="store_true",
                        help='surpress tamarin output in the terminal')  # TODO working but stupid
    parser.add_argument('-o', '--log', action="store_true",
                        help='create a log file')  # TODO not implemented
    parser.add_argument('-i', '--ignore', action="store_true", default=False,
                        help='ignore timeouts and erros in the results')  # WORKING
    parser.add_argument('-l', '--lemmas', type=str,
                        help='string of lemmas to prove comma separated')  # WORKING
    parser.add_argument('-p', '--preprocess', type=str,
                        help='string of preprocessor flags which are needed (comma separated)')  # WORKING
    parser.add_argument('-fl', '--flags', type=str,
                        help='file containing preprocessor flags. Check documentation for format')  # WORKING
    parser.add_argument('--tam', type=str, default='',
                        help='string of additional tamarin flags. E.g.: --tam="--auto-sources"')  # WORKING
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('filename', nargs='?', type=str)  # WORKING
    group.add_argument('-f', '--file', default=None,
                       help='input commands as .tamjson file')  # WORKING
    args = parser.parse_args()
    main(args)


if __name__ == '__main__':
    pre_process()
