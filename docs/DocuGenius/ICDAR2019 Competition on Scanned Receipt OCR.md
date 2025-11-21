## Page 1

1
ICDAR2019 Competition on Scanned Receipt OCR
and Information Extraction
Zheng Huang, Kai Chen, Jianhua He, Xiang Bai, Dimosthenis Karatzas, Shjian Lu, and C.V. Jawahar
Abstract—Scanned receipts OCR and key information ex- card recognition, license plate recognition and hand-written
traction (SROIE) represent the processeses of recognizing text text recognition). However, receipts OCR has much higher
from scanned receipts and extracting key texts from them
accuracy requirements than the general OCR tasks for many
and save the extracted tests to structured documents. SROIE
commercialapplications.AndSROIEbecomesmorechalleng-
plays critical roles for many document analysis applications and
holdsgreatcommercialpotentials,butverylittleresearchworks ing when the scanned receipts have low quality. Therefore, in
and advances have been published in this area. In recognition the existing SROIE systems, human resources are still heavily
of the technical challenges, importance and huge commercial used in SROIE. There is an urgent need to research and
potentialsofSROIE,weorganizedtheICDAR2019competition
develop fast, efficient and robust SROIE systems to reduce
on SROIE. In this competition, we set up three tasks, namely,
and even eliminate manual work.
Scanned Receipt Text Localisation (Task 1), Scanned Receipt
OCR (Task 2) and Key Information Extraction from Scanned WiththetrendsofOCRsystemsgoingtobemoreintelligent
Receipts (Task 3). A new dataset with 1000 whole scanned and document analytics, SROIE holds unprecedented poten-
receipt images and annotations is created for the competition. tialsandopportunities,whichattractedhugeinterestsfrombig
The competition opened on 10th February, 2019 and closed on
companies, such as Google, Baidu and Alibaba. Surprisingly,
5th May, 2019. There are 29, 24 and 18 valide submissions
therearelittleresearchworkspublishedinthetopicofSROIE.
received for the three competition tasks, respectively. In this
reportwewillpresentsthemotivation,competitiondatasets,task While robust reading, document layout analysis and named
definition,evaluationprotocol,submissionstatistics,performance entity recognition are relevant to the SROIE, none of the
of submitted methods and results analysis. According to the existing research and past ICDAR competitions fully address
wide interests gained through SROIE and the healthy number
the problems faced by SROIE [1,2,3].
of submissions from academic, research institutes and industry
Inrecognitionoftheabovechallenges,importanceandhuge
over different countries, we believe the competition SROIE is
successful. And it is interesting to observe many new ideas and commercial potentials of SROIE, we organized the ICDAR
approaches are proposed for the new competition task set on 2019competitiononSROIE,aimingtodrawattentionfromthe
keyinformationextraction.Accordingtotheperformanceofthe community and promote research and development efforts on
submissions, we believe there is still a large gap on the expected
SROIE. We believe the this competition could be of interests
information extraction performance. Task of key information
to the ICDAR community from several aspects.
extractionisstillverychallengingandcanbesetformanyother
important document analysis applications. It is hoped that this First, to support the competition, a large-scale and well-
competition will help draw more attention from the community annotated invoice datasets are provided, which is crucial to
and promote research and development efforts on SROIE. the success of deep learning based OCR systems. While
many datasets have been collected for OCR research and
competitions,tothebestofourknowledge,thereisnopublicly
I. INTRODUCTION
available receipt dataset. Compared to the existing ICDAR
ScannedreceiptsOCRisaprocessofrecognizingtextfrom and other OCR datasets, the new dataset has some special
scanned structured and semi-structured receipts and invoices. features and challenges, e.g., some receipts having poor paper
On the other hand, extracting key texts from receipts and quality, poor ink and printing quality; low resolution scanner
invoices and save the texts to structured documents can serve and scanning distortion; folded invoices; too many unneeded
many applications and services, such as efficient archiving, interfering texts in complex layouts; long texts and small font
fast indexing and document analytics. Scanned receipts OCR sizes. To address the potential privacy issue, some sensitive
and key information extraction (SROIE) play critical roles fields (such as name, address and contact number etc) of
in streamlining document-intensive processes and office au- the receipts are blurred. The datasets can be an excellent
tomation in many financial, accounting and taxation areas. complement to the existing ICDAR and other OCR datasets.
However, SROIE also faces big challenges. With performance Second, three specific tasks are proposed: receipt OCR and
greatly boosted by recent breakthroughs in deep learning key information extraction. Compared to the other widely
technologies in terms of accuracy and processing speed, OCR studied OCR tasks for ICDAR, receipt OCR (including text
is becoming mature for many practical tasks (such as name detectionandrecognition)isamuchlessstudiedproblemand
hassomeuniquechallenges.Ontheotherhand,researchworks
Z. Huang is with Shanghai Jiaotong University, China, huang- onextractionofkeyinformationfromreceiptshavebeenrarely
zheng@sjtu.edu.cn. Jianhua He is with Aston University, UK,
published.Thetraditionalapproachesusedinthenamedentity
j.he7@aston.ac.uk.KaiChen(kaichen@onlyou.com)iswithOnlyou,China.
Xiang Bai (xbai@hust.edu.cn) is with Huazhong University of Science and recognition research are not directly applicable to the second
Technology, China. Dimosthenis Karatzas (dimos@cvc.uab.es), Universitat task of SROIE.
Auto´noma de Barcelona, Spain. Shijian Lu (Shijian.Lu@ntu.edu.sg)
Third, comprehensive evaluation method is developed for
is with Nanyang Technological University, Singapore. C. V. Jawahar
(jawahar@iiit.ac.in)iswithIIITHyderabad,India. the two competition tasks. In combination with the new
1202
raM
81
]IA.sc[
1v31201.3012:viXra

## Page 2

2
receipt datasets, it enables wide development, evaluation and III. COMPETITIONTASKS
enhancement of OCR and information extraction technologies
A. Task 1 - Scanned Receipt Text Localisation
forSROIE.ItwillhelpattractinterestsonSROIE,inspirenew
insights, ideas and approaches. 1) Task Description: Localizing and recognizing text are
Thecompetitionopenedon10thFebruary,2019andclosed conventional tasks that has appeared in many previous com-
on5thMay,2019.Thereare29,24and18validesubmissions petitions, such as the ICDAR Robust Reading Competition
received for the three competition tasks, respectively. In this (RRC)2013,ICDARRRC2015andICDARRRC2017[1][2].
report we will presents the motivation, competition datasets, The aim of this task is to accurately localize texts with 4
task definition, evaluation protocol, submission statistics, per- vertices. The text localization ground truth will be at least at
formance of submitted methods and results analysis. Accord- the level of words. Participants will be asked to submit a zip
ingtothewideinterestsgainedthroughSROIEandthehealthy file containing results for all test images.
numberofsubmissionsfromacademic,researchinstitutesand 2) Evaluation Protocol: As participating teams may apply
industry over different countries, we believe the competition localization algorithms to locate text at different levels (e.g.
SROIE is successful. It is hoped that this competition will textlines),fortheevaluationoftextlocalizazationinthistask,
help draw more attention from the community and promote the methodology based on DetVal will be implemented. The
research and development efforts on SROIE. methodology address partly the problem of one-to-many and
many to one correspondences of detected texts. In our evalua-
II. DATASETANDANNOTATIONS tionprotocolmeanaverageprecision(mAP)andaveragerecall
The dataset has 1000 whole scanned receipt images, which will be calculated, based on which F1 score will be computed
are used for all three competition tasks but with different and used for ranking [3].
annotations. Each receipt image contains around about four
key text fields, such as goods name, unit price and total cost,
B. Task 2 - Scanned Receipt OCR
etc. The text annotated in the dataset mainly consists of digits
andEnglishcharacters.Figure1showssomeexamplescanned 1) Task Description: The aim of this task is to accurately
receipt images. recognize the text in a receipt image. No localisation infor-
The dataset is split into a training/validation set (“trainval”) mation is provided, or is required. Instead the participants are
andatestset(“test”).The“trainval”setconsistsof600receipt required to offer a list of words recognised in the image. The
images are made available to the participants along with their task will be restricted to words comprising Latin characters
annotations. The “test” set consists of 400 images, which will and numbers only.
bemadeavailableafewweeksbeforethesubmissiondeadline. The ground truth needed to train for this task is the list
For receipt detection and OCR tasks, each image in the of words that appear in the transcriptions. In order to obtain
dataset is annotated with text bounding boxes (bbox) and the ground truth for this task, you should tokenise all strings
the transcript of each text bbox. Locations are annotated as splitting on space. For example the string “Date: 12/3/56”
rectangles with four vertices, which are in clockwise order should be tokenised “Date:”, “12/3/56”. While the string
starting from the top. Annotations for an image are stored in “Date: 12 / 3 / 56” should be tokenised “Date:” “12”, “/”,
a text file with the same file name. The annotation format is “3”, “/”, “56”.
similar to that of ICDAR2015 dataset, which is illustrated in 2) Evaluation Protocol: For the Recognition ranking we
Fig.1(a). For the information extraction task, each image in willmatchallwordsprovidedbytheparticipantstothewords
the dataset is also annotated and stored with a text file with in the ground truth. If certain words are repeated in an image,
format, which is illustrated in Fig.1(b). theyareexpectedtoalsoberepeatedinthesubmissionresults.
We will calculate Precision (# or correct matches over the
number of detected words) and Recall (# of correct matches
over the number of ground truth words) metrics, and will use
the F1 score as the final ranking metric.
C. Task3-KeyInformationExtractionfromScannedReceipts
1) TaskDescription: Theaimofthistaskistoextracttexts
(a) Task1andTask2.
of a number of key fields from given receipts, and save the
texts for each receipt image in a json file. Participants will be
askedtosubmitazipfilecontainingresultsforalltestinvoice
images.
2) Evaluation Protocol: For each test receipt image, the
extracted text is compared to the ground truth. An extract text
ismarkedascorrectifbothsubmittedcontentandcategoryof
theextractedtextmatchesthegroundtruth;Otherwise,marked
(b) Task3.
asincorrect.ThemAPiscomputedoveralltheextractedtexts
Fig.1. Annotationformatforthetasks. of all the test receipt images. F1 scored is computed based on
mAP and recall. F1 score is used for ranking.

