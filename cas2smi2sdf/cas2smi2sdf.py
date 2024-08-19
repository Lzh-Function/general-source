import numpy as np
import pandas as pd
from pubchempy import get_properties
from rdkit import Chem
from rdkit.Chem import AllChem
from openbabel import pybel
import os
from argparse import ArgumentParser
import requests
from datetime import datetime

# cas to smiles
def cas2smi(args):
    """
    input
    df_path ... path of .csv file contained cas-number(column name: cas)
    url ... API (notification)
    csv_dir_path ... path of the directory which you want to put in df_smiles(.csv)
    name ... result(.csv) name

    output
    df_smiles ... DataFrame of SMILES 
    """

    df_cas = pd.read_csv(args.df_path, index_col=0)
    all_cas = df_cas["cas"]
    length = len(all_cas)
    df_smiles = pd.DataFrame([], columns=["CID", "CAS", "IsomericSMILES", "XLogP", "MolecularWeight", "MolecularFormula", "IUPACName"])
    properties = ["IsomericSMILES", "XLogP", "MolecularWeight", "MolecularFormula", "IUPACName"]
    
    payload = {"text": f"cas2smi start: {length}"}
    r = requests.post(url=args.url, json=payload)

    # get_properties
    cas_done = []
    for i, cas in enumerate(all_cas):
        if (cas not in cas_done) and (cas != np.nan):
            try:
                info = get_properties(properties, cas, "name", as_dataframe=True)
            except:
                cas_done.append(cas)
                if (i+1) % 10000 == 0:
                    payload = {"text": f"cas2smi {i+1}/{length} done."}
                    r = requests.post(url=args.url, json=payload)
                    continue
        else:
            continue
        
        info["CAS"] = cas
        info["CID"] = info.index

        df_smiles = pd.concat([df_smiles, info], axis=0)
        cas_done.append(cas)

        if (i+1) % 10000 == 0:
            payload = {"text": f"cas2smi {i+1}/{length} done."}
            r = requests.post(url=args.url, json=payload)
    
    df_smiles.reset_index(inplace=True, drop=True)
    df_smiles.to_csv(os.path.join(args.csv_dir_path, f"{datetime.now().strftime("%Y%m%d")}_{args.name}.csv"))
    
    payload = {"text": "cas2smi finished."}
    r = requests.post(url=args.url, json=payload)

    return df_smiles

# split
def split_longest(smi):
    smi = smi.split(".")
    max_index = max(range(len(smi)), key=lambda i: len(smi[i]))
    return smi[max_index]

# smiles to sdf
def smi2sdf(df_smiles, args):
    """
    input
    url ... API (notification)
    sdf_dir_path ... path of the directory which you want to put in .sdf file

    output
    failed ... list of SMILES which failed to generate structure
    """
    smiles = df_smiles["IsomericSMILES"]
    
    smiles.apply(split_longest)
    length = len(smiles)

    payload = {"text": f"smi2sdf start: {length}"}
    r = requests.post(url=args.url, json=payload)

    failed = []

    for i, smi in enumerate(smiles):
        try:
            ligs = pybel.readstring("smi", smi)
            ligs.localopt()
        except:
            failed.append([i, smi])
            if (i+1) % 10000 == 0:
                payload = {"text": f"smi2sdf {i+1}/{length} done."}
                r = requests.post(url=args.url, json=payload)
            continue

        fileout = os.path.join(args.sdf_dir_path, f"{i}.sdf")
        ligs.write("sdf", fileout)

        if (i+1) % 10000 == 0:
            payload = {"text": f"smi2sdf {i+1}/{length} done."}
            r = requests.post(url=args.url, json=payload)
    
    payload = {"text": "smi2sdf finished."}
    r = requests.post(url=args.url, json=payload)

    return failed

def main(args):
    df_smiles = cas2smi(args)
    failed = smi2sdf(df_smiles, args)
    if len(failed) != 0:
        if len(failed) <= 10:
            for smi in failed:
                print(f"failed: {smi[1]}")
        else:
            print("failed smi were more than 10")
        with open(os.path.join(args.csv_dir_path, f"{datetime.now().strftime("%Y%m%d")}_{args.name}_failed.txt"), "w") as f:
            for smi in failed:
                f.write(str(smi) + "\n")
    else:
        print("no failed smi")

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--df_path")
    parser.add_argument("--csv_dir_path")
    parser.add_argument("--name")
    parser.add_argument("--sdf_dir_path")
    parser.add_argument("--url")
    args = parser.parse_args()
    
    main(args)
