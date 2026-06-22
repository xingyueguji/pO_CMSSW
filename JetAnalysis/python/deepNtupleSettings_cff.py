import FWCore.ParameterSet.Config as cms

def candidateBtaggingMiniAOD(process, isMC = True, jetPtMin = 15, jetR = 0.4, jetCorrLevels = ['L2Relative', 'L3Absolute']):
    # DeepNtuple settings
    R = str(int(jetR*10))
    jetCorrectionsAK = ('AK4PF', jetCorrLevels, 'None')

    bTagInfos = [
        'pfDeepCSVTagInfos',
        'pfDeepFlavourTagInfos',
        'pfImpactParameterTagInfos',
        'pfInclusiveSecondaryVertexFinderTagInfos',
        'pfParticleTransformerAK4TagInfos',
        'pfUnifiedParticleTransformerAK4TagInfos'
    ]

    bTagDiscriminators = [
        'pfDeepCSVJetTags:probb',
        'pfDeepCSVJetTags:probbb',
        'pfDeepCSVJetTags:probc',
        'pfDeepCSVJetTags:probudsg',
        'pfDeepFlavourJetTags:probb',
        'pfDeepFlavourJetTags:probbb',
        'pfDeepFlavourJetTags:probc',
        'pfDeepFlavourJetTags:probg',
        'pfDeepFlavourJetTags:problepb',
        'pfDeepFlavourJetTags:probuds',
        'pfParticleTransformerAK4JetTags:probb',
        'pfParticleTransformerAK4JetTags:probbb',
        'pfParticleTransformerAK4JetTags:probc',
        'pfParticleTransformerAK4JetTags:probg',
        'pfParticleTransformerAK4JetTags:problepb',
        'pfParticleTransformerAK4JetTags:probuds',
        'pfUnifiedParticleTransformerAK4JetTags:probb',
        'pfUnifiedParticleTransformerAK4JetTags:probbb',
        'pfUnifiedParticleTransformerAK4JetTags:probc',
        'pfUnifiedParticleTransformerAK4JetTags:probg',
        'pfUnifiedParticleTransformerAK4JetTags:problepb',
        'pfUnifiedParticleTransformerAK4JetTags:probu',
        'pfUnifiedParticleTransformerAK4JetTags:probd',
        'pfUnifiedParticleTransformerAK4JetTags:probs',
        'pfUnifiedParticleTransformerAK4JetTags:probtaup1h0p',
        'pfUnifiedParticleTransformerAK4JetTags:probtaup1h1p',
        'pfUnifiedParticleTransformerAK4JetTags:probtaup1h2p',
        'pfUnifiedParticleTransformerAK4JetTags:probtaup3h0p',
        'pfUnifiedParticleTransformerAK4JetTags:probtaup3h1p',
        'pfUnifiedParticleTransformerAK4JetTags:probtaum1h0p',
        'pfUnifiedParticleTransformerAK4JetTags:probtaum1h1p',
        'pfUnifiedParticleTransformerAK4JetTags:probtaum1h2p',
        'pfUnifiedParticleTransformerAK4JetTags:probtaum3h0p',
        'pfUnifiedParticleTransformerAK4JetTags:probtaum3h1p',
        'pfUnifiedParticleTransformerAK4JetTags:probele',
        'pfUnifiedParticleTransformerAK4JetTags:probmu',
        'pfUnifiedParticleTransformerAK4JetTags:ptcorr',
        'pfUnifiedParticleTransformerAK4JetTags:ptnu',
    ]

    # Create gen-level information
    if isMC:
        from RecoHI.HiJetAlgos.hiSignalParticleProducer_cfi import hiSignalParticleProducer as hiSignalGenParticles
        process.hiSignalGenParticles = hiSignalGenParticles.clone(
            src = "prunedGenParticles"
        )
        from PhysicsTools.PatAlgos.producersHeavyIons.heavyIonJets_cff import allPartons
        process.allPartons = allPartons.clone(
            src = 'hiSignalGenParticles'
        )
        process.packedGenParticlesForJetsNoNu = cms.EDFilter("CandPtrSelector",
            src = cms.InputTag("packedGenParticlesSignal"),
            cut = cms.string("abs(pdgId) != 12 && abs(pdgId) != 14 && abs(pdgId) != 16")
        )
        from RecoJets.JetProducers.ak4GenJets_cfi import ak4GenJets
        setattr(process,f'ak{R}GenJetsRecluster', ak4GenJets.clone(
            src = 'packedGenParticlesForJetsNoNu',
            rParam = jetR
        ))
        setattr(process,f'genAK{R}Task', cms.Task(process.hiSignalGenParticles, process.allPartons, process.packedGenParticlesForJetsNoNu, getattr(process,f'ak{R}GenJetsRecluster')))

    # Remake secondary vertices
    from RecoVertex.AdaptiveVertexFinder.inclusiveVertexing_cff import inclusiveCandidateVertexFinder, candidateVertexMerger, candidateVertexArbitrator, inclusiveCandidateSecondaryVertices
    process.inclusiveCandidateVertexFinder = inclusiveCandidateVertexFinder.clone(
        tracks = "packedPFCandidates",
        primaryVertices = "offlineSlimmedPrimaryVertices",
        minHits = 0,
        minPt = 0.8
    )
    process.candidateVertexMerger = candidateVertexMerger.clone()
    process.candidateVertexArbitrator = candidateVertexArbitrator.clone(
        tracks = "packedPFCandidates",
        primaryVertices = "offlineSlimmedPrimaryVertices"
    )
    process.inclusiveCandidateSecondaryVertices = inclusiveCandidateSecondaryVertices.clone()
    process.svTask = cms.Task(process.inclusiveCandidateVertexFinder, process.candidateVertexMerger, process.candidateVertexArbitrator, process.inclusiveCandidateSecondaryVertices)
    svSource = cms.InputTag("inclusiveCandidateSecondaryVertices")

    # Create unsubtracted reco jets
    from PhysicsTools.PatAlgos.tools.jetTools import addJetCollection
    addJetCollection(
        process,
        postfix            = "UnsubJets",
        labelName          = f"AK{R}PF",
        jetSource          = cms.InputTag(f"ak{R}PFUnsubJets"),
        algo               = "ak", #name of algo must be in this format
        rParam             = jetR,
        pvSource           = cms.InputTag("offlineSlimmedPrimaryVertices"),
        pfCandidates       = cms.InputTag("packedPFCandidates"),
        svSource           = svSource,
        muSource           = cms.InputTag("slimmedMuons"),
        elSource           = cms.InputTag("slimmedElectrons"),
        getJetMCFlavour    = isMC,
        genJetCollection   = cms.InputTag(f"ak{R}GenJetsRecluster" if isMC else ""),
        genParticles       = cms.InputTag("hiSignalGenParticles" if isMC else ""),
        jetCorrections     = jetCorrectionsAK,
    )
    getattr(process,f'patJetsAK{R}PFUnsubJets').useLegacyJetMCFlavour = False
    getattr(process,f'patJetPartonMatchAK{R}PFUnsubJets').maxDeltaR = jetR

    from PhysicsTools.PatAlgos.producersLayer1.jetProducer_cff import ak4PFJets
    setattr(process,f'ak{R}PFUnsubJets', ak4PFJets.clone(
        src = 'packedPFCandidates',
        rParam = jetR,
        jetPtMin = jetPtMin
    ))
    process.patAlgosToolsTask.add(getattr(process,f'ak{R}PFUnsubJets'))

    # Create HIN subtracted reco jets
    from PhysicsTools.PatAlgos.tools.jetTools import addJetCollection
    addJetCollection(
        process,
        postfix            = "",
        labelName          = f"AKCs{R}PF",
        jetSource          = cms.InputTag(f"akCs{R}PFJets"),
        algo               = "ak", #name of algo must be in this format
        rParam             = jetR,
        pvSource           = cms.InputTag("offlineSlimmedPrimaryVertices"),
        pfCandidates       = cms.InputTag("packedPFCandidates"),
        svSource           = svSource,
        muSource           = cms.InputTag("slimmedMuons"),
        elSource           = cms.InputTag("slimmedElectrons"),
        getJetMCFlavour    = isMC,
        genJetCollection   = cms.InputTag(f"ak{R}GenJetsRecluster" if isMC else ""),
        genParticles       = cms.InputTag("hiSignalGenParticles" if isMC else ""),
        jetCorrections     = jetCorrectionsAK,
    )
    getattr(process,f'patJetsAKCs{R}PF').embedPFCandidates = True
    getattr(process,f'patJetPartonMatchAKCs{R}PF').maxDeltaR = jetR

    if not isMC:
        for label in [f"patJetsAK{R}PFUnsubJets", f"patJetsAKCs{R}PF"]:
            getattr(process, label).addGenJetMatch = False
            getattr(process, label).addGenPartonMatch = False
            getattr(process, label).embedGenJetMatch = False
            getattr(process, label).embedGenPartonMatch = False
            getattr(process, label).genJetMatch = ""
            getattr(process, label).genPartonMatch = ""
    else:
        getattr(process,f'patJetPartonAssociationLegacyAK{R}PFUnsubJets').coneSizeToAssociate = min(jetR, 0.3)
        getattr(process,f'patJetPartonAssociationLegacyAKCs{R}PF').coneSizeToAssociate = min(jetR, 0.3)

    from PhysicsTools.PatAlgos.producersHeavyIons.heavyIonJets_cff import PackedPFTowers, hiPuRho
    process.PackedPFTowers = PackedPFTowers.clone()
    process.hiPuRho = hiPuRho.clone(
        src = 'PackedPFTowers'
    )
    from PhysicsTools.PatAlgos.producersLayer1.jetProducer_cff import akCs4PFJets
    setattr(process,f'akCs{R}PFJets', akCs4PFJets.clone(
        src = 'packedPFCandidates',
        rParam = jetR,
        jetPtMin = jetPtMin
    ))
    for mod in ["PackedPFTowers", "hiPuRho", f"akCs{R}PFJets"]:
        process.patAlgosToolsTask.add(getattr(process, mod))

    # Create b-tagging sequence ----------------
    from PhysicsTools.PatAlgos.tools.jetTools import updateJetCollection
    updateJetCollection(
        process,
        labelName = f"AKCs{R}DeepFlavour",
        jetSource = cms.InputTag(f'patJetsAKCs{R}PF'),
        jetCorrections = jetCorrectionsAK,
        pfCandidates = cms.InputTag('packedPFCandidates'),
        pvSource = cms.InputTag("offlineSlimmedPrimaryVertices"),
        svSource = svSource,
        muSource = cms.InputTag('slimmedMuons'),
        elSource = cms.InputTag('slimmedElectrons'),
        btagInfos = bTagInfos,
        btagDiscriminators = bTagDiscriminators,
        explicitJTA = False
    )

    setattr(process,f'unsubUpdatedPatJetsAKCs{R}DeepFlavour', cms.EDProducer("JetMatcherDR",
        source = cms.InputTag(f"updatedPatJetsAKCs{R}DeepFlavour"),
        matched = cms.InputTag(f"patJetsAK{R}PFUnsubJets")
    ))
    process.patAlgosToolsTask.add(getattr(process,f'unsubUpdatedPatJetsAKCs{R}DeepFlavour'))

    getattr(process,f'pfImpactParameterTagInfosAKCs{R}DeepFlavour').maxDeltaR = jetR
    for taginfo in [f"pfDeepFlavourTagInfosAKCs{R}DeepFlavour", f"pfParticleTransformerAK4TagInfosAKCs{R}DeepFlavour", f"pfUnifiedParticleTransformerAK4TagInfosAKCs{R}DeepFlavour"]:
        getattr(process, taginfo).jet_radius = jetR

    if hasattr(process,f'updatedPatJetsTransientCorrectedAKCs{R}DeepFlavour'):
        getattr(process,f'updatedPatJetsTransientCorrectedAKCs{R}DeepFlavour').addTagInfos = True
        getattr(process,f'updatedPatJetsTransientCorrectedAKCs{R}DeepFlavour').addBTagInfo = True
    else:
        raise ValueError(f'I could not find updatedPatJetsTransientCorrectedAKCs{R}DeepFlavour to embed the tagInfos, please check the cfg')

    # Remove PUPPI
    process.patAlgosToolsTask.remove(process.packedpuppi)
    process.patAlgosToolsTask.remove(process.packedpuppiNoLep)
    getattr(process,f'pfInclusiveSecondaryVertexFinderTagInfosAKCs{R}DeepFlavour').weights = ""
    for taginfo in [f"pfDeepFlavourTagInfosAKCs{R}DeepFlavour", f"pfParticleTransformerAK4TagInfosAKCs{R}DeepFlavour", f"pfUnifiedParticleTransformerAK4TagInfosAKCs{R}DeepFlavour"]:
        getattr(process, taginfo).fallback_puppi_weight = True
        getattr(process, taginfo).fallback_vertex_association = True
        getattr(process, taginfo).unsubjet_map = f"unsubUpdatedPatJetsAKCs{R}DeepFlavour"
        getattr(process, taginfo).puppi_value_map = ""

    # Match with unsubtracted jets
    setattr(process,f'unsubAK{R}JetMap', getattr(process,f'unsubUpdatedPatJetsAKCs{R}DeepFlavour').clone(
        source = f"selectedUpdatedPatJetsAKCs{R}DeepFlavour"
    ))
    process.patAlgosToolsTask.add(getattr(process,f'unsubAK{R}JetMap'))

    # Add extra b tagging algos
    from RecoBTag.ImpactParameter.pfJetProbabilityBJetTags_cfi import pfJetProbabilityBJetTags
    setattr(process,f'pfJetProbabilityBJetTagsAKCs{R}DeepFlavour', pfJetProbabilityBJetTags.clone(tagInfos = [f"pfImpactParameterTagInfosAKCs{R}DeepFlavour"]))
    process.patAlgosToolsTask.add(getattr(process,f'pfJetProbabilityBJetTagsAKCs{R}DeepFlavour'))

    # Associate to forest sequence
    if isMC:
        process.forest.associate(getattr(process,f'genAK{R}Task'))
    process.forest.associate(process.svTask)
    process.forest.associate(process.patAlgosToolsTask)
