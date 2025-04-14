This files contains the python scripts necessary for reproducing the experiences described in the paper as well as generating the tables of results.
Since the benchmarks are very long to run and the results files are to heavy to be stored on a git, we also provide a file data.json that contains the data extracted from our results, before analysis.

#### Running the strategies benchmark.
Running the strategy benchmark requires to create the folders develop,escapeFinal,proba,smartmarin,backtracking,blacklisting and to clone the corresponding tamarin git inside. The links are provided in the paper.
Then the benchmark can be run with the command `python3 benchmark.py`. The results of this lemmas will be store in the file propre.
To extract information from these results, you can run the script `python3 generateDataJson,py` that will generate the file data.json.

#### Running the tactic generation benchmark.
Running the tactic generation benchmark requiers to create a folder tacticGeneration and to clone the corresponding git inside.
To run the benchmark, you can then run `python3 tacticGenBench.py`. The results will be stored in the foolder results.
To extract information from these results, you can run the script `python3 generateDataJson,py` that will generate the file data.json.

#### Analysing the results.
To analyse the results, we provide the script `results.py` that generates the tables and graph presented in the paper and stores them in the forlders tables and graphs.
