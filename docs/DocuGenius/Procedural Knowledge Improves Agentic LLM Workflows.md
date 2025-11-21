## Page 1

Procedural Knowledge Improves Agentic LLM Workflows
Vincent Hsiao
NRCPostdoctoralFellow,NavalResearchLaboratory
Washington,DC
UnitedStates
vincent.hsiao.ctr@us.navy.mil
Mark Roberts
NavyCenterforAppliedResearchinAI,NavalResearchLaboratory
Washington,DC
UnitedStates
mark.c.roberts20.civ@us.navy.mil
Leslie Smith
NavyCenterforAppliedResearchinAI,NavalResearchLaboratory
Washington,DC
UnitedStates
leslie.n.smith20.civ@us.navy.mil
November12,2025
Abstract
Largelanguagemodels(LLMs)oftenstrugglewhenperformingagentictaskswithout
substantialtoolsupport,prom-ptengineering,orfinetuning. Despiteresearchshowing
thatdomain-dependent,proceduralknowledgecandramaticallyincreaseplanningef-
ficiency,littleworkevaluatesitspotentialforimprovingLLMperformanceonagentic
tasks that may require implicit planning. We formalize, implement, and evaluate an
agenticLLMworkflowthatleveragesproceduralknowledgeintheformofahierarchical
task network (HTN). Empirical results of our implementation show that hand-coded
HTNscandramaticallyimproveLLMperformanceonagentictasks,andusingHTNscan
boosta20bor70bparameterLLMtooutperformamuchlarger120bparameterLLM
baseline. Furthermore,LLM-createdHTNsimproveoverallperformance,thoughless
so. Theresultssuggestthatleveragingexpertise–fromhumans,documents,orLLMs–to
curate procedural knowledge will become another important tool for improving LLM
workflows.
Keywords LargeLanguageModels,AgenticSystems,TaskNetworks
1 Introduction
Proceduralknowledgegenerallydescribesasequenceforsolvingaproblemandhasplayedanimportant
roleinAI.Forexample,spanningnearly50yearsofautomatedplanningresearch,proceduralknowledge
hasbeeneffectiveforareassuchasdecomposingabstracttasksintoconcreteactions(27;2),control
rulesforsearch(1),learningmacrooperators(6),planrecognition(7),knowledge-basedplanning(18),
and planning and acting (8), to name only a few. Procedural knowledge also plays a central role in
DISTRIBUTIONSTATEMENTA.Approvedforpublicrelease;distributionisunlimited.
5202
voN
01
]IA.sc[
1v86570.1152:viXra

## Page 2

cognitivesystems(17),whereaspecificmoduleinthesystemmanagesandappliessuchknowledgeto
problemsolving. Recently,proceduralknowledgeisusedasakindofmeta-strategytoassistinsolving
complexproblems(e.g.,(3)).
WhileLLMshaveshownimpressivecapability,theyoftenperformpoorlyonplanningproblems(13),and,
aswewillshowlater,LLMperformancegenerallydegradesastaskcomplexityincreases. Incomplex
agentictasks,successfultaskcompletionoftenhingesonanimplicitplanthatspecifieswhatactions
to take and in what sequence to take them, a capability that current LLMs often fail to consistently
complete correctly. Part of the gap is that LLMs are mostly constructed to predict the next token,
whileplanningrequiresmanagingdetailsthatspandifferenttemporalhorizonsanddifferentlevelsof
abstraction. LLMslackaclearlyunderstoodwaytotrackthechangethatresultsfromtakingactionin
theworld.
In contrast, this paper examines whether providing explicit procedural knowledge improves LLM
performanceonagentictasks. Toprovideanintuitiveexample(formalizedin§3),considerthetaskof
bookingatravelitinerary. Experiencedtravelersfollowasequencesuchas: bookflights,bookhotel,
and reserve attractions or restaurants. The sequence might vary by circumstance, but its presence
makes the problem much easier to solve. The sequence manages dependencies (e.g., confirm flights
beforebookingthehotel)andeachstepnarrowsthedetailsconsideredinsubsequentsteps. Butusing
anabstractsequencerequiresaprocessthat: 1)tracksprogressontheoverallprocedure,2)maintains
statechangesacrosssteps,3)takesactionstocompleteeachstep,4)verifieseachstepisfinishedbefore
proceeding.
Whensolvingatravelproblemlikethis,LLMslackthecapabilitytotracktheselayersallatonce,leading
toinefficientorunsuccessfulworkflows. Forexample,anLLMmightbookarestaurantreservationat
thedestinationbeforeverifyingflighttiming,onlytobacktracktoaddresssuchforeseeableconflicts.
Bytreatingcomplextasksasaseriesofindependentdecisionsratherthanattendingtointerconnected
dependencies,LLMsstruggletoleverageprocedural(i.e.,hierarchical,goal-oriented)knowledge.
Inthispaper,weaddresstwoquestions: CanweembedproceduralknowledgeinanLLMworkflow? and
WillproceduralknowledgeimproveLLMperformance? Wewillshowthattheanswertobothquestions
isYes! Tothatend:
• WeformalizetheproblemasanMDPandintegrateproceduralknowledgeusingHierarchicalTask
Networks(HTNs),whereabstracttasksdecomposeintototallyorderedsubtasks. AnHTNensures
logicalconsistencyandresourceavailability.
• WedescribeandimplementahybridLLM-HTNsystem,ProcLLM,thatusesHTNsinanagenticLLM
workflow. Importantly,thisworkflowiscompatiblewithanyLLM.
• Weevaluatetheruntime,success,andnumberofcyclesofProcLLMonfourbenchmarkproblems,
twofromtheliteratureandtwosyntheticproblems. For the problems and HTNs we studied, HTN
knowledge always improves LLM performance, often significantly.
• WedemonstratethatsmallerLLMsbenefitmorefromthisworkflowandinsomecasesexceedthe
performanceofmuchlargerLLMswithoutHTNknowledge.
• Finally,weshowthatLLM-createdHTNsimproveperformance,thoughtheresultsaremixedcompared
tohand-codedHTNs.
Overall,thesefindingssuggestthatLLMworkflowscanbenefitconsiderablyfromproceduralknowledge,
notonlyinoverallperformancebutalsoinareducedmodelsizeandimprovedresponsetimeforthe
same level of performance. Although our implementation uses an Agentic LLM workflow with HTN
knowledge,theprocessisstraightforwardandresultsmayeventuallygeneralizetootherLLMworkflows,
soweclosewithsomepossiblefuturedirections.
2 Related Work
Agentic LLMs. WedefineagenticLLMasalargelanguagemodelframeworkthatcanact,usetools,
andplantoautonomouslyaccomplishtasks. Manyproblemscannotbesolvedinasingleforwardpassof
anLLM,motivatingworkflowtechniquessuchaspromptchaining(32),wheretheoutputofoneprompt
becomestheinputtoanother. EarlycommunitysystemslikeAutoGPT(34)showcasedthepotentialof
2

## Page 3

chainingandmemory-augmentedreasoningforopen-endedtasks,whileframeworkssuchasLangChain
providedmodularinfrastructureforbuildingagenticpipelinesaroundLLMs
OneofthefirstacademicapproachesinthisareawastheReActframework(35),whereagentreasoning
choicesareinterleavedwithactionselectioninordertointeractwithexternalenvironments. Another
notablecontributionwasExpeL(38),whereanagentthatlearnsfromexperiencesandnaturallanguage
tomakeinformeddecisionswithoutrequiringparametricupdates.
Although there are many variations of this framework, for the purpose of this paper, we will use a
frameworksimilartotheoneusedbyReflexion(Fig. 2in(23)). TheReflexionagentemploysanLLM
(denotedastheagent)andanenvironmentthatprocessesactionsacrossmultipleiterations. Ateach
iteration,theagentreceivesanobservationfromtheenvironment. Thisobservationiscombinedwitha
promptgiventotheLLMtooutputsomeaction. Theenvironmentprocessesthisactionandthenreturns
theobservationforthenextiteration.
PerhapstheclosesttothispaperistheconcurrentworkofBelcakandMolchanov(3). Intheiruniversal
deepresearch(UDR)framework,astrategycompilerisusedtotakearesearchstrategyfromtheuser
andcompileitintoalistofstepsandcorrespondingoutputsthatadeepresearchtoolneedstoexecute
stepbystep. Thestructureisenforcedbyincorporatingcodecommentsandyielddirectivesthatspecify
the goal of each step and the intended outputs of the step. Our approach is more general, and we
canhypothesizethatthereexistsatasknetworkthatwhenappliedtooursystemwouldreplicatethe
behaviorofUDR.
LLMs and Tool-use. TosupplementcapabilitiesindomainswhereLLMshavepoorperformance,itis
commontoallowLLMstointerfacewithexternaltools. ThesetoolsenhancetheLLMswithcapabilities
thattheymightotherwisenothave(31)andtherearenumerouspaperscoveringvariousaspectsofthis
field of research (12; 20). Early demonstrations included Toolformer (21), which fine-tuned LLMs to
invokeAPIsfromdemonstrations,andMRKL(15),whichintegratedsymbolicreasoningwithtool-use.
Unlikepastwork,oursystemallowstheLLMagenttowritearbitrarycodetocallarbitraryAPIs. Thisis
differentfromworkswheretheexternaltoolsarepresentedinastandardizedin-contextformattoan
LLMforusage(e.g.,MCPservers). AllowingtheLLMtowritearbitrarycodealsogivesmoreflexibility
inproblemsolving(e.g.,codingallowstheLLMtoembedtoolcallsinalgorithms),whichstandardized
toolformatsdonotpermit.
Multi-agent Systems. The extension from single-agent to multi-agent frameworks has become an
importantlineofresearch. InAgentOrchestra(37),anorchestratoragentcreatesaplanthatisthen
executedbyspecializedsub-agents. Unlikeourexplicittasknetworkrepresentation,AgentOrchestra
usesasimpleliststructure. SagaLLM(4)proposesatransactionalsystemtohandlemulti-stepplanning
inmulti-agentLLMsystems. Otherworks,suchasCAMEL(19),demonstratedemergentcoordination
betweenspecializedLLMagentsbyrole-playingtasksandnegotiatingvianaturallanguage.
Hybrid Systems. Various hybrid systems have been developed for application to specific domains.
Forexample,(11)providesasurveyofLLM-basedagenticrecommendersthatincorporatesubsystems
similar to planning and acting modules. AutoConcierge (36) employs LLMs to convert user requests
intoformalizedrepresentationstobeusedbyareasoner. Thisisalsosimilartotheapproachfrom(10),
whereuserrequestsandAPIcallsaretranslatedintoconstraintsforanSMTsolver. Bothapproaches
useLLMstoconvertuserdataintoformalizedproblemdescriptions,whicharethensolvedtoprovidea
solution. Thisisdifferentfromourapproach,whichinsteadusesaformalizedrepresentationtoassist
theLLMintheproblem-solvingprocess.
OtherthanagenticLLMsystems,therearemanyLLM-modulosystemsthatcombineLLMswithexternal
verifiersandorsolvers(14). ISR-LLM(39)employsanLLMtotranslateplanningproblemsinnatural
language into PDDL and then iteratively calls the external planner to verify LLM-generated plans.
BeyondagenticLLMsystems,manyhybridapproachescombineLLMswithexternalverifiersorsolvers
(14). ISR-LLM(39),forinstance,employsanLLMtotranslateplanningproblemsinnaturallanguage
intoPDDLandtheniterativelycallsanexternalplannertoverifyandrefineplans. Similarly,program
synthesisapproaches(5)useLLMstogeneratecandidatecodethatisexecutedandverifiedexternally.
3

## Page 4

