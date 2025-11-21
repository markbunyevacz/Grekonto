## Page 1

Agent-R1: Training Powerful LLM Agents with
End-to-End Reinforcement Learning
MingyueCheng,JieOuyang,ShuoYu,RuiranYan,YucongLuo,
ZiruiLiu,DaoyuWang,QiLiu,EnhongChen
StateKeyLaboratoryofCognitiveIntelligence,
UniversityofScienceandTechnologyofChina,Hefei,China
Abstract
Large Language Models (LLMs) are increasingly being explored for building
Agentscapableofactiveenvironmentalinteraction(e.g.,viatooluse)tosolvecom-
plexproblems. ReinforcementLearning(RL)isconsideredakeytechnologywith
significantpotentialfortrainingsuchAgents;however,theeffectiveapplicationof
RLtoLLMAgentsisstillinitsnascentstagesandfacesconsiderablechallenges.
Currently,thisemergingfieldlacksin-depthexplorationintoRLapproachesspecif-
ically tailored for the LLM Agent context, alongside a scarcity of flexible and
easilyextensibletrainingframeworksdesignedforthispurpose. Tohelpadvance
thisarea,thispaperfirstrevisitsandclarifiesReinforcementLearningmethodolo-
giesforLLMAgentsbysystematicallyextendingtheMarkovDecisionProcess
(MDP) framework to comprehensively define the key components of an LLM
Agent. Secondly,weintroduceAgent-R1,amodular,flexible,anduser-friendly
trainingframeworkforRL-basedLLMAgents,designedforstraightforwardadap-
tationacrossdiversetaskscenariosandinteractiveenvironments. Weconducted
experimentsonMultihopQAbenchmarktasks,providinginitialvalidationforthe
effectivenessofourproposedmethodsandframework.
§ https://github.com/0russwest0/Agent-R1. 1
1 Introduction
Inrecentyears,largelanguagemodels(LLMs)havedemonstratedremarkablecapabilitiesinnatural
languageunderstandingandgeneration[2,4],andareincreasinglybeingappliedtomorecomplex
intelligent tasks[24]. When LLMs are assigned an “agent” role, they are expected not only to
performcognitivetaskssuchasreasoninganddecision-making,butalsotoactautonomously,learn
continuously,andadapttochangeswithininteractiveenvironments[35,25,16]. Unliketraditional
static reasoning tasks[30], LLMs functioning as agents must maintain memory across multiple
dialogue rounds[37], exhibit sequential decision-making capabilities, and respond effectively to
environmentalfeedback—bringingthemclosertoreal-worldautonomousintelligentsystems[27,13].
Thisdirectionopensnewpossibilitiesforbuildinggeneralartificialintelligencewithself-evolving
andproblem-solvingcapabilities[31,9].
WhileReinforcementLearning(RL)[5,26,6]hasdemonstratednotablesuccessinenhancingLLMca-
pabilitiesforrelativelywell-definedtaskssuchasmathematicalproblemsolvingandcodegeneration
[15,19,1],itsapplicationtodevelopingLLMsasautonomous,interactiveagentsiscomparatively
nascent. Agentsettingsinherentlyrequiremodelstomakesequentialdecisions,maintainmemory
acrossturns,andadapttostochasticenvironmentalfeedback[35,27],presentinguniquechallenges
distinctfrommorestatictasks[16,30]. ThisleadstospecificdifficultieswhenapplyingRL;partic-
ularlyinmulti-turninteractionscenarios,agenttrainingcanencounterinstability,complexreward
1ThispaperservesasthetechnicalreportoftheAgent-R1project.
Preprint.Underreview.
5202
voN
81
]LC.sc[
1v06441.1152:viXra

## Page 2

Tool Caller 1
Workflow In Router Tool Caller 2 Out In Planner Tool Caller 1 Tool Caller 2 Out
Tool Caller 2
human-designed workflows
Agentic Actor prompt engineering for reasoning or action
e.g. React In Reasoner Tool Caller 1 Out
Workflow Tool Caller 1
interact with the environment passively
Environment
Agent Action no workflow
In Agent Environment Out no prompt engineering
interact with the environment actively
Feedback
Figure1: Comparisonofworkflows,agenticworkflows,andautonomousagents. Workflowsrely
onhuman-designedroutingorplanning,whileagenticworkflows(e.g.,ReAct)introduceiterative
reasoning–actingloops. Fullyautonomousagentsremovepredefinedworkflowsandinteractwiththe
environmentproactivelythroughanend-to-endaction–feedbackcycle.
signaldesign,andlimitedgeneralization[3,10,20]. Thus,thereremainsaneedforamoredetailed
explorationofhowRLmethodologiescanbesystematicallyappliedandadaptedtoLLMagents,
alongsideaneedforflexibleandscalabletrainingframeworks[14,18].
Tosystematicallyaddresstheseaspects,thispaperpresentscontributionsfrombothaconceptual
and practical standpoint. Conceptually, we focus on clarifying the application of Reinforcement
LearningtoLLMAgents.WeachievethisbyextendingthestandardMarkovDecisionProcess(MDP)
framework[22],providingadetailedaccountofhowitscorecomponents—StateSpace,ActionSpace,
StateTransitionProbability,andRewardFunction—canbeadaptedtocomprehensivelymodelthe
multi-turn,interactivenatureofLLMAgents[7,36]. BuildinguponthisadaptedMDPformulation,
wefurtherelaborateonmechanismsforoptimizingagentpolicyfrommulti-turntrajectories[17],
emphasizingtheimportanceofdistinguishingagent-generatedactionsfromenvironmentalfeedback
andincorporatingintermediate(process)rewards[11,27]toguidelearningeffectively. Inaddition,
tofacilitatethepracticalapplicationoftheseconcepts,wedevelopAgent-R1,aflexibleanduser-
friendlytrainingplatformforRL-basedLLMAgents. Thankstoitsmodulararchitecture,Agent-R1
supportsrapidintegrationofvariousenvironmentinterfacesandtaskscenarios,andcandynamically
adapttodifferentcomputationalresourcerequirements,enablingeasyscalabilitytocomplexand
diverseapplications[32,12].
Throughsystematicexperimentsonthechallengingtaskofmulti-hopquestionanswering(Multi-hop
QA),wevalidatetheeffectivenessofourapproachandframework[16,33]. Thistaskfocuseson
complexreasoninginvolvingcross-documentlogicalchainingandinformationretrieval,imposing
high demands on the agent’s multi-step decision-making ability, adaptability to environmental
feedback,andknowledgeconstructionprocesses. Experimentalresultsdemonstratethatourmethods
andframeworkcanenhancethemodel’sperformanceinsuchdynamicinteractiveenvironments[29].
2 FromLargeLanguageModelstoAgents: AnMDPPerspective
Thesequentialdecision-makingprocessesinherentinLargeLanguageModel(LLM)applications
canbeeffectivelyformulatedwithintheMarkovDecisionProcess(MDP)framework,whetherfor
simple text generation or for the complex interactions of LLM Agents. However, evolving the
MDPformulationfromitsapplicationtoLLMsinthecontextofstatic,single-turntextgeneration
tasks (such as in mathematics or code generation), to one suitable for LLM Agents that engage
in inherently dynamic, multi-turn, and richly interactive environmental dialogues, necessitates
substantialextensions. ThissectiondelineatesthesecriticaldifferencesbycontrastingthecoreMDP
componentsforaStaticLLMversusaLLMAgent.
2

## Page 3

Table1: ComparisonofMarkovDecisionProcess(MDP)componentsforaStaticLLMversusan
LLMAgent,highlightingthenecessaryextensionsforinteractive,multi-turnscenarios.
MDPComponent StaticLLM LLMAgent
StateSpace(S) The state s primarily encapsu- The state s is significantly more
t t
lates the current textual context, comprehensive, retaining the his-
including the initial prompt and toryofmulti-turninteractionsand
the sequence of tokens generated environmental feedback. This en-
so far. Its focus is on predicting ables decisions informed by a full
the next coherent token. s = dialogue history. Each T repre-
t i
(w ,w ,...,w ). sents a full turn of agent action
p 1 t
and environment feedback. s =
t
(w ,T ,...,T ,Tpartial).
p 1 k k+1
ActionSpace(A) Theactiona correspondstoselect- The fundamental action is also to-
t
ing the next token w from the ken generation from V. However,
t+1
LLM’svocabularyV. specifictokensequencescanbein-
terpretedascommandstoinvokeex-
ternaltools,enablingactiveenviron-
mentalintervention.
StateTransition(P) State transitions are determinis- Thestatetransitionmechanismin-
tic. The next state is uniquely corporates environmental interac-
determined by appending the se- tion, which can be stochastic. It
lectedtokentothecurrentsequence. distinguishesbetweendeterministic
P(s |s ,a ) = 1ifs = s ⊕ generativetransitions(P )andpo-
t+1 t t t+1 t G
a . tentially stochastic environmental
t
transitions (P ) triggered by tool
E
use.
RewardFunction(R) Rewards are typically sparse and The reward structure is richer and
provided at the end of a complete more dense. In addition to a final
generation, evaluating the overall outcomereward(r ),agentscanre-
f
qualityofthefinaloutput. ceiveintermediateprocessrewards
(r )forsuccessfullyexecutingsteps
p
liketoolinvocation,providingmore
frequentfeedback.
2.1 StateSpace(S)
Static LLM: In single-turn text generation, the state s primarily encapsulates the current tex-
t
tual context. This includes the initial prompt w and the sequence of tokens generated thus far
p
w ,w ,...,w :
1 2 t
s =(w ,w ,w ,...,w ). (1)
t p 1 2 t
The state space is focused on capturing the information necessary to predict the next token in a
coherentsequence.
LLMAgent: ForanAgentengaginginmulti-turninteractions,thestates mustbesignificantly
t
morecomprehensive. Itneedstoretainnotonlythetextualcontextbutalsothehistoryofinteractions
andenvironmentalfeedback. Thestateisthusextendedto:
s =(w ,T ,T ,...,T ,Tpartial). (2)
t p 1 2 k k+1
Here, each T represents a complete interaction turn, comprising the Agent’s generated tokens
i
(w ,...,w ) and the subsequent environmental feedback w , i.e., T = (w ,...,w ,w ).
i1 iTi ei i i1 iTi ei
ThetermTpartialdenotesthepartiallygeneratedsequenceinthecurrent,ongoingturn. Thisenriched
k+1
staterepresentationenablestheAgenttomakedecisionsinformedbyacomprehensivehistoryof
dialogueandenvironmentaloutcomes(e.g.,resultsfromtoolutilization).
3

## Page 4

Table2: CoredifferencesintheMDPformulationforStaticLLMsvs. LLMAgents.
Component StaticLLM LLMAgent
State(S) Captures only the current text se- Captures the full history of multi-
quence. turninteractionsandenvironmental
feedback.
Action(A) Generatingthenexttoken. Generatingtokensthatcanalsofunc-
tionascommandstoinvokeexternal
tools.
StateTransition(P) Deterministic: appendingatokende- Stochastic: the next state depends
terminesthenextstate. onnon-deterministicfeedbackfrom
envrionment.
Reward(R) Receives a single, sparse reward at Receivesdenseprocessrewardsfor
theendofthegeneration. intermediate steps in addition to a
finalreward.
2.2 ActionSpace(A)
StaticLLM:Theactiona correspondstotheselectionofthenexttokenw fromtheLLM’s
t t+1
vocabularyV. TheactionspaceA(s )istypicallythesetV.
t
LLMAgent: Similarly,anAgent’sactiona istheselectionofthenexttokenfromV. However,
t
theimplicationofanactionsequencecanbebroader. Specificsequencesoftokensgeneratedby
the Agent might be interpreted as commands to invoke external tools or APIs. Thus, while the
fundamentalactionremainstokengeneration,itsfunctionaloutcomecanextendbeyondmeretext
productiontoactiveenvironmentalintervention.
2.3 StateTransitionProbability(P)
StaticLLM:StatetransitionsinLLMtextgenerationaredeterministic. Giventhecurrentstates
t
andanactiona (selectingtokenw ),thenextstates isuniquelydeterminedbyappending
t t+1 t+1
w tothecurrentsequence:
t+1
(cid:26)
1, ifs =s ⊕a
P(s |s ,a )= t+1 t t , (3)
t+1 t t 0, otherwise
where⊕denotessequenceconcatenation.
LLMAgent: ThestatetransitionmechanismforAgentsintroducesacrucialdistinctionbyincorpo-
ratingenvironmentalinteraction,whichcanbestochastic. Transitionscanbecategorizedbasedon
whetheranactioninstigatessuchinteraction:
(cid:26)
P (s |s ,a ), ifa triggerstool/environmentinteraction
P(s |s ,a )= E t+1 t t t , (4)
t+1 t t P (s |s ,a ), otherwise(standardtokengeneration)
G t+1 t t
WhileP (generativetransition)mirrorsthedeterministicnatureofStaticLLMtokengeneration
G
(P (s |s ,a )=1ifs =s ⊕a ,and0otherwise),P (environmentaltransition)reflectsthe
G t+1 t t t+1 t t E
uncertaintyinherentintoolexecutionandenvironmentalresponses. Thenextstates thendepends
t+1
notonlyontheAgent’sactionbutalsoontheoutcomefromtheexternalenvironment(e.g.,anAPI
response,resultofacomputation),whichformspartoftheenvironmentalfeedbackw .
ei
2.4 RewardFunction(R)
StaticLLM:Rewardsaretypicallysparseandprovidedattheendofacompletegenerationsequence,
i.e.,uponreachingaterminalstates . Thisisoftenaresult-basedreward,R(s ),evaluatingthe
T T
overallquality(e.g.,coherence,relevance)ofthegeneratedtext.
4

## Page 5

Illustration of Agent-R1 Training Trajectory
User Instruction q 𝑡1 𝑎1 𝑟1 … 𝑡𝑘 𝑎𝑘 𝑟𝑘 append 𝑡𝑘+1 𝑎𝑘+1 + <tool_response> 𝑟𝑘+1</tool_response>
LLM - Rollout
feedback
reasoning
multi-turn
<think> Thinking process 𝑡𝑘+1 </think>
Assistant stop continue
final answer action
custom tool usage Environment
<answer> ans </answer> <tool_call> 𝑎𝑘+1 </tool_call>
Figure2: IllustrationoftheAgent-R1trainingtrajectory. Theagentperformsmulti-turnreasoning
andtool-basedactionsduringrollout,receivesenvironmentfeedback,andappendstoolresponsesto
formthenextstate. Thistrajectory—containingthinkingsteps,actions,andfeedback—servesasthe
basisforreinforcementlearningupdatesinAgent-R1.
LLMAgent: TherewardstructureforAgentsisoftenricherandmoredense,accommodatingthe
multi-turnnatureoftheirtasks. TherewardR(s ,a ,s )canbedefinedas:
t t t+1

r (s ), ifs isaterminalstate
 f t+1 t+1
R(s ,a ,s )= r (s ,a ,s ), ifa triggersasignificantintermediateevent . (5)
t t t+1 p t t t+1 t
0, otherwise(e.g.,duringroutinetokengeneration)
Here,r (s )isthefinaloutcomerewardfortaskcompletion. Crucially,Agentscanalsoreceive
f t+1
processrewards,r (s ,a ,s ),forsuccessfullyexecutingintermediatesteps,suchaseffective
p t t t+1
toolinvocationormakingtangibleprogresstowardsagoal. Theseintermediatesignalsprovidemore
frequentfeedback,guidingthelearningprocessmoreeffectively.
Insummary,adaptingtheMDPframeworkfromStaticLLMstoLLMAgentsinvolvessignificant
enhancements across the core components discussed. The state space expands to incorporate in-
teractionhistoryandenvironmentalfeedback;actions,whilefundamentallytokengeneration,can
triggerexternaleffects;statetransitionsintegrateenvironmentalstochasticity;andtherewardsystem
becomesmoregranularwiththeinclusionofprocessrewards. Theseextensionsarecrucialforen-
ablingreinforcementlearningalgorithmstotrainsophisticatedAgentscapableofcomplex,multi-step
reasoningandinteractionwithindynamicenvironments.
3 Agent-R1Framework
To better accommodate the reinforcement learning requirements of LLM Agents, we introduce
Agent-R1, a flexible and highly extensible agent reinforcement learning training framework as
showninFigure2. Drawingfromexistingefficientreinforcementlearninginfrastructures,weextend
traditionalsingle-turnreinforcementlearningtrainingframeworkstofullyadapttothemulti-turn
interactivecharacteristicsofagents,enablingseamlessintegrationwithdiversetaskenvironments
andscalabletrainingacrossincreasinglycomplexagentsettings. Figure3andFigure4illustratethe
workflowcomparisonbetweentraditionalsingle-turnreinforcementlearningtrainingframeworks
andAgent-R1’smulti-turnreinforcementlearningtraining,whereFigure3showsthegeneration
stageandFigure4showsthelearningstage. Themostsignificantdifferencebetweensingle-turnand
multi-turnreinforcementlearningliesintherolloutphase: single-turnrolloutprocessesonlyrequire
the Actor Model to generate responses once, while multi-turn rollout involves multiple complex
interactions. Toachieveflexibleandeasilyextensiblemulti-turnrollout,wehavecarefullydesigned
twocoremodules: ToolandToolEnv.
3.1 ToolandToolEnv: CoreModulesforInteractiveRollout
Theinteractiverolloutprocess,centraltotrainingLLMAgents,reliesheavilyontwokeycomponents:
ToolandToolEnv. Acleardivisionofresponsibilitiesbetweenthesemodulesisfundamentaltothe
Agent-R1designphilosophy.
5

## Page 6

Figure3: FlowdiagramofSingle-TurnRLandMulti-TurnRL(Agent-R1)ingenerationstage.
Figure4: FlowdiagramofSingle-TurnRLandMulti-TurnRL(Agent-R1)inlearningstage.
TheToolisconceivedasanexecutorofspecific,atomicactions. Itsprimaryroleistoencapsulate
a distinct capability—such as calling an external API, executing a piece of code, or accessing a
database. Wheninvoked,aToolperformsitsactionandreturnsthedirect,rawoutcomeofthataction.
Itessentiallyreports“whathappened"factually.
Conversely,theToolEnvactsastheorchestratorandinterpreterwithinthereinforcementlearning
(RL)environment. IttakestherawoutputfromaToolanddetermineshowthatoutputaffectsthe
Agent’sperceivedstateandtheoveralltaskprogression. ToolEnvisresponsibleformanagingthe
statetransitionswithintheRLloop,calculatingappropriaterewardsignalsbasedonthesetransitions
and tool outcomes, and packaging the new state information for theagent. It dictates“what this
outcomemeansfortheagentandthetask."
3.1.1 ToolDesign
Toolsserveasthecriticalinterfaceconnectingagentstoexternalenvironmentsorfunctionalities. In
theAgent-R1framework,weutilizeToolsastheunifiedinterfaceforagent-environmentinteraction,
whereallexternalfunctionalitiesareencapsulatedintostandardized,directlycallable"tools"bythe
agent. DrawinginspirationfromOpenAI’sFunctionCallingparadigm,theAgent-R1framework
provideshigh-levelabstractionandstandardizationofToolsthroughtheBaseToolabstractbaseclass.
Itsdesignfocusesontwocoremodules:
CoreExecutionLogic: AsthemostcriticalabstractmethodwithintheBaseToolclass,allconcrete
toolsubclassesmustimplementtheexecutionmethod. Thismethodencapsulatesthecorelogicofthe
tool,defininghowitprocessesinputparameters,performsitsspecificoperation(suchasinteracting
withanexternalAPI,executingcode,oraccessingadatabase),andreturnsastructuredresult.
6

## Page 7

ToolMetadataSpecification: Toensurethestandardizationandparsabilityoftoolinvocation,the
followingmetadataattributesaredefined:
• Identification and Description: The name attribute (a unique string identifier) and the
descriptionattribute(providingdetailedinformationaboutthetool’sfunctionality,usecases,
andexpectedeffects)worksynergistically. Agentsunderstandthesetoidentifyandselect
appropriatetoolsbasedonthecurrentcontext.
• ParameterStructureDefinition: TheparametersattributefollowsJSONSchemaspecifi-
cationstodefinetheinputparameterstructurerequiredfortoolinvocation. Thisincludes
parameter names, data types, detailed descriptions, and whether they are required. The
standardizationofparametersensuresagentscangeneratetoolinvocationparametersthat
conformtoexpectedformats.
Thisdesign,centeredontheexecutemethod’spivotalroleinperformingactionsandtheclearmetadata
specificationsthatenableagentunderstanding,allowsLLMagentstoeffectivelyinteractwithexternal
environmentsviastructuredinterfaces. Theoutcomesoftoolexecutionarethenprocessedbythe
ToolEnvmodule,whichisresponsibleformanagingthecorrespondingenvironmentalstatetransitions.
Thisinterplayisfundamentalforagentstosolvecomplexproblemsinmulti-turninteractionsand
formsacohesivelinkwithToolEnv’sstatemanagementdesign.
3.1.2 ToolEnvDesign
TheToolEnvmoduleactsasthedynamicenvironmentwithintheAgent-R1reinforcementlearning
framework. It is responsible for managing the agent’s interaction with the world, particularly
when tools are involved. This module implements the two core functionalities required of an
RL environment: state transition and reward calculation, especially in the context of multi-turn
interactionsandnon-deterministicoutcomesfromtooluse. Thedesignisformalizedthroughthe
BaseToolEnvabstractbaseclass.
Core State Transition and Reward Logic: The most critical abstract method is step. This
method is the primary engine for environmental interaction: it receives the agent’s raw output
(e.g., generated text potentially containing tool calls) and processes this output to identify and
orchestratetoolinvocationsincoordinationwiththeToolmodule. Basedontheagent’sactionsand
anyfeedbackfromtoolexecution,stepthenupdatestheenvironment’sinternalstate. Italsocalculates
anappropriaterewardsignalreflectingtheoutcomeoftheactionandthenewstate. Finally,itreturns
thenewstate,thereward,andotherrelevantinformation(suchassuccessstatusandactivityflags)to
theagent. Thismethodencapsulatesthelogicforbothstandardgenerativestatetransitionsandthe
morecomplex,potentiallystochastictransitionsresultingfromtoolinteractions.
SupportingMechanismsforInteractionManagement: Tofacilitatethestepmethod’scompre-
hensiveroleandmanagethenuancesoftool-basedinteractions,severalkeyauxiliarymethodsare
definedwithinBaseToolEnv. Theprocess_responses_idsmethodprovidescustomizablelogicfor
identifyingtoolcalltriggerswithintherawtokenIDsequencesgeneratedbytheLLM,determining
theprecisepointofinvocation. Subsequently,extract_tool_callsisresponsibleforparsingtheseraw
LLMresponsestoidentifyandstructureintendedtoolinvocationrequests,includingthetool’sname
anditsparameters. Followingatool’sexecution,format_tool_responseconvertstherawresults(ob-
tainedfromTool.execute)intoastringformatsuitableforpresentationtotheLLMaspartofthenew
environmentalstate. Complementingthese,thestopmethodimplementsthelogicfordetermining
trajectoryterminationconditions,assessingwhetherthecurrentinteractionshouldendbasedonLLM
output,taskcompletion,errorstates,orpredefinedlimits.
This design, centered on the step method’s pivotal role in driving environmental dynamics and
supportedbyclearmechanismsformanagingtoolcallsandtrajectorylifecycle,enablestheAgent-R1
frameworktoeffectivelysimulatecomplexinteractivescenarios. Itcarefullydistinguishesbetween
deterministictextgenerationandthenon-deterministic,environment-alteringstatechangesintroduced
bytooluse,whicharecrucialforagentlearning.
7

## Page 8

3.2 OptimizingAgentPolicyfromMulti-TurnTrajectories
Aftertherolloutphase,wehaveobtainedcomprehensivemulti-turninteractiontrajectories. Each
trajectorycontainsthesequenceofstates,theagent’sactions(generatedtextportions),andthereward
signals.Asnoted,theenvironmentprovidesrewardsignalsforeachinteractionturn,whicharetermed
processrewards(r ),inadditiontoapotentialfinaloutcomereward(r ). Toclearlydelineate
p f
thetokensgeneratedbytheLLMagent(itsactions)fromtheenvironmentalfeedbackortheinitial
promptwithinthetrajectory,weintroduceanActionMask. Thismaskidentifiespreciselywhich
partsofthesequencecorrespondtotheagent’slearnableactions.
Reinforcementlearningoptimizesthepolicymodel’sactionstomaximizeexpectedcumulativere-
wards. TheAgent-R1frameworkleveragesthedetailedinformationfromthesemulti-turntrajectories,
includingtheactionmasksandprocessrewards,toachievethisduringitslearningstage(asillustrated
inFigure4). Keyaspectsofhowthisinformationisutilizedinclude:
Refined and Aligned Advantage Calculation As seen in the generation stage (Figure 3), the
“Advantages” are no longer solely based on the final outcome reward and value estimates from
theCriticModel. The“ProcessRewards”gatheredfromToolEnvduringtherolloutareexplicitly
incorporated. ThismeanstheadvantageAˆ ateachrelevantsteptwithinatrajectoryreflectsnot
t
onlyfuturediscountedrewards(derivedfromoutcomerewardsandvaluefunctionestimates)butalso
theimmediatesuccessofintermediatesteps,suchaseffectivetoolinvocation(capturedbyprocess
rewards). The“Advantages”blockinFigure3showsittakinginputfrom“Values”(CriticModel),
“OutcomeReward”(RewardModel), and“ProcessRewards”. Crucially, thecalculationofthese
advantagesAˆ (e.g.,usingGeneralizedAdvantageEstimation-GAE)isperformedsuchthattheyare
t
alignedwiththeagent’sactionsasidentifiedbytheActionMask. Whilerewardsaccruebasedon
statetransitionsandvaluefunctionsestimatestategoodness,thefinaladvantagesusedforupdating
thepolicyarepertinenttothespecifictimestepswheretheagentgeneratedanaction. Thisensures
thatcredit(positiveornegativeadvantage)isassignedtotheactualdecisionsmadebytheagent,
ratherthantopartsofthesequenceitdidnotcontrol,suchasprompttokensorfixedenvironmental
responses. Theseaction-alignedadvantagesarethenpassedtothelearningstage(Figure4).
MaskedPolicyOptimization(ActorLoss) Inthelearningstage(Figure4),theActorModel(pol-
icy)isupdatedtoincreasetheprobabilityofactionsthatleadtohigheradvantages. The“Trajectory”
dataisfedintotheActorModeltoproduce“NewActionLogits”. TheActionMaskplaysacrucial
rolehere. WhencalculatingtheActorLoss(oftenapolicygradientlosslikePPO’sclippedsurrogate
objective),themaskensuresthatthelossiscomputedonlyoverthetokensgeneratedbytheagent.
The“Ratio”betweenthenewpolicy’sactionprobabilitiesandtheoldpolicy’sactionprobabilities
(derivedfrom“NewActionLogits”and“ActionLogits”fromthegenerationphase,respectively)is
modulatedbythesealignedadvantages,andthiscalculationisguidedbytheActionMask.
ValueFunctionUpdate(CriticLoss) TheCriticModelistrainedtomoreaccuratelyestimatethe
expectedcumulativereward(value)fromdifferentstates. Usingthe“Trajectory”data,itgenerates
“NewValues”. TheCriticLossistypicallyameansquarederrorbetweenthese“NewValues”and
theobservedreturns(whichincludebothprocessandoutcomerewards)fromthetrajectory,orthe
targetvaluesderivedfromthesereturnsandexistingvalueestimates(e.g.,inTDlearning). Thishelps
thecriticprovidebetterbaselineestimatesforadvantagecalculationinsubsequentiterations.
Byensuringthatthe“Advantages”arecalculatedinalignmentwiththeagent’sactualactions(and
subsequentlyusedwiththe“ActionMask”duringpolicyoptimization),Agent-R1providesamore
preciseandeffectivelearningsignal. ThisdetailedfeedbackmechanismallowstheActorandCritic
modelstolearnmoreefficientlyfromcomplex,extendeddialoguesandtool-usescenarios,driving
theagenttowardsmasteringsophisticatedtasks.
4 EmpiricalStudy
WeempiricallyevaluateAgent-R1’sefficacyanddesigncontributionsinachallengingmulti-hop
questionansweringscenariowhereLLMsuseexternalsearch. Thisstudyfirstvalidatestheframe-
work’seffectivenessintrainingLLMagentswithvariousReinforcementLearning(RL)algorithms
formulti-turninteractivetasks. Second,anablationanalysisinvestigatestheimpactofkeypolicy
8

## Page 9

optimization refinements: the action mask for loss computation (“loss mask”) and for aligning
advantages(“advantagemask”). TheoverarchinggoalistoassesstheLLM’slearnedabilityfortool
invocationandinformationretrieval,highlightingAgent-R1’sutility.
4.1 ExperimentalSetup
TasksandDatasets OurstudyusesMulti-hopQuestionAnswering(MultihopQA)datasets. The
trainingsetcomprises51,200samples,equallyandrandomlydrawnfromtheHotpotQA[34]and
2WikiMultihopQA[8]trainingsplits. WeevaluateonthefulldevelopmentsetsofHotpotQAand
2WikiMultihopQA(in-domain)andMusique[28](out-of-domain),whichrequiremulti-stepretrieval
andreasoning.
ModelsandTools ExperimentsuseQwen2.5-3B-Instruct[23]withintheNousToolEnvusingits
native function calling. The agent employs a single wikisearch tool querying a KILT Wikipedia
corpus(36Mpassages[21],embeddingsbybge-large-en-v1.5),returningtop5documents.
RL Algorithms and Baselines We evaluate PPO, GRPO, REINFORCE++, REIN-
FORCE++Baseline, and RLOO to assess Agent-R1’s adaptability. These are compared against
twobaselines: NaiveRAG(single-passretrieval)andBaseToolCall(nativefunctioncallingwith
wikisearchtool).
RewardFormulation Asparsefinaloutcomerewardr isused,definedas:
f
(cid:26)
r , ifr =1
r = answer format , (6)
f r −1, ifr <1
format format
Here,r =EM(a ,a )istheExactMatchscore. Theformattingscore,r =(r +
answer pred gold format formata
r )/2,averagesbinaryindicatorsforcorrectfinalanswerpresentation(r )andvalidtool
formatt formata
callsyntax(r ).Thisstructurestrictlyrewardsperfectlyformatted,correctanswersandpenalizes
formatt
anyformattingerrors.
4.2 MainResults
Theprimaryresultsofourframeworkvalidation,evaluatingtheperformanceofvariousReinforcement
Learning(RL)algorithmssupportedbyAgent-R1againstbaselinemethods,arepresentedinTable3.
Theexperimentswereconductedonthreemulti-hopquestionansweringdatasets. HotpotQAand
2WikiMultihopQA (2Wiki) served as in-domain datasets, while Musique was used as an out-of-
domaindataset. ThereportedscoresareExactMatch(EM)values,representingtheprimarymetric
fortasksuccess.
Table 3: Exact Match (EM) Performance Comparison of RL Algorithms and Baselines on Mul-
tihopQA Datasets. †Denotes in-domain datasets; *denotes out-of-domain dataset. Among RL
algorithms,bestperformancepercolumnisinbold,secondbestisunderlined.
Method HotpotQA† 2Wiki† Musique* Average
BaseToolCall 0.1372 0.0891 0.0277 0.0847
NaiveRAG 0.1916 0.1792 0.0277 0.1328
PPO 0.4136 0.5468 0.1552 0.3719
GRPO 0.4405 0.5741 0.1485 0.3877
REINFORCE++ 0.3768 0.4796 0.1336 0.3300
REINFORCE++Baseline 0.3966 0.5406 0.1485 0.3619
RLOO 0.4089 0.5641 0.1419 0.3716
Table 3 clearly demonstrates that all RL-trained agents substantially outperform both the Base
Tool Call (0.0847) and Naive RAG (0.1328) baselines. For instance, the weakest RL agent (RE-
INFORCE++, average EM 0.3300) still surpassed RAG by a factor of approximately 2.5. This
significantmarginhighlightsthecrucialroleofRLintrainingproficientLLMagentscapableof
9

## Page 10

complex multi-turn decision-making and effective tool use, moving beyond simpler heuristic or
single-passmethods.
Among the RL methods, GRPO (average EM 0.3877) exhibited the best overall performance,
closelyfollowedbyPPO(0.3719)andRLOO(0.3716). PPOnotablyexcelledonthechallenging
out-of-domainMusiquedataset. WhileREINFORCE++(0.3300)wastheweakestRLperformer,
incorporatingabaselineinREINFORCE++Baseline(0.3619)providedaclearbenefit,thoughitdid
notmatchthetop-tieralgorithms. TheseresultsrobustlyvalidateAgent-R1’sefficacyintraining
powerfulLLMagentsviaend-to-endRL,showingconsistent,substantialgainsoverbaselinesacross
diversedatasetsandRLalgorithms. Thisaffirmsthevalueofourframeworkforoptimizingagent
policiesininteractivesettings.
4.3 AblationStudyonPolicyOptimizationRefinements
To investigate the significance of specific policy optimization refinements within the Agent-R1
framework—namely,theuseofanactionmaskforlosscomputation(termed“lossmask”)andfor
the alignment of advantages (termed “advantage mask”)—we conducted an ablation study. This
studyutilizedthePPOandGRPOalgorithms. Theresults,intermsofExactMatch(EM)scores,are
presentedinTable4,whereeachablationstepisshownrelativetotheconfigurationinthepreceding
rowforthatalgorithm.
Table4: AblationStudyonPolicyOptimizationComponents. ScoresareExactMatch(EM).(cid:44)→
indicatesaconfigurationderivedfromtheimmediatelyprecedingrowwithinitsalgorithmgroupby
disablingthespecifiedcomponent. Baselineconfigurations(firstrowofeachgroup)use✓todenote
enabledcomponents. The’advantagemask’isnotseparatelyablatedforGRPOinthissetup.
Configuration HotpotQA 2Wiki Musique Average
PPO(lossmask✓,adv. mask✓) 0.4136 0.5468 0.1552 0.3719
(cid:44)→Advantagemaskdisabled 0.3630 0.4641 0.1138 0.3136
(cid:44)→Lossmaskdisabled 0.3429 0.4631 0.1005 0.3022
GRPO(lossmask✓) 0.4405 0.5741 0.1485 0.3877
(cid:44)→Lossmaskdisabled 0.4260 0.5485 0.1422 0.3722
The ablation experiments (Table 4) underscore the critical roles of both the loss mask and the
advantagemask. DisablingthelossmaskconsistentlydegradesperformanceforbothPPO(e.g.,
averageEMdroppingfrom0.3136to0.3022whenremovedfromaPPOvariantwiththeadvantage
maskalreadydisabled)andGRPO(averageEMdroppingfrom0.3877to0.3722). Thishighlights
its necessity in focusing gradients on agent-generated tokens. Similarly, for PPO, disabling the
advantage mask (while the loss mask is active, comparing the first two PPO rows) causes a
substantialperformancedropfromanaverageEMof0.3719to0.3136,affirmingtheimportanceof
accuratecreditassignment. Thesefindingsvalidatethatthesemaskingstrategiesarecrucialdesign
choiceswithinAgent-R1foreffectivepolicyoptimizationininteractiveLLMagents.
5 Conclusion
This work clarifies how Reinforcement Learning can be effectively applied to LLM Agents by
extendingtheclassicalMDPframeworktocapturemulti-turninteraction,environmentalfeedback,
andprocessrewards. Basedontheseinsights,weintroducedAgent-R1,amodularandextensible
frameworkthatsupportsmulti-turnrollouts,precisecreditassignment,andflexibleintegrationof
toolsandenvironments. Experimentsonmulti-hopquestionansweringdemonstratethatAgent-R1
enablesLLMagentstoachievesubstantialimprovementsoverbaselinemethods,andablationresults
confirmtheimportanceofitskeypolicyoptimizationcomponents. WehopeAgent-R1providesa
foundationforfutureworkonscalableandunifiedRLtrainingforagenticLLMs.
References
[1] YuntaoBai,SauravKadavath,SandipanKundu,AmandaAskell,JacksonKernion,AndyJones,
AnnaChen, AnnaGoldie, AzaliaMirhoseini, CameronMcKinnon, etal. Constitutionalai:
10

## Page 11

Harmlessnessfromaifeedback. arXivpreprintarXiv:2212.08073,2022.
[2] TomBrown,BenjaminMann,NickRyder,MelanieSubbiah,JaredDKaplan,PrafullaDhariwal,
ArvindNeelakantan,PranavShyam,GirishSastry,AmandaAskell,etal. Languagemodelsare
few-shotlearners. Advancesinneuralinformationprocessingsystems,33:1877–1901,2020.
[3] MingyueCheng,YucongLuo,JieOuyang,QiLiu,HuijieLiu,LiLi,ShuoYu,BohouZhang,
JiaweiCao, JieMa, etal. Asurveyonknowledge-orientedretrieval-augmentedgeneration.
arXivpreprintarXiv:2503.10677,2025.
[4] AakankshaChowdhery,SharanNarang,JacobDevlin,MaartenBosma,GauravMishra,Adam
Roberts,PaulBarham,HyungWonChung,CharlesSutton,SebastianGehrmann,etal. Palm:
Scalinglanguagemodelingwithpathways. JournalofMachineLearningResearch,24(240):1–
113,2023.
[5] PaulFChristiano,JanLeike,TomBrown,MiljanMartic,ShaneLegg,andDarioAmodei. Deep
reinforcementlearningfromhumanpreferences. Advancesinneuralinformationprocessing
systems,30,2017.
[6] DayaGuo,DejianYang,HaoweiZhang,JunxiaoSong,RuoyuZhang,RunxinXu,QihaoZhu,
ShirongMa,PeiyiWang,XiaoBi,etal. Deepseek-r1: Incentivizingreasoningcapabilityin
llmsviareinforcementlearning. arXivpreprintarXiv:2501.12948,2025.
[7] TaichengGuo,XiuyingChen,YaqiWang,RuidiChang,ShichaoPei,NiteshVChawla,Olaf
Wiest,andXiangliangZhang. Largelanguagemodelbasedmulti-agents: Asurveyofprogress
andchallenges. arXivpreprintarXiv:2402.01680,2024.
[8] Xanh Ho, Anh-Khoa Duong Nguyen, Saku Sugawara, and Akiko Aizawa. Constructing
a multi-hop qa dataset for comprehensive evaluation of reasoning steps. arXiv preprint
arXiv:2011.01060,2020.
[9] Sirui Hong, Mingchen Zhuge, Jonathan Chen, Xiawu Zheng, Yuheng Cheng, Jinlin Wang,
CeyaoZhang,ZiliWang,StevenKaShingYau,ZijuanLin,etal. Metagpt: Metaprogramming
foramulti-agentcollaborativeframework.InTheTwelfthInternationalConferenceonLearning
Representations,2023.
[10] Wenlong Huang, Fei Xia, Ted Xiao, Harris Chan, Jacky Liang, Pete Florence, Andy Zeng,
Jonathan Tompson, Igor Mordatch, Yevgen Chebotar, et al. Inner monologue: Embodied
reasoningthroughplanningwithlanguagemodels. arXivpreprintarXiv:2207.05608,2022.
[11] AaronJaech,AdamKalai,AdamLerer,AdamRichardson,AhmedEl-Kishky,AidenLow,Alec
Helyar, AleksanderMadry, AlexBeutel, AlexCarney, etal. Openaio1systemcard. arXiv
preprintarXiv:2412.16720,2024.
[12] ChuangJiang,MingyueCheng,XiaoyuTao,QingyangMao,JieOuyang,andQiLiu. Table-
mind: Anautonomousprogrammaticagentfortool-augmentedtablereasoning. arXivpreprint
arXiv:2509.06278,2025.
[13] BowenJin, HansiZeng, ZhenruiYue, JinsungYoon, SercanArik, DongWang, HamedZa-
mani,andJiaweiHan. Search-r1: Trainingllmstoreasonandleveragesearchengineswith
reinforcementlearning. arXivpreprintarXiv:2503.09516,2025.
[14] GuohaoLi,HasanHammoud,HaniItani,DmitriiKhizbullin,andBernardGhanem. Camel:
Communicativeagentsfor"mind"explorationoflargelanguagemodelsociety. Advancesin
NeuralInformationProcessingSystems,36:51991–52008,2023.
[15] HunterLightman,VineetKosaraju,YuriBurda,HarrisonEdwards,BowenBaker,TeddyLee,
JanLeike,JohnSchulman,IlyaSutskever,andKarlCobbe. Let’sverifystepbystep. InThe
TwelfthInternationalConferenceonLearningRepresentations,2023.
[16] Xiao Liu, Hao Yu, Hanchen Zhang, Yifan Xu, Xuanyu Lei, Hanyu Lai, Yu Gu, Hangliang
Ding,KaiwenMen,KejuanYang,etal. Agentbench: Evaluatingllmsasagents. arXivpreprint
arXiv:2308.03688,2023.
11

## Page 12

[17] YucongLuo, YitongZhou, MingyueCheng, JiahaoWang, DaoyuWang, TingyuePan, and
JintaoZhang. Timeseriesforecastingasreasoning: Aslow-thinkingapproachwithreinforced
llms. arXivpreprintarXiv:2506.10630,2025.
[18] JieOuyang,TingyuePan,MingyueCheng,RuiranYan,YucongLuo,JiayingLin,andQiLiu.
Hoh: Adynamicbenchmarkforevaluatingtheimpactofoutdatedinformationonretrieval-
augmentedgeneration. arXivpreprintarXiv:2503.04800,2025.
[19] LongOuyang,JeffreyWu,XuJiang,DiogoAlmeida,CarrollWainwright,PamelaMishkin,
ChongZhang,SandhiniAgarwal,KatarinaSlama,AlexRay,etal. Traininglanguagemodelsto
followinstructionswithhumanfeedback. Advancesinneuralinformationprocessingsystems,
35:27730–27744,2022.
[20] JoonSungPark,JosephO’Brien,CarrieJunCai,MeredithRingelMorris,PercyLiang,and
MichaelSBernstein. Generativeagents: Interactivesimulacraofhumanbehavior. InProceed-
ingsofthe36thannualacmsymposiumonuserinterfacesoftwareandtechnology,pages1–22,
2023.
[21] FabioPetroni,AleksandraPiktus,AngelaFan,PatrickLewis,MajidYazdani,NicolaDeCao,
JamesThorne,YacineJernite,VladimirKarpukhin,JeanMaillard,etal. Kilt: abenchmarkfor
knowledgeintensivelanguagetasks. InProceedingsofthe2021ConferenceoftheNorthAmer-
icanChapteroftheAssociationforComputationalLinguistics: HumanLanguageTechnologies,
pages2523–2544,2021.
[22] JiahaoQiu,XuanQi,TongchengZhang,XinzheJuan,JiachengGuo,YifuLu,YiminWang,
ZixinYao,QihanRen,XunJiang,etal. Alita:Generalistagentenablingscalableagenticreason-
ingwithminimalpredefinitionandmaximalself-evolution. arXivpreprintarXiv:2505.20286,
2025.
[23] Qwen, :, An Yang, Baosong Yang, Beichen Zhang, Binyuan Hui, et al. Qwen2.5 technical
report,2025.
[24] ColinRaffel,NoamShazeer,AdamRoberts,KatherineLee,SharanNarang,MichaelMatena,
YanqiZhou,WeiLi,andPeterJLiu. Exploringthelimitsoftransferlearningwithaunified
text-to-texttransformer. Journalofmachinelearningresearch,21(140):1–67,2020.
[25] TimoSchick,JaneDwivedi-Yu,RobertoDessì,RobertaRaileanu,MariaLomeli,EricHambro,
LukeZettlemoyer,NicolaCancedda,andThomasScialom. Toolformer: Languagemodelscan
teachthemselvestousetools. AdvancesinNeuralInformationProcessingSystems,36:68539–
68551,2023.
[26] ZhihongShao,PeiyiWang,QihaoZhu,RunxinXu,JunxiaoSong,XiaoBi,HaoweiZhang,
MingchuanZhang,YKLi,YangWu,etal. Deepseekmath: Pushingthelimitsofmathematical
reasoninginopenlanguagemodels. arXivpreprintarXiv:2402.03300,2024.
[27] Noah Shinn, Federico Cassano, Ashwin Gopinath, Karthik Narasimhan, and Shunyu Yao.
Reflexion:Languageagentswithverbalreinforcementlearning.AdvancesinNeuralInformation
ProcessingSystems,36:8634–8652,2023.
[28] Harsh Trivedi, Niranjan Balasubramanian, Tushar Khot, and Ashish Sabharwal. Musique:
Multihopquestionsviasingle-hopquestioncomposition. TransactionsoftheAssociationfor
ComputationalLinguistics,10:539–554,2022.
[29] Daoyu Wang, Mingyue Cheng, Qi Liu, Shuo Yu, Zirui Liu, and Ze Guo. Paperarena: An
evaluation benchmark for tool-augmented agentic reasoning on scientific literature. arXiv
preprintarXiv:2510.10909,2025.
[30] GuanzhiWang,YuqiXie,YunfanJiang,AjayMandlekar,ChaoweiXiao,YukeZhu,LinxiFan,
andAnimaAnandkumar. Voyager: Anopen-endedembodiedagentwithlargelanguagemodels.
arXivpreprintarXiv:2305.16291,2023.
[31] LeiWang,ChenMa,XueyangFeng,ZeyuZhang,HaoYang,JingsenZhang,ZhiyuanChen,
JiakaiTang,XuChen,YankaiLin,etal. Asurveyonlargelanguagemodelbasedautonomous
agents. FrontiersofComputerScience,18(6):186345,2024.
12

## Page 13

[32] QingyunWu,GaganBansal,JieyuZhang,YiranWu,BeibinLi,ErkangZhu,LiJiang,Xiaoyun
Zhang, Shaokun Zhang, Jiale Liu, et al. Autogen: Enabling next-gen llm applications via
multi-agentconversations. InFirstConferenceonLanguageModeling,2024.
[33] ZhihengXi,YiwenDing,WenxiangChen,BoyangHong,HonglinGuo,JunzheWang,Xin
Guo,DingwenYang,ChenyangLiao,WeiHe,etal. Agentgym: Evaluatingandtraininglarge
languagemodel-basedagentsacrossdiverseenvironments. InProceedingsofthe63rdAnnual
Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pages
27914–27961,2025.
[34] ZhilinYang,PengQi,SaizhengZhang,YoshuaBengio,WilliamCohen,RuslanSalakhutdinov,
andChristopherDManning. Hotpotqa: Adatasetfordiverse,explainablemulti-hopquestion
answering. InProceedingsofthe2018conferenceonempiricalmethodsinnaturallanguage
processing,pages2369–2380,2018.
[35] ShunyuYao,JeffreyZhao,DianYu,NanDu,IzhakShafran,KarthikRNarasimhan,andYuan
Cao.React:Synergizingreasoningandactinginlanguagemodels.InTheeleventhinternational
conferenceonlearningrepresentations,2022.
[36] ShuoYu,MingyueCheng,QiLiu,DaoyuWang,JiqianYang,JieOuyang,YucongLuo,Chenyi
Lei,andEnhongChen. Multi-sourceknowledgepruningforretrieval-augmentedgeneration: A
benchmarkandempiricalstudy. InProceedingsofthe34thACMInternationalConferenceon
InformationandKnowledgeManagement,pages3931–3941,2025.
[37] Shuo Yu, Mingyue Cheng, Daoyu Wang, Qi Liu, Zirui Liu, Ze Guo, and Xiaoyu Tao.
Memweaver: Ahierarchicalmemoryfromtextualinteractivebehaviorsforpersonalizedgenera-
tion. arXivpreprintarXiv:2510.07713,2025.
13
