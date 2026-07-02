#!/usr/bin/env python3
"""Tier-1 (exact scalar-directional) robustness analysis for EX-C1..EX-C8.

Design-first statistical treatment that SEPARATES four things the manuscript
conflates:

  1. finite locked-design evidence        (k / N, ties, contradictions, margins)
  2. Wilson policy classification          (the predeclared S/U/R classifier)
  3. dependence-aware robustness           (cluster bootstrap, leave-one-cluster-out)
  4. tie-policy and threshold sensitivity  (tau in {0.90,0.95,0.99}; 3 tie policies)
  5. budget / seed-count expansion         (N = 80,160,240,320 where a validated
                                            larger trace already exists)

The Wilson rule and the cell-labeling convention are NOT re-derived: they are
reused verbatim from the locked artifacts and validated against the published
per-record numbers (per_claim_external_audit.csv, external_forest_data.csv) and
against the locked tie/contradiction split (expanded_seed_sensitivity.csv).

NO data is invented. Records without a per-cell file (EX-C2, EX-C4) have their
per-cell-dependent checks (cluster, leave-one-cluster-out, and for EX-C4 the
tie split) reported as NOT AVAILABLE, with the reason, rather than imputed.

Run from the repo root:  python3 artifact/external_audit/tier1_robustness/tier1_robustness_analysis.py
Deterministic: fixed RNG seed, B = 10,000 cluster-bootstrap resamples.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pandas as pd

# ----------------------------------------------------------------------------
# Locked constants (reused, not re-derived)
# ----------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[3]
OUTDIR = ROOT / "artifact/external_audit/tier1_robustness"
# Self-contained in the anonymous artifact: the 6 per-cell measurement CSVs are
# vendored locally under per_cell_inputs/ (EX-C2/EX-C4 are intentionally absent --
# their per-cell traces are not materialized). Aggregate and seed-expansion
# evidence are reused from their locked artifact locations.
PHASE1 = OUTDIR / "per_cell_inputs"
PER_CLAIM_AGG = ROOT / "artifact/results/paper/output/figures/section5/per_claim_external_audit.csv"
EXPANDED_SEED = ROOT / "artifact/external_audit/budget_sensitivity/expanded_seed_sensitivity.csv"

TAU_PRIMARY = 0.95
TAUS = [0.90, 0.95, 0.99]
B_BOOT = 10_000
SEED = 20240622
Z975 = NormalDist().inv_cdf(0.975)  # 1.9599639845... (exact; reproduces locked CIs)


def wilson_ci(k: float, n: int, z: float = Z975) -> tuple[float, float]:
    """Wilson score interval. Accepts float k for the tie half-preserving
    PROJECTION only (flagged downstream); integer k for all primary evidence."""
    if n <= 0:
        return 0.0, 1.0
    phat = k / n
    z2n = z * z / n
    denom = 1.0 + z2n
    center = (phat + z2n / 2.0) / denom
    half = (z / denom) * math.sqrt((phat * (1.0 - phat) / n) + (z * z) / (4.0 * n * n))
    return max(0.0, center - half), min(1.0, center + half)


def classify(lo: float, hi: float, tau: float = TAU_PRIMARY) -> str:
    """The predeclared Wilson policy classifier (verbatim from the locked rule)."""
    if lo >= tau:
        return "Sustained"
    if hi <= 1.0 - tau:
        return "Reversed"
    return "Unresolved"


# ----------------------------------------------------------------------------
# Record configuration. Cluster units are DESIGN-MOTIVATED (locked design axes),
# never chosen from outcomes.
# ----------------------------------------------------------------------------
RECORDS = [
    dict(rid="EX-C1", claim_id="ext_2202_14025v1_legacy_claim12",
         file=PHASE1 / "ext_2202_14025v1_legacy_claim12_measurements.csv",
         metric="compilation runtime (pytket vs Qiskit)",
         a_col="pytket_time_seconds", b_col="qiskit_time_seconds",
         cluster_col="circuit_size", cluster_name="circuit_size (benchmark size)",
         secondary_col="qiskit_optimization_level",
         axis_cols=["circuit_size", "qiskit_optimization_level", "repetition"]),
    dict(rid="EX-C2", claim_id="ext_2411_00518v2_claim1", file=None,
         metric="approximation ratio (knapsack QTG-copula)",
         agg_k=80, agg_N=80,
         cluster_name="knapsack instance (16 by locked design)",
         missing_reason="per-cell measurement trace for this record is not materialized in "
                        "the artifact; only the locked aggregate (N=80 k=80) is available"),
    dict(rid="EX-C3", claim_id="ext_2304_08814v2_claim5",
         file=PHASE1 / "ext_2304_08814v2_claim5_measurements.csv",
         metric="CNOT gate count (TKET vs Qiskit)",
         a_col="tket_cx_count", b_col="qiskit_cx_count",
         cluster_col="circuit", cluster_name="benchmark circuit",
         secondary_col="qiskit_optimization_level",
         axis_cols=["circuit", "qiskit_optimization_level", "qiskit_seed"]),
    dict(rid="EX-C4", claim_id="ext_2411_00518v2_claim3", file=None,
         metric="probability value (knapsack QTG-copula)",
         agg_k=45, agg_N=80,
         cluster_name="knapsack size (5 by locked design)",
         missing_reason="per-cell measurement trace for this record is not materialized in "
                        "the artifact; only the locked aggregate (N=80 k=45) is available; the "
                        "tie/contradiction split among the 35 non-preserved cells is not recoverable"),
    dict(rid="EX-C5", claim_id="ext_2409_08844v2_claim4",
         file=PHASE1 / "ext_2409_08844v2_claim4_measurements.csv",
         metric="two-qubit gate depth (TKET vs Qiskit)",
         a_col="tket_2q_depth", b_col="qiskit_2q_depth",
         cluster_col="circuit", cluster_name="benchmark circuit",
         secondary_col="qiskit_optimization_level",
         axis_cols=["circuit", "qiskit_optimization_level", "qiskit_seed"]),
    dict(rid="EX-C6", claim_id="ext_2202_14025v1_legacy_claim6",
         file=PHASE1 / "ext_2202_14025v1_legacy_claim6_measurements.csv",
         metric="CX-depth overhead (pytket vs Qiskit)",
         a_col="pytket_cx_depth", b_col="qiskit_cx_depth",
         cluster_col="random_seed", cluster_name="random circuit instance (random_seed)",
         secondary_col="qiskit_optimization_level",
         axis_cols=["random_seed", "qiskit_optimization_level"],
         cluster_note="n_qubits and removed_edges are fixed; the design varies the random "
                      "circuit (random_seed, 20 instances) x optimization level (4). A naive "
                      "n_qubits|removed_edges grouping would collapse this record to a single "
                      "cluster; random_seed (the random circuit instance) is the "
                      "design-motivated dependence unit used here."),
    dict(rid="EX-C7", claim_id="ext_2409_08844v2_claim3",
         file=PHASE1 / "ext_2409_08844v2_claim3_measurements.csv",
         metric="two-qubit gate count (TKET vs Qiskit)",
         a_col="tket_cx_count", b_col="qiskit_cx_count",
         cluster_col="circuit", cluster_name="benchmark circuit",
         secondary_col="qiskit_optimization_level",
         axis_cols=["circuit", "qiskit_optimization_level", "qiskit_seed"]),
    dict(rid="EX-C8", claim_id="ext_2409_08844v2_claim1",
         file=PHASE1 / "ext_2409_08844v2_claim1_measurements.csv",
         metric="construction/run time (Cirq vs Qiskit)",
         a_col="cirq_time_seconds", b_col="qiskit_time_seconds",
         cluster_col="circuit_size", cluster_name="circuit_size (benchmark size)",
         secondary_col=None,
         axis_cols=["circuit_size", "repetition"]),
]

# Locked ground truth for validation gates (from the published locked artifacts).
EXPECTED = {
    "EX-C1": dict(k=80, lo=0.9542, hi=1.0,    cls="Sustained"),
    "EX-C2": dict(k=80, lo=0.9542, hi=1.0,    cls="Sustained"),
    "EX-C3": dict(k=62, lo=0.6721, hi=0.8527, cls="Unresolved", ties=18, contra=0),
    "EX-C4": dict(k=45, lo=0.4534, hi=0.6659, cls="Unresolved"),
    "EX-C5": dict(k=44, lo=0.4412, hi=0.6542, cls="Unresolved", ties=15, contra=21),
    "EX-C6": dict(k=34, lo=0.3226, hi=0.5343, cls="Unresolved", ties=26, contra=20),
    "EX-C7": dict(k=0,  lo=0.0,    hi=0.0458, cls="Reversed",   ties=18, contra=62),
    "EX-C8": dict(k=0,  lo=0.0,    hi=0.0458, cls="Reversed"),
}


# ----------------------------------------------------------------------------
# Per-cell loading + labeling (preserved = locked outcome; tie = raw metric
# equality; contradicted = non-preserved & not tied). Signed margin sign is
# derived from the locked outcome and validated for consistency.
# ----------------------------------------------------------------------------
def load_cells(rec: dict) -> pd.DataFrame:
    df = pd.read_csv(rec["file"])
    if "claim_id" in df.columns:
        df = df[df["claim_id"].astype(str) == rec["claim_id"]].copy()
    elif "external_claim_id" in df.columns:
        df = df[df["external_claim_id"].astype(str) == rec["claim_id"]].copy()
    df = df.reset_index(drop=True)
    a = df[rec["a_col"]].astype(float)
    b = df[rec["b_col"]].astype(float)
    raw = a - b                              # A minus B, no direction applied
    preserved = df["outcome"].astype(int).to_numpy()
    tied = (raw == 0.0).to_numpy()

    # Derive favorable sign s in {+1,-1}: preserved (outcome==1) => s*raw > 0.
    pres_mask = preserved == 1
    contra_mask = (preserved == 0) & (~tied)
    s = None
    if pres_mask.any():
        signs = np.sign(raw[pres_mask].to_numpy())
        if np.all(signs > 0):
            s = +1
        elif np.all(signs < 0):
            s = -1
    if s is None and contra_mask.any():       # 0-preserved records: use contradictions
        signs = np.sign(raw[contra_mask].to_numpy())
        if np.all(signs > 0):                 # contradicted => favorable<0 => s = -1
            s = -1
        elif np.all(signs < 0):
            s = +1
    if s is None:
        s = +1                                # degenerate (all tied); margin all 0
    favorable = s * raw

    # Consistency validation of the labeling decomposition.
    assert np.all(favorable[pres_mask] > 0), f"{rec['rid']}: preserved cell with margin<=0"
    assert np.all(favorable[tied] == 0), f"{rec['rid']}: tie cell with nonzero margin"
    assert np.all(favorable[contra_mask] < 0), f"{rec['rid']}: contradicted cell with margin>=0"

    df["_preserved"] = preserved
    df["_tied"] = tied.astype(int)
    df["_contradicted"] = contra_mask.astype(int)
    df["_signed_margin"] = favorable
    df["_cluster"] = df[rec["cluster_col"]].astype(str)
    df["_A"] = a
    df["_B"] = b
    return df


def counts(df: pd.DataFrame) -> tuple[int, int, int, int]:
    n = len(df)
    k = int(df["_preserved"].sum())
    ties = int(df["_tied"].sum())
    contra = int(df["_contradicted"].sum())
    return n, k, ties, contra


# ----------------------------------------------------------------------------
# Robustness procedures
# ----------------------------------------------------------------------------
def cluster_bootstrap(df: pd.DataFrame, rng: np.random.Generator, b: int = B_BOOT):
    clusters = sorted(df["_cluster"].unique())
    kcl = len(clusters)
    frames = {c: df[df["_cluster"] == c] for c in clusters}
    verdicts, rates = [], []
    for _ in range(b):
        pick = rng.choice(clusters, size=kcl, replace=True)
        pooled = pd.concat([frames[c] for c in pick], ignore_index=True)
        n = len(pooled)
        k = int(pooled["_preserved"].sum())
        rate = k / n
        lo, hi = wilson_ci(k, n)
        verdicts.append(classify(lo, hi))
        rates.append(rate)
    verdicts = np.array(verdicts)
    rates = np.array(rates)
    prop = {v: float(np.mean(verdicts == v)) for v in ("Sustained", "Unresolved", "Reversed")}
    med = float(np.median(rates))
    lo_r, hi_r = (float(x) for x in np.percentile(rates, [2.5, 97.5]))
    return kcl, prop, med, lo_r, hi_r


def leave_one_cluster_out(df: dict, rec: dict):
    clusters = sorted(df["_cluster"].unique())
    out = []
    for c in clusters:
        sub = df[df["_cluster"] != c]
        n, k, ties, contra = counts(sub)
        lo, hi = wilson_ci(k, n)
        out.append(dict(removed=c, N=n, preserved=k, contradicted=contra, tied=ties,
                        rate=k / n, lo=lo, hi=hi, verdict=classify(lo, hi)))
    return clusters, out


def tie_policies(n: int, k: int, ties: int):
    """Return (policy, N_eff, k_eff, rate, lo, hi, verdict, note) for 3 policies."""
    rows = []
    # 1. main: ties non-preserving (the locked primary rule)
    lo, hi = wilson_ci(k, n)
    rows.append(("main_ties_nonpreserving", n, float(k), k / n, lo, hi, classify(lo, hi),
                 "locked primary rule"))
    # 2. ties excluded from N
    ne = n - ties
    if ne > 0:
        lo, hi = wilson_ci(k, ne)
        rows.append(("ties_excluded", ne, float(k), k / ne, lo, hi, classify(lo, hi),
                     "tied cells removed from denominator"))
    else:
        rows.append(("ties_excluded", 0, float(k), float("nan"), 0.0, 1.0, "Unresolved",
                     "all cells tied; undefined"))
    # 3. ties half-preserving (PROJECTION, not a binomial model)
    keff = k + 0.5 * ties
    lo, hi = wilson_ci(keff, n)
    rows.append(("ties_half_preserving", n, keff, keff / n, lo, hi, classify(lo, hi),
                 "SENSITIVITY PROJECTION: non-integer successes; not a standard binomial model"))
    return rows


def load_budget(rid: str) -> pd.DataFrame | None:
    esd = pd.read_csv(EXPANDED_SEED)
    sub = esd[esd["record_id"] == rid].copy()
    return sub if len(sub) else None


# ----------------------------------------------------------------------------
# Drive analysis
# ----------------------------------------------------------------------------
def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    agg = pd.read_csv(PER_CLAIM_AGG).set_index("claim_id")

    per_cell_rows = []
    primary_rows = []
    threshold_rows = []
    cluster_rows = []
    loco_rows = []
    tie_rows = []
    budget_rows = []
    status_rows = []

    cell_store: dict[str, pd.DataFrame] = {}

    # ---- Steps 1-2: per-cell tables + primary finite-design evidence ----
    for rec in RECORDS:
        rid = rec["rid"]
        exp = EXPECTED[rid]
        if rec["file"] is None:
            n, k = rec["agg_N"], rec["agg_k"]
            ties = 0 if k == n else None          # all-preserved => 0 ties; else unknown
            contra = 0 if k == n else None
            lo, hi = wilson_ci(k, n)
            verdict = classify(lo, hi)
            assert k == exp["k"], f"{rid}: aggregate k mismatch"
            primary_rows.append(dict(record_id=rid, N=n, preserved=k,
                                     contradicted=("" if contra is None else contra),
                                     tied=("" if ties is None else ties),
                                     preservation_rate=round(k / n, 6),
                                     wilson_lower=round(lo, 6), wilson_upper=round(hi, 6),
                                     tau=TAU_PRIMARY, primary_verdict=verdict))
            continue

        df = load_cells(rec)
        cell_store[rid] = df
        n, k, ties, contra = counts(df)

        # ---- VALIDATION GATES against locked artifacts ----
        assert n == 80, f"{rid}: N={n} (expected 80)"
        assert k == exp["k"], f"{rid}: k={k} (expected {exp['k']})"
        lo, hi = wilson_ci(k, n)
        assert abs(lo - exp["lo"]) < 2e-4 and abs(hi - exp["hi"]) < 2e-4, \
            f"{rid}: Wilson [{lo:.4f},{hi:.4f}] != locked [{exp['lo']},{exp['hi']}]"
        assert classify(lo, hi) == exp["cls"], f"{rid}: verdict != locked {exp['cls']}"
        if "ties" in exp:
            assert ties == exp["ties"], f"{rid}: ties={ties} (expected {exp['ties']})"
            assert contra == exp["contra"], f"{rid}: contra={contra} (expected {exp['contra']})"
        assert k + ties + contra == n, f"{rid}: k+ties+contra != N"

        primary_rows.append(dict(record_id=rid, N=n, preserved=k, contradicted=contra,
                                 tied=ties, preservation_rate=round(k / n, 6),
                                 wilson_lower=round(lo, 6), wilson_upper=round(hi, 6),
                                 tau=TAU_PRIMARY, primary_verdict=classify(lo, hi)))

        for i, row in df.reset_index(drop=True).iterrows():
            axis = ";".join(f"{c}={row[c]}" for c in rec["axis_cols"])
            per_cell_rows.append(dict(
                record_id=rid, cell_id=i, claim_id=rec["claim_id"],
                baseline_A_value=row["_A"], baseline_B_value=row["_B"],
                metric=rec["metric"], signed_margin=row["_signed_margin"],
                preserved=int(row["_preserved"]), contradicted=int(row["_contradicted"]),
                tied=int(row["_tied"]), axis_values=axis,
                candidate_cluster_unit=row["_cluster"],
                cluster_unit_type=rec["cluster_name"]))

    primary = {r["record_id"]: r for r in primary_rows}

    # ---- Step 3: threshold sensitivity (all 8 records; needs only k,N) ----
    for rec in RECORDS:
        rid = rec["rid"]
        n = primary[rid]["N"]
        k = primary[rid]["preserved"]
        prim_v = primary[rid]["primary_verdict"]
        for tau in TAUS:
            lo, hi = wilson_ci(k, n)
            v = classify(lo, hi, tau)
            threshold_rows.append(dict(record_id=rid, tau=tau, wilson_lower=round(lo, 6),
                                       wilson_upper=round(hi, 6), verdict=v,
                                       changed_from_primary=(v != prim_v)))

    # ---- Steps 4 & 5: cluster bootstrap + leave-one-cluster-out ----
    for rec in RECORDS:
        rid = rec["rid"]
        prim_v = primary[rid]["primary_verdict"]
        if rec["file"] is None:
            note = ("degenerate: all cells preserved (80/80), so any cluster resample is "
                    "trivially Sustained, but no per-cell cluster assignment is materialized"
                    if rec.get("agg_k") == rec.get("agg_N") else "no per-cell data")
            cluster_rows.append(dict(record_id=rid, cluster_unit=rec["cluster_name"],
                                     num_clusters="", B="", sustained_prop="",
                                     unresolved_prop="", reversed_prop="",
                                     median_preservation_rate="", lower_2p5="", upper_97p5="",
                                     cluster_status=f"not-available ({rec['missing_reason']})"))
            continue
        df = cell_store[rid]
        kcl, prop, med, lo_r, hi_r = cluster_bootstrap(df, rng)
        if kcl < 3:
            cstatus = "dependence-limited (<3 clusters)"
        elif prop[prim_v] >= 0.95:
            cstatus = "cluster-stable"
        else:
            cstatus = "cluster-sensitive"
        cluster_rows.append(dict(record_id=rid, cluster_unit=rec["cluster_name"],
                                 num_clusters=kcl, B=B_BOOT,
                                 sustained_prop=round(prop["Sustained"], 4),
                                 unresolved_prop=round(prop["Unresolved"], 4),
                                 reversed_prop=round(prop["Reversed"], 4),
                                 median_preservation_rate=round(med, 4),
                                 lower_2p5=round(lo_r, 4), upper_97p5=round(hi_r, 4),
                                 cluster_status=cstatus))

        clusters, loco = leave_one_cluster_out(df, rec)
        changed = False
        rates = []
        for r in loco:
            ch = r["verdict"] != prim_v
            changed = changed or ch
            rates.append(r["rate"])
            loco_rows.append(dict(record_id=rid, cluster_unit=rec["cluster_name"],
                                  removed_cluster=r["removed"], N=r["N"],
                                  preserved=r["preserved"], contradicted=r["contradicted"],
                                  tied=r["tied"], preservation_rate=round(r["rate"], 6),
                                  wilson_lower=round(r["lo"], 6), wilson_upper=round(r["hi"], 6),
                                  verdict=r["verdict"], changed_from_primary=ch))

    # ---- Step 6: tie-policy sensitivity ----
    for rec in RECORDS:
        rid = rec["rid"]
        prim_v = primary[rid]["primary_verdict"]
        if rec["file"] is None:
            if rec.get("agg_k") == rec.get("agg_N"):   # EX-C2: all preserved, 0 ties
                for pol in ("main_ties_nonpreserving", "ties_excluded", "ties_half_preserving"):
                    n, k = rec["agg_N"], rec["agg_k"]
                    lo, hi = wilson_ci(k, n)
                    tie_rows.append(dict(record_id=rid, tie_policy=pol, N_effective=n,
                                         preserved_effective=float(k),
                                         preservation_rate_effective=round(k / n, 6),
                                         verdict_projection=classify(lo, hi),
                                         changed_from_primary=False,
                                         note="0 ties (all preserved) -> tie policy is a no-op"))
            else:                                       # EX-C4: split unknown
                tie_rows.append(dict(record_id=rid, tie_policy="(all policies)", N_effective="",
                                     preserved_effective="", preservation_rate_effective="",
                                     verdict_projection="", changed_from_primary="",
                                     note=f"not-available: {rec['missing_reason']}"))
            continue
        n, k, ties, contra = counts(cell_store[rid])
        for pol, ne, keff, rate, lo, hi, v, note in tie_policies(n, k, ties):
            tie_rows.append(dict(record_id=rid, tie_policy=pol, N_effective=ne,
                                 preserved_effective=round(keff, 4),
                                 preservation_rate_effective=(round(rate, 6) if rate == rate else ""),
                                 verdict_projection=v, changed_from_primary=(v != prim_v),
                                 note=note))

    # ---- Step 7: budget / seed-count expansion ----
    for rec in RECORDS:
        rid = rec["rid"]
        prim_v = primary[rid]["primary_verdict"]
        bud = load_budget(rid)
        if bud is None:
            budget_rows.append(dict(record_id=rid, N="", preserved="", contradicted="",
                                    tied="", preservation_rate="", wilson_lower="",
                                    wilson_upper="", verdict="", changed_from_primary="",
                                    note="budget-unavailable: no validated larger trace "
                                         "(record not in expanded_seed_sensitivity.csv)"))
            continue
        for row in bud.itertuples(index=False):
            n = int(row.N); k = int(row.k_preserved)
            ties = int(row.ties); contra = int(row.contradictions)
            lo, hi = wilson_ci(k, n)
            v = classify(lo, hi)
            # Cross-check against the locked file's own verdict.
            assert v == row.verdict, f"{rid} N={n}: recomputed {v} != locked {row.verdict}"
            budget_rows.append(dict(record_id=rid, N=n, preserved=k, contradicted=contra,
                                    tied=ties, preservation_rate=round(k / n, 6),
                                    wilson_lower=round(lo, 6), wilson_upper=round(hi, 6),
                                    verdict=v, changed_from_primary=(v != prim_v),
                                    note=("baseline N=80" if n == 80 else
                                          "validated re-sampled seed expansion")))

    # ---- Step 8: per-dimension robustness status ----
    thr = pd.DataFrame(threshold_rows)
    clu = {r["record_id"]: r for r in cluster_rows}
    tie = pd.DataFrame(tie_rows)
    bud_df = pd.DataFrame(budget_rows)
    loco_df = pd.DataFrame(loco_rows)

    for rec in RECORDS:
        rid = rec["rid"]
        prim_v = primary[rid]["primary_verdict"]

        # threshold
        tsub = thr[thr["record_id"] == rid]
        flips = tsub[tsub["changed_from_primary"]]["tau"].tolist()
        threshold_status = "threshold-stable" if not flips else \
            f"threshold-sensitive (flips at tau={','.join(str(t) for t in flips)})"

        # cluster
        cluster_status = clu[rid]["cluster_status"]

        # leave-one-cluster-out
        if rec["file"] is None:
            loco_status = "not-available (no per-cell data)"
        else:
            ls = loco_df[loco_df["record_id"] == rid]
            loco_status = "leave-one-cluster-out stable" if not ls["changed_from_primary"].any() \
                else "leave-one-cluster-out sensitive"

        # tie
        if rec["file"] is None:
            tie_status = "tie-stable (0 ties)" if rec.get("agg_k") == rec.get("agg_N") \
                else "not-available (no per-cell data)"
        else:
            tsel = tie[(tie["record_id"] == rid) & (tie["changed_from_primary"] != "")]
            tie_status = "tie-stable" if not tsel["changed_from_primary"].any() else \
                "tie-sensitive (" + ",".join(
                    tsel[tsel["changed_from_primary"]]["tie_policy"].tolist()) + ")"

        # budget
        bsel = bud_df[(bud_df["record_id"] == rid) & (bud_df["verdict"] != "")]
        if bsel.empty:
            budget_status = "budget-unavailable"
        else:
            budget_status = "budget-stable" if not bsel["changed_from_primary"].any() \
                else "budget-sensitive"

        status_rows.append(dict(record_id=rid, primary_verdict=prim_v,
                                threshold_status=threshold_status, cluster_status=cluster_status,
                                leave_one_cluster_status=loco_status, tie_status=tie_status,
                                budget_status=budget_status,
                                overall_interpretation=interpret(rid, prim_v, threshold_status,
                                                                  cluster_status, loco_status,
                                                                  tie_status, budget_status)))

    # ---- Step 9: write outputs ----
    def write(name, rows, cols):
        pd.DataFrame(rows)[cols].to_csv(OUTDIR / name, index=False)

    write("tier1_primary_evidence.csv", primary_rows,
          ["record_id", "N", "preserved", "contradicted", "tied", "preservation_rate",
           "wilson_lower", "wilson_upper", "tau", "primary_verdict"])
    write("tier1_threshold_sensitivity.csv", threshold_rows,
          ["record_id", "tau", "wilson_lower", "wilson_upper", "verdict", "changed_from_primary"])
    write("tier1_cluster_resampling.csv", cluster_rows,
          ["record_id", "cluster_unit", "num_clusters", "B", "sustained_prop", "unresolved_prop",
           "reversed_prop", "median_preservation_rate", "lower_2p5", "upper_97p5", "cluster_status"])
    write("tier1_leave_one_cluster_out.csv", loco_rows,
          ["record_id", "cluster_unit", "removed_cluster", "N", "preserved", "contradicted",
           "tied", "preservation_rate", "wilson_lower", "wilson_upper", "verdict",
           "changed_from_primary"])
    write("tier1_tie_policy_sensitivity.csv", tie_rows,
          ["record_id", "tie_policy", "N_effective", "preserved_effective",
           "preservation_rate_effective", "verdict_projection", "changed_from_primary", "note"])
    write("tier1_budget_seed_expansion.csv", budget_rows,
          ["record_id", "N", "preserved", "contradicted", "tied", "preservation_rate",
           "wilson_lower", "wilson_upper", "verdict", "changed_from_primary", "note"])
    write("tier1_robustness_status.csv", status_rows,
          ["record_id", "primary_verdict", "threshold_status", "cluster_status",
           "leave_one_cluster_status", "tie_status", "budget_status", "overall_interpretation"])
    write("tier1_per_cell_table.csv", per_cell_rows,
          ["record_id", "cell_id", "claim_id", "baseline_A_value", "baseline_B_value", "metric",
           "signed_margin", "preserved", "contradicted", "tied", "axis_values",
           "candidate_cluster_unit", "cluster_unit_type"])

    print("All validation gates passed. Wrote 8 CSVs to", OUTDIR)
    for r in status_rows:
        print(f"  {r['record_id']}: {r['primary_verdict']:9s} | {r['threshold_status']} | "
              f"{r['cluster_status']} | {r['tie_status']} | {r['budget_status']}")


def interpret(rid, v, thr, clu, loco, tie, bud) -> str:
    parts = []
    if "stable" in thr and "stable" in clu and ("stable" in loco) and "stable" in tie:
        parts.append(f"{v} is stable across all applicable checks")
    else:
        parts.append(f"{v} under the locked primary rule, but not robust on all axes")
    if "sensitive" in thr:
        parts.append("verdict softens at tau=0.99 (finite-N: interval cannot reach the stricter boundary)")
    if "sensitive" in tie:
        parts.append("verdict depends on tie policy")
    if "not-available" in clu or "not-available" in loco:
        parts.append("dependence checks not assessable (no per-cell data)")
    elif "dependence-limited" in clu:
        parts.append("dependence-limited")
    return "; ".join(parts) + "."


if __name__ == "__main__":
    main()