These hybrid formulations highlight a broader paradigm: using LLMs as flexible natural-language
interfaceswhiledelegatingcorrectnessandreliabilitytosymbolicoralgorithmiccomponents.
LLMs and Planning. Inchallengingtasks,anagentmayneedtogenerateaplanbeforecompleting
thetask. ManyresearchershaveinvestigatedhowLLMscanbeusedeffectivelyforplanning(26)(25)
(14). Therehavebeenimpressivegainsinthisareaofresearch;forexample,arecentnotableexample
isbyVermaetal.(30)whichclaimsupto94%planningaccuracyusingafine-tuningapproachpaired
with chain-of-thought reasoning. Despite these gains, planning remains a challenging task (24) (29)
with many results showing that LLMs still have many weaknesses when applied to these problems.
Furthermore,manyapproachesstillrequireconsiderablescaffolding.
A consistent claim is that the effectiveness of LLM planning is reduced as task complexity increases.
Kambhampati (13) argues that LLMs engage in universal approximate retrieval, where they rely on
patternmatchingratherthansystematicreasoning. Thissufficesforgeneratingimmediatesolutionsor
shortinferencechains,butcanrunintoissueswhentaskcomplexityincreases,whichcanbeseenin
ACPBench(16)wherethetaskofgeneratingjustthenextactionhasamuchhighersuccessratethan
themorecomplextasks. ThissuggeststhatcurrentLLMsaremosteffectiveatsolvingshorttasksthat
donotneedmulti-stepplanning. Anaturalsolutionwouldbeasfollows: Whentheprovidedtaskistoo
complexforanLLMagent,decomposethetaskintosubtasksforwhichtheLLMiseffective.
Unlike other works in this area, our focus is not directly on the ability of an LLM to produce a plan
(i.e., a sequence of steps solving the planning task). Rather, in many tasks that agentic LLMs are
appliedtosolve,asortofmeta-planningisarequisiteprocessforsolvingcomplexprobleminstances.
Bydecomposingataskintosmallersubtasks,themeta-planningrequiredwillbelesscomplexandthe
agenticsystemwillbelessimpactedbyweaknessesofcurrentLLMswhenencounteringcomplextasks.
3 Preliminaries
WerepresentproceduralknowledgeusingaHierarchicalTaskNetwork(HTN),describednext. Wethen
formalizetheproblemasaMarkovDecisionProcess(MDP)wherethepolicythatsolvestheMDPisan
LLM.Finally,weanalyzewhyweexpectProcLLMtoperformwell.
Hierarchical Task Networks (HTNs). Becauseourfocusisonhowproceduralknowledgeimproves
LLMperformance,ourdescriptionofHTNssacrificesexactformalityforamorenotionalunderstanding.
A full formal treatment can be found in (8). Let K be a set of tasks; a task κ ∈ K is a labeled name
of something the system needs to do. Figure 1 (top) shows an HTN decomposition tree where K
relates to the travel problem from §1. HTNs decompose complex tasks (white boxes) into primitive
tasks (gray boxes) using methods (ovals). Complex tasks describe abstract tasks that need to be
decomposed and primitive tasks describe concrete executable tasks. Figure 1 shows two methods.
Methodm-process-user-requestdecomposesκ p into⟨κ 1 ,..,κ 4 ⟩, wheretheκ 1 (dashedbox)haspassed
the verify check (described below). Method choose departing flight decomposes κ 2 into primitive
tasks: ⟨understand flight tool,write flight to notes⟩.
For a set of methods M, a method m ∈ M is a tuple (head,task,pre,subtasks), where the head is the
nameandanyparamatersofthemethod,task matchesthetasknamethemethodcandecompose,pre
is a(possibly empty) set ofpreconditions for applyingthe method ina state, and subtasks is atotally
orderedsequenceoftasks⟨κ 1 ,κ 2 ,..,κ n ⟩. Amethodthatmatchesataskisrelevant,andHTNplanners
oftenselectthefirstrelevantmethodinM(Asdescribedin§4,ProcLLM’sAlgorithm1,Line24uses
FindFirstRelevantMethodtoselectmethods).
MarkovDecisionProcess(MDP)Model. Weformalizeagentictasksasafinite-horizondeterministic
MarkovDecisionProcess(MDP),definedbythetupleM=(S,A,T,r,H),whereS isthesetofstates
withasubsetofabsorbingterminalstates,S ⊂S,Aissetofactions,T :S×A→S isadeterministic
term
state transition function, where s i+1 = T(s i ,a i ), r : S ×A → R is a reward function, and H is a finite
horizon. Anepisodeterminateseitherbyreachingaterminalstateorbyexceedingthehorizon(timeout).
4

## Page 5

1{"m-travel-process-user-request": {
2 "task": "process user request",
3 "subtasks": {"1": "understand user request",
4 "2": "choose a departing flight",
5 "3": "choose a returning flight",
6 "4": "choose an accommodation" },
7 "verify": "answer.txt contains a solution in the correct format that follows the problem specification",
8 "verify_files": {"file1": "problem_specification.txt",
9 "file2": "answer.txt" }},
10"m-choose-departing-flight": {
11 "task": "choose a departing flight",
12 "subtasks": {"1": "understand flights tool",
13 "2": "write flight to notes" },
14 "verify": "notes contains details about a flight number and cost for a flight from origin to destination on departure
date consistent with request preferences",
15 "verify_files": {"file1": "files/notes.txt",
16 "file2": "files/problem_specification.txt",
17 "file3": "files/request.txt" } },
18"m-understand-flights-tool": {
19 "name": "understand flights tool",
20 "effect": "notes contains details about flights tool methods inputs and outputs",
21 "effect_files": {"file1": "files/notes.txt",
22 "file2": "files/tools_specification.txt" } } }
Figure1: Top: Anin-progressHTNdecompositiontreefortheTravelPlannerproblemof§1. Whiteboxes
indicateabstracttasks,roundovalsindicatemethodsthatdecomposetasks,andgrayboxesindicate
primitivetasksfortheLLMtoexecute. Thedashedboxforκ 1 indicatesithaspassedverify. Bottom:
Notionalmethodsforthesameproblem.
5

## Page 6

For our domains, we define a function verify : S → {0,1}, that identifies terminal states (i.e.,
verify(s)=1ifs∈S and0otherwise). Therewardfunctionisthen:
term
(cid:40)
r(sa)= r success ifverify(T(s , a))=1 (aterminalstate)
,
r otherwise
step
wherer =1isapositiverewardfortaskcompletionandr isanegativerewardfornon-terminal
success step
steps(e.g.,r
step
=−0.1). PrimitivetasksfromtheHTNarelinkedtoS term,whichcanbeverifiedusing
verify.
Anagent’sbehaviorisdescribedbyastochasticpolicyπ :S×A→[0,1],whereπ(s,a)=P(a
i
=a|s
i
=s)
is the probability of selecting a in state s. A solution to M is a policy π that maximizes the expected
reward(inthiscaseapolicythatreachesaterminalstateinthefeweststeps).
Initial Analysis. In this work, we investigate the use of an agentic LLM system as the policy π that
operates within this MDP framework. We show that divide-and-conquer mechanisms such as task
decompositioncanbeusedtoconstrainπ toworkonsmallerproblems,increasingtheexpectedreward
obtainedbyouragenticLLM.
ThegeneralMDPmodelallowsustohypothesizeaboutwhyweexpectthisapproachtowork. Weassume
thatthereexistsatask-awareassemblyfunctionA:S×K →C andletC i bethecontextproducedfrom
states i usedasinputtotheLLMateachiteration.
Task Success Rate. A task succeeds if a terminal state s ∈ S is reached within H steps. Let
term
(a 0 ,...,a H−1 ) be a sequence of actions that arrives at a terminal state from an initial state s 0. As-
sumingdeterministictransitions,theprobabilityoftakingtheseactionsdependssolelyontheLLM’s
parameterizationθ,whichgovernsactionselection:
H−1
(cid:89)
P (a ,a ,...,a )= P (a |C )
θ 0 1 H−1 θ i i
i=0
Here, P θ (a i |C i ) represents the LLM’s conditional probability of selecting action a i given context C i.
Thisfactorizationarisesbecauseeachactiondependsonlyonthecurrentcontext(Markovproperty).
Task Decomposition. A task decomposition splits a problem into a sequence of smaller subtasks,
(κ 0 ,...,κ n−1 ). Let P θ (κ j ) be the probability of successfully completing subtask j. Decomposition
improvestasksuccessif:
n−1
(cid:89)
P
θ
(fulltask)< P
θ
(κ
j
)
j=0
Wehypothesizethatwecanimprovetherightsideofthisequationthroughcontextualscaffolding. We
assumethattheLLM’sabilitytocompleteasubtaskP
θ
(κ
j
)increasesbyreducingcontextcomplexity.
When the agent works on a specific subtask κ j, the assembly function A(s i ,κ j ) generates a focused
contextC′ . Byconstrainingtheproblemspacethroughreducingcontextcomplexity,theconditional
i,j
probabilityofselectingacorrectactiona i shouldincrease:
P (a |C′ )>P (a |C )
θ i i,j θ i i
Becausetheprobabilityofsuccessforasubtaskκ j,P
θ
(κ
j
),istheproductoftheindividualP
θ
(a
i
|C
i
′
,j
),
thetasksuccessrateP
θ
(κ
j
)willalsoincrease.
4 ProcLLM: Embedding Procedural knowledge into an agentic LLM
ProcLLMimplementsaplanningandactingsystem(8)inwhichanagentiteratesbetweenHTNplanning,
where it updates the current (sub)task based on progress, and action execution, where it executes
primitivetasks(i.e.,actions)andverifiesthattheyarecompleted. RelatingProcLLMtotheformalism,
wenextdescribethecomponentsofthissystem,asshowninFigure2.
Environment and states S. Forthebenchmarkswestudyinthispaper,theenvironmentcorresponds
toafilesystemwithtextfilesandpythoncodefiles(Figure2,bottominyellow). Theagentisprovided
6

## Page 7

