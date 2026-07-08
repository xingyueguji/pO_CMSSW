# HiForest — proton–Oxygen (pO) 2025, W → µν / W → eν

HiForest ntuplizer setup used to produce forest trees from **miniAOD** for the
2025 **proton–Oxygen** run, in the muon and electron channels (W analysis).

This repository is the standalone `HeavyIonsAnalysis` package only. Everything
else comes from a stock `CMSSW_15_0_14` release — see *Provenance* below.

---

## Quick start (lxplus)

```bash
# 1. Fresh release (the package was built/validated against this exact release)
cmsrel CMSSW_15_0_14
cd CMSSW_15_0_14/src
cmsenv

# 2. Pull this package in as src/HeavyIonsAnalysis
#    (the repo root IS the HeavyIonsAnalysis package, so clone it into that name)
git clone <YOUR_REPO_URL> HeavyIonsAnalysis

# 3. Build
scram b -j8

# 4. Run
cd HeavyIonsAnalysis/Configuration/test
cmsRun forest_miniAOD_run3_pO_DATA.py   # data
cmsRun forest_miniAOD_run3_pO_MC.py     # MC
```

Output: `HiForestMiniAOD.root` (written via `TFileService`).

> Use a CMSSW architecture/release that contains the `Run3_2025_OXY` era
> (present since CMSSW_15_0_0). `CMSSW_15_0_14` is the exact base used here.

---

## The two config files

| Config | Type | Global Tag |
|---|---|---|
| `Configuration/test/forest_miniAOD_run3_pO_DATA.py` | data | `150X_dataRun3_Prompt_v3` |
| `Configuration/test/forest_miniAOD_run3_pO_MC.py`   | MC   | `150X_mcRun3_2025_forpO_realistic_v9` |
| `Configuration/test/forest_miniAOD_run3_pPb_DATA.py` | data (pPb, W→µν) | placeholder — see *pPb adaptation* below |
| `Configuration/test/forest_miniAOD_run3_pPb_MC.py`   | MC (pPb, W→µν)   | placeholder — see *pPb adaptation* below |

Common to both:

- **Era:** `Run3_2025_OXY` (`from Configuration.Eras.Era_Run3_2025_OXY_cff import Run3_2025_OXY`) — stock CMSSW.
- **Input:** miniAOD (`PoolSource`). Default examples point at xrootd; replace `process.source.fileNames` with your own list / use CRAB.
- **HLT paths stored** (`hltobject.triggerNames`):
  `HLT_OxyL1SingleMu0_v`, `HLT_OxyL1SingleMuOpen_v`,
  `HLT_OxyL1SingleEG10_v`, `HLT_OxyL1SingleEG15_v`,
  `HLT_MinimumBiasHF_OR_BptxAND_v`
- **Lepton models** (reused from Run3 2024 PbPb training, shipped in this package):
  - electron ID/iso: `EGMAnalysis/data/Run3_2024_PbPb/{eleid_BDT.ubj,eleiso_BDT.ubj}`
  - electron scale/smear: `EGMAnalysis/data/Run3_2024_PbPb/SSHIRun2024A.dat`
  - muon iso: `MuonAnalysis/data/Run3_2024_PbPb/muiso_BDT.ubj`
  - lepton-spectra weights: `Configuration/data/lepton_spectra_train_weights_Run3_2024_PbPb.json.gz`
  - `era = "Run3_2024_PbPb"` for `hiElectrons` / `hiMuons`
- **Photons off** (`ggHiNtuplizer.doPhotons = False`); centrality via `HFtowers`.

> **Note on `hiElectrons_cfi` / `hiMuons_cfi` / `correctedPatElectronProducer_cfi`.**
> The configs `process.load(...)` these, but you will not find matching `.py`
> files — they are **auto-generated** by `scram b` from the plugins'
> `fillDescriptions` (into `$CMSSW_BASE/cfipython/...`), which `process.load`
> also searches. The producers are `HIElectronInfoProducer` (label `hiElectrons`),
> `HIMuonMVAProducer` (label `hiMuons`) and `CorrectedPatElectronProducer`
> (default label `correctedPatElectronProducer`). This is expected; just build first.

### What differs between DATA and MC
- DATA uses `hievtanalyzer_data_cfi`; MC uses `hievtanalyzer_mc_cfi` + adds the
  gen analyzer (`HiGenAnalyzer_cfi`, `HiGenParticleAna`) and `muonAnalyzer.doGen = True`,
  `ggHiNtuplizer.doGenParticles = True`.
- Jet sequence: DATA `akCs4PFJetSequence_pponPbPb_data_cff`, MC `..._mc_cff`.
- **W pre-selection (DATA only).** A `superFilterPath` is prepended to every path:
  ```
  clusterCompatibilityFilter * primaryVertexFilter *
  goodElectrons(pt>=15) * goodMuons(pt>=15 && passed('CutBasedIdLoose')) *
  oneLepton(>=1 good e or µ)
  ```
  The MC config has **no** such lepton filter (keeps all events). Add the same
  block to the MC config if you want a matched pre-selection.

---

## pPb adaptation (W → µν), branch `pPb_WToMuNu`

`forest_miniAOD_run3_pPb_{DATA,MC}.py` are copies of the pO configs with the
species-dependent items isolated and marked `TODO(pPb)` in the file headers.
Before submitting to CRAB, set:

1. **Era** — `CMSSW_15_0_X` has **no pPb era** (only `Run3_2025_OXY`,
   `Run3_2025_NEON`, `Run3_pp_on_PbPb_2025`, UPC variants). The pPb configs
   default to the generic `Run3_2025` (pPb is reconstructed pp-style);
   replace it with the official era of whatever release the pPb prompt reco
   uses — that release, not 15_0_14, should be the base for the production.
