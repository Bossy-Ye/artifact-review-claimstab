#!/usr/bin/env python
"""Validated reconstruction + budget-sensitivity for EX-C3, EX-C5, EX-C6, EX-C7.

Modes:
  compute <REC> <s0> <s1>   compute raw cells for seeds [s0,s1] -> recon_raw/<REC>_<s0>_<s1>.jsonl
                            (use the locked toolchain; C6 must be chunked to at most
                             20 seeds per process to avoid native pytket instability)
  verify (default)          recompute gate/diff/expansion rows in memory and compare them
                            with the committed CSVs (plain python3; read-only)
  consolidate               explicitly replace gate/diff/expansion CSVs

The metric/transpilation logic is the locked reconstruction used for the
reported expansion. The original long-run driver is not included in this
anonymous package; consolidation is independently re-runnable from the shipped
raw JSONL and Tier-1 per-cell inputs.
"""
import sys, csv, json, math, random, itertools, glob, os
from math import sqrt

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
LOCKED = REPO + "/artifact/external_audit/tier1_robustness/per_cell_inputs/"
OUT = REPO + "/artifact/external_audit/budget_sensitivity"
RAW = OUT + "/recon_raw"
Z = 1.959963985; TAU = 0.95

ARCH = [(0,1),(1,2),(2,3)]; OPTS = [0,1,2,3]
DENSE_QUBITS = 10; DENSE_REMOVED = [(0,1),(2,3),(4,5),(6,7),(8,9)]
CIRCUITS = {
 "linear_3_remote_cx": '\nOPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[3];\nh q[0];\ncx q[0],q[2];\ncx q[2],q[1];\ncx q[0],q[1];\n',
 "linear_4_crossing_ladder": '\nOPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[4];\nh q[0];\nh q[3];\ncx q[0],q[3];\ncx q[3],q[1];\ncx q[0],q[2];\ncx q[2],q[1];\ncx q[3],q[0];\n',
 "linear_4_bidirectional_mix": '\nOPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[4];\nh q[0];\ncx q[0],q[3];\ncx q[1],q[3];\ncx q[3],q[2];\ncx q[2],q[0];\ncx q[1],q[0];\ncx q[3],q[1];\n',
 "linear_4_repeated_remote": '\nOPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[4];\nh q[0];\ncx q[0],q[3];\ncx q[0],q[2];\ncx q[3],q[1];\ncx q[1],q[3];\ncx q[2],q[0];\ncx q[3],q[0];\ncx q[1],q[2];\n',
}
KIND = {"EX-C3":"line","EX-C5":"line","EX-C7":"line","EX-C6":"dense"}

def wilson(k,n,z=Z):
    if n==0: return (0.0,1.0)
    p=k/n; den=1+z*z/n; c=(p+z*z/(2*n))/den
    h=(z/den)*sqrt(p*(1-p)/n+z*z/(4*n*n)); return (max(0.0,c-h),min(1.0,c+h))
def classify(lo,hi):
    return "Sustained" if lo>=TAU else ("Reversed" if hi<=1-TAU else "Unresolved")
def lab(a,b):
    return "preserved" if a<b else ("tied" if a==b else "contradicted")

