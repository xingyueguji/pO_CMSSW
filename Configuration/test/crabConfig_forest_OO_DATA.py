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
# TODO(OO) before submitting — all marked CHANGE_ME below:
#   1. DATASET   : confirm names/how many IonPhysics streams exist:
#                    dasgoclient -query="dataset dataset=/IonPhysics*/OORun2025*/MINIAOD"
#   2. STORAGE   : your T2/T3 storage site and /store/user area
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
STORAGE  = 'CHANGE_ME_T2_XX_Site'
TAG      = 'HiForestMiniAOD_OO2025_WZ_v1'

config = config()

config.General.requestName = TAG + '_' + DATASET.split('/')[1]
config.General.workArea = 'crab_projects_OO'
config.General.transferOutputs = True
config.General.transferLogs = False

config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'forest_miniAOD_run3_OO_DATA.py'
config.JobType.maxMemoryMB = 4000
config.JobType.allowUndistributedCMSSW = True

config.Data.inputDataset = DATASET
config.Data.inputDBS = 'global'
config.Data.splitting = 'Automatic'
config.Data.lumiMask = LUMIMASK
# Optionally restrict to a run range:
# config.Data.runRange = 'XXXXXX-YYYYYY'
config.Data.outLFNDirBase = '/store/user/%s/OO2025/forest/' % 'CHANGE_ME_username'
config.Data.publication = False
config.Data.outputDatasetTag = TAG

config.Site.storageSite = STORAGE