with the following text (.txt) files or python (.py) code, where the first column rwa indicates allowed
read/write/appendactions,respectively.
r ProblemSpecoutlinesthedomain-specificrulesoftheproblemtosolveandformatofAnswer,which
isthesameforallrequestinstances. (See§Cforfulldetails.)
r Request contains problem instance details to be solved such as the initial configuration of the
problemandthegoalconfiguration. (See§Cforfulldetails.)
r ToolsSpec is a human readable description of Tools, which are APIs that include source code,
informationaltextfiles,orstructuredtext(e.g.,csv,JSON).
rwa Notesstartsemptyandwillcontaintheagent’sprogressordetailsaboutthetaskortaskhistory.
rwa Solverisonlyprovidedforsomeproblems;theenvironmentexecutesit,writingtooutputanderror.
rwa Answerstartsemptyandwillcontaintheagent’ssolutiontotheoveralltask.
ThecontentofthefilesaswellasotherdetailsareassembledintocontextC =A(e
1
,e
2
,...,e
k
)containing
one or more elements e i. For ProcLLM this includes the action context C a = A a (s ,trace,κ)), and the
verifycontextC
v
=A
v
(s,trace,κ).
Algorithm 1AgeneralprocedureforProcLLM.
Input: TaskSequenceK,MethodsM,horizonH
1: procedureProcLLM(K,M,H)
2: UpdateTask(K,M)
3: foriin1,...,H do
4: ifK ==∅thenbreak
5: κ ←head(K)
6: C a ←A a (s ,trace,κ)
7: a(params)←action-LLM(C a )
8: trace←‘’
9: ifa=verifythen
10: C v ←A v (s , κ)
11: verified,feedback ←verify-LLM(C v )
12: trace←feedback
13: ifverifiedthen
14: pop(K) ▷removefirsttaskκ fromK
15: UpdateTask(K,M)
16: else ▷applyr/w/atoenv’t;(performss′ ←T(s , a))
17: trace←file ▷writefiletothetrace
18: ifa=write(file,content)thenfile.clear()
19: file←file+content
20: iffile=Solverthen
21: out,err←Exec(Solver)
22: trace←trace+out+err
23: procedureUpdateTask(K,M)
24: m←FindFirstRelevantMethod(head(K),M)
25: ifm then
26: push(m.subtasks,K) ▷Prependm.subtasks
27: UpdateTask(K,M) ▷Decomposefurther
Actions A and transition T. Theagentcantakeoneoffouractions: verify,read,write,orappend.
Theinternalactionverifycallsaprocessthatchecksifthecurrenttaskhasbeensatisfied,returninga
booleanverifiedifthetaskiscompletedaswellasfeedbackwhichisaddedtothetrace. Theverify
stepisdomain-specificandusestheverify-LLM.(Adetailedexampleoftheverifypromptisprovided
inAppendixF.)
The external actions modify the writeable files, which are subsequently assembled into the context.
read(file): copiesfileintoNotes
Theseinclude: write(file,content): overwritesfilewithcontent
append(file,content): appendscontenttofile
TheseexternalactionsmustbeinaJSONformatfortheenvironmenttoexecute(foradetailedexample,
7

## Page 8

Figure2: Systemoverview,labeledwithcomponentsoftheMDP.Blueboxesdenotetextfiles,orange
boxesdenoteLLMs,redboxesdenotepythonfiles,andgreenboxesdenoteAPIfiles(scripts/databas-
es/etc.).
8

## Page 9

see Appendix B.2). The environment implements a transition function as a set of scripts that calls
Exec(Solver)andotherwisemodifiesfilesasindicatedintheactions.
Tasks K and Methods M. ForProcLLM,thetasksandmethodsaredomain-dependent. Mostdomains
willhavethetaskprocess user request,whichisthetopleveltaskthattheagentwillstartwith. Figure1
shows some simplified methods and their associated sub/tasks; the actual methods and tasks in the
system’scodediffersslightlyfromthissimpleform. Forthemethodsinthissystem,nopreconditions
arespecified. Inadditiontothe(head,task,subtask),methodsinProcLLMalsoincludedetailsforthe
verifystep.
Asanexample,inFigure1,themostabstracttaskprocess user requestdecomposesintofoursubtasks
(Lines3-6)andtheverifycontextincludesadditionaldetails(Lines7-9). Thesecondsubtaskchoose
departing flightisfurtherdecomposedbym-choose-departing-flight(Lines10-17)whereoneofthe
subtasksistounderstandtheflighttool,asdescribedinm-understand-flight-tool(Lines18-22).
Workflow of ProcLLM. Figure 2 shows an overview of the system with the key components of the
system. Alongthetopofthediagram,movinglefttoright,aretheagenticcomponentsthatproducean
action. Thebottomofthediagramshowsthecomponentsthatmakeuptheenvironment.
Algorithm 1 provides pseudocode for ProcLLM. If methods M are provided, Line 2 calls UpdateTask
to decompose K. UpdateTask (Lines 23-27) decomposes head(K) if there are relevant methods. If
verifiedisTrue,UpdateTaskwillremovehead(K)andmayfurtherdecomposeK,wheretheleavesare
primitivetasksthatdescribewhat action-LLMshoulddo. K remainsunchangedifverifiedisFalse,M
isempty,ortherearenorelevantmethodsforhead(K).
AftercallingUpdateTask,ProcLLMthenprocessesasequenceoftasksK uptothehorizonH (Line3)
or until K is empty (Line 4). Line 6 assembles an action context C a from the current environment
state s, the execution trace of the last system execution, and the current task κ. C a is processed by
action-LLM(Line7)whichproducesaparameterizedactiona,whichiseitheraninternalverifyaction
oranexternalread/write/appendaction. Foraverifyaction(Lines9-15),Line10assemblesaverify
contextC v fromthesystemstateandcurrenttask,whichisprocessedbytheverify-LLM(Line11).
If there remain tasks to complete, Lines 16-22 execute external actions in the environment. These
externalactionsareJSONoutputthatisparsedintoanactiona. Forthispaper,asetofpythonscripts
implementsthetransitionT(s
,
a)),whichproducesanewsystemstateathatisfedintotheagentforthe
nextcycle.
5 Empirical Evaluation
We evaluate ProcLLM on two benchmarks with external APIs and two with a combinatorial solution
space often solved with search, summarized in the table below. Travel Planning (TP), based on
(33),requiresbookingasingle-cityitineraryusingseveraltools. Recipe Generator (RG),asynthetic
problem,requiresproposingarecipefromalistofingredientsusingatoolandsolver. Blocks World
(BW), a planning benchmark (28), requires rearranging stacks of blocks. Unit Movement (UM),
anothersyntheticbenchmark,requiresmovingunitsaroundagraph.
Solver? Tools? ProblemType Source
TP Y Y ToolUse (33)
RG Y Y AlgorithmicToolUse Thispaper
BW Planning (28)
UM Game Thispaper
The agent is given a horizon of H = 100. Solutions are automatically verified using human-written
simulators and test functions. We test three conditions: human-created M (Human-TN), LLM-created
M(LLM-TN),orM=∅(No-TN).ForNo-TN,K hasonetaskdescribingtheendconditionsforsolvingthe
9

## Page 10

Table1: Comparison: MeansuccessrateonsubtasksinreducedTravelPlannerbenchmark(Verification
setfrom(33))
Model Flight1 Flight2 Hotel
Nemotron70bNo-TN 0.023 0.0 0.0
Nemotron70bHuman-TN 0.535 0.419 0.116
GPT-oss120bNo-TN 0.0 0.0 0.0
GPT-oss120bHuman-TN 0.814 0.605 0.395
probleminstance;itfunctionssimilartoavanillareflexionagent(23). Experimentsareperformedonan
AMDEPYC7H1264coreCPUwiththeLLMsbeingservedthroughollamahostedonA100GPUs.
TravelPlanning. Thistool-useproblemisbasedontheTravelPlannerbenchmark(33),wheretheagent
canaccessdatabaseAPIs(FlightSearch, RestaurantSearch,etc.) tocreateanitinerarysatisfyinga
userrequest. Theoriginalbenchmarkcontainsverydifficultmulti-constrainttaskswhereGPT-4hada
low0.6%successrate(33). Althoughotherworkshaveclaimedhighersuccessratesonthisbenchmark,
theyrequireconsiderablehuman-writtencodescaffolding(10)ortheyuseasimplifiedversionofthis
benchmark(e.g.,eliminatingtooluseinthecaseof(9)).
We use several simplifications so task completion is within reach of current models while keeping
successnon-trivial. First,wefilterthevalidationsetof(33)toobtainsingledestinationtravelrequests.
Second, we used a subset of the original benchmark: book a flight from origin to destination, book
accommodation,andbookareturnflight. Thissubtaskbenchmarkremainssufficientlydifficult. Request
isfilledwithauserrequestfromthevalidationsetof(33). ProblemSpecspecifiesthattheagentshould
onlyfulfillpartsoftherequestinorder(incontrastto(33)).
We created 43 problems to solve for TP. Table 1 shows the success rate for completing the task up
toagivencolumn. Forexample,forFlight 2,NemotronwithHuman-TNchosecorrectdepartingand
returning flights in 41.9% of the requests. For both Nemotron and GPT-oss, Human-TN substantially
improvestasksuccessrateoverNo-TN.
Recipe Generator (RG). In this tool use task, an agent is given a list of cooking ingredients and
askedtoreturnadishthatcanbemadefromtheseingredients. Toprocessuserrequests, theagent
uses two python functions: get_ingredient_from_dish(dish) returns the ingredients for a dish, and
get_dish_from_ingredient(ingredient) returns a list of dishes for an ingredient. verify succeeds for
anydishthatcanbemadefromanysubsetofingredients,andtheagentcanwritearbitrarypythoncode
callingthesefunctions.
UsingGPT-4,wegeneratedadatabaseofingredientsanddishes. Aprobleminstanceisconstructedby
randomlyselectingadish,extractingitsingredients,andaugmentingthislistwithadditionalingredients.
Thisprocessensuressolvableproblemsthatarealsochallenging.
Over20probleminstances(notshownforspacereasons), atasknetworkimprovesresults. GPT-oss-
120b had a base success rate of 0% for No-TN and 25% for Human-TN. Because solutions to this task
mayrequirealgorithmicsolutions(e.g. filteringapicallresults),weappliedacodingfine-tunedLLM
Nemotron-70b,whichaveragedasuccessrateof50%forNo-TNand80%forHuman-TN.
Blocks World (BW). This problem adapts the BlocksWorld benchmark from PlanBench (28), where
GPT-4 succeeded on 34.3% problems. In PlanBench, problems have 3-5 blocks, and the LLM prompt
includestherulesofthetask,anexampleproblem,andasolutiontotheexampleproblem.
Wemadeseveralchanges. ProblemSpecdescribestheproblemandtheacceptablesolutionformatand
Requestcontainstheinitialstate. However,thesefilesprovidenoexplicitsolutionexample. Toassess
theimpactofproblemcomplexity,werandomlychoosebinitialblocksthatmustbeinafinalstackof
heighth;asolutioniscorrectforstackingh,regardlessofotherblocksb−h.
Fig 3 reveals a downward trend in task success as complexity increases (from b = 3 to b = 9). Either
tasknetwork(Human-TNorLLM-TN)greatlyincreasesthesuccessrate;thesuccessrateofGPT-oss-120b
Human-TN remains 70% in contrast to GPT-oss-120b No-TN of below 5%. Furthermore, the smaller
GPT-oss-20bHuman-TNsignificantlyoutperformsGPT-oss-120b.
10

## Page 11

Figure 3: Success rates for BlockWorld and Unit Movement domains, evaluated across increasing
problemcomplexity(bstartingblocksandhfinalstackheightforBW,numberofunitsnforUM).Bars
showmeansuccessrates,with95%Wilsonconfidenceintervals.
UnitMovement(UM).Inthistask,foreachprobleminstancewegenerateagraphGwiththefollowing
properties(FigureA.1showsanexampleproblem). Atargetnodev T ∈Gisadjacenttofourneighbors
vadj, each with an edge (vadj,v T ). Each neighbor has three outer neighbors; that is, for each node
vadj ,thereareatleast3outernodesvout withanedge(vadj,vout). Aftergeneratingtheabovenodesets,
i i
weadd12morerandomedgesbetweenneighboringnodes(excludingthetargetv T). Forthreeofthe
sectionsofthegraphweplacenunitstorandomnodesineachsection. Werandomlynameeachnode
(e.g. Seaside,Canyon,Gardens)andeachunitbasedontheirsection(e.g. Bravo_0,Alpha_1). Thegoal
ofthetaskistomoveunitssothatthetargetissurroundedfromthreeneighborswithatleastleastk
unitsateachnode.
Wevariedproblemcomplexitybythenumberofnunitspergroupandthenumberk unitsrequiredfor
surrounding. Figure3revealstwoinsights. First,Human-TNincreasesthetasksuccessrateregardless
of the base capability of the LLM used in the system; at (n = 10,k = 6), the 20b model Human-TN
outperforms 120b No-TN. Second, higher (n,k) values seem show a non-linear correlation with task
difficulty;futureworkshouldexplorewhethertheLLMisexploitingproblemstructuretosolvelarger
problems.
6 Discussion
TheevaluationofProcLLMshowsthatHuman-TNandLLM-TNimprovetasksuccessrate,oftensignificantly
andevenacrossNo-TNsuccesscapabilityanddifferentbenchmarks. Wealsovariedproblemcomplexity
andshowedthat,inBWandUM,theLLMsystemwithataskplannerseemstohaveaslowerdecrease
11