def compute(rec, s0, s1):
    os.makedirs(RAW, exist_ok=True)
    from qiskit import qasm2, transpile, QuantumCircuit
    from qiskit.transpiler import CouplingMap
    from pytket.architecture import Architecture
    from pytket.circuit import OpType
    from pytket.passes import DefaultMappingPass, DecomposeSwapsToCXs
    from pytket.qasm import circuit_from_qasm_str
    out=[]
    if KIND[rec]=="line":
        tket_cache={}
        for cn,qasm in CIRCUITS.items():
            c=circuit_from_qasm_str(qasm); a=Architecture(ARCH)
            DefaultMappingPass(a).apply(c); DecomposeSwapsToCXs(a).apply(c)
            tket_cache[cn]=dict(tket_cx_count=int(c.n_gates_of_type(OpType.CX)),
                                tket_2q_depth=int(c.depth_2q()), tket_depth=int(c.depth()))
            for opt in OPTS:
                for seed in range(s0,s1+1):
                    qc=qasm2.loads(qasm)
                    o=transpile(qc,basis_gates=["cx","u3"],coupling_map=CouplingMap([tuple(e) for e in ARCH]),
                                optimization_level=opt,seed_transpiler=seed)
                    raw=dict(tket_cache[cn], qiskit_cx_count=int(o.count_ops().get("cx",0)),
                             qiskit_2q_depth=int(o.depth(lambda i:len(i.qubits)==2)), qiskit_depth=int(o.depth()))
                    out.append(dict(record=rec, key=[cn,opt,seed], raw=raw))
    else:
        all_edges=list(itertools.combinations(range(DENSE_QUBITS),2))
        removed={tuple(e) for e in DENSE_REMOVED}; edges=[e for e in all_edges if e not in removed]
        for seed in range(s0,s1+1):
            for opt in OPTS:
                rng=random.Random(seed); lines=["OPENQASM 2.0;",'include "qelib1.inc";',f"qreg q[{DENSE_QUBITS}];"]
                for _ in range(40):
                    a,b=rng.choice(all_edges); lines.append(f"cx q[{a}],q[{b}];")
                qasm="\n".join(lines)+"\n"
                inp=QuantumCircuit.from_qasm_str(qasm); idp=int(inp.depth(lambda i:len(i.qubits)==2))
                qo=transpile(inp,basis_gates=["cx","u3"],coupling_map=CouplingMap(edges),optimization_level=opt,seed_transpiler=seed)
                qd=int(qo.depth(lambda i:len(i.qubits)==2))
                tc=circuit_from_qasm_str(qasm)
                DefaultMappingPass(Architecture(edges)).apply(tc); DecomposeSwapsToCXs(Architecture(edges)).apply(tc)
                td=int(tc.depth_2q())
                raw=dict(input_cx_depth=idp, qiskit_cx_depth=qd, pytket_cx_depth=td,
                         qiskit_overhead=(qd/idp if idp else None), pytket_overhead=(td/idp if idp else None))
                out.append(dict(record=rec, key=[seed,opt], raw=raw))
    fn=f"{RAW}/{rec}_{s0}_{s1}.jsonl"
    with open(fn,"w") as f:
        for r in out: f.write(json.dumps(r)+"\n")
    print(f"{rec} seeds {s0}-{s1}: {len(out)} cells -> {fn}")

MA={"EX-C3":"tket_cx_count","EX-C5":"tket_2q_depth","EX-C7":"qiskit_cx_count","EX-C6":"qiskit_overhead"}
MB={"EX-C3":"qiskit_cx_count","EX-C5":"qiskit_2q_depth","EX-C7":"tket_cx_count","EX-C6":"pytket_overhead"}
LOG={"EX-C3":"ext_2304_08814v2_claim5_measurements.csv","EX-C5":"ext_2409_08844v2_claim4_measurements.csv",
     "EX-C7":"ext_2409_08844v2_claim3_measurements.csv","EX-C6":"ext_2202_14025v1_legacy_claim6_measurements.csv"}
BASE={"line":[0,1,2,3,4],"dense":list(range(20))}
EXPN={"line":{80:5,160:10,240:15,320:20},"dense":{80:20,160:40,240:60,320:80}}

def fmatch(x,y,tol=1e-6):
    if x is None or y is None: return x==y
    return abs(float(x)-float(y))<=tol

def _normalize_rows(rows, fields):
    return [{field: str(row.get(field, "")) for field in fields} for row in rows]


