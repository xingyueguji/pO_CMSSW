# CRAB3 config: OO 2025 data HiForest (W/Z lepton channels)
#
# Submit (after cmsenv + voms-proxy-init + source /cvmfs/cms.cern.ch/common/crab-setup.sh):
#   crab submit -c crabConfig_forest_OO_DATA.py
#
# The W/Z-triggered events are spread across ALL IonPhysics streams (they are
# event-split, not trigger-split), so the full analysis needs every
# /IonPhysicsN PD. Use multicrab_OO_DATA.py to submit them all in one go;
# this file alone submits the single PD set in DATASET below.
#
# Output goes to CERNBox: T3_CH_CERNBOX maps /store/user/zheng/... to
# /eos/user/z/zheng/... (LFN must be /store/user/<CERN username>/).
#
# Input confirmed in DAS: 60 streams, /IonPhysics{0..59}/OORun2025-PromptReco-v1/MINIAOD
# (PromptReco with CMSSW_15_0_9_patch3, GT 150X_dataRun3_Prompt_v1).
# There are also PromptReco skims /IonPhysics*/OORun2025-Ion*-PromptReco-v1/USER;
# if one of them is a lepton skim with miniAOD-format content, it would be a
# much smaller input for W/Z — check the skim names/content in DAS before
# considering a switch.
#
# LUMIMASK: the OO golden JSON (runs 394153-394217) from
#   https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions25OO/
# Golden = all subsystems certified — correct for the combined W/Z e+mu
# analysis. The *_muon.json variant only relaxes non-muon subsystems: valid
# only for a muon-channel-only measurement (slightly more lumi); silver /
# withVdm are not for standard physics. If the URL download bothers CRAB,
# wget the file next to this config and put the bare filename here.

from CRABClient.UserUtilities import config

DATASET  = '/IonPhysics0/OORun2025-PromptReco-v1/MINIAOD'
LUMIMASK = ('https://cms-service-dqmdc.web.cern.ch/CAF/certification/'
            'Collisions25OO/Cert_Collisions2025OO_394153_394217_golden.json')
STORAGE  = 'T3_CH_CERNBOX'
TAG      = 'HiForestMiniAOD_OO2025_WZ_v2'

config = config()

config.General.requestName = TAG + '_' + DATASET.split('/')[1]
config.General.workArea = 'crab_projects_OO'
config.General.transferOutputs = True
config.General.transferLogs = False

config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'forest_miniAOD_run3_OO_DATA.py'
# CRAB caps 1-core jobs at 3000 MB and the forest peaks above that (it
# loads ~150 MB of BDT/ONNX models on top of event processing) — the v1
# probe jobs were memory-killed. Request 2 cores to unlock a 5000 MB
# ceiling; CMSSW 15_0 forest modules are thread-safe, so both cores work.
config.JobType.numCores = 1
config.JobType.maxMemoryMB = 3000
config.JobType.allowUndistributedCMSSW = True

config.Data.inputDataset = DATASET
config.Data.inputDBS = 'global'
config.Data.splitting = 'Automatic'
config.Data.lumiMask = LUMIMASK
# Optionally restrict to a run range:
# config.Data.runRange = 'XXXXXX-YYYYYY'
config.Data.outLFNDirBase = '/store/user/zheng/OO2025/forest/'
config.Data.publication = False
config.Data.outputDatasetTag = TAG

config.Site.storageSite = STORAGE
