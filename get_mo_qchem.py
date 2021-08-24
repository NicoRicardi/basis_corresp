#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 24 13:52:30 2021

@author: nico
"""

import CCJob as ccj
import CCJob.utils as ut
from CCJob.Composable_templates import Tdefaults, Tinp, Trem_kw, Tmolecule, Tbasis
#import slurm_stuff_yggdrasil as slrm
import slurm_stuff_baobab as slrm
import sys
import os

def get_qchem_coeffs(xyz, basfile, print_orbitals=20):
    root = os.getcwd()
    basname = basfile.replace(".nwchem", "")
    meta_HF  = dict(method="HF", status=None, basename="mp2")
    meta_HF["path"] = os.path.join(root, basname)
    already_done = ut.status_ok(path=meta_HF["path"])
    if already_done == False:
        memory = 14000
        bs_kw = "gen"  
        bs_string = ut.read_file("aug-cc-pVDZ.bas")
        if bs_string[-1] == "\n":
            bs_string = bs_string[:-1]
        rem_extras = ["thresh = 14", "basis_lin_dep_thresh = 5"]
        extra_basic = Tbasis.substitute(**{"basis_specs": bs_string})
        rem_kw = Trem_kw.substitute(Tdefaults["rem_kw"], **dict(memory=memory, 
                                    method="hf", basis=bs_kw, print_orbitals=print_orbitals,
                                    rem_extras="\n".join(rem_extras)))
        with open(xyz, "r") as f:
            lines = f.readlines()
        coords = "".join(lines[2:])
        molecule = Tmolecule.substitute(Tdefaults["molecule"], **dict(xyz=coords))
        specs_HF = ut.myupd(Tdefaults["inp"], rem_kw=rem_kw, molecule=molecule, extras=extra_basic)
        queue_HF = dict(** slrm.shabug_M)  
        ut.run_job(specs_HF, queue_HF, meta_HF, Tinp,  
                batch_mode=False)  # because we want to extract data and copy matrices
        
        ut.save_status(meta_HF)

if __name__ == "__main__":
    _, xyz, basfile = sys.argv
    get_qchem_coeffs(xyz, basfile)