def _write_rows(path, fields, rows):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _committed_rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def consolidate(*, write=False):
    cells={r:{} for r in KIND}
    for fn in glob.glob(RAW+"/*.jsonl"):
        for line in open(fn):
            d=json.loads(line); rec=d["record"]; cells[rec][tuple(d["key"])]=d["raw"]
    gate=[]; diff=[]; exp=[]
    for rec in ["EX-C3","EX-C5","EX-C6","EX-C7"]:
        kind=KIND[rec]; mA=MA[rec]; mB=MB[rec]
        locked={}
        for r in csv.DictReader(open(LOCKED+LOG[rec])):
            key=(r["circuit"],int(r["qiskit_optimization_level"]),int(r["qiskit_seed"])) if kind=="line" else (int(r["random_seed"]),int(r["qiskit_optimization_level"]))
            locked[key]=r
        base=BASE[kind]
        gkeys=[(c,o,s) for c in CIRCUITS for o in OPTS for s in base] if kind=="line" else [(s,o) for s in base for o in OPTS]
        nt=len(gkeys); mm=lm=0
        for key in gkeys:
            rc=cells[rec].get(key)
            lk=locked.get(key)
            if rc is None or lk is None:
                diff.append(dict(record_id=rec,key=str(key),note="MISSING recon or locked cell")); continue
            ra=rc[mA]; rb=rc[mB]; la=lk[mA]; lb=lk[mB]
            if kind=="line":
                ok=(int(ra)==int(float(la))) and (int(rb)==int(float(lb)))
            else:
                ok=fmatch(ra,la) and fmatch(rb,lb)
            rlab=lab(ra,rb); llab="preserved" if int(lk["outcome"])==1 else ("tied" if float(la)==float(lb) else "contradicted")
            mm+=int(ok); lm+=int(rlab==llab)
            if not (ok and rlab==llab):
                diff.append(dict(record_id=rec,key=str(key),recon_metric_A=ra,locked_metric_A=la,
                    recon_metric_B=rb,locked_metric_B=lb,recon_margin=float(ra)-float(rb),
                    locked_margin=float(la)-float(lb),recon_label=rlab,locked_label=llab,
                    metric_match=ok,label_match=(rlab==llab)))
        status="PASS" if (mm==nt and lm==nt) else ("LABEL_COMPATIBLE_METRIC_DRIFT" if lm==nt else "FAIL")
        gate.append(dict(record_id=rec,n_cells=nt,metric_match=f"{mm}/{nt}",label_match=f"{lm}/{nt}",gate_status=status,log=LOG[rec]))
        if status=="PASS":
            def stat(seedset):
                ks=[(c,o,s) for c in CIRCUITS for o in OPTS for s in seedset] if kind=="line" else [(s,o) for s in seedset for o in OPTS]
                p=t=c=0
                for key in ks:
                    rc=cells[rec][key]; L=lab(rc[mA],rc[mB])
                    p+=L=="preserved"; t+=L=="tied"; c+=L=="contradicted"
                n=len(ks); lo,hi=wilson(p,n); return n,p,t,c,lo,hi,classify(lo,hi)
            _,_,_,_,_,_,v_base=stat(list(range(EXPN[kind][80])))
            for N in [80,160,240,320]:
                n,p,t,c,lo,hi,v=stat(list(range(EXPN[kind][N])))
                exp.append(dict(record_id=rec,N=n,k_preserved=p,s_hat=f"{p/n:.4f}",ties=t,contradictions=c,
                    wilson_lower=f"{lo:.4f}",wilson_upper=f"{hi:.4f}",verdict=v,
                    verdict_change_from_N80=("(baseline)" if N==80 else ("yes" if v!=v_base else "no")),
                    method="re-sampled seed expansion (validated reconstruction)"))
    gate_fields=["record_id","n_cells","metric_match","label_match","gate_status","log"]
    diff_fields=["record_id","key","recon_metric_A","locked_metric_A","recon_metric_B","locked_metric_B","recon_margin","locked_margin","recon_label","locked_label","metric_match","label_match","note"]
    expansion_fields=["record_id","N","k_preserved","s_hat","ties","contradictions","wilson_lower","wilson_upper","verdict","verdict_change_from_N80","method"]
    outputs = [
        (OUT+"/reconstruction_gate_report.csv", gate_fields, gate),
        (OUT+"/reconstructed_vs_locked_diff.csv", diff_fields, diff),
        (OUT+"/expanded_seed_sensitivity.csv", expansion_fields, exp),
    ]
    stale=[]
    for path, fields, computed in outputs:
        if write:
            _write_rows(path, fields, computed)
        elif _committed_rows(path) != _normalize_rows(computed, fields):
            stale.append(os.path.relpath(path, REPO))
    print("=== GATE ===")
    for g in gate: print(f"  {g['record_id']}: metric {g['metric_match']} label {g['label_match']} -> {g['gate_status']}")
    print(f"diff rows: {len(diff)}")
    print("=== EXPANSION (PASS only) ===")
    for e in exp: print(f"  {e['record_id']} N={e['N']}: k={e['k_preserved']} tie={e['ties']} con={e['contradictions']} shat={e['s_hat']} W[{e['wilson_lower']},{e['wilson_upper']}] {e['verdict']} change={e['verdict_change_from_N80']}")
    if stale:
        for path in stale:
            print(f"STALE: {path}")
        return 1
    print("reconstruction outputs written" if write else "committed reconstruction outputs match raw evidence (read-only)")
    return 0

def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    mode = args[0] if args else "verify"
    if mode == "compute":
        if len(args) != 4:
            raise SystemExit("usage: recon_driver.py compute <EX-C3|EX-C5|EX-C6|EX-C7> <seed_start> <seed_end>")
        compute(args[1], int(args[2]), int(args[3]))
        return 0
    if mode == "verify":
        return consolidate(write=False)
    if mode == "consolidate":
        return consolidate(write=True)
    raise SystemExit("usage: recon_driver.py [verify|consolidate|compute ...]")


if __name__=="__main__":
    raise SystemExit(main())
