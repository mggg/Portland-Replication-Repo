# Portland Rank Choice Voting Replication Repository

This repository contains the code and data used to replicate the findings of the study conducted by MGGG on rank choice voting for Portland, Oregon's 2024 city council election.

## How to Replicate

To replicate the study results on a high-performance cluster for both relevant bloc scenarios:

1. Navigate to the respective folder.
2. Run the following command:

```console
$ sbatch runner.sh
```

This generates JSON files representing simulated elections in the `Results` folder, along with visual representations of each election in the `Histograms` folder. You can track the progress of each election run on the cluster by accessing its respective file in the `Port_logs`, while the terminal output for each run is stored in the `Port_outputs` folder.

For instance, to replicate the scenarios involving two voting blocs, execute the above command within the `1000_Election_Results/2_bloc` directory.

## Election Scenarios  

Within this study, the following election scenarios were used to simulate rank choice voting patterns in Portland:  

|  | Voter Cohesion/Crossover Scenario                | Support splits in 3-bloc setting (POC-WP-WM) | Support splits in 2-bloc setting (POC-W) |
|---------|--------------------------------------------------|---------------------------------------------|------------------------------------------|
| A       | Race predominates                                | 80-10-10 / 10-45-45 / 10-45-45             | 80-20 / 10-90                            |
| B       | Race+Ideology                                    | 60-30-10 / 30-60-10 / 10-10-80             | 60-40 / 25-75                            |
| C       | Low polarization                                 | 40-30-30 / 30-40-30 / 30-30-40             | 60-40 / 40-60                            |
| D       | Ideology predominates                           | 45-45-10 / 45-45-10 / 10-10-80             | N/A                                      |
| E       | WP prefer POC                                    | 80-10-10 / 80-10-10 / 10-10-80             | 80-20 / 40-60                            |
| F       | Race+Ideology with strong POC cohesion           | 80-10-10 / 30-60-10 / 10-5-85              | 80-20 / 30-70                            |
| G       | POC crossover, WP major crossover                | 60-30-10 / 45-45-10 / 10-5-85              | 60-40 / 30-70                            |

Each election scenerio was run 1000 times.

The code for setting up these scenarios is located in  `submit_port.sh` for each corresponding bloc.

## Data  

## Notes
Due to the computational demands of the election scenarios, the simulations were executed on a high-performance cluster. The completion time for the two-bloc scenarios averaged approximately 10 hours, while the three-bloc runs required approximately 20 hours to finish.