## Page 3

3
(a) (b) (c) (d) (e)
Fig.2. Examplesofscannedreceiptsforthecompetitiontasks.
IV. ORGANIZATION 1) 1st ranking method “SCUT-DLVC-Lab-Refinement”:
The competition SROIE made use of the Robust Reading This method utilizes a refinement-based Mask-RCNN.
Competition (RRC) web portal to maintain information of Inthemethodredundantinformationandrefinedetected
the competition, download links for the datasets, and user bounding-box results are iteratively removed. Finally,
interfaces for participants to register and submit their results the submitted result is ensembled from several models
[4].GreatsupporthasbeenreceivedfromtheRRCwebteam. with different backbones.
The timeine for the SROIE competition is shown below. 2) 2nd ranking method: “Ping An Property & Casualty
Insurance Company”: This method uses an anchor-free
• Website online: February 15, 2019
detection frameworkwith FishNet as thebackbone. The
• Registration open: February 20 – March 31, 2019
trainingandtestingimagesarepre-processedtoroughly
• Trainingandvalidationdatasetsavailable:March1,2019
align their scales with OpenCV adaptive threshold. The
• Test dataset available: March 31, 2019
detection results are post-processed according to the
• Tasks 1 and 2 submission deadline: April 22, 2019
classification score map. It can well solve the problem
• Task 3 submission open: April 23, 2019
of short detection of long text line.
• Task 3 submission Deadline: May 5, 2019
3) 3rdrankingmethod“H&HLab”:InthismethodEAST
Bythesubmissiondeadline,wereceived29submissionsfor
and multi oriented corner are ensembled to create a
Task1,24forTask2and18forTask3.Someteamssubmitted
robust scene text detector. To make network learning
multiple results for the same task. We took measures to iden-
easier, the mutli-oriented corner network is modified
tify multiple submissions and only took the last submission
with a new branch borrowed from east added.
from mulitple ones in ranking.
V. SUBMISSIONANDRESULTS B. Task 2 Performance and Ranking
Afterthesubmissiondeadlines,wecollectedallsubmissions Fig. 4 lists the top-10 submissions of Task 2.
and evaluate their performance through automated process The methods used by the top 3 submissions for Task 2 are
with scripts developed by the RRC web team. The winners presented below.
are determined for each task based on the score achieved by
1) 1st ranking method “ H&H Lab”: This method mainly
the corresponding primary metric. A workshop is planned to
usesCRNNforTask2.Differentfromthecontentinthe
present the summary of the competition and give awards to
paper,thestructureofCNNismodififiedtobePVANet-
the winners.
likeandusesmultipleGRUlayers.Thetrainingstrategy
is adjusted to further improve the recognition result.
A. Task 1 Performance and Ranking
2) 2nd ranking method ”INTSIG-HeReceipt-Ensemble”:
Fig. 3 lists the top-10 submissions of Task 1. This recognition method is based on CNN and RNN.
The methods used by the top 3 submissions for Task 1 are With different backbones and recurrent structure set-
presented below. tings, the team trained several models seperately and

