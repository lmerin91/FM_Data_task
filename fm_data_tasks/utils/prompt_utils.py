"""Prompt utils."""
from pathlib import Path

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from transformers import AutoModel, AutoTokenizer, pipeline

from fm_data_tasks.utils.data_utils import DATA2TASK

PREFIXES = {
    "iTunes-Amazon": "Song A is name: Illusion (  feat . Emeli Sand ' © & Professor Green ). Song B is name: Transmission [ feat . Emeli Sand ' © & Professor Green ]. Same Song? No\n\nSong A is name: Praise the sky ( feat . Meghan Trainor ). Song B is name: Praise the sky. Same Song? Yes\n\nSong A is name: Drive it  ( Featuring Jackson T. Brown ). Song B is name: Drive it ( Featuring Jackson T. Brown ) ( Main Version ). Same Song? Yes\n\nSong A is name: Jump Up ( feat . Tyler ). Song B is name: Jump Up ( feat . Tyler ) [ Explicit ]. Same Song? Yes\n\nSong A is name: Fight Song Anthem. genre: Country , Music , Urban Cowboy , Contemporary Country. Song B is name: Fight Song Anthem [ Explicit ]. genre: Country. Same Song? Yes\n\nSong A is name: Over it. Song B is name: Over it [ Clean ]. Same Song? Yes\n\nSong A is name: Original Don ( feat . Nicki Minaj) [Extended]. Song B is name: Original Don ( feat . Nicki Minaj) [Remix]. Same Song? No\n\nSong A is name: Amazing 2.0 ( feat . Justin Bieber ). time: 3:14. Song B is name: Amazing ( feat . Justin Bieber ).  time: 6:14. Same Song? Yes\n\nSong A is name: Run this town ( feat . JT ). Song B is name: Fight the law ( feat . JT ). Same Song? No\n",
    "Beer": "Product A is Beer_Name: Bourbon Barrel Red Oak Ale. Brew_Factory_Name: Big Brewing Company. Style: American Amber / Red Ale. ABV: 7.60%. Product B is Beer_Name: Bourbon Barrel Red Oak Ale. Brew_Factory_Name: Halo Street Brewery. Style: American Amber / Red Ale. ABV: 7.60%. Are Product A and Product B the same? Yes\n\nProduct A is Beer_Name: Red Imperial Red Ale. Brew_Factory_Name: Brew Brewing Company. Style: American Amber / Red Ale. ABV: 5.40%. Product B is Beer_Name: Red Imperial Red Ale - Bourbon Barrel Aged. Brew_Factory_Name: Brew Brewing Company. Style: American Amber / Red Ale. ABV: 5.40%. Are Product A and Product B the same? No\n\nProduct A is Beer_Name: Red Rocket Amber Ale. Brew_Factory_Name: Third Base Sports Bar & Brewery. Style: American Amber / Red Ale. ABV: 6.40%. Product B is Beer_Name: Blue Cat Red Toad Amber Ale. Brew_Factory_Name: Blue Cat Brew Pub. Style: Premium Bitter/ESB. ABV: 5.70%. Are Product A and Product B the same? No\n\nProduct A is Beer_Name: The Gentle Mongoose Holy City. Brew_Factory_Name: Brewing City Brewing. Style: American Amber / Red Ale. ABV: 6.90%. Product B is Beer_Name: Holy City The Gentle Mongoose. Brew_Factory_Name: Holy City Brewing. Style: Amber Ale. ABV: 6.90%. Are Product A and Product B the same? Yes\n\nProduct A is Beer_Name: Freedom Soho Red. Brew_Factory_Name: Freedom Brewery Ltd. Style: American Amber / Red Ale. ABV: 4.70%. Product B is Beer_Name: Freedom Soho Red. Brew_Factory_Name: Freedom. Style: Amber Lager/Vienna. ABV: 4.70%. Are Product A and Product B the same? Yes\n\nProduct A is Beer_Name: Blarney Rock Irish Ale. Brew_Factory_Name: Rockyard Brewing. Style: American Amber / Red Ale. ABV: 6.00%. Product B is Beer_Name: Rockyard Blarney Rock Irish Ale. Brew_Factory_Name: Rockyard Brewing Company. Style: Irish Ale. ABV: -. Are Product A and Product B the same? Yes\n\nProduct A is Beer_Name: Red Rocket Amber Ale. Brew_Factory_Name: Third Base Sports Bar & Brewery. Style: American Amber / Red Ale. ABV: 6.40%. Product B is Beer_Name: Red Duck Amber Ale. Brew_Factory_Name: Purrumbete Brewing. Style: Amber Ale. ABV: 4.80%. Are Product A and Product B the same? No\n",
    "Fodors-Zagats": "Product A is name: ` bamboo garden '. addr: ' 4850 flamingo rd. '. city: ` las vegas '. phone: 702/871 -3262. type: asian. class: 425. Product B is name: ` buzio \\ 's in the rio '. addr: ' 3700 w. flamingo rd. '. city: ` las vegas '. phone: 702-252-7697. type: seafood. class: 658. Are A and B the same? No\n\nProduct A is name: ` le chardonnay '. addr: ' 8284 melrose ave. '. city: ` los angeles '. phone: 213/655 -8880. type: french. class: type: 12. Product B is name: ` le chardonnay ( los angeles ) '. addr: ' 8284 melrose ave. '. city: ` los angeles '. phone: 213-655-8880. type: ` french bistro '. class: type: 12. Are A and B the same? Yes\n\nProduct A is name: lespinasse. addr: ' 2 e. 55th st. '. city: ` new york '. phone: 212/339 -6719. type: american. class: type: 43. Product B is name: ` lespinasse ( new york city ) '. addr: ' 2 e. 55th st. '. city: ` new york city '. phone: 212-339-6719. type: asian. class: type: 43. Are A and B the same? Yes\n\nProduct A is name: ` cafe roma '. addr: ' 3570 las vegas blvd. s '. city: ` las vegas '. phone: 702/731 -7547. type: ` coffee shops/diners '. class: 433. Product B is name: 'em eril \\ 's new orleans fish house '. addr: ' 3799 las vegas blvd. s. '. city: ` las vegas '. phone: 702-891-7374. type: seafood. class: 659. Are A and B the same? No\n\nProduct A is name: ` smith & wollensky '. addr: ' 201 e. 49th st. '. city: ` new york '. phone: 212/753 -1530. type: american. class: 62. Product B is name: ` smith & wollensky '. addr: ' 797 third ave. '. city: ` new york city '. phone: 212-753-1530. type: steakhouses. class: type: 62. Are A and B the same? Yes\n",
    "Walmart-Amazon": "Product A is modelno: va1932wm. Product B is modelno: . Are A and B the Same? No, because modelno: va1932 and modelno: are not the same\n\nProduct A is modelno: hp ce278a. Product B is modelno: ce278ad. Are A and B the Same? No, because modelno: hp ce278a and modelno: ce278ad are not the same\n\nProduct A is modelno: a3l791-03-blu-s. Product B is modelno: a3l980-07-blu-s. Are A and B the Same? No, because modelno: a3l791-03-blu-s and modelno: a3l980-07-blu-s are not the same\n\nProduct A is modelno: va1932wm. Product B is modelno: va705b. Are A and B the Same? No, because modelno: va1932 and modelno: va705b are not the same\n\nProduct A is modelno: ipd2pcbk. Product B is modelno: ipd2pcpu. Are A and B the Same? No, because modelno: ipd2pcbk and modelno: ipd2pcpu are not the same\n\nProduct A is modelno: c9514fn # 14. Product B is modelno:  modelno: c9561fn # 140. Are A and B the Same? No, because modelno: c9514fn # 14 and modelno: c9561fn # 140 are not the same\n\nProduct A is title: sharp electronics xldh259n 160w micro system with ipod dock black. modelno: xldh259n. Product B is title: sharp electronics xldh259n 160w micro system with docking slot for ipod black. modelno: xldh259n. Are A and B the Same? Yes, because modelno: xldh259n and modelno: xldh259 are the same\n\nProduct A is title: iomega 1tb ego desktop usb 2.0 portable hard drive - midnight blue. modelno: 34837. Product B is title: iomega ego helium 320 gb usb 2.0 portable external hard drive 34943. modelno: 34943. Are A and B the Same? No, because modelno: 34837 and modelno: 34943 are not the same\n\nProduct A is title: innovera heavyweight photo paper matte 8-1 2 x 11 50 sheets pack. modelno: 99650. Product B title: innovera 99650 - heavyweight photo paper matte 8-1 2 x 11 50 sheets pack. modelno: . Are A and B the Same? Yes, because modelno: 99650 and Product B title: innovera 99650 are the same\n",
    "DBLP_ACM": {
        "vldb": "Product A is title: mapinfo spatialware : a spatial information server for rdbms. authors: chebel mina. venue: vldb. year: 1998. Product B is title: mapinfo spatialware : a spatial information server for rdbms. authors: chebel mina. venue: very large data bases. year: 1998. Are A and B the same? Yes\n\nProduct A is title: sampling large databases for association rules. authors: hannu toivonen. venue: vldb. year: 1996. Product B is title: sampling large databases for association rules. authors: hannu toivonen. venue: very large data bases. year: 1996. Are A and B the same? Yes\n\nProduct A is title: an ultra highly available dbms. authors: svein-olaf hvasshovd , svein erik bratsberg , øystein torbjørnsen. venue: vldb. year: 2000. Product B is title: an ultra highly available dbms. authors: svein-olaf hvasshovd , svein erik bratsberg , &#216; ystein torbj &#248; rnsen. venue: very large data bases. year: 2000. Are A and B the same? Yes\n\nProduct A is title: e.piphany epicenter technology overview. authors: sridhar ramaswamy. venue: vldb. year: 2000. Product B is title: e.piphany epicenter technology overview. authors: sridhar ramaswamy. venue: very large data bases. year: 2000. Are A and B the same? Yes\n\nProduct A is title: on the costs of multilingualism in database systems. authors: a. kumaran , jayant r. haritsa. venue: vldb. year: 2003. Product B is title: analysis of locking behavior in three real database systems. authors: vigyan singhal , alan jay smith. venue: the vldb journal -- the international journal on very large data bases. year: 1997. Are A and B the same? No\n\nProduct A is title: dynamic multi-resource load balancing in parallel database systems. authors: robert marek , erhard rahm. venue: vldb. year: 1995. Product B is title: parallel database systems 101. authors: jim gray. venue: international conference on management of data. year: 1995. Are A and B the same? No\n\nProduct A is title: processing sliding window multi-joins in continuous queries over data streams. authors: lukasz golab , m. tamer özsu. venue: vldb. year: 2003. Product B is title: processing set expressions over continuous update streams. authors: sumit ganguly , minos garofalakis , rajeev rastogi. venue: international conference on management of data. year: 2003. Are A and B the same? No\n\nProduct A is title: odefs : a file system interface to an object-oriented database. authors: narain h. gehani , william d. roome , h. v. jagadish. venue: vldb. year: 1994. Product B is title: unisql/x unified relational and object-oriented database system. authors: won kim. venue: the vldb journal -- the international journal on very large data bases. year: 1994. Are A and B the same? No\n\nProduct A is title: dwms : data warehouse management system. authors: narendra mohan. venue: vldb. year: 1996. Product B is title: strudel : a web site management system. authors: mary fernandez , daniela florescu , jaewoo kang , alon levy , dan suciu. venue: the vldb journal -- the international journal on very large data bases. year: 1997. Are A and B the same? No\n\nProduct A is title: sampling large databases for association rules. authors: hannu toivonen. venue: vldb. year: 1996. Product A is title: sampling large databases for association rules. authors: hannu toivonen. venue: the vldb journal -- the international journal on very large data bases. year: 1996. Are A and B the same? No\n",
        "sigmod record": "Product A is title: automata theory for xml researchers. authors: frank neven. venue: sigmod record. year: 2002. Product B is title: automata theory for xml researchers. authors: frank neven. venue: acm sigmod record. year: 2002. Are A and B the same? Yes\n\nProduct A is title: reasoning on regular path queries. authors: giuseppe de giacomo , moshe y. vardi , maurizio lenzerini , diego calvanese. venue: sigmod record. year: 2003. Product B is title: reasoning on regular path queries. authors: d. calvanese , g. de giacomo , m. lenzerini , m. y. vardi. venue: acm sigmod record. year: 2003. Are A and B the same? Yes\n\nProduct A is title: 3d geographic network displays. authors: taosong he , stephen g. eick , kenneth c. cox. venue: sigmod record. year: 1996. Product B is title: 3d geographic network displays. authors: kenneth c. cox , stephen g. eick , taosong he. venue: acm sigmod record. year: 1996. Are A and B the same? Yes\n\nProduct A is title: optimizing jan jannink 's implementation of b + - tree deletion. authors: h. olivie , r. maelbrancke. venue: sigmod record. year: 1995. Product B is title: optimizing jan jannink 's implementation of b + - tree deletion. authors: r. maelbrancke , h. olivi &#233;. venue: acm sigmod record. year: 1995. Are A and B the same? Yes\n\nProduct A is title: automata theory for xml researchers. authors: frank neven. venue: sigmod record. year: 2002. Product B is title: automata theory for xml researchers. authors: frank neven. venue: very large databases year: 2002. Are A and B the same? No\n\nProduct A is title: book review column. authors: karl aberer. venue: sigmod record. year: 2002. Product B is title: book review column. authors: karl aberer. venue: acm sigmod record. year: 2002. Are A and B the same? Yes\n\nProduct A is title: book review column. authors: karl aberer. venue: sigmod record. year: 2002. Product B is title: book reviews. authors: karl aberer. venue: acm sigmod record. year: 2002. Are A and B the same? No\n\nProduct A is title: book review column. authors: karl aberer. venue: sigmod record. year: 2003. Product B is title: book review column. authors: karl aberer. venue: acm sigmod record. year: 2003. Are A and B the same? Yes\n\nProduct A is title: book review column. authors: karl aberer. venue: sigmod record. year: 2003. Product B is title: book reviews. authors: karl aberer. venue: acm sigmod record. year: 2003. Are A and B the same? No\n",
        "vldb j": "Product A is title: an architecture to support scalable online personalization on the web. authors: kaushik dutta , debra e. vandermeer , krithi ramamritham , anindya datta , shamkant b. navathe. venue: vldb j.. year: 2001. Product B is title: an architecture to support scalable online personalization on the web. authors: anindya datta , kaushik dutta , debra vandermeer , krithi ramamritham , shamkant b. navathe. venue: the vldb journal -- the international journal on very large data bases. year: 2001. Are A and B the same? Yes\n\nProduct A is title: answering queries using views : a survey. authors: alon y. halevy. venue: vldb j.. year: 2001. Product B is title: answering queries using views : a survey. authors: alon y. halevy. venue: the vldb journal -- the international journal on very large data bases. year: 2001. Are A and B the same? Yes\n\nProduct A is title: efficient schemes for managing multiversionxml documents. authors: shu-yao chien , carlo zaniolo , vassilis j. tsotras. venue: vldb j.. year: 2002. Product B is title: efficient schemes for managing multiversionxml documents. authors: s.-y . chien , v. j. tsotras , c. zaniolo. venue: the vldb journal -- the international journal on very large data bases. year: 2002. Are A and B the same? Yes\n\nProduct A is title: index configuration in object-oriented databases. authors: elisa bertino. venue: vldb j.. year: 1994. Product B is title: a cost model for clustered object-oriented databases. authors: georges gardarin , jean-robert gruser , zhao-hui tang. venue: very large data bases. year: 1995. Are A and B the same? No\n\nProduct A is title: incremental computation and maintenance of temporal aggregates. authors: jun yang , jennifer widom. venue: vldb j.. year: 2003. Product B is title: incremental maintenance of recursive views using relational calculus/sql. authors: guozhu dong , jianwen su. venue: acm sigmod record. year: 2000. Are A and B the same? No\n\nProduct A is title: index nesting - an efficient approach to indexing in object-oriented databases. authors: jiawei han , beng chin ooi , hongjun lu , kian-lee tan. venue: vldb j.. year: 1996. Product B is title: converting relational to object-oriented databases. authors: joseph fong. venue: acm sigmod record. year: 1997. Are A and B the same? No\n\nProduct A is title: concurrency control in hierarchical multidatabase systems. authors: henry f. korth , abraham silberschatz , sharad mehrotra. venue: vldb j.. year: 1997. Product B is title: dynamic load balancing in hierarchical parallel database systems. authors: luc bouganim , daniela florescu , patrick valduriez. venue: very large data bases. year: 1996. Are A and B the same? No\n\nProduct A is title: instance-based attribute identification in database integration. authors: roger h. l. chiang , ee-peng lim , chua eng huang cecil. venue: vldb j.. year: 2003. Product B is title: a case-based approach to information integration. authors: maurizio panti , luca spalazzi , alberto giretti. venue: very large data bases. year: 2000. Are A and B the same? No\n\nProduct A is title: answering queries using views : a survey. authors: alon y. halevy. venue: vldb j.. year: 2001. Product A is title: answering queries using views : a survey. authors: alon y. halevy. venue: international conference on management of data year: 2001.. Are A and B the same? No\n",
        "acm trans . database syst .": "Product A is title: tail recursion elimination in deductive databases. authors: kenneth a. ross. venue: acm trans . database syst .. year: 1996. Product B is title: tail recursion elimination in deductive databases. authors: kenneth a. ross. venue: acm transactions on database systems ( tods ). year: 1996. Are A and B the same? Yes\n\nProduct A is title: disjunctive datalog. authors: heikki mannila , thomas eiter , georg gottlob. venue: acm trans . database syst .. year: 1997. Product B is title: disjunctive datalog. authors: thomas eiter , georg gottlob , heikki mannila. venue: acm transactions on database systems ( tods ). year: 1997. Are A and B the same? Yes\n\nProduct A is title: space optimization in deductive databases. authors: s. sudarshan , divesh srivastava , raghu ramakrishnan , jeffrey f. naughton. venue: acm trans . database syst .. year: 1995. Product B is title: introduction to constraint databases. authors: bart kuijpers. venue: acm sigmod record. year: 2002. Are A and B the same? No\n\nProduct A is title: solving satisfiability and implication problems in database systems. authors: sha guo , mark allen weiss , wei sun. venue: acm trans . database syst .. year: 1996. Product B is title: temporal database system implementations. authors: michael h. b &#246; hlen. venue: acm sigmod record. year: 1995. Are A and B the same? No\n\nProduct A is title: disjunctive datalog. authors: heikki mannila , thomas eiter , georg gottlob. venue: acm trans . database syst .. year: 1997. Product B is title: disjunctive datalog. authors: heikki mannila , thomas eiter , georg gottlob. venue: acm sigmod record. year: 1997. Are A and B the same? No\n",
        "sigmod conference": "Product A is title: javax.xxl : a prototype for a library of query processing algorithms. authors: bernhard seeger , jens-peter dittrich , jochen van den bercken. venue: sigmod conference. year: 2000. Product B is title: javax.xxl : a prototype for a library of query processing algorithms. authors: jochen van den bercken , jens-peter dittrich , bernhard seeger. venue: international conference on management of data. year: 2000. Are A and B the same? Yes\n\nProduct A is title: orthogonal optimization of subqueries and aggregation. authors: milind joshi , césar a. galindo-legaria. venue: sigmod conference. year: 2001. Product B is title: orthogonal optimization of subqueries and aggregation. authors: c &#233; sar galindo-legaria , milind joshi. venue: international conference on management of data. year: 2001. Are A and B the same? Yes\n\nProduct A is title: from structured documents to novel query facilities. authors: sophie cluet , michel scholl , serge abiteboul , vassilis christophides. venue: sigmod conference. year: 1994. Product B is title: from structured documents to novel query facilities. authors: v. christophides , s. abiteboul , s. cluet , m. scholl. venue: international conference on management of data. year: 1994. Are A and B the same? Yes\n\nProduct A is title: the naos system. authors: christine collet , thierry coupaye. venue: sigmod conference. year: 1995. Product B is title: the naos system. authors: c. collet , t. coupaye. venue: international conference on management of data. year: 1995. Are A and B the same? Yes\n\nProduct A is title: highly concurrent cache consistency for indices in client-server database systems. authors: michael j. carey , markos zaharioudakis. venue: sigmod conference. year: 1997. Product B is title: index concurrency control in firm real-time database systems. authors: brajesh goyal , jayant r. haritsa , s. seshadri , v. srinivasan. venue: very large data bases. year: 1995. Are A and B the same? No\n\nProduct A is title: selectivity estimation in spatial databases. authors: viswanath poosala , sridhar ramaswamy , swarup acharya. venue: sigmod conference. year: 1999. Product B is title: selectivity estimation for spatio-temporal queries to moving objects. authors: yong-jin choi , chin-wan chung. venue: international conference on management of data. year: 2002. Are A and B the same? No\n\nProduct A is title: the need for distributed asynchronous transactions. authors: lyman do , prabhu ram , pamela drew. venue: sigmod conference. year: 1999. Product B is title: atomicity versus anonymity : distributed transactions for electronic commerce. authors: j. d. tygar. venue: very large data bases. year: 1998. Are A and B the same? No, because Product A venue: sigmod conference and Product B venue: very large data bases are not the same\n\nProduct A is title: query optimization in compressed database systems. authors: zhiyuan chen , flip korn , johannes gehrke. venue: sigmod conference. year: 2001. Product B is title: query caching and optimization in distributed mediator systems. authors: s. adali , k. s. candan , y. papakonstantinou , v. s. subrahmanian. venue: the vldb journal -- the international journal on very large data bases. year: 1996. Are A and B the same? No\n\nProduct A is title: orthogonal optimization of subqueries and aggregation. authors: milind joshi , césar a. galindo-legaria. venue: sigmod conference. year: 2001. Product B is title: orthogonal optimization of subqueries and aggregation. authors: milind joshi , césar a. galindo-legaria. venue: very large databases. year: 2001. Are A and B the same? No\n",
    },
    "Buy": "name: Transcend 8GB Compact Flash Card (133x) - TS8GCF133. description: Transcend 8GB CompactFlash Card (133x). manufacturer? TRANSCEND INFORMATION\n\nname: LG 42LG30 42' LCD TV. description: LG 42LG30 42' LCD HDTV - 12,000:1 Dynamic Contrast Ratio - Invisible Speaker. manufacturer? LG Electronics\n\nname: Speck Products SeeThru Case for Apple MacBook Air - MBA-PNK-SEE. description: Plastic - Pink. manufacturer? Speck Products\n\nname: Peerless Universal Tilt Wall Mount. description: Peerless Smart Mount ST660P Universal Tilt Wall Mount for 37' to 60' Screens (Black) up to 200lbs. manufacturer? Peerless\n\nname: Apple Time Capsule Network Hard Drive - MB277LL/A. description: 1TB - Type A USB. manufacturer? Apple\n\nname: Sirius SUPH1 Sirius Universal Home Kit. description: Sirius Satellite Radio Receiver. manufacturer? Sirius\n\nname: OmniMount TV Top Shelf Mount. description: OmniMount CCH1B Set-Top Center-Channel Shelf. manufacturer? OMNIMOUNT SYSTEMS, INC\n\nname: Monster Cable iFreePlay Cordless Headphone - AI SH HPHONE. description: Connectivity: Wireless - Stereo - Behind-the-neck. manufacturer? Monster\n\nname: Pure Digital Flip Mino Digital Camcorder - F360B. description: Flip Video Mino 60 min Black. manufacturer? Pure Digital Technol\n\nname: Elgato EyeTV Hybrid Analog/Digital TV Tuner Stick - 10020630. description: Elgato EyeTV Hybrid TV Tuner Stick for Analog and HDTV Reception - USB. manufacturer? ELGATO SYSTEMS\n",
    "Restaurant": "name: oceana. addr: 55 e. 54th st.. phone: 212/759-5941. type: seafood. city? new york\n\nname: oceana. addr: 55 e. 54th st.. phone: 212-759-5941. type: seafood. city? new york city\n",
    "Hospital": {
        "EmergencyService": "Is there a spelling error in: yes? No, it doesn't have an x.\n\nIs there a spelling error in: yes? No, it doesn't have an x.\n\nIs there a spelling error in: yex? Yes, it has an x.\n",
        "City": "Is there a spelling error in: birmingham? No, it doesn't have an x.\n\nIs there a spelling error in: sheffield? No, it doesn't have an x.\n\nIs there a spelling error in: birminghxm? Yes, it has an x.\n",
        "Score": "Is there a spelling error in: nan? No, it doesn't have an x.\n\nIs there a spelling error in: nan? No, it doesn't have an x.\n\nIs there a spelling error in: 1xx%? Yes, it has an x.\n",
        "HospitalType": "Is there a spelling error in: acute care hospitals? No, it doesn't have an x.\n\nIs there a spelling error in: acute care hospitals? No, it doesn't have an x.\n\nIs there a spelling error in: acutexcarexhospitals? Yes, it has an x.\n",
        "CountyName": "Is there a spelling error in: calhoun? No, it doesn't have an x.\n\nIs there a spelling error in: marion? No, it doesn't have an x.\n\nIs there a spelling error in: xhambers? Yes, it has an x.\n",
        "MeasureName": "Is there a spelling error in: pneumonia patients given the most appropriate initial antibiotic(s)? No, it doesn't have an x.\n\nIs there a spelling error in: heart attack patients given aspirin at discharge? No, it doesn't have an x.\n\nIs there a spelling error in: allxheartxsurgeryxpatientsxwhosexbloodxsugarx(bloodxglucose)xisxkeptxunderxgoodxcontrolxinxthexdaysxrightxafterxsurgery? Yes, it has an x.\n",
        "HospitalName": "Is there a spelling error in: fayette medical center? No, it doesn't have an x.\n\nIs there a spelling error in: huntsville hospital? No, it doesn't have an x.\n\nIs there a spelling error in: medixal xenter enterprise? Yes, it has an x.\n",
        "Condition": "Is there a spelling error in: heart attack? No, it doesn't have an x.\n\nIs there a spelling error in: surgical infection prevention? No, it doesn't have an x.\n\nIs there a spelling error in: hearx axxack? Yes, it has an x.\n",
        "Stateavg": "Is there a spelling error in: al_pn-4? No, it doesn't have an x.\n\nIs there a spelling error in: al_ami-3? No, it doesn't have an x.\n\nIs there a spelling error in: xax-1? Yes, it has an x.\n",
        "MeasureCode": "Is there a spelling error in: ami-7a? No, it doesn't have an x.\n\nIs there a spelling error in: scip-inf-2? No, it doesn't have an x.\n\nIs there a spelling error in: xax-1? Yes, it has an x.\n",
        "ZipCode": "Is there a spelling error in: 35640? No, it doesn't have an x.\n\nIs there a spelling error in: 36302? No, it doesn't have an x.\n\nIs there a spelling error in: x6x05? Yes, it has an x.\n",
        "Sample": "Is there a spelling error in: 13 patients? No, it doesn't have an x.\n\nIs there a spelling error in: 97 patients? No, it doesn't have an x.\n\nIs there a spelling error in: 4 xatients? Yes, it has an x.\n",
        "HospitalOwner": "Is there a spelling error in: proprietary? No, it doesn't have an x.\n\nIs there a spelling error in: government - hospital district or authority? No, it doesn't have an x.\n\nIs there a spelling error in: goverxmext - hospital district or authority? Yes, it has an x.\n",
        "Address1": "Is there a spelling error in: 126 hospital ave? No, it doesn't have an x.\n\nIs there a spelling error in: 2000 pepperell parkway? No, it doesn't have an x.\n\nIs there a spelling error in: 400xnxedwardsxstreet? Yes, it has an x.\n",
        "ProviderNumber": "Is there a spelling error in: 10005? No, it doesn't have an x.\n\nIs there a spelling error in: 10055? No, it doesn't have an x.\n\nIs there a spelling error in: 1xx32? Yes, it has an x.\n",
        "State": "Is there a spelling error in: al? No, it doesn't have an x.\n\nIs there a spelling error in: al? No, it doesn't have an x.\n\nIs there a spelling error in: ax? Yes, it has an x.\n",
        "PhoneNumber": "Is there a spelling error in: 3343762205? No, it doesn't have an x.\n\nIs there a spelling error in: 2562651000? No, it doesn't have an x.\n\nIs there a spelling error in: 2568453x50? Yes, it has an x.\n",
    },
}


def get_manual_prompt(data_name: str):
    """Get manual prompt for data name."""
    if data_name not in set([Path(pth).name for pth in DATA2TASK.keys()]):
        raise ValueError(f"{data_name} not recognized for prompts")
    return PREFIXES[data_name]


def get_validation_prompt(validation_path: str, num_examples: int = 10):
    """Get prompt from validation errors."""
    return get_cluster_k_prompts(
        df=pd.read_feather(validation_path),
        num_exs=num_examples,
        model_name="sentence-transformers/sentence-t5-base",
        pipeline_name="st",
    )


def setup_hf_pipeline(model_name: str, tokenizer_name: str):
    """Get HF embedding pipeline."""
    model = AutoModel.from_pretrained(model_name)
    tok = AutoTokenizer.from_pretrained(tokenizer_name)
    pipe = pipeline("feature-extraction", model=model, tokenizer=tok)
    return pipe


def extract_hf_features(errors: pd.DataFrame, pipeline: pipeline, text_col="text"):
    """Extract HF features."""
    feats = pipeline(errors[text_col].tolist())
    return feats


def setup_st_pipeline(model_name: str):
    """Get Sentence Transformer pipeline."""
    pipeline = SentenceTransformer(model_name)
    return pipeline


def extract_st_features(
    errors: pd.DataFrame, model: SentenceTransformer, text_col="text"
):
    """Extract ST features."""
    feats = model.encode(errors[text_col].tolist())
    return feats


