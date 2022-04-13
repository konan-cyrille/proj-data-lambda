import pandas as pd
import json


def drugs_referenced_in(df_d, df_j):
    drugs = df_d.drug.to_list()
    drugs = [d.lower() for d in drugs]
    json_output = {}
    for drug in drugs:
        list_ref_in = []
        for ind, row in df_j.iterrows():
            #print(row)
            if drug in row['title'].lower():
                ref_in = {'date':row['date'], 'journal':row['journal']}
                list_ref_in.append(ref_in)
        json_output[drug] = list_ref_in
        
    return json_output


df_drugs = pd.read_csv("../data/drugs.csv")
df_clinical_trials = pd.read_csv("../data/clinical_trials.csv")
df_pubmed = pd.read_csv("../data/pubmed.csv")

df_clinical_trials["source"] = "clinical_trials"
df_pubmed["source"] = "pubmed"
df_clinical_trials.rename(columns={'scientific_title':'title'}, inplace=True)

df_to_concat = [df_clinical_trials, df_pubmed]
# df_clinical_trials[["date", "scientific_title", "journal"]].append(df_pubmed[["date", "title", "journal"]])
df_joined = pd.concat(df_to_concat)
df_joined = df_joined[["title", "date", "journal","source"]]

df_output = drugs_referenced_in(df_drugs, df_joined)

with open("output_json.json", "w") as outfile:
    json.dump(df_output, outfile, indent=4)