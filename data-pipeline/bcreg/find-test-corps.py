#!/usr/bin/python
import psycopg2
import datetime
import os
import logging

from bcreg.config import config
from bcreg.eventprocessor import EventProcessor, CORP_TYPES_IN_SCOPE
from bcreg.bcregistries import BCRegistries, system_type

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'WARNING').upper()
logging.basicConfig(level=LOG_LEVEL)


specific_corps = [ '0176097', '0318626', '0178676', 'A0027307',
'A0072604', 'A0089098', 'A0074145', 'A0081787', 'A0097512', '1216662', 'A0075092', 'A0089744', 'A0093462', '0837462', 
'A0080940', 'A0083141', 'A0083112', 'A0101123', '1255921', '0400647', 'A0074738', '0178617', '0658092', 'A0064349', 
'1251085', 'A0075220', 'A0084589', 'A0084769', '1016423', '1170320', 'A0071377', 'A0093553', 'C1107260', '1132002', 
'A0105449', 'A0105272', 'C1244030', 'A0064112', 'A0087950', '0983515', '0995083', 'A0082467', 'A0085501', '0176097', 
'0331609', 'A0076446', '0997948', 'CP0002161', '0318626', 'A0072702', 'A0076556', 'A0082923', '1148542', 'A0070144', 
'1127777', 'A0074140', 'A0083205', 'A0084234', 'A0103118', '0040222', 'A0072882', 'A0079443', '1159817', 'S0064220', 
'A0075461', 'A0078321', 'FM0810226', 'A0072493', '0889413', 'A0096631', 'A0114172', 'A0114906', 'A0082921', 'A0087200', 
'A0113693', '0519772', 'LLC0000404', '1105165', '0067330', '0630501', 'A0069057', 'A0076608', 'A0081501', 'A0084228', 
'0019638', 'A0065428', 'A0089331', '0993198', 'A0104990', 'A0109632', '0817081', 'A0076296', 'A0082633', 'A0087871', 
'A0098910', '1256429', 'QE0000590', 'A0079836', 'A0079127', 'A0081549', 'A0082924', 'A0088749', '0024915', '0202814', 
'1166574', 'A0067730', 'A0097455', '1137086', '1153411', '0736631', 'A0082925', '1170012', '1257225', '1249467', 
'0912594', 'A0087395', 'A0107672', 'A0087345', 'A0093681', '1110844', 'CP0000852', '0017622', '0178676', 'A0071052', 
'A0071866', 'A0073745', 'A0075243', 'A0077701', 'A0080048', 'A0085306', '1267090', '0886671', 'A0099169', 'A0076809', 'A0073451', 
'A0077030', 'A0079422', 'LLC0001115', 'A0074611', 'A0081998', 'A0099518', 'A0114190', '1222766', 'A0082920', 'A0088683', 'A0110587', 
'0000351', '1256866', '0722839', 'A0068915', 'A0079755', '0338417', 'A0085639', 'A0097618', '1251901', 'A0063444', '0965532', 
'A0087869', 'A0113037', '1252588', 'A0113501', '1252420', '1225425', 'A0077406', '1183409', 'A0081854', '1154400', '1189196', 
'1198688', 'A0089494', 'A0093555', 'A0062459', 'A0068399', 'A0084217', 'A0084423', 'A0106627', 'XS0073885', '0197365', 'A0078795', 
'A0082922', '1246753', '0026378', 'A0074203', 'A0079106', 'A0083737', '1157768', '1213690', 'A0079809', 'A0099974', 'A0044761', 
'0067382', 'A0065568', 'A0067421', 'A0075097', '1043978', 'C0749875', 'A0085124', 'A0085625', '0023236', '0320081', 'A0080991', 
'A0090015', 'XS0074537', 'A0068402', '0577507', 'A0064083', 'A0071139', '0014696', 'A0096264', 'LP0693424', 'A0085546', '1205125', 
'1243770', '0018682', 'A0085327', 'A0083551', 'A0087524', '1085924', 'LLC0000318', 'A0114060', '1215091', '0022191', '0019355', 
'XS0058557', 'A0096561', '0476954', 'A0064380', 'A0070434', '1112586', 'A0104343', '1169332', '1255928', 'A0027307',
'0327633', '0767769', '0863017', '0869896', '1074941', '1155907', '1157072', '1238926', '0032234', '0201241', 
'0433217', '1054780', '1114746', '1221325', 'FM0809672', '0398703', '0755705', '1007139', 'A0114989', '0563176', 
'1012158', '0338855', '0471070', '0626139', '0692303', 'C1248568', '0685926', '0879144', '1007130', 'FM0747181', 
'0505512', '0795451', '0974032', '1070288', '1135920', '1223855', 'C1248022', '0382121', '0466497', '0928152', 
'1009939', '1020306', '1011223', '1162346', '0757827', '0889916', '0901074', '1044075', '1070749', '1110840', 
'FM0820468', 'FM0821395', '0646180', '0669441', '0746540', '0965948', 'FM0612366', '1169796', 'CP0001579', '1204541', 
'FM0816977', '1257033', '0912758', '0992710', '1068417', '1087252', 'FM0781769', 'FM0828445', '1236417', '0417298', 
'FM0515144', 'A0095921', '1049054', '1200734', 'FM0818521', 'FM0642693', '1099722', '1147284', 'C1248582', '0773571', 
'FM0703656', 'C1245884', 'FM0818437', 'FM0835869', '0324311', '0779735', 'A0070684', '1011411', 'FM0813843', '0314081', 
'0537068', '0931559', '0936955', '1153065', 'FM0826568', 'FM0806372', 'LP0830021', '0438537', '0486858', '0608406', 
'0904037', 'CP0002291', 'C1248019', 'FM0806868', 'FM0807499', '0346837', '0438532', '0533851', '0687388', '0939645', 
'1020522', 'FM0681133', '1083998', 'FM0830783', 'A0039192', '0058045', '1034932', '1116837', '1124919', '1124755', 
'S0055242', 'FM0813012', '0436187', '0585397', '0608700', '0703692', '0784931', '0893874', '0888702', '1044326', 
'1118134', 'FM0726996', '1171194', 'CP0000088', 'FM0766028', 'FM0818010', '0049438', '0306922', '0903790', '1073246', 
'1117686', 'FM0803352', '0925623', '1206692', '1206461', 'FM0810099', 'FM0826880', '0576004', '0688157', '0926373', 
'1247258', '0098746', '0726025', '0788855', '0859341', '1206668', 'C0779398', 'FM0772178', 'FM0800255', 'CP0002290', 
'0751116', 'FM0551215', '1135924', '0583165', '1077601', '1083599', '1190374', 'FM0795899', '0493986', 'XP0534324', 
'0992649', '1208565', 'FM0809786', 'FM0820103', '0315729', '0645515', '0875819', 'FM0620900', '1075240', '1106207', 
'1116002', 'FM0804866', '0832542', '0913502', '0977144', '1133908', '1186701', 'C1219545', '0927783', 'FM0671654', 
'1240462', '0743763', 'C0892742', 'FM0830138', 'FM0817275', '0211208', '0873262', '0672930', '0692570', 'FM0139194', 
'CP0002347', '0786994', 'FM0592157', 'FM0789790', '0249257', '0412962', '1007615', '1144427', 'FM0816720', 'FM0797305', 
'0234066', 'FM0806894', 'C1248096', '0446396', '0778658', '0983214', '1073926', '0669513', '0916668', '1040702', 
'C1245468', 'FM0807729', 'FM0833431', '0446579', '0684321', '0768966', '1134810', '1208186', 'C1248632', '1240463', 
'0392343', '0422427', '0722662', '0815928', '0857428', '0966005', '1135929', '0036238', '0645073', '0646257', 
'0929912', '1003545', '1035219', 'A0106310', 'CP0002289', 'CP0001965', 'C1245509', 'FM0830815', '1242550', 'FM0800316', 
'0562876', '0996190', 'FM0834512', 'FM0806133', '0633280', 'FM0418994', '0991953', 'FM0766566', 'FM0810730', 'FM0809705', 
'0850561', 'S0022307', '0985072', 'FM0642692', '0235191', '0776468', '0964721', 'CP0002142', '1201327', '0162193', 
'0892096', '1127323', '1144899', '1229738', 'FM0806913', 'FM0830112', '0035275', '0198595', '1021665', '1180036', 
'FM0804695', 'FM0828031', 'FM0830348', '0542088', '0568848', 'S0032541', '0940071', '0952499', 'CP0002237', '1245938', 
'FM0799231', '1238236', 'A0016625', '0417313', '0610234', '1219686', 'FM0837580', 'FM0805900', '0587568', '0908923', 
'1158210', '1234789', '1033110', 'FM0827327', 'A0111729', 'FM0814754', '0057932', '0725023', '0760854', 'FM0822126', 
'0088656', 'FM0419486', '0991963', 'FM0815856', '0200021', '0603291', '1067184', 'FM0818374', 'C1248832', '0322577', 
'FM0826478', 'FM0808080', '0541894', '0651522', '0681303', '0849645', '1011412', 'CP0002337', '0855250', '1273661', 
'FM0809164', '0760609', 'FM0803272', 'C1248024', '0591347', 'FM0644889', '1011166', 'CP0002069', 'CP0002232', 'FM0803309', 
'FM0804348', '0354564', '0757904', '0766824', '0835393', 'S0049674', 'FM0759498', '0177353', '0423581', '0717689', 
'0826129', '0862700', 'FM0784632', 'FM0828597', '0413649', '0915930', 'FM0725913', 'FM0810088', '1247184', '0688148', 
'FM0418993', '0933377', '0940325', '0975572', '1069906', 'C1153116', 'CP0001794',
'0045728', '0071773', '0055099', '0891085', '0036860', '0007021', '0108610', 'S0001104', '0025099', '0040909', 'A0113685', 'A0113677',
'XP0538736', 'A0117171', 'XS0073189', 'LLC0001117', 'A0062479', 'A0016173',
]