def get_cluster_samples(df: pd.DataFrame, embs: np.ndarray, num_clusters=10):
    """Cluster embeddings and sample one point from each."""
    kmeans = KMeans(n_clusters=num_clusters, random_state=1234).fit(embs)
    # Get cluster labels for each sample
    labels = kmeans.labels_
    df.loc[:, "cluster_labels"] = labels
    # Sample one per cluster
    sample = df.groupby("cluster_labels").apply(lambda df: df.sample(1))
    return sample


def get_cluster_k_prompts(
    df: pd.DataFrame,
    num_exs: int = 10,
    model_name: str = "sentence-transformers/sentence-t5-base",
    pipeline_name: str = "st",
):
    """Generate prompt from cluster of data errors."""
    errors = df[
        df["label_str"].str.lower().str.strip() != df["preds"].str.lower().str.strip()
    ]
    if pipeline_name == "hf":
        pipeline = setup_hf_pipeline(model_name, tokenizer_name=model_name)
        embs = extract_hf_features(errors, pipeline)
    elif pipeline_name == "st":
        pipeline = setup_st_pipeline(model_name)
        embs = extract_st_features(errors, pipeline)
    else:
        raise ValueError("pipeline_name must be either hf or st")
    samples = get_cluster_samples(
        errors, embs, num_clusters=min(errors.shape[0], num_exs)
    )
    new_prompt = (
        "\n\n".join(
            [
                (txt + label).strip()
                for txt, label in zip(samples["text"], samples["label_str"])
            ]
        )
        + "\n"
    )
    return new_prompt
