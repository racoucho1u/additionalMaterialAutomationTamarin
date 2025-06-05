This files contains the python scripts necessary for reproducing the experiences described in the paper as well as generating the tables of results.
Since the benchmarks are very long to run and the results files are to heavy to be stored on a git, we also provide a file data.json that contains the data extracted from our results, before analysis.

#### Running the strategies benchmark.
Running the strategy benchmark requires to create the folders develop,escapeFinal,proba,smartmarin,backtracking,blacklisting and to clone the corresponding tamarin git inside (see Table below).

| Strategy    | Folder | Link to git | Description |
| -------- | ------- | ------- | ------- |
| Develop  | develop | [develop](https://github.com/tamarin-prover/tamarin-prover), commit 9c3f9e59 | Default heuristic |
| Escape | escapeFinal   | [escape](https://anonymous.4open.science/r/tamarin-prover-0833) | Deprioritize goals in loop |
| Backtrack    | backtracking    | [backtrack](https://anonymous.4open.science/r/tamarin-prover-7D14/) | Backtracking to the goal before the loop |
| Blacklist | blacklisting | [blacklist](https://anonymous.4open.science/r/tamarin-prover-EFD7) | Backtracking and deprioritizing the goals responsible for backtracking |
| Probabilistic | proba | [probabilistic](https://anonymous.4open.science/r/tamarin-prover-7C6D/) | Choose a problematic goal with decreasing probability |
|SmartTamarin | smartmarin | [smartTamarin](https://anonymous.4open.science/r/tamarin-prover-8CDB/) | Deprioritize branches rather than goals |



Then the benchmark can be run with the command `python3 benchmark.py`. The results of this lemmas will be store in the directory propre.
To extract information from these results, you can run the script `python3 generateDataJson.py` that will generate the file data.json.

#### Running the tactic generation benchmark.
Running the tactic generation benchmark requiers to create a folder tacticGeneration and to clone the corresponding git inside ([tactic-generation](https://anonymous.4open.science/r/tamarin-prover-8725/)).
To run the benchmark, you can then run `python3 tacticGenBench.py`. The results will be stored in the foolder results.
To extract information from these results, you can run the script `python3 generateDataJson,py` that will generate the file data.json.

#### Analysing the results.
To analyse the results, we provide the script `results.py` that generates the tables and graph presented in the paper and stores them in the forlders tables and graphs.