2. **Global tags** — data: prompt GT of the pPb period; MC: pPb-campaign
   realistic GT. Current values are pO placeholders.
3. **Input datasets** — data: the pPb muon PD (2016 pPb: `PASingleMuon`;
   a new run may use `IonPhysics*`-style streams). MC: a `WToMuNu` pPb
   sample with the correct beam boost and nPDFs.
4. **Trigger list** (`hltobject.triggerNames`) — placeholders are the 2016
   pPb 8.16 TeV reference paths (`HLT_PAL3Mu12_v` was the W→µν trigger).
   Replace with the actual pPb menu names; the `HLT_Oxy*` paths of the pO
   configs do not exist in a pPb menu.
5. **Centrality input** — `hiMuons`/`hiElectrons` iso BDTs consume
   `centralityBin:HFtowers` (fed from `hiCentrality`). Confirm `hiCentrality`
   exists in the pPb miniAOD (2016 pPb used `pACentrality`); otherwise the
   centrality source must be changed.
6. **Lepton BDTs** — still the `Run3_2024_PbPb` trainings (same re-use the pO
   setup made). `HIMuonMVAProducer` throws for any other `era` string, so a
   pPb retraining also needs a code hook. Validate on pPb before trusting iso.
7. **Beam direction** — pPb runs have p→Pb and Pb→p periods. Lab-frame
   quantities are stored, so nothing changes in the forest, but keep the two
   periods in separate productions; the CM rapidity shift (~0.465 at 8.16 TeV)
   and eta flip are applied at analysis level.

**MET caveat:** no MET collection is stored by this forest. For W mT, either
rebuild PF MET offline from the PF-candidate tree (stored with `ptMin = 0`,
`|eta| < 5` for exactly this purpose) or add a small `slimmedMETs` analyzer.

The W pre-selection (`superFilterPath`: ≥1 lepton with pT ≥ 15, loose ID) is
kept identical to the pO data config; MC remains unfiltered.

---

## Forest content (paths)

`HiForestInfo`, centrality, event analyzer, HLT/L1 objects, unpacked tracks &
vertices, PF candidates, (gen particles for MC), muons (`hiMuons` +
`muonAnalyzer`), e/γ (`correctedElectrons` → `hiElectrons` → `ggHiNtuplizer`),
CS PF jets, `hiFJRhoAnalyzer`, met filters (`skimanalysis`).

---

## Example input samples (from the configs)

- **DATA:** `/store/data/pORun2025/IonPhysics0/MINIAOD/PromptReco-v1/000/394/007/00000/ad40e573-5f90-4a6b-a69c-2b8ef3c12137.root`
- **MC (DY→ee, POWHEG, pO 9.62 TeV):**
  `/store/group/phys_heavyions/anstahll/CERN/pO2025/MC/2025_10_10/POWHEG/POWHEG_9p62TeV_2025Run3/DYToEE_M_50_POWHEG_pO_9p62TeV_TuneCP5_2025Run3_RECO_2025_10_10/260306_235202/0000/POWHEG_DYToEE_M_50_RECO_1.root`

Both read via `root://xrootd-cms.infn.it/`. The MC path is a private group area
(`phys_heavyions/anstahll`) — you need access or substitute your own signal
(e.g. `WToMuNu` / `WToENu`) miniAOD.

---

## Provenance / how this was minimized

Extracted from the CMSSW fork branch **`HiForest_pO_CMSSW_15_0_X`**
(source-zip commit `81078670369831bb11f5a078491d731a8eaff2c1`).

That branch is a full `cms-sw/cmssw` checkout. It was diffed file-by-file (git
blob SHAs) against stock release tags. Result — relative to **`CMSSW_15_0_14`**:

- **125 new files**, all under `HeavyIonsAnalysis/` (this package).
- **0 modifications** to any stock `HeavyIonsAnalysis` file.
- **0 modifications** to any other CMSSW package that matters for the build.
  (The only other byte-diffs in the whole 61k-file tree were
  `PhysicsTools/Heppy/test/crab/heppy_config.py` and
  `Utilities/General/ibeos/dasgoclient` — CMSSW IB/CI artifacts, unrelated to
  HiForest — plus a `pull_request_template.md`. None are included here.)

So the complete, faithful "pO HiForest setup" is exactly this `HeavyIonsAnalysis`
package on top of a clean `CMSSW_15_0_14`. All build dependencies
(`fastjet`, `correctionlib`, `PhysicsTools/XGBoost`, `MuonAnalysis/MuonAssociators`,
`RecoHI/HiJetAlgos`, …) are satisfied by the release.

## Note on large files

A few BDT models are committed directly (largest ~40 MB):

```
EGMAnalysis/data/Run3_2023_PbPb/eleiso_BDT.ubj   ~40 MB
MuonAnalysis/data/Run3_2023_PbPb/muiso_BDT.ubj   ~38 MB
MuonAnalysis/data/Run3_2024_PbPb/muiso_BDT.ubj   ~38 MB
EGMAnalysis/data/Run3_2024_PbPb/eleid_BDT.ubj    ~25 MB
EGMAnalysis/data/Run3_2024_PbPb/eleiso_BDT.ubj   ~11 MB
```

All are under GitHub's 100 MB hard limit, so a plain `git push` works. If you
prefer, track `*.ubj` with `git-lfs` before the first commit (requires
`git lfs` on lxplus to pull).