specific_corps_2 = [
                    '0641655',
                    '0820416',
                    '0700450',
                    '0803224',
                    'LLC0000192',
                    'C0277609',
                    'A0072972',
                    'A0051862',
                    'C0874156',
                    '0874244',
                    '0593707',
                    'A0068919',
                    'A0064760',
                    'LLC0000234',
                    'A0077118',
                    'A0062459',
                    '0708325',
                    '0679026',
                    '0707774',
                    'C0874057',
                    'A0028374',
                    'A0053381',
                    'A0051632',
                    '0578221',
                    'A0032100',
                    '0874088',
                    '0803207',
                    '0873646',
                    '0078162',
                    '0754041',
                    'XS1000180',
                    'LP1000140',
                    'A0059911',
                    'S1000080',
                    '0637981',
                    'A0051632',
                    '0578221',
                    '0497648',
                    'A0038634',
                    '0136093',
                    '0869404',
                    '0641396',
                    'LP0745132',
                    'C0283576',
                    '0860306',
                    '0673578',
                    '0763302',
                    '0860695',
                    'A0039853',
                    'A0036994',
                    '1185488',
                    '0979020',
                    '0354136',
                    '1164165',
                    '1059630',
                    '0093733',
                    '0197646',
                    'A0082127',
                    '0206786',
                    '0908182',
                    'FM005513',
                    '0616651',
                    'FM0418446',
                    'FM0464421',
                    'FM0464206',
                    '0143311',
                    '0006965',
                    'A0008669',
                    '0206483',
                    '0287583',
                    '0517093',
                    '0046062',
                    '0545062',
                    'A0027307',
                    '0046397',
                    '0503852',
                    'A0053913',
                    '0358554',
                    'C0184104',
                    'C0429174',
                    'A0020540',
                    '0693705',
                    '1101218',
                    '0650761',
                    '0928747',
                    '0347474',
                    '1101218',
                    '0450252',
                    'A0056744',
                    'A0087698',
                    'A0087699',
                    '0296354',
                    '0859276',
                    'A0045786',
                    '0791684',
                    '0675400',
                    '0675765',
                    'A0107449',
                    'A0107446',
                    'A0107438',
                    '1181944',
                    'A0107427',
                    'A0107426',
                    'A0107424',
                    'A0107423',
                    '0142362',
                    'FM0550949',
                    'FM0501860',
                    '0643505',
                    '0510537',
                    'C0733137',
                    'FM0327778',
                    'FM0327777',
                    'FM0327770',
                    'FM0327756',
                    '1188712',
                    '0855234',
                    'A0093289',
                    'A0053723',
                    'A0082657',
                    '0319629',
                    '0747962',
                    'A0011423',
                    'A0080841',
                    '0945957',
                    'A0092209',
                    'A0070194',
                    '0338518',
                    '1199242',
                    '0072808',
                    '0946908',
                    '0730909',
                    '1198849',
                    '0149514',
                    '0390058',
                    # more test data from the additional company types
                    '1071287', # very short credential effective periods
                    '1001845',
                    'FM0472969', # for Dissolution effective date -> event.trigger_dts field for the dissolution filing event
                    'FM0345136', # for Each section of the timeline should reference the name at that point in time
                    'XP0068811', # for It is not accurate to say a firm is related to itself
                    'FM0547930', # for A number of PROD entities I attempted to test with do not appear in VON
                    'FM0027827', 'LP0043506', 'LP0004424', 'XP0646920', 'LL0000038', 'LL0000063', 'MF0000041', 'MF0000022',
                    'LL0000145', # for All status changes (from active to historical and vice versa) should be displayed in the timeline
                    'S0000009', 
                    'S0000872', # for “0001-01-01” displays as “Dec 31, 1” on the Organization data.  Displays as “Dec 31, 1, 11:40 PM” on the Credential data
                    'XS0054137', # forThey reinstated (became active) and then 10 minutes later changed jurisdiction.  The reinstatement is either missing or not visible on the timeline. Home Jurisdiction is British Columbia on the first credential and should be Ontario.  Home Jurisdiction is British Columbia on the second credential and should be Federal
                    'XS0059885', # for Has 2 credentials because of a change of jurisdiction. Home Jurisdiction is British Columbia on the first credential and should be Ontario.  Home Jurisdiction is British Columbia on the second credential and should be Federal.
                    '1047742', # for had a “Correction - Put Back On” on March 16 making it active.  It is currently active in COLIN.  However the Orgbook shows it as historical
                    'FM0688355', # Relationships are not consistently showing. FM0688355 is a firm owned by CP0001939 ...
                    'CP0001939', # 
                    'FM0415725', # FM0415725, is also now only showing relationships on the corporate owner
                    'A0101881', # owner of FM0415725
                    'XS0015243', # Home jurisdiction is displaying as 'BC' when no record exists in CPRD.Jurisdiction. In these cases we are better off to have nothing display at all. E.g. XS0015243.
                    'CP0000527', # Registration type shows as CO-OPS when looking up CO-OP records. For corp_typ_cd 'A' or 'BC' we use the corp_type.full_desc from the DB. CO-OPS should also use the full_desc (Cooperative). E.g. CP0000527.
                    'CP0000527', # Credential reason is rendering with code for certain COOP records. E.g. for CP0000527
                    'CP0000103', #
                    'CP0000851', # In the DB the entity became historical due to amalgamation (HAM) as of event ID 102030389 which occurred on 1976-12-31 00:00:00. In VON we are seeing the status of HIS as a result of a System to D2 event on Feb 26, 2019.
                    'CP0001048', # In the DB the date for the creation event which set the entity to active and listed the first name is 1899-12-31. In VON the main search shows the name effective date as a day earlier – 1899-12-30. Date issue also exists when you select the first section of the timeline and in that case both the date and the time are wrong.
                    'FM0745134', # Error'ed in Prod
                    'FM0485314',
                    'FM0616907',
                    'FM0429408',
                    'FM0415725',
                    'FM0485314',
                    'FM0616907',
                    'FM0429408',
                    '1204452',  # relationship issues between these next 3
                    'FM0777306',
                    'FM0776052',
                    'FM0368694', # didn't show up in test
                    'S0047404',
                    'PA0000027', # last round of test corps
                    'PA0000139',
                    'PA0000159',
                    'PA0000375',
                    '0277447',   # missing in prod
                    'FM0780183', # dba for the above
                    '0276176',   # quartech
                    'S1000224',  # errored out in test
                    'FM1000148',
                    'FM1000145',
                    'FM1000020',
                    'FM1000019',
                    'FM1000331',
                    'FM1000146',
                    'FM1000018',
                    'FM1000200',
                    'FM0743811', # potential deadlock issues
                    '0964770',
                    'FM0653232',
                    'FM0784088',
                    'FM0769586',
                    'FM0784089',
                    'FM0649949',
                    'FM0649943',
                    'FM0649946',
                    'C1218404',
                    'FM0784092',
                    'FM0783805',
                    'FM0784112',
                    '1136244',
'0786125', '0805487', '0857035', '1146610', '1221189', 'LL0001586', '1146432', 'FM0786101', '0788664', 'FM0786068', 'C1221192', '1221199', 'FM0786071', '1050538', 'FM0786094', '0712502', '0921740', '1073125', '1113564', '1191606', '1220807', 'A0110897', 'FM0786099', '0714019', '0803629', '1170226', '0989579', '1050151', '1146495', 'FM0786104', '0733489', '1139377', '1203043', 'A0110898', '0747068', '0842810', '1053874', '1080979', 'FM0786103', 'FM0786105', 'FM0786107', '0728412', '0773237', '0909072', '1146905', '0764208', '0981555', '1059466', '0951462', '0958642', '0978647', '1196759', '1221191', '0804112', '0865102', '1011794', 'FM0786070', '0392781', '0886926', '0929091', '1044485', '1146454', '0788671', '0803927', '0820240', '0820773', '0914456', '1062602', '1221195', 'FM0786098', '0811943', '1196120', '1202694', '1221188', '1219810', 'FM0786096', 'FM0786069', '1062713', '0857107', '0872623', '1041100', '1047420', '1221091', '1221198', 'FM0786102', '0779758', '0979020', '1023677', '1059918', '1154479', '1205923', '1217785', 'A0110899', 'FM0786097', '0898643', '1032093', '1041245', '0941797', '1158755', '1217934', '1221197', 'FM0786100', 'FM0786095', '0899190', '1081464', 'A0110896', '0818116', '0938923', '1053137', '1191976', 'FM0786074', 'FM0786106', '1125622', '1221200', '1221193', '0693705', '0747568', '0931646', '0733162', '0788683', '0801423', '1221190', '1221196', '1221194', '0738753', '1191667', '1209635', '1217177', '0842348', '1101251', '1219655', 'FM0786072', '1011546', '1009629', '1146464',
'A0080609', '1099982', '0730805', 'A0077091', '1091495', '0332563', '0378593', '0317167', '0618270', '0798257', '0953267', '1162048', 'A0091542', 'A0101682', 'A0071533', '0965000', 'A0098806', '1125543', '1194624', '1215860', '0730937', 'A0067077', '0458948', '1057027', '1213440', '0852418', '0978351', 'A0106584', 'A0053149', '1219032', '1028915', '1213465', '0530692', '0704567', '1110376', '0703754', '0979990', 'FM0760271', '0207899', '0718055', '0504939', '0636414', '1028921', '0775430', '0916103', 'A0097981', '1131823', '0479710', '0454816', '0788674',
                    '1225093', # ticket # 847
                    'FM0514501',
                    'A0067332',
                    'C1224093',
                    'S0001569',
                    'FM0783403',  # latest batch of test data
                    'FM0782737',
                    '1214962',
                    '1215240',
                    'FM0783301',
                    'FM0781697',
                    '1217143',
                    '1217769',
                    'FM0781343',
                    'A0110609',
                    'LP0781421',
                    '1217576',
                    '1214853',
                    'XP0782410',
                    '1217989',
                    '1216391',
                    '1216440',
                    '1214861',
                    '1214854',
                    '1215239',
                    'A0110364',
                    'A0110579',
                    'XP0783279',
                    'FM0781564',
                    'FM0783319',
                    '1217306',
                    'FM0782128',
                    'FM0782631',
                    'A0110346',
                    '1216444',
                    '1216882',
                    '1216439',
                    'FM0782551',
                    '1216443',
                    'S0071602',
                    'FM0781674',
                    'FM0781671',
                    '1215396',
                    '1214599',
                    '1214434',
                    'FM0782584',
                    'S0071582',
                    'A0110363',
                    '1217577',
                    '1215060',
                    '1217554',
                    '1217112',
                    'A0043183', # additional test corps
                    'FM0251249',
                    'FM0606634',
                    'FM0251484',
                    'LP0438693',
                    '1219655',
                    '1219810',
                    'FM0130037',
                    '0786125', '0805487', '0857035', '1146610', '1221189', 'LL0001586', '1146432', 'FM0786101', '0788664', 'FM0786068', 'C1221192', '1221199', 'FM0786071', '1050538', 'FM0786094', '0712502', '0921740', '1073125', '1113564', '1191606', '1220807', 'A0110897', 'FM0786099', '0714019', '0803629', '1170226', '0989579', '1050151', '1146495', 'FM0786104', '0733489', '1139377', '1203043', 'A0110898', '0747068', '0842810', '1053874', '1080979', 'FM0786103', 'FM0786105', 'FM0786107', '0728412', '0773237', '0909072', '1146905', '0764208', '0981555', '1059466', '0951462', '0958642', '0978647', '1196759', '1221191', '0804112', '0865102', '1011794', 'FM0786070', '0392781', '0886926', '0929091', '1044485', '1146454', '0788671', '0803927', '0820240', '0820773', '0914456', '1062602', '1221195', 'FM0786098', '0811943', '1196120', '1202694', '1221188', '1219810', 'FM0786096', 'FM0786069', '1062713', '0857107', '0872623', '1041100', '1047420', '1221091', '1221198', 'FM0786102', '0779758', '0979020', '1023677', '1059918', '1154479', '1205923', '1217785', 'A0110899', 'FM0786097', '0898643', '1032093', '1041245', '0941797', '1158755', '1217934', '1221197', 'FM0786100', 'FM0786095', '0899190', '1081464', 'A0110896', '0818116', '0938923', '1053137', '1191976', 'FM0786074', 'FM0786106', '1125622', '1221200', '1221193', '0693705', '0747568', '0931646', '0733162', '0788683', '0801423', '1221190', '1221196', '1221194', '0738753', '1191667', '1209635', '1217177', '0842348', '1101251', '1219655', 'FM0786072', '1011546', '1009629', '1146464',
                    'A0080609', '1099982', '0730805', 'A0077091', '1091495', '0332563', '0378593', '0317167', '0618270', '0798257', '0953267', '1162048', 'A0091542', 'A0101682', 'A0071533', '0965000', 'A0098806', '1125543', '1194624', '1215860', '0730937', 'A0067077', '0458948', '1057027', '1213440', '0852418', '0978351', 'A0106584', 'A0053149', '1219032', '1028915', '1213465', '0530692', '0704567', '1110376', '0703754', '0979990', 'FM0760271', '0207899', '0718055', '0504939', '0636414', '1028921', '0775430', '0916103', 'A0097981', '1131823', '0479710', '0454816', '0788674',
                    '1196236',
                    'FM0786693', '0392781', '1222085', '1221842', '1221944', '1221909', '1221947',
                    '0686268','FM0621367',
                    'FM0789723',
                    '1237010',
                    '1237089',
                    '1237149',
                    '1237164',
                    '1237228',
                    '1237234',
                    '1237247',
                    '1235577',
                    '1236975',
                    '1237281',
                    '1236398',
                    '0036103',
                    '0014947',
                    '0020288',
                    '0163588',
                    '0187871',
                    '0640905',
                    '0131809',
                    '0337062',
                    '0496513',
                    '0337062',
                    '1156638',
                    '1164820',
                    '1052899', # test cases Sept 1
                    'S0073442',
                    'FM0810412',
                    '1256313',
                    'FM0810423',
                    '1257153',
                    'A0113969',
                    'FM0810236',
                    'C1257482',
                    '1257499',
                    '1257336',
                    'FM0810201',
                    'FM0811249',
                    'FM0811249',
                    'C1256334',
                    'CP0002369',
                    'S0073434',
                    '1263326',
                    '1265645',
                    '0003938',
                    '0837735',
                    '1016676',
                    '1052899',
]