## Page 12

in task success rate than the LLM system without a task planner. This is true in both domains for
GPT-oss-120b, but the results for GPT-oss-20b show less improvement; we hypothesize that smaller
models such as GPT-oss-20b can run into context length issues that are not addressed by our task
networkapproach. Wefurtherexamineseveralmorequestionsabouttheseresults.
Why is No-TN doing so poorly? Althoughnotobviousfromtheresultspresentedsofar,therearesome
subtle differences in model behavior that we would like to discuss. To explain, consider the first few
steps that an LLM may need to take to solve one of the agentic problems seen so far. In each of the
problems,thereisarequest.txtandaproblem specification.txt. Thefirstfewstepsofsolvingan
agentictaskistoreadeachofthesefilesandthentakenotesonthefilesintotheshort-termmemoryfile
(Notes). Somemodels(e.g.,nemotron,codestral,llama)arenaturallyproficientinthisandwillgenerate
asequenceofactions:
1. Readrequest.txt
2. Append[requestdetails]
3. Readproblem specification.txt
4. Append[specdetails]
Thissequenceofactionscanbegeneratedevenifthetasknetworkdoesnothaveexplicittasknodes
abouttakingnotes(orevenwithoutatasknetworkatall). However,ourexperimentswithGPT-oss-120b
revealedthesystemwouldgetstuckinloopslike:
1. Readrequest.txt
2. Readproblem specification.txt
3. Readrequest.txt
4. Readproblem specification.txt
5. etc.
Thiscausesthesystemtotimeoutandfailasaresult. Wecanalleviatethisproblemfordomainssuch
asBWbyexplicitlyextendingthefinalgoalforthetask. Forexample,wecouldchangesolve the user
request into solve the user request and have notes on the request and problem specification. But
such
changesmaynotscaleifaproblemhasmanygoals.
Are LLM-constructed task networks better? (LLM-TN)TostudyLLM-TN,weconstructedaprompt
thatincludestheproblemspecification,theagentprompt,andtwovalidtasknetworknodeexamples
andaskedGemini2.5Protoproduceatasknetwork(LLM-TN).InFigure3,weseethattasksuccess
rateofLLM-TN(brownbars)doesbetterthanNo-TNwhilevaryingagainstHuman-TN.
Does Human-TN or LLM-TN save runtime? Figure 4 shows runtime statistics for GPT-oss-120b in
ProcLLMacrosstheevaluationbenchmarks(FigureA.2showsfulldetails). ForBlocksWorldandUnit
Movement,thestatisticsareaveragedoverallproblemsizes.
Inthreeofthefourbenchmarks,thetaskplannerdecreasesthenumberofsystemiterationsrequired
foragivenprobleminstance. TheexceptionisRecipeGenerator,wheretheLLMwithNo-TNproduces
quick but always incorrect outputs, unlike other benchmarks where No-TN typically fails via timeout.
OneexplanationisthattheLLMcantreattherequestinRecipeGeneratorasaquerytobeanswered
directly, bypassing the APIs altogether. This shortcutting behavior mirrors earlier findings ((3)) that
LLMscandefaulttosuperficialstrategiesunlessconstrainedexternally.
Using a task network typically increases the average time per iteration while decreasing the total
number of iterations. One important takeaway is that using the task network does not significantly
increasethetimeittakestocompleteatask. Insomecases,suchasonBlocksWorld,usingGPT-oss-20b
inProcLLMwilloutcompeteGPT-oss-120binbothtimeandperformancemetrics.
7 Conclusion
WehavearguedthatproceduralknowledgehelpsLLMworkflows. Weformalized,implemented,and
evaluatedProcLLMthatusesHTNstoimproveLLMperformanceoncomplexagentictasks. ProcLLM
leveragedanHTNtodecomposecomplextasksintosubtasksthatcompletedbyanagenticLLM.While
12

## Page 13

Figure 4: A comparison of average runtime statistics for GPT-oss across different benchmarks (BW -
BlocksWorld,TP-TravelPlanner,UM-UnitMovement). (SeeFig.A.2forfulldetails)
ProcLLMusesafilesystemastheenvironment,thisframeworkcouldbeappliedtoemployLLMagents
inmoregeneralMDPdomains(e.g.,games,controlproblems).
WedemonstratedonfourbenchmarksthattheHTNdecompositioninProcLLMsignificantlyincreased
task success in difficult multi-step agentic tasks. This is effective regardless of the base LLM. This
improvementusesnaturallanguagedescriptions;ProcLLMdoesnotrequiretranslationtoaplanning
formalism(e.g.,PDDL,HDDL).Usingnaturallanguageallowsaflexibleandnaturaltradeoffinthelevel
of abstraction for HTN planning. The high-level planning afforded by the task planner increases the
likelihoodofcompletinglong,complextasksandalsoreducestheprobabilityofmanycommonagentic
LLMissues,suchasactionlooping,thatareexacerbatedbyadeficiencyinimplicittaskplanning.
LLM generated task networks sometimes do well, but they seem to generally lack the specificity of
human generated networks. In future work, it would be interesting to see if LLMs can build task
networksfromthegroundupinacurriculumlearningfashion,startingwithsimpletasksthatgradually
becomemorecomplex. Also,itwouldbeinterestingtoexploreanequivalentapproachin(3)wherean
LLMtransformstheHTNrecipeintocodeforspeedandconsistentreplicability. Finally,proceduresare
frequentlycodifiedintodocumentsasrecipes,checklists,orstandardoperatingprocedures. Beyond
learningnetworksthroughcurriculumlearning,wecouldexploremethodsforusingRAG(e.g.,(22))or
fine-tuning(e.g.,(30))toimprovethedistillationoftasknetworksfromdomaindocuments
Acknowledgments
WethankNRLforfundingthisresearch.
13

## Page 14

References
[1] FahiemBacchusandFrodualdKabanza.2000. UsingTemporalLogicstoExpressSearchControl
KnowledgeforPlanning. ArtificialIntelligence 116,1(Jan.2000),123–191. https://doi.org/10.
1016/S0004-3702(99)00071-5
[2] Fahiem Bacchus and Qiang Yang. 1994. Downward refinement and the efficiency of hierarchi-
cal problem solving. Artificial Intelligence 71, 1 (1994), 43–100. https://doi.org/10.1016/
0004-3702(94)90062-0
[3] PeterBelcakandPavloMolchanov.2025. UniversalDeepResearch: BringYourOwnModeland
Strategy. arXivpreprintarXiv:2509.00244 (2025).
[4] Edward Y Chang and Longling Geng. 2025. SagaLLM: Context Management, Validation, and
TransactionGuaranteesforMulti-AgentLLMPlanning. arXivpreprintarXiv:2503.11951 (2025).
[5] Mark Chen, Jerry Tworek, Heewoo Jun, Qiming Yuan, Henrique Ponde De Oliveira Pinto, Jared
Kaplan,HarriEdwards,YuriBurda,NicholasJoseph,GregBrockman,etal.2021. Evaluatinglarge
languagemodelstrainedoncode. arXivpreprintarXiv:2107.03374 (2021).
[6] A.I.ColesandA.J.Smith.2007. Marvin: AHeuristicSearchPlannerwithOnlineMacro-Action
Learning. JournalofArtificialIntelligenceResearch 28(Feb.2007),119–156. https://doi.org/
10.1613/jair.2077
[7] Christopher W. Geib and Robert P. Goldman. 2009. A Probabilistic Plan Recognition Algorithm
Based on Plan Tree Grammars. Artificial Intelligence 173, 11 (July 2009), 1101–1132. https:
//doi.org/10.1016/j.artint.2009.01.003
[8] MalikGhallab,DanaNau,andPaoloTraverso.2025. Acting,PlanningandLearning. Cambridge
UniversityPress. authorpreprinthttps://projects.laas.fr/planning/.
[9] AtharvaGundawar,MuditVerma,LinGuan,KarthikValmeekam,SiddhantBhambri,andSubbarao
Kambhampati.2024. Robustplanningwithllm-moduloframework: Casestudyintravelplanning.
arXivpreprintarXiv:2405.20625 (2024).
[10] YilunHao,YongchaoChen,YangZhang,andChuchuFan.2024. Largelanguagemodelscanplan
yourtravelsrigorouslywithformalverificationtools. CoRR (2024).
[11] Chengkai Huang, Junda Wu, Yu Xia, Zixu Yu, Ruhan Wang, Tong Yu, Ruiyi Zhang, Ryan A Rossi,
BranislavKveton,DongruoZhou,etal.2025. Towardsagenticrecommendersystemsintheeraof
multimodallargelanguagemodels. arXivpreprintarXiv:2503.16734 (2025).
[12] Xu Huang, Weiwen Liu, Xiaolong Chen, Xingmei Wang, Hao Wang, Defu Lian, Yasheng Wang,
Ruiming Tang, and Enhong Chen. 2024. Understanding the planning of LLM agents: A survey.
arXivpreprintarXiv:2402.02716 (2024).
[13] SubbaraoKambhampati.2024. Canlargelanguagemodelsreasonandplan? AnnalsoftheNew
YorkAcademyofSciences 1534,1(2024),15–18.
[14] Subbarao Kambhampati, Karthik Valmeekam, Lin Guan, Mudit Verma, Kaya Stechly, Siddhant
Bhambri, Lucas Paul Saldyt, and Anil B Murthy. 2024. Position: LLMs can’t plan, but can help
planninginLLM-moduloframeworks.InForty-firstInternationalConferenceonMachineLearning.
[15] EhudKarpas,OmriAbend,YonatanBelinkov,BarakLenz,OpherLieber,NirRatner,YoavShoham,
Hofit Bata, Yoav Levine, Kevin Leyton-Brown, et al. 2022. MRKL Systems: A modular, neuro-
symbolic architecture that combines large language models, external knowledge sources and
discretereasoning. arXivpreprintarXiv:2205.00445 (2022).
[16] Harsha Kokel, Michael Katz, Kavitha Srinivas, and Shirin Sohrabi. 2025. Acpbench: Reasoning
aboutaction,change,andplanning.InProceedingsoftheAAAIConferenceonArtificialIntelligence,
Vol.39.26559–26568.
[17] JohnE.Laird,ChristianLebiere,andPaulS.Rosenbloom.2017. AStandardModeloftheMind:
Toward a Common Computational Framework across Artificial Intelligence, Cognitive Science,
Neuroscience,andRobotics. AIMagazine 38,4(Dec.2017),13–26. https://doi.org/10.1609/
aimag.v38i4.2744
[18] PatLangleyandHowardEShrobe.2021. HierarchicalProblemNetworksforKnowledge-Based
Planning. (Sept.2021),19.
14

## Page 15

[19] GuohaoLi,HasanHammoud,HaniItani,DmitriiKhizbullin,andBernardGhanem.2023. Camel:
Communicativeagentsfor"mind"explorationoflargelanguagemodelsociety. AdvancesinNeural
InformationProcessingSystems 36(2023),51991–52008.
[20] Xinyi Li, Sai Wang, Siqi Zeng, Yu Wu, and Yi Yang. 2024. A survey on LLM-based multi-agent
systems: workflow,infrastructure,andchallenges. Vicinagearth 1,1(2024),9.
[21] TimoSchick,JaneDwivedi-Yu,RobertoDessì,RobertaRaileanu,MariaLomeli,LukeZettlemoyer,
NicolaCancedda,andThomasScialom.2023. Toolformer: Languagemodelscanteachthemselves
tousetools,2023. arXivpreprintarXiv:2302.04761 (2023).
[22] KaizeShi,XueyaoSun,QingLi,andGuandongXu.2024. Compressinglongcontextforenhancing
ragwithamr-basedconceptdistillation. arXivpreprintarXiv:2405.03085 (2024).
[23] Noah Shinn, Federico Cassano, Ashwin Gopinath, Karthik Narasimhan, and Shunyu Yao. 2023.
Reflexion: Languageagentswithverbalreinforcementlearning. AdvancesinNeuralInformation
ProcessingSystems 36(2023),8634–8652.
[24] ParshinShojaee,ImanMirzadeh,KeivanAlizadeh,MaxwellHorton,SamyBengio,andMehrdad
Farajtabar.2025. Theillusionofthinking: Understandingthestrengthsandlimitationsofreasoning
modelsviathelensofproblemcomplexity. arXivpreprintarXiv:2506.06941 (2025).
[25] TomSilver,SohamDan,KavithaSrinivas,JoshuaBTenenbaum,LeslieKaelbling,andMichaelKatz.
2024. Generalizedplanninginpddldomainswithpretrainedlargelanguagemodels.InProceedings
oftheAAAIconferenceonartificialintelligence,Vol.38.20256–20264.
[26] ChanHeeSong,JiamanWu,ClaytonWashington,BrianMSadler,Wei-LunChao,andYuSu.2023.
Llm-planner: Few-shot grounded planning for embodied agents with large language models. In
ProceedingsoftheIEEE/CVFinternationalconferenceoncomputervision.2998–3009.
[27] AustinTate.1977. GeneratingProjectNetworks.InProc.ofIJCAI (IJCAI’77).MorganKaufmann
PublishersInc.,SanFrancisco,CA,USA,888–893.
[28] KarthikValmeekam,MatthewMarquez,AlbertoOlmo,SarathSreedharan,andSubbaraoKamb-
hampati. 2023. Planbench: An extensible benchmark for evaluating large language models on
planning and reasoning about change. Advances in Neural Information Processing Systems 36
(2023),38975–38987.
[29] KarthikValmeekam,KayaStechly,AtharvaGundawar,andSubbaraoKambhampati.2024. Planning
instrawberryfields: Evaluatingandimprovingtheplanningandschedulingcapabilitiesoflrmo1.
arXivpreprintarXiv:2410.02162 (2024).
[30] PulkitVerma,NgocLa,AnthonyFavier,SwaroopMishra,andJulieA.Shah.2025. TeachingLLMsto
Plan: LogicalChain-of-ThoughtInstructionTuningforSymbolicPlanning. arXiv:2509.13351[cs.AI]
https://arxiv.org/abs/2509.13351
[31] ZhiruoWang,ZhoujunCheng,HaoZhu,DanielFried,andGrahamNeubig.2024. Whataretools
anyway? asurveyfromthelanguagemodelperspective. arXivpreprintarXiv:2403.15452 (2024).
[32] Tongshuang Wu, Ellen Jiang, Aaron Donsbach, Jeff Gray, Alejandra Molina, Michael Terry, and
Carrie J Cai. 2022. Promptchainer: Chaining large language model prompts through visual
programming.InCHIConferenceonHumanFactorsinComputingSystemsExtendedAbstracts.
1–10.
[33] Jian Xie, Kai Zhang, Jiangjie Chen, Tinghui Zhu, Renze Lou, Yuandong Tian, Yanghua Xiao, and
Yu Su. 2024. Travelplanner: A benchmark for real-world planning with language agents. arXiv
preprintarXiv:2402.01622 (2024).
[34] HuiYang,SifuYue,andYunzhongHe.2023. Auto-gptforonlinedecisionmaking: Benchmarksand
additionalopinions. arXivpreprintarXiv:2306.02224 (2023).
[35] ShunyuYao,JeffreyZhao,DianYu,NanDu,IzhakShafran,KarthikNarasimhan,andYuanCao.2022.
React: Synergizing reasoning and acting in language models. arXiv preprint arXiv:2210.03629
(2022).
[36] YankaiZeng,AbhiramonRajasekharan,ParthPadalkar,KinjalBasu,JoaquínArias,andGopalGupta.
2024. Automatedinteractivedomain-specificconversationalagentsthatunderstandhumandialogs.
InInternationalSymposiumonPracticalAspectsofDeclarativeLanguages.Springer,204–222.
15

## Page 16

[37] Wentao Zhang, Ce Cui, Yilei Zhao, Rui Hu, Yang Liu, Yahui Zhou, and Bo An. 2025. Agen-
torchestra: Ahierarchicalmulti-agentframeworkforgeneral-purposetasksolving. arXivpreprint
arXiv:2506.12508 (2025).
[38] Andrew Zhao, Daniel Huang, Quentin Xu, Matthieu Lin, Yong-Jin Liu, and Gao Huang. 2024.
Expel: Llmagentsareexperientiallearners.InProceedingsoftheAAAIConferenceonArtificial
Intelligence,Vol.38.19632–19642.
[39] Zhehua Zhou, Jiayang Song, Kunpeng Yao, Zhan Shu, and Lei Ma. 2024. Isr-llm: Iterative self-
refinedlargelanguagemodelforlong-horizonsequentialtaskplanning.In2024IEEEInternational
ConferenceonRoboticsandAutomation(ICRA).IEEE,2081–2088.
16

## Page 17

Figure A.1: An example problem instance for the unit movement domain showing the initial starting
position(bluecircles)andavalidsolution(redcircles).
A Additional Figures
17

## Page 18

FigureA.2: AcomparisonofaverageruntimestatisticsforGPT-oss120bacrossdifferentbenchmarks
(BW-BlocksWorld,TP-TravelPlanner,UM-UnitMovement).
B Prompts
B.1 Standard Agent Prompt
This prompt is given to the agent at each iteration for all domains. Only the content of the read and
writeablefilesmaydifferacrossdomains.
18

## Page 19

Your goal is to interact with a system that processes commands in order to solve
(cid:44)→ a given task. The task is specified in the problem specification document
(cid:44)→ and the task instance in the request file. You MUST read and take notes on
(cid:44)→ these files to solve the problem. You will only be able to see the
(cid:44)→ information from the immediately preceding action, so make sure you take
(cid:44)→ notes such that this information is not lost.
You have the following actions and files available to you:
1. Read: reads [action_arg1]. Line numbers will be displayed.
Read [action_arg1]
2. Write: overwrites text file [action_arg1] with [action_arg2].
Write [action_arg1] [action_arg2]
3. Append: appends the text file [action_arg1] with [action_arg2].
Append [action_arg1] [action_arg2]
4. Verify: Send a request to check if current task has been achieved.
Verify
You are allowed to read and write the following file (r/w):
solver.py (r/w): this file is automatically executed after every revision. The
(cid:44)→ standard output of this file is written to output.txt
files/notes.txt (r/w): the contents of this file will always be displayed in the
(cid:44)→ notes section down below.
answer.txt (r/w): a file to hold the final answer to user request
You are allowed to access the following read-only files (r):
files/request.txt (r): the user request
files/problem_specification.txt (r): a problem specification document
files/tools_specification.txt (r): a document specifying tools
output.txt (r): the stdout of solver.py
The contents of files/notes.txt is:
***NOTES START***
{}
***NOTES END***
Your last response was:
***LAST RESPONSE START***
{}
***LAST RESPONSE END***
The last ten commands executed were:
***LAST COMMAND START***
{}
***LAST COMMAND END***
Here is the output of your last command:
***LAST COMMAND OUTPUT***
{}
***LAST COMMAND OUTPUT END***
Your Limitations:
19

## Page 20

1. Do not attempt to read or write to any files not listed. This will result in
(cid:44)→ a file access denied error.
2. You can only open one file at a time.
3. If you get a file access denied error, make sure you use the correct path and
(cid:44)→ extension.
General Instructions:
1. Your response should be in a json format (formatted with newlines) and
(cid:44)→ include the following components:
* observation: a detailed observation about the current state of the task and
(cid:44)→ what you have done so far
* thought: reasoning about what next steps are valid and how to proceed
* action {{name: , action_arg1: , action_arg2: }}: action [read, write, append,
(cid:44)→ or verify] and arguments for the action
2. There is no limit on how long your json can be, but do not include additional
(cid:44)→ nested components.
3. If you receive a JSONDecode error, this means your json response is
(cid:44)→ improperly formatted.
4. Think step by step. Justify each step with something from existing notes or
(cid:44)→ previous responses.
5. Respond only with your json action. Use an empty string if any arguments are
(cid:44)→ unneeded.
6. A task planner will give you a task to follow with an effect. Focus on
(cid:44)→ achieving this effect.
7. Call the verify action when the current effect is satisfied to move onto the
(cid:44)→ next task.
8. You MUST take notes to solve the problem. Make sure to take notes after a
(cid:44)→ read.
9. Do not include section headings (e.g. ***) in your response.
Your current task is:
Task: {}
The effect that you are trying to achieve is:
Effect: {}
B.2 Agent Action Examples
TheagentisexpectedtorespondwithaJSONthatwillbeparsedandprocessedasanaction. Hereare
someexamples:
{
"observation": "Currently, no notes have been taken and no files have been
(cid:44)→ read. The task is to take notes on the problem specification file.",
"thought": "To achieve the effect of having notes contain the information from
(cid:44)→ the problem specification file, I first need to read the problem
(cid:44)→ specification file. Then, I will append the contents of this file to the
(cid:44)→ notes.txt file to ensure persistence of the information.",
"action": {
"name": "Read",
"action_arg1": "files/problem_specification.txt",
"action_arg2": ""
}
}
20

## Page 21

{
"observation": "Having read the request file (files/request.txt), I've
(cid:44)→ obtained additional context: a 3-day trip from Missoula to Dallas (March
(cid:44)→ 23rd-25th, 2022) with a budget of $1,900. This aligns with my initial
(cid:44)→ notes but adds a budget constraint. My current understanding is that I
(cid:44)→ need to use Flights.py for flights and Accommodations.py for lodging
(cid:44)→ within this budget. However, I still lack detailed insights from the
(cid:44)→ problem specification file beyond the initial notes. To ensure
(cid:44)→ completeness, I'll append these new details to notes.txt.",
"thought": "With the request's context in mind, particularly the budget, my
(cid:44)→ next steps should involve utilizing the specified tools (Flights.py and
(cid:44)→ Accommodations.py) while considering the $1,900 budget. Before executing
(cid:44)→ code, it's prudent to update my notes with the latest understanding,
(cid:44)→ including the budget constraint, to maintain a comprehensive record of my
(cid:44)→ approach.",
"action": {
"name": "Append",
"action_arg1": "files/notes.txt",
"action_arg2": "Additional context from request file: Budget for Missoula to
(cid:44)→ Dallas trip (March 23rd-25th, 2022) is $1,900. Next steps involve using
(cid:44)→ Flights.py and Accommodations.py with budget consideration."
}
}
{
"observation": "Read the problem specification which defines the allowed
(cid:44)→ actions and required output format. Notes provide the initial state, goal
(cid:44)→ state, and a sequence to unstack all blocks to the table. To achieve the
(cid:44)→ goal, we will first execute the unstack/put sequence to clear the table,
(cid:44)→ then pick and stack blocks in the order required by the goal: cyan at
(cid:44)→ bottom, then blue, orange, green, yellow, purple. This yields a complete
(cid:44)→ plan using only pick, put, unstack, and stack actions.",
"thought": "Construct a plan consisting of the 8 unstack/put steps from the
(cid:44)→ notes, followed by pick/stack steps to build the goal tower. Write this
(cid:44)→ plan to answer.txt in the exact line-by-line format required.",
"action": {
"name": "Write",
"action_arg1": "answer.txt",
"action_arg2": "unstack black green\nput black\nunstack green cyan\nput
(cid:44)→ green\nunstack cyan blue\nput cyan\nunstack blue purple\nput blue\npick
(cid:44)→ blue\nstack blue cyan\npick orange\nstack orange blue\npick green\nstack
(cid:44)→ green orange\npick yellow\nstack yellow green\npick purple\nstack purple
(cid:44)→ yellow"
}
}
21

## Page 22

B.3 Example mid-iteration prompt
Your goal is to interact with a system that processes commands in order to solve
(cid:44)→ a given task. The task is specified in the problem specification document
(cid:44)→ and the task instance in the request file. You MUST read and take notes on
(cid:44)→ these files to solve the problem. You will only be able to see the
(cid:44)→ information from the immediately preceding action, so make sure you take
(cid:44)→ notes such that this information is not lost. You have the following actions
(cid:44)→ and files available to you:
1. Read: reads [action_arg1]. Line numbers will be displayed.
Read [action_arg1]
2. Write: overwrites text file [action_arg1] with [action_arg2].
Write [action_arg1] [action_arg2]
3. Append: appends the text file [action_arg1] with [action_arg2].
Append [action_arg1] [action_arg2]
4. Verify: Send a request to check if current task has been achieved.
Verify
You are allowed to read and write the following file (r/w):
solver.py (r/w): this file is automatically executed after every revision. The
(cid:44)→ standard output of this file is written to output.txt
files/notes.txt (r/w): the contents of this file will always be displayed in the
(cid:44)→ notes section down below.
answer.txt (r/w): a file to hold the final answer to user request
You are allowed to access the following read-only files (r):
files/request.txt (r): the user request
files/problem_specification.txt (r): a problem specification document
files/tools_specification.txt (r): a document specifying tools
output.txt (r): the stdout of solver.py
The contents of files/notes.txt is:
***NOTES START***
The user will provide a request to make a travel plan. You do not need to
(cid:44)→ complete the entire travel plan, but only the flight and accommodations for
(cid:44)→ the user's trip. You will need to use code files Flights.py and
(cid:44)→ Accommodations.py to access the database for required to solve the user
(cid:44)→ request
Your solution should be returned in a json format in answer.txt with two flights
(cid:44)→ (departing and returning) as well as the accommodation used for the duration
(cid:44)→ of the traveler's stay:
departing_flight: flight number
returning_flight: flight number
accommodation: name
Be aware that the accommodations returned by the Accommodations tool may have
(cid:44)→ names that do not seem to correspond with the city that you used for the
(cid:44)→ search; this is expected behavior and you should proceed with the results
(cid:44)→ you obtained using the tools.
22

## Page 23