## Page 4

4
Fig.3. Top10methodsforTask1-ScannedReceiptTextLocalisation.
then implement model ensemble. Finally, according to VI. DISCUSSIONS
the official requirement, they split line output into word
level. As both OCR and information extraction of scanned re-
3) 3rd ranking method “Ping An Property & Casualty ceipts are new tasks for ICDAR competitions, the organizers
Insurance Company”: The team employed an encoder- proposedtosetthetasksofdetectionandOCRfortheSROIE
decoder sequence method with attention mechanism. competition along side the task of information extraction.
First, they created 2 millions of systhesis text lines, There are two main considerations: firstly, we hope to at-
wherethereceiptbackgroundisused.Eachlineconsists tract sufficient interest for this new competition with some
of one to five words. Then, they fine-tuned the network established taskes; secondly, text detection and OCR are key
with real-world receipt data. processes for the task of information extraction. According to
the submitted methods and results, we believe such setting on
thecomptetiontasksissuccessful.Thenumberofsubmissions
C. Task 3 Performance and Ranking for all the three tasks are encouragingly high. And the top
ranking teams for Task 3 are mostly doing well with the first
Fig. 5 lists the top-10 submissions of Task 3.
two tasks.
The methods used by the top 3 submissions for Task 3 are
From the aspects of task performance, unsurprisingly, the
presented below.
detection and OCR results for Task 1 and Task 2 are very
1) 1strankingmethod“PingAnProperty&CasualtyInsur- good, with 16 teams obtaining Hmean of more than 90% for
anceCompany”:Basedonourdetectionandrecognition Taks 1 and 7 teams obtained Hmean of more than 90% for
results on Task1 and 2, this team used a lexicon (which Task 2. The results for Taks 1 and Task 2 shows that the
is built from the train data set ) to auto-correct results existing approaches for general text detection and recognition
and use RegEx to extract key information. For every are performing well for scanned receipts. However, if we take
keyword (company, cash, date, and address), they used the strict requirement of receipt applications into account, say
different patterns of regular expression. 99% accuracy, it is noted that, even the best OCR method
2) 2nd ranking method: “Enetity detection”: This method in Task 2 can’t deliver the required performance. Therefore,
combines the strategy of content parsing and entity we believe that the challenge for scanned receipt OCR is
awared detector based on ‘EAST‘ to obtain selected still there, which demands further research and development
candidates. A text classifier with RNN embedding was efforts. For the Task 3 of key information extraction, we can
applied for final results. see only one method achieves Hmean of more than 90%
3) 3rd ranking method “ H&H Lab”: The team completed (which is 90.49%), and more than half of the submitted
Task 3 using a structure similar to BiGRU-CNNs-CRF, methods achieve Hmean of less than 80%. Therefore, there
and designed a number of constraint rules to correct the are still large space for improvement for the new task of key
results. information extraction.