with BCRegistries() as bc_registries:
    # get 5 corps for each type in scope (in addition to the above list)
    for corp_type in CORP_TYPES_IN_SCOPE:
        print(corp_type)
        sql = """
                select corp_num
                from bc_registries.corporation
                where corp_typ_cd = '""" + corp_type + """'
                order by corp_num desc
               """
        corps = bc_registries.get_bcreg_sql("corps_by_type", sql, cache=False)
        n_corps = min(len(corps), 5)
        for i in range(n_corps):
            specific_corps.append(corps[i]['corp_num'])

    with EventProcessor() as event_processor:
        print("Get last processed event")
        prev_event_id = 0

        print("Get last max event")
        max_event_date = bc_registries.get_max_event_date()
        max_event_id = bc_registries.get_max_event(max_event_date)
        #max_event_id = 101944500 
        #max_event_date = bc_registries.get_event_id_date(max_event_id)
        
        # get specific test corps (there are about 6)
        print("Get specific corps")
        corps = bc_registries.get_specific_corps(specific_corps)
        corps_2 = bc_registries.get_specific_corps(specific_corps_2)
        corps.extend(corps_2)

        print("Find unprocessed events for each corp")
        last_event_dt = bc_registries.get_event_effective_date(prev_event_id)
        max_event_dt = bc_registries.get_event_effective_date(max_event_id)
        corps = bc_registries.get_unprocessed_corp_events(prev_event_id, last_event_dt, max_event_id, max_event_dt, corps)
        
        print("Update our queue")
        event_processor.update_corp_event_queue(system_type, corps, max_event_id, max_event_date)