Origin: Detroit
Destination: San Diego
Departure Date: 2022-03-05
Returning Date: 2022-03-07
Duration: 3 days
Budget: $3000
Traveler: solo
FlightSearch.run method:
- Inputs:
* Departure City (string)
* Destination City (string)
* Date (string in YYYY-MM-DD format)
- Expected Output:
* List of flight options (each containing flight number, departure/arrival
(cid:44)→ times, price, etc.)
***NOTES END***
Your last response was:
***LAST RESPONSE START***
{
"observation": "We have read the tools specification which shows how to import
(cid:44)→ and use the Flights tool. To obtain flight options we need to write code
(cid:44)→ in solver.py that imports the Flights class, creates an instance, runs the
(cid:44)→ search for Detroit to San Diego on 2022-03-05, and prints the results. The
(cid:44)→ solver will then be executed and its stdout captured in output.txt for
(cid:44)→ later analysis.",
"thought": "Next step is to write the described code into solver.py so that
(cid:44)→ the flight search is performed and results are printed. This will allow us
(cid:44)→ to later read output.txt and extract a departing flight number and cost.",
"action": {
"name": "Write",
"action_arg1": "solver.py",
"action_arg2": "from tools.Flights import Flights\n\ndef main():\n
(cid:44)→ FlightSearch = Flights()\n results = FlightSearch.run(\"Detroit\",
(cid:44)→ \"San Diego\", \"2022-03-05\")\n print(results)\n\nif __name__ ==
(cid:44)→ \"__main__\":\n main()\n"
}
}
***LAST RESPONSE END***
The last ten commands executed were:
***LAST COMMAND START***
Verify
Read files/request.txt
Append files/notes.txt
Verify
Read files/tools_specification.txt
Append files/notes.txt
Verify
Read solver.py
Read files/tools_specification.txt
23

## Page 24

Write solver.py
***LAST COMMAND END***
Here is the output of your last command:
***LAST COMMAND OUTPUT***
Updated solver.py:
from tools.Flights import Flights
def main():
FlightSearch = Flights()
results = FlightSearch.run("Detroit", "San Diego", "2022-03-05")
print(results)
if __name__ == "__main__":
main()
Code executed with stdout:
Flight Number Price DepTime ... OriginCityName DestCityName Distance
3306155 F3528556 720 08:33 ... Detroit San Diego 1956.0
[1 rows x 9 columns]
***LAST COMMAND OUTPUT END***
Your Limitations:
1. Do not attempt to read or write to any files not listed. This will result in
(cid:44)→ a file access denied error.
2. You can only open one file at a time.
3. If you get a file access denied error, make sure you use the correct path and
(cid:44)→ extension.
General Instructions:
1. Your response should be in a json format (formatted with newlines) and
(cid:44)→ include the following components:
* observation: a detailed observation about the current state of the task and
(cid:44)→ what you have done so far
* thought: reasoning about what next steps are valid and how to proceed
* action {name: , action_arg1: , action_arg2: }: action [read, write, append,
(cid:44)→ or verify] and arguments for the action
2. There is no limit on how long your json can be, but do not include additional
(cid:44)→ nested components.
3. If you receive a JSONDecode error, this means your json response is
(cid:44)→ improperly formatted.
4. Think step by step. Justify each step with something from existing notes or
(cid:44)→ previous responses.
5. Respond only with your json action. Use an empty string if any arguments are
(cid:44)→ unneeded.
6. A task planner will give you a task to follow with an effect. Focus on
(cid:44)→ achieving this effect.
7. Call the verify action when the current effect is satisfied to move onto the
(cid:44)→ next task.
8. You MUST take notes to solve the problem. Make sure to take notes after a
(cid:44)→ read.
9. Do not include section headings (e.g. ***) in your response.
24

## Page 25

Your current task is:
Task: choose a departing flight
The effect that you are trying to achieve is:
Effect: notes contains details about a flight number and cost for a flight from
(cid:44)→ origin to destination on departure date consistent with request preferences
B.3.1 Example response to the previous prompt
{
"observation": "The solver.py execution printed flight search results to
(cid:44)→ output.txt, showing a flight with number F3528556, price 720, departure
(cid:44)→ time 08:33, etc. We need to capture these details in notes.txt.",
"thought": "To satisfy the effect, I will read output.txt to obtain the flight
(cid:44)→ information, then append a concise note with the departing flight number
(cid:44)→ and its cost to notes.txt.",
"action": {
"name": "Read",
"action_arg1": "output.txt",
"action_arg2": ""
}
}
C Domain Specification
For each domain, we write problem specification documents that the agent needs to read in order
to complete a task (e.g. what they need to actually do to complete the agentic task). Each problem
instance also has an automatically generated request.txt that describes the problem details for a
specificprobleminstance.
C.1 Domain: Travel Planner
C.1.1 Problem Specification
The user will provide a request to make a travel plan. You do not need to
(cid:44)→ complete the entire travel plan, but only the flight and accommodations for
(cid:44)→ the user's trip. You will need to use code files Flights.py and
(cid:44)→ Accommodations.py to access the database for required to solve the user
(cid:44)→ request
Your solution should be returned in a json format in answer.txt with two flights
(cid:44)→ (departing and returning) as well as the accommodation used for the duration
(cid:44)→ of the traveler's stay:
departing_flight: flight number
returning_flight: flight number
accommodation: name
25

## Page 26

Be aware that the accommodations returned by the Accommodations tool may have
(cid:44)→ names that do not seem to correspond with the city that you used for the
(cid:44)→ search; this is expected behavior and you should proceed with the results
(cid:44)→ you obtained using the tools.
C.1.2 Example User Request
Please create a travel plan for a 3-day trip from Missoula to Dallas scheduled
(cid:44)→ from March 23rd to March 25th, 2022. The budget for this trip is set at
(cid:44)→ $1,900.
C.2 Domain: Recipe Generator
C.2.1 Problem Specification
The user will provide a request containing a list of ingredients, your job is to
(cid:44)→ select a valid recipe using those ingredients.
You do not need to use all ingredients provided by the user. Any recipe that can
(cid:44)→ be made from the ingredients provided by the user is a valid recipe. For
(cid:44)→ example, if the user provides the ingredient list:
Chicken Breast
Tomatoes
Soy Sauce
Sesame Oil
Brown Sugar
Garlic
The following recipe:
Dish: Chicken and Tomato Stir Fry
Ingredients:
Chicken Breast
Tomatoes
Soy Sauce
Sesame Oil
is valid solution to the user request, and a valid final output is:
Chicken and Tomato Stir Fry
C.2.2 Example User Request
Hello, I'd like to request a recipe for the following ingredients:
Chicken Breast
Tomatoes
Soy Sauce
26

## Page 27

Sesame Oil
Garlic
Ginger
C.3 Domain: Blocks World
C.3.1 Problem Specification
I am playing with a set of blocks where I need to arrange the blocks into stacks.
(cid:44)→ Here are the actions I can do:
Pick up a block
Unstack a block from on top of another block
Put down a block
Stack a block on top of another block
I have the following restrictions on my actions:
I can only pick up or unstack one block at a time.
I can only pick up or unstack a block if my hand is empty.
I can only pick up a block if the block is on the table and the block is clear.
(cid:44)→ A block is clear if the block has no other blocks on top of it and if the
(cid:44)→ block is not picked up.
I can only unstack a block from on top of another block if the block I am
(cid:44)→ unstacking was really on top of the other block.
I can only unstack a block from on top of another block if the block I am
(cid:44)→ unstacking is clear.
Once I pick up or unstack a block, I am holding the block.
I can only put down a block that I am holding.
I can only stack a block on top of another block if I am holding the block being
(cid:44)→ stacked.
I can only stack a block on top of another block if the block onto which I am
(cid:44)→ stacking the block is clear.
Once I put down or stack a block, my hand becomes empty.
Once you stack a block on top of a second block, the second block is no longer
(cid:44)→ clear.
Please provide a plan as a list of actions with space deliminated arguments line
(cid:44)→ by line in the following format in answer.txt:
pick [block]: pick a block up
put [block]: put a block down
stack [block1] [block2]: stack block1 on block2
unstack [block1] [block2]: unstack block1 from on top of block2
An example plan:
unstack blue red
put blue
pick red
stack red green
Write an answer to answer.txt. The plan will be checked automatically so please
(cid:44)→ follow the above format. The only actions allowed are [pick, put, stack,
(cid:44)→ unstack].
27

## Page 28

C.3.2 Example User Request (n=9,k =6)
As initial conditions I have that:
the blue block is on the table
the gray block is on top of the blue block
the red block is on top of the gray block
the orange block is on top of the red block
the yellow block is on top of the orange block
the black block is on top of the yellow block
the cyan block is clear
the cyan block is on top of the black block
the purple block is clear
the purple block is on the table
the green block is clear
the green block is on the table
My goal is to have that:
the orange block is on top of the gray block
the blue block is on top of the orange block
the black block is on top of the blue block
the yellow block is on top of the black block
the red block is on top of the yellow block
C.4 Domain: Unit Movement
C.4.1 Problem Specification
You are an AI strategist tasked with controlling a team of infantry units in a
(cid:44)→ wargame. You are given the current game state and must output a list of
(cid:44)→ actions for your units to execute in a single turn.
Game State:
The game is played on a network. Units have location, and a unit ID.
Example unit:
{"unit_id": "Eagle_0", "location": "Westwood"},
Available Actions:
* Move:
{"unit_id": "unit_id", "action_type": "move", "location": target_location}
The unit will move to target_location.
Output Format:
Each action must be a valid JSON object as described above in a list. Do not
(cid:44)→ include any other text besides the JSON list.
Example Output for two units:
[
{"unit_id": "Blue_0", "action_type": "move", "location": "Village"},
{"unit_id": "Blue_1", "action_type": "move", "location": "Southshore"}
]
28

## Page 29

To make the task easier for more complex problem instances, it can be beneficial
(cid:44)→ to group units together, decide on a general top level movement strategy,
(cid:44)→ and then decide on unit movement within each group to follow the top level
(cid:44)→ strategy.
C.4.2 Example User Request (n=15,k =9)
Goal:
Surround the target location {Eastfield} from at least three neighboring
(cid:44)→ locations with your units. A neighboring location is considered covered
(cid:44)→ if there are at least 9 units at that location.
Units:
Infantry (Hotel_0) at (Crestview)
Infantry (Hotel_1) at (Meadow)
Infantry (Hotel_2) at (Hillcrest)
Infantry (Hotel_3) at (Hillcrest)
Infantry (Hotel_4) at (Hillcrest)
Infantry (Hotel_5) at (Crestview)
Infantry (Hotel_6) at (Hillcrest)
Infantry (Hotel_7) at (Hillcrest)
Infantry (Hotel_8) at (Hillcrest)
Infantry (Hotel_9) at (Hillcrest)
Infantry (Hotel_10) at (Meadow)
Infantry (Hotel_11) at (Crestview)
Infantry (Hotel_12) at (Hillcrest)
Infantry (Hotel_13) at (Hillcrest)
Infantry (Hotel_14) at (Hillcrest)
Infantry (Lima_0) at (Bayview)
Infantry (Lima_1) at (Creekbend)
Infantry (Lima_2) at (Bayview)
Infantry (Lima_3) at (Townsend)
Infantry (Lima_4) at (Bayview)
Infantry (Lima_5) at (Creekbend)
Infantry (Lima_6) at (Bayview)
Infantry (Lima_7) at (Creekbend)
Infantry (Lima_8) at (Creekbend)
Infantry (Lima_9) at (Creekbend)
Infantry (Lima_10) at (Bayview)
Infantry (Lima_11) at (Creekbend)
Infantry (Lima_12) at (Creekbend)
Infantry (Lima_13) at (Townsend)
Infantry (Lima_14) at (Creekbend)
Infantry (Mike_0) at (Prairie)
Infantry (Mike_1) at (Prairie)
Infantry (Mike_2) at (Prairie)
Infantry (Mike_3) at (Summit)
Infantry (Mike_4) at (Prairie)
Infantry (Mike_5) at (Pineside)
Infantry (Mike_6) at (Summit)
Infantry (Mike_7) at (Prairie)
Infantry (Mike_8) at (Prairie)
Infantry (Mike_9) at (Prairie)
Infantry (Mike_10) at (Prairie)
29

## Page 30

Infantry (Mike_11) at (Prairie)
Infantry (Mike_12) at (Pineside)
Infantry (Mike_13) at (Summit)
Infantry (Mike_14) at (Summit)
Location Network (location - neighbors):
Eastfield - ['Seabreeze', 'Skyline', 'Moonlight', 'Centerville']
Seabreeze - ['Eastfield', 'Meadow', 'Hillcrest', 'Crestview']
Skyline - ['Eastfield', 'Townsend', 'Bayview', 'Creekbend']
Moonlight - ['Eastfield', 'Summit', 'Pineside', 'Prairie']
Centerville - ['Eastfield', 'Riverbend', 'Lakeside', 'Sunnyside']
Meadow - ['Seabreeze', 'Lakeside', 'Prairie']
Hillcrest - ['Seabreeze', 'Sunnyside', 'Creekbend']
Crestview - ['Seabreeze']
Townsend - ['Skyline', 'Bayview']
Bayview - ['Skyline', 'Pineside', 'Lakeside', 'Riverbend', 'Townsend']
Creekbend - ['Skyline', 'Hillcrest']
Summit - ['Moonlight', 'Pineside']
Pineside - ['Moonlight', 'Summit', 'Bayview']
Prairie - ['Moonlight', 'Meadow']
Riverbend - ['Centerville', 'Bayview']
Lakeside - ['Centerville', 'Bayview', 'Meadow']
Sunnyside - ['Centerville', 'Hillcrest']
D Methods
D.1 Travel Planner
{
"method1": {
"task": "process user request",
"subtasks": {
"subtask1": "take notes on origin, destination, departure date,
(cid:44)→ returning date and other preferences",
"subtask2": "choose a departing flight",
"subtask3": "choose a returning flight",
"subtask4": "choose an accommodation"
},
"effect": "answer.txt contains a solution in the correct format that
(cid:44)→ follows the problem specification",
"effect_files": {
"file1": "answer.txt",
"file2": "files/problem_specification.txt"
}
},
"method2": {
"task": "take notes on origin, destination, departure date, returning
(cid:44)→ date and other preferences",
"subtasks": {
"subtask1": "take notes on the problem specification file"
},
30

## Page 31

"effect": "notes contains same details as request and contains origin,
(cid:44)→ destination, departure date and returning date for the trip",
"effect_files": {
"file1": "files/notes.txt",
"file2": "files/request.txt"
}
},
"method3": {
"task": "choose a departing flight",
"effect": "notes contains details about a flight number and cost for a
(cid:44)→ flight from origin to destination on departure date consistent with
(cid:44)→ request preferences",
"subtasks": {
"subtask1": "understand flights tool"
},
"effect_files": {
"file1": "files/notes.txt",
"file2": "files/problem_specification.txt",
"file3": "files/request.txt"
}
},
"method4": {
"task": "choose a returning flight",
"effect": "notes contains details about a flight number and cost for a
(cid:44)→ returning flight consistent with request preferences",
"effect_files": {
"file1": "files/notes.txt",
"file2": "files/problem_specification.txt",
"file3": "files/request.txt"
}
},
"method5": {
"task": "choose an accommodation",
"effect": "notes contains details about an accomodation consistent with
(cid:44)→ request preferences",
"subtasks": {
"subtask1": "understand accommodation tool"
},
"effect_files": {
"file1": "files/notes.txt",
"file2": "files/problem_specification.txt",
"file3": "files/request.txt"
}
},
"method6": {
"task": "understand flights tool",
"effect": "notes contains details about flights tool methods inputs and
(cid:44)→ outputs",
"effect_files": {
"file1": "files/notes.txt",
"file2": "files/tools_specification.txt"
}
},
"method7": {
"task": "understand accommodation tool",
31

## Page 32

"effect": "notes contains details about accommodation tool methods
(cid:44)→ inputs and outputs",
"effect_files": {
"file1": "files/notes.txt",
"file2": "files/tools_specification.txt"
}
},
"method8": {
"task": "take notes on the problem specification file",
"effect": "notes contain the information from the problem specification
(cid:44)→ file",
"effect_files": {
"file1": "files/problem_specification.txt",
"file2": "files/notes.txt"
}
}
}
D.2 Recipe Generator
{
"method1": {
"task": "process user request",
"subtasks": {
"subtask1": "take notes on user request and problem specification",
"subtask2": "understand the tools specification"
},
"effect": "the answer to the user request can be found in answer.txt",
"effect_files": {
"file1": "answer.txt",
"file2": "files/request.txt",
"file3": "files/problem_specification.txt"
}
},
"method2": {
"task": "solve user request",
"effect": "a valid recipe is chosen",
"effect_files": {
"file1": "files/request.txt",
"file2": "files/problem_specification.txt",
"file3": "files/notes.txt"
}
},
"method3": {
"task": "understand the tools specification",
"effect": "details of provided tools and correct module import path are
(cid:44)→ recorded in notes",
"effect_files": {
"file1": "files/tools_specification.txt",
"file2": "files/notes.txt"
}
},
"method4": {
32

## Page 33

"task": "take notes on the problem specification file",
"effect": "notes contain the information from the problem specification
(cid:44)→ file",
"effect_files": {
"file1": "files/problem_specification.txt",
"file2": "files/notes.txt"
}
},
"method5": {
"task": "take notes on user request",
"effect": "notes contain the information from the user request",
"effect_files": {
"file1": "files/request.txt",
"file2": "files/notes.txt"
}
},
"method6": {
"task": "take notes on user request and problem specification",
"effect": "notes contain information from the user request and problem
(cid:44)→ specification files",
"effect_files": {
"file1": "files/request.txt",
"file2": "files/problem_specification.txt",
"file3": "files/notes.txt"
}
}
}
D.3 Blocks World
{
"method1": {
"task": "process user request",
"subtasks": {
"subtask1": "take notes on problem specification",
"subtask2": "take notes on user request",
"subtask3": "unstack all blocks"
},
"effect": "answer.txt contains a solution to the user request in the
(cid:44)→ correct format",
"effect_files": {
"file1": "files/problem_specification.txt",
"file2": "files/request.txt",
"file3": "answer.txt"
}
},
"method2": {
"task": "take notes on problem specification",
"effect": "notes contain the information from the problem specification
(cid:44)→ file",
"effect_files": {
"file1": "files/problem_specification.txt",
33

## Page 34

"file2": "files/notes.txt"
}
},
"method3": {
"task": "solve the user request",
"effect": "notes contain steps to solve the user request",
"effect_files": {
"file1": "files/request.txt",
"file2": "files/problem_specification.txt",
"file3": "files/notes.txt"
}
},
"method4": {
"task": "unstack all blocks",
"effect": "notes contain the intermediate steps to unstack all blocks
(cid:44)→ such that they are all clear and no blocks are being held",
"effect_files": {
"file1": "files/request.txt",
"file2": "files/problem_specification.txt",
"file3": "files/notes.txt"
}
},
"method5": {
"task": "take notes on user request",
"effect": "notes contain a copy of the user request about the initial
(cid:44)→ condition and goal",
"effect_files": {
"file1": "files/request.txt",
"file2": "files/notes.txt"
}
}
}
D.4 Unit Movement
{
"method1": {
"task": "process user request",
"subtasks": {
"subtask1": "take notes on problem specification",
"subtask2": "take notes on user request",
"subtask3": "group units",
"subtask4": "move units"
},
"effect": "the answer to the user request can be found in answer.txt in
(cid:44)→ the correct format",
"effect_files": {
"file1": "answer.txt",
"file2": "files/request.txt",
"file3": "files/problem_specification.txt"
}
},
"method2": {
34

## Page 35

"task": "move units",
"subtasks": {
"subtask1": "move group 1",
"subtask2": "move group 2",
"subtask3": "move group 3"
},
"effect": "notes contain movement actions to achieve the user request",
"effect_files": {
"file1": "files/request.txt",
"file2": "files/problem_specification.txt",
"file3": "files/notes.txt"
}
},
"method3": {
"task": "move group 1",
"effect": "notes contain moves for units in group 1",
"effect_files": {
"file1": "files/notes.txt"
}
},
"method4": {
"task": "move group 2",
"effect": "notes contain moves for units in group 2",
"effect_files": {
"file1": "files/notes.txt"
}
},
"method5": {
"task": "move group 3",
"effect": "notes contain moves for units in group 3",
"effect_files": {
"file1": "files/notes.txt"
}
},
"method6": {
"task": "group units",
"effect": "notes contain a grouping of units into three distinct groups
(cid:44)→ and a group level strategy for moving each group to achieve the
(cid:44)→ request goal",
"effect_files": {
"file1": "files/request.txt",
"file2": "files/notes.txt"
}
},
"method7": {
"task": "take notes on user request and problem specification",
"effect": "notes contain information from the user request and problem
(cid:44)→ specification files",
"effect_files": {
"file1": "files/request.txt",
"file2": "files/problem_specification.txt",
"file3": "files/notes.txt"
}
},
"method8": {
35

## Page 36

"task": "take notes on user request",
"effect": "notes contain information from the user request file",
"effect_files": {
"file1": "files/request.txt",
"file2": "files/notes.txt"
}
},
"method9": {
"task": "take notes on problem specification",
"effect": "notes contain information from the problem specification
(cid:44)→ file",
"effect_files": {
"file1": "files/problem_specification.txt",
"file2": "files/notes.txt"
}
}
}
E LLM-generated Task Networks
E.1 Blocks World
{
"method1": {
"task": "process user request",
"subtasks": {
"subtask1": "formulate plan",
"subtask2": "write final plan to answer.txt"
},
"effect": "the answer to the user request can be found in answer.txt in the
(cid:44)→ correct format",
"effect_files": {
"file1": "answer.txt",
"file2": "files/request.txt",
"file3": "files/problem_specification.txt"
}
},
"method2": {
"task": "formulate plan",
"subtasks": {
"subtask1": "take notes on problem and request",
"subtask2": "generate plan to clear misplaced blocks",
"subtask3": "generate plan to build goal stacks"
},
"effect": "the full plan to solve the blocksworld problem is stored in
(cid:44)→ notes.txt",
"effect_files": {
"file1": "files/notes.txt",
"file2": "files/request.txt"
}
},
"method3": {
"task": "take notes on problem and request",
36

## Page 37

"subtasks": {
"subtask1": "take notes on problem specification",
"subtask2": "take notes on user request"
},
"effect": "notes contain the initial state, goal state, and rules of the
(cid:44)→ problem",
"effect_files": {
"file1": "files/notes.txt",
"file2": "files/request.txt",
"file3": "files/problem_specification.txt"
}
},
"method4": {
"task": "take notes on problem specification",
"effect": "notes contain the rules of the blocksworld problem",
"effect_files": {
"file1": "files/notes.txt",
"file2": "files/problem_specification.txt"
}
},
"method5": {
"task": "take notes on user request",
"effect": "notes contain the initial and goal block configurations",
"effect_files": {
"file1": "files/notes.txt",
"file2": "files/request.txt"
}
},
"method6": {
"task": "generate plan to clear misplaced blocks",
"effect": "notes contains the sequence of unstack and put actions to move
(cid:44)→ all misplaced blocks to the table",
"effect_files": {
"file1": "files/notes.txt",
"file2": "files/request.txt"
}
},
"method7": {
"task": "generate plan to build goal stacks",
"effect": "notes contains the sequence of pick and stack actions to build
(cid:44)→ the goal configuration from the blocks on the table",
"effect_files": {
"file1": "files/notes.txt",
"file2": "files/request.txt"
}
},
"method8": {
"task": "write final plan to answer.txt",
"effect": "the final, combined plan from notes.txt is written to answer.txt
(cid:44)→ in the correct format",
"effect_files": {
"file1": "answer.txt",
"file2": "files/notes.txt"
}
}
37

## Page 38

}
E.2 Unit Movement
{
"method1": {
"task": "process user request",
"effect": "the answer to the user request can be found in answer.txt in the
(cid:44)→ correct format",
"effect_files": {
"file1": "answer.txt",
"file2": "files/request.txt",
"file3": "files/problem_specification.txt"
},
"subtasks": {
"subtask1": "compose actions",
"subtask2": "write answer file"
}
},
"method2": {
"task": "compose actions",
"effect": "notes.txt contains the JSON list of unit actions for the turn",
"effect_files": {
"file1": "files/notes.txt",
"file2": "files/request.txt",
"file3": "files/problem_specification.txt"
},
"subtasks": {
"subtask1": "take notes on request and spec",
"subtask2": "plan strategy",
"subtask3": "write actions to notes"
}
},
"method3": {
"task": "take notes on request and spec",
"effect": "notes.txt contains relevant information extracted from the
(cid:44)→ request and problem specification",
"effect_files": {
"file1": "files/notes.txt",
"file2": "files/request.txt",
"file3": "files/problem_specification.txt"
},
"subtasks": {
"subtask1": "read request",
"subtask2": "read problem specification",
"subtask3": "write notes"
}
},
"method4": {
"task": "read request",
"effect": "the contents of files/request.txt have been read and can be used
(cid:44)→ for note taking",
"effect_files": {
38

## Page 39

"file1": "files/request.txt"
}
},
"method5": {
"task": "read problem specification",
"effect": "the contents of files/problem_specification.txt have been read
(cid:44)→ and can be used for note taking",
"effect_files": {
"file1": "files/problem_specification.txt"
}
},
"method6": {
"task": "write notes",
"effect": "files/notes.txt now contains extracted information from the
(cid:44)→ request and specification",
"effect_files": {
"file1": "files/notes.txt",
"file2": "files/request.txt",
"file3": "files/problem_specification.txt"
}
},
"method7": {
"task": "plan strategy",
"effect": "files/notes.txt is updated with a high-level movement strategy
(cid:44)→ for the infantry units",
"effect_files": {
"file1": "files/notes.txt",
"file2": "files/request.txt",
"file3": "files/problem_specification.txt"
}
},
"method8": {
"task": "write actions to notes",
"effect": "files/notes.txt now contains the final JSON list of unit
(cid:44)→ actions",
"effect_files": {
"file1": "files/notes.txt",
"file2": "files/request.txt",
"file3": "files/problem_specification.txt"
}
},
"method9": {
"task": "write answer file",
"effect": "answer.txt contains the JSON list of unit actions in the required
(cid:44)→ format",
"effect_files": {
"file1": "answer.txt",
"file2": "files/notes.txt",
"file3": "files/request.txt",
"file4": "files/problem_specification.txt"
}
}
}
39

## Page 40

E.3 Prompt for generating task networks
The following prompt was used as input to Gemini 2.5 Pro to generate the two LLM-generated task
networksabove. TheemptysectionlabeledtaskspecificationisfilledwiththeProblemSpecfileforthe
domainbeingtested.
There is a system that processes commands in order to solve a given task. The
(cid:44)→ task is specified in the problem specification document and the task
(cid:44)→ instance in the request file. An agent is given the following actions to
(cid:44)→ perform:
1. Read: reads [action_arg1]. Line numbers will be displayed.
Read [action_arg1]
2. Write: overwrites text file [action_arg1] with [action_arg2].
Write [action_arg1] [action_arg2]
3. Append: appends the text file [action_arg1] with [action_arg2].
Append [action_arg1] [action_arg2]
4. Verify: Send a request to check if current task has been achieved.
Verify
The agent is allowed to read and write the following file (r/w):
files/notes.txt (r/w): the contents of this file will always be displayed in the
(cid:44)→ notes section down below.
answer.txt (r/w): a file to hold the final answer to user request
The agent is allowed to access the following read-only files (r):
files/request.txt (r): the user request
files/problem_specification.txt (r): a problem specification document
The agent can only see the contents of the last action it performed (e.g.
(cid:44)→ observations are Markovian), so the agent needs to take frequent notes. The
(cid:44)→ agent will follow a task network with nodes of the form:
{
"method1": {
"task": "process user request",
"subtasks": {
"subtask1": "[other subtask]",
"subtask2": "[other subtask]"
},
"effect": "the answer to the user request can be found in answer.txt in
(cid:44)→ the correct format",
"effect_files": {
"file1": "answer.txt",
"file2": "files/request.txt",
"file3": "files/problem_specification.txt"
}
},
....
"method7": {
"task": "take notes on [example1] and [example2]",
"subtasks": {
"subtask1": "[other subtask]",
"subtask2": "[other subtask]"
40

## Page 41

},
"effect": "notes contain information from [example1] and [example2]
(cid:44)→ documents",
"effect_files": {
"file1": "files/[example1].txt",
"file2": "files/[example2].txt",
"file3": "files/notes.txt"
}
}
}
which specify the name of the task, the effect of the task, the files that can
(cid:44)→ be used to confirm the result of the task and possibly a list of subtasks
(cid:44)→ that may need to be completed. For the following problem, please write a
(cid:44)→ task network for nodes of the above format to assist the agent in solving
(cid:44)→ the task.
General instructions:
1. Please respond only with the task network and no additional text.
2. The agent will need to use the verify action to move onto the next task, so
(cid:44)→ no verification subtasks are needed.
3. Make sure that the keys for subtasks are numbered backwards in the order that
(cid:44)→ the agent should complete the task in.
4. All subtasks should have a corresponding task node. The subtasks component is
(cid:44)→ not needed for leaf nodes of the task network.
5. The values in the subtask list "[other subtask]" should correspond to the
(cid:44)→ name of the subtask it is referring to (e.g. "take notes on xyz").
6. The top level task should be called "process user request".
7. Effect files denote the files needed for the verifier to check if a given
(cid:44)→ task node is completed (e.g. if the task is to write an answer, the problem
(cid:44)→ specification and request should be included as effect files so the answer
(cid:44)→ can be checked against it).
8. Make sure each task is numbered task[number].
The task specification:
*** TASK SPEC START ***
{}
*** TASK SPEC END ***
F Verification
ToverifywhetheranagentLLMhassuccessfullycompletedatask,wesendarequesttoaverifierLLM
tocheckifthetheeffectofthetasknetworknodehasbeensatisfied. Onlythecontentsoftheeffectfiles
foragiventasknodeareplacedintothecontextoftheverifierLLM.Thisallowsformoreconsistent
evaluation(andalleviateslongcontextissuesinusingsmallerLLMsforverification).
F.1 Verification Code (success checking in Fig 2)
with open('verification_prompt.txt') as f:
lines = f.readlines()
prompt = "".join(lines)
task_specification = get_current_task_network_node(current_task)
41

## Page 42

check = task_specification["effect"]
files_to_check = ""
counter = 1
while "file" + str(counter) in task_specification["effect_files"]:
file_to_check = task_specification["effect_files"]["file" + str(counter)]
files_to_check += "## Here are the contents of " + file_to_check[:-4] + ":
(cid:44)→ \n"
with open(files_directory + "/" + file_to_check) as f:
lines = f.readlines()
files_to_check += "".join(lines) + "\n"
counter += 1
prompt = prompt.format(check, files_to_check)
last_output = llm_model.instruct_query(prompt)
success = True if "PASS: TRUE" in last_output else False
if success:
predicates.add(stack[-1][0])
stack = stack[:-1]
if len(stack) == 0:
break
current_task = update_task()
F.2 Verification Prompt
Thisverificationpromptwastunedwithmeta-promptingonGPT-4.
**Here is your task:**
Your goal is to determine if the provided files satisfy the specified effect.
(cid:44)→ Follow these steps carefully:
### **Task Specification**
The effect that needs to be satisfied is:
{}
### **File Contents**
Here are the contents of the files provided:
{}
### **Instructions**
1. **Understand the Effect:** Carefully read the effect and identify its
(cid:44)→ conditions.
2. **Analyze the File Contents:** Compare the file contents explicitly against
(cid:44)→ the conditions of the effect.
- Break down the effect into specific criteria (e.g., "summarized version"
(cid:44)→ means the main ideas in "request" should be present in "notes").
- Check whether these criteria are satisfied in the files.
3. **Provide a Detailed Analysis:** State which criteria are satisfied and which
(cid:44)→ are not, with reasons based on the file contents.
### **Your Response Format**
Begin your response with:
42

## Page 43

```
ANALYSIS:
<Your detailed analysis of whether the files satisfy the effect, with explicit
(cid:44)→ reasoning.>
```
End your response with one of the following lines:
```
PASS: TRUE
```
*only if all conditions of the effect are satisfied.*
```
PASS: FALSE
```
*if any condition of the effect is not satisfied.*
---
43