## Page 5

5
Fig.4. Top10methodsforTask2-ScannedReceiptOCR.
Fig.5. Top10methodsforTask3-KeyInformationExtractionfromScannedReceipts.
From the aspects of technical approaches used in the subit- proposed. Most of the submitted methods use different ideas
ted methods, it is observed that for the first two tasks, while and approaches. As this task is new and presents an open
the traditional network models are applied, many top ranking research issues, we expect more innovative approaches will
methods use ensamble of multiple architectures or models to be proposed after the competion.
improveperformance.Andsomemethodsuselargedatasetsof
synthetic texts. For the Task 3 of key information extraction,
itisinterestingtoobservemanynewideasandapproachesare

## Page 6

6
VII. CONCLUSION
We organized the one of the first competitions on the
OCR and information extraction for scanned receipts. For the
competition SROIE we prepared new datasets and evaluation
protocols for three competition tasks. A good number of
submissions were received for all three tasks, which showed
a broad interests on the topic from the academic and industry.
Anditisinterestingtoobservemanynewideasandapproaches
are proposed for the new competition task of key information
extraction. According to the performance of the submissions,
webelievethereisstillalargegapontheexpectedinformation
extractionperformance.Thetaskofkeyinformationextraction
is still very challenging and can be set for many other
importantdocumentanalysisapplications.Itwillbeinteresting
toextendonthiscompetitionwithmorechallengingandlarger
datasets and applications in the future. The new datasets used
in this competition will be made available after the event.
ACKNOWLEDGEMENT
The ICDAR19 competition SROIE is supported in part by
the European Union’s Horizon 2020 research and innovation
programme under the Marie Skłodowska-Curie grant agree-
ment No 824019. The organizers thank Cheng Li of Onlyou
forhisgreatsupportonthecreationofthecompetitiondatasets
and overall managment, Sergi Robles and the RRC web team
for their tremendous support on the registration, submission
and evaluation jobs.
REFERENCES
[1] He J., Chen H., et al, ‘Adaptive congestion control for DSRC vehicle
networks’,IEEEComm.Lett.,Feb.2010,14,(2),p.127-129.
[2] D.Karatzas,F.Shafait,S.Uchida,M.Iwamura,L.Gomez,S.Robles,J.
Mas,D.Fernandez,J.Almazan,L.P.delasHeras:ICDAR2013Robust
ReadingCompetition.ICDAR,2013.
[3] D.Karatzas,L.Gomez-Bigorda,A.Nicolaou,D.Ghosh,A.Bagdanov,
M. Iwamura, J. Matas, L. Neumann, VR. Chandrasekhar, S. Lu, F.
Shafait,S.Uchida,E.Valveny:ICDAR2015robustreadingcompetition.
ICDAR,2015.
[4] Everingham,M.andEslami,S.M.A.andVanGool,L.andWilliams,C.
K.I.andWinn,J.andZisserman,A.:ThePascalVisualObjectClasses
Challenge:ARetrospective.IJCV,2015
[5] D.Karatzas,L.Rushinol,TheRobustReadingCompetitionAnnotation
andEvaluationPlatform.
