#!/usr/bin/env python3
"""Expand CPT database from ~2,869 to 5,000+ codes."""

import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cpt_database.json")

def mc(code, desc, cat, subcat, spec, rvu=1.0, gp=0, bil=False, addon=False,
       cosurg=False, asst=False, tier=3, fam="unclassified", est=True):
    return {
        "code": str(code), "description": desc, "category": cat, "subcategory": subcat,
        "specialty": spec, "work_rvu": rvu, "global_period_days": gp,
        "bilateral_eligible": bil, "addon_code": addon, "cosurgeon_eligible": cosurg,
        "assistant_allowed": asst, "hierarchy_tier": tier, "code_family": fam,
        "inclusive_of": [], "never_primary_with": [], "typical_modifiers": [],
        "estimated": est
    }

def gen_all():
    c = []
    S, F, O = "Surgery", "fracture_care", "orthopedics"
    
    # === 1. ORTHOPEDIC FRACTURES (~300 codes) ===
    # Clavicle 23500-23550
    fx = [
        ("23500","Closed tx clavicular fx; without manipulation",2.70),
        ("23505","Closed tx clavicular fx; with manipulation",4.22),
        ("23515","Open tx clavicular fx, includes internal fixation",10.88),
        ("23520","Closed tx sternoclavicular dislocation; without manipulation",3.18),
        ("23525","Closed tx sternoclavicular dislocation; with manipulation",4.52),
        ("23530","Open tx sternoclavicular dislocation, acute or chronic",9.85),
        ("23532","Open tx sternoclavicular dislocation; with fascial graft",11.22),
        ("23540","Closed tx acromioclavicular dislocation; without manipulation",2.82),
        ("23545","Closed tx acromioclavicular dislocation; with manipulation",4.33),
        ("23550","Open tx acromioclavicular dislocation, acute or chronic",10.25),
    ]
    for code,desc,rvu in fx:
        asst = rvu > 8
        c.append(mc(code,desc,S,F,O,rvu,90,True,asst=asst))
    
    # Scapula
    for code,desc,rvu in [("23570","Closed tx scapular fx; without manipulation",2.55),
        ("23575","Closed tx scapular fx; with manipulation",4.15),
        ("23585","Open tx scapular fx includes internal fixation",12.55)]:
        c.append(mc(code,desc,S,F,O,rvu,90,True,asst=rvu>8))
    
    # Proximal humerus
    for code,desc,rvu in [
        ("23600","Closed tx proximal humeral fx; without manipulation",3.15),
        ("23605","Closed tx proximal humeral fx; with manipulation",5.85),
        ("23615","Open tx proximal humeral fx, includes internal fixation",14.25),
        ("23616","Open tx proximal humeral fx; with prosthetic replacement",18.55),
        ("23620","Closed tx greater humeral tuberosity fx; without manipulation",2.55),
        ("23625","Closed tx greater humeral tuberosity fx; with manipulation",4.25),
        ("23630","Open tx greater humeral tuberosity fx, includes internal fixation",9.85)]:
        c.append(mc(code,desc,S,F,O,rvu,90,True,asst=rvu>8))
    
    # Humerus shaft 24500-24586
    hum = [
        ("24500","Closed tx humeral shaft fx; without manipulation",3.36),
        ("24505","Closed tx humeral shaft fx; with manipulation",5.89),
        ("24515","Open tx humeral shaft fx with plate/screws",13.75),
        ("24516","Tx humeral shaft fx with intramedullary implant",12.88),
        ("24530","Closed tx supracondylar humeral fx; without manipulation",3.60),
        ("24535","Closed tx supracondylar humeral fx; with manipulation",6.43),
        ("24538","Percutaneous skeletal fixation supracondylar humeral fx",8.55),
        ("24545","Open tx humeral supracondylar fx, includes internal fixation",14.22),
        ("24546","Open tx humeral supracondylar fx; with intercondylar extension",16.50),
        ("24560","Closed tx humeral epicondylar fx; without manipulation",2.95),
        ("24565","Closed tx humeral epicondylar fx; with manipulation",4.88),
        ("24566","Percutaneous skeletal fixation humeral epicondylar fx",7.25),
        ("24575","Open tx humeral epicondylar fx, includes internal fixation",10.85),
        ("24576","Closed tx humeral condylar fx; without manipulation",3.15),
        ("24577","Closed tx humeral condylar fx; with manipulation",5.22),
        ("24579","Open tx humeral condylar fx, includes internal fixation",12.45),
        ("24582","Percutaneous skeletal fixation humeral condylar fx",8.10),
        ("24586","Open tx periarticular fx and/or dislocation of elbow",16.88),
    ]
    for code,desc,rvu in hum:
        c.append(mc(code,desc,S,F,O,rvu,90,True,asst=rvu>8,cosurg=rvu>16))
    
    # Elbow dislocations
    for code,desc,rvu in [
        ("24600","Closed tx elbow dislocation; without anesthesia",3.85),
        ("24605","Closed tx elbow dislocation; requiring anesthesia",5.55),
        ("24615","Open tx acute or chronic elbow dislocation",10.85),
        ("24620","Closed tx Monteggia fx dislocation with manipulation",6.55),
        ("24635","Open tx Monteggia fx dislocation, includes internal fixation",13.85),
        ("24650","Closed tx radial head or neck fx; without manipulation",2.45),
        ("24655","Closed tx radial head or neck fx; with manipulation",4.15),
        ("24665","Open tx radial head or neck fx, includes internal fixation",9.55),
        ("24666","Open tx radial head fx; with prosthetic replacement",12.25),
        ("24670","Closed tx ulnar fx proximal end; without manipulation",2.65),
        ("24675","Closed tx ulnar fx proximal end; with manipulation",4.55),
        ("24685","Open tx ulnar fx proximal end, includes internal fixation",10.25)]:
        c.append(mc(code,desc,S,F,O,rvu,90,True,asst=rvu>8))
    
    # Radius/Ulna 25500-25609
    ru = [
        ("25500","Closed tx radial shaft fx; without manipulation",2.80),
        ("25505","Closed tx radial shaft fx; with manipulation",4.75),
        ("25515","Open tx radial shaft fx, includes internal fixation",10.50),
        ("25520","Closed tx radial shaft fx and distal radioulnar joint dislocation (Galeazzi)",5.85),
        ("25525","Open tx radial shaft fx with internal fixation and closed tx DRUJ (Galeazzi)",12.15),
        ("25526","Open tx radial shaft fx with internal fixation and open tx DRUJ (Galeazzi)",14.55),
        ("25530","Closed tx ulnar shaft fx; without manipulation",2.65),
        ("25535","Closed tx ulnar shaft fx; with manipulation",4.50),
        ("25545","Open tx ulnar shaft fx, includes internal fixation",10.22),
        ("25560","Closed tx radial and ulnar shaft fx; without manipulation",3.45),
        ("25565","Closed tx radial and ulnar shaft fx; with manipulation",5.95),
        ("25574","Open tx radial AND ulnar shaft fx; of radius OR ulna",11.85),
        ("25575","Open tx radial AND ulnar shaft fx; of radius AND ulna",14.90),
        ("25600","Closed tx distal radial fx (Colles/Smith); without manipulation",2.95),
        ("25605","Closed tx distal radial fx (Colles/Smith); with manipulation",5.05),
        ("25606","Percutaneous skeletal fixation of distal radial fx",8.45),
        ("25607","Open tx distal radial extra-articular fx, with internal fixation",11.22),
        ("25608","Open tx distal radial intra-articular fx; 2 fragments",12.88),
        ("25609","Open tx distal radial intra-articular fx; 3+ fragments",14.55),
    ]
    for code,desc,rvu in ru:
        c.append(mc(code,desc,S,F,O,rvu,90,True,asst=rvu>8))
    
    # Wrist (carpal) fractures
    for code,desc,rvu in [
        ("25622","Closed tx carpal scaphoid fx; without manipulation",2.55),
        ("25624","Closed tx carpal scaphoid fx; with manipulation",4.25),
        ("25628","Open tx carpal scaphoid fx, includes internal fixation",9.15),
        ("25630","Closed tx carpal bone fx (excl scaphoid); without manipulation",2.15),
        ("25635","Closed tx carpal bone fx (excl scaphoid); with manipulation",3.55),
        ("25645","Open tx carpal bone fx (other than scaphoid), each bone",8.25)]:
        c.append(mc(code,desc,S,F,O,rvu,90,True,asst=rvu>8))
    
    # Hand/Finger 26600-26785
    hf = [
        ("26600","Closed tx metacarpal fx, single; without manipulation, each",2.15),
        ("26605","Closed tx metacarpal fx, single; with manipulation, each",3.55),
        ("26607","Closed tx metacarpal fx, with external fixation, each",5.22),
        ("26608","Percutaneous skeletal fixation metacarpal fx, each",6.15),
        ("26615","Open tx metacarpal fx, includes internal fixation, each",8.25),
        ("26641","Closed tx carpometacarpal dislocation, thumb, with manipulation",4.85),
        ("26645","Closed tx carpometacarpal fx dislocation, thumb (Bennett)",5.15),
        ("26650","Open tx Bennett fx, with internal fixation",9.25),
        ("26665","Open tx carpometacarpal fx dislocation, with internal fixation",9.85),
        ("26670","Closed tx CMC dislocation, other than thumb; without manipulation",2.55),
        ("26675","Closed tx CMC dislocation, other than thumb; with manipulation",3.95),
        ("26676","Percutaneous skeletal fixation CMC dislocation",5.88),
        ("26685","Open tx CMC dislocation, includes internal fixation",8.65),
        ("26700","Closed tx MCP dislocation; without anesthesia",3.15),
        ("26705","Closed tx MCP dislocation; requiring anesthesia",4.55),
        ("26706","Percutaneous skeletal fixation MCP dislocation",5.75),
        ("26715","Open tx MCP dislocation, includes internal fixation",7.85),
        ("26720","Closed tx phalangeal shaft fx, prox/mid; without manipulation",1.85),
        ("26725","Closed tx phalangeal shaft fx, prox/mid; with manipulation",3.25),
        ("26727","Percutaneous skeletal fixation phalangeal shaft fx",5.55),
        ("26735","Open tx phalangeal shaft fx, includes internal fixation",7.45),
        ("26740","Closed tx articular fx MCP/IP joint; without manipulation",2.05),
        ("26742","Closed tx articular fx MCP/IP joint; with manipulation",3.45),
        ("26746","Open tx articular fx MCP/IP joint, includes internal fixation",7.95),
        ("26750","Closed tx distal phalangeal fx; without manipulation",1.55),
        ("26755","Closed tx distal phalangeal fx; with manipulation",2.65),
        ("26756","Percutaneous skeletal fixation distal phalangeal fx",4.35),
        ("26765","Open tx distal phalangeal fx, includes internal fixation",6.25),
        ("26770","Closed tx IP joint dislocation; without anesthesia",2.45),
        ("26775","Closed tx IP joint dislocation; requiring anesthesia",3.65),
        ("26776","Percutaneous skeletal fixation IP joint dislocation",5.15),
        ("26785","Open tx IP joint dislocation, includes internal fixation",7.25),
    ]
    for code,desc,rvu in hf:
        c.append(mc(code,desc,S,F,O,rvu,90,True,asst=rvu>8))
    
    # Pelvis 27193-27248
    pelv = [
        ("27193","Closed tx pelvic ring fx; without manipulation",3.25,False),
        ("27194","Closed tx pelvic ring fx; with manipulation",6.55,False),
        ("27197","Closed tx posterior pelvic ring fx; without manipulation",4.15,False),
        ("27198","Closed tx posterior pelvic ring fx; with manipulation",7.85,False),
        ("27200","Closed tx coccygeal fx",1.85,False),
        ("27202","Open tx coccygeal fx",5.55,False),
        ("27215","Open tx iliac spine/wing fx, includes internal fixation",12.85,False),
        ("27216","Percutaneous skeletal fixation posterior pelvic bone fx",14.25,False),
        ("27217","Open tx anterior pelvic bone fx, includes internal fixation",16.55,False),
        ("27218","Open tx posterior pelvic bone fx, includes internal fixation",18.85,False),
        ("27220","Closed tx acetabulum fx; without manipulation",3.85,False),
        ("27222","Closed tx acetabulum fx; with manipulation",7.25,False),
        ("27226","Open tx posterior/anterior acetabular wall fx",20.55,False),
        ("27227","Open tx acetabular fx involving single column",22.85,False),
        ("27228","Open tx acetabular fx involving both columns",26.50,False),
        ("27230","Closed tx femoral neck fx; without manipulation",3.55,False),
        ("27232","Closed tx femoral neck fx; with manipulation",6.85,False),
        ("27235","Percutaneous skeletal fixation femoral neck fx",10.55,False),
        ("27236","Open tx femoral neck fx, internal fixation or prosthetic replacement",15.85,False),
        ("27238","Closed tx intertrochanteric femoral fx; without manipulation",3.75,False),
        ("27240","Closed tx intertrochanteric femoral fx; with manipulation",7.15,False),
        ("27244","Tx intertrochanteric femoral fx; with plate/screw implant",14.25,False),
        ("27245","Tx intertrochanteric femoral fx; with intramedullary implant",14.85,False),
        ("27246","Closed tx greater trochanteric fx, without manipulation",2.65,False),
        ("27248","Open tx greater trochanteric fx, includes internal fixation",9.85,False),
        ("27250","Closed tx hip dislocation; without anesthesia",4.55,False),
        ("27252","Closed tx hip dislocation; requiring anesthesia",7.25,False),
        ("27253","Open tx hip dislocation, without internal fixation",12.55,False),
        ("27254","Open tx hip dislocation with acetabular wall and femoral head fx",22.85,False),
    ]
    for item in pelv:
        code,desc,rvu,bil = item
        c.append(mc(code,desc,S,F,O,rvu,90,bil,asst=rvu>8,cosurg=rvu>16))
    
    # Femur 27500-27514
    fem = [
        ("27500","Closed tx femoral shaft fx, without manipulation",4.15),
        ("27501","Closed tx supracondylar femoral fx without intercondylar extension",4.25),
        ("27502","Closed tx femoral shaft fx, with manipulation",7.55),
        ("27503","Closed tx supracondylar femoral fx with manipulation",7.85),
        ("27506","Open tx femoral shaft fx with intramedullary implant",16.55),
        ("27507","Open tx femoral shaft fx with plate/screws",15.85),
        ("27508","Closed tx distal femoral condyle fx; without manipulation",3.85),
        ("27509","Percutaneous skeletal fixation femoral supracondylar fx",11.25),
        ("27510","Closed tx distal femoral condyle fx; with manipulation",6.55),
        ("27511","Open tx femoral supracondylar fx without intercondylar extension",17.25),
        ("27513","Open tx femoral supracondylar fx with intercondylar extension",19.85),
        ("27514","Open tx distal femoral condyle fx, includes internal fixation",16.25),
    ]
    for code,desc,rvu in fem:
        c.append(mc(code,desc,S,F,O,rvu,90,False,asst=rvu>8,cosurg=rvu>16))
    
    # Patella and tibial plateau
    for code,desc,rvu in [
        ("27520","Closed tx patellar fx, without manipulation",2.85),
        ("27524","Open tx patellar fx, with internal fixation",11.25),
        ("27530","Closed tx tibial plateau fx; without manipulation",3.45),
        ("27532","Closed tx tibial plateau fx; with skeletal traction",6.85),
        ("27535","Open tx tibial plateau fx; unicondylar",14.55),
        ("27536","Open tx tibial plateau fx; bicondylar",18.85)]:
        c.append(mc(code,desc,S,F,O,rvu,90,True,asst=rvu>8,cosurg=rvu>16))
    
    # Knee dislocations
    for code,desc,rvu in [
        ("27550","Closed tx knee dislocation; without anesthesia",4.25),
        ("27552","Closed tx knee dislocation; requiring anesthesia",6.55),
        ("27556","Open tx knee dislocation; without ligament repair",14.25),
        ("27557","Open tx knee dislocation; with ligament repair",18.85),
        ("27558","Open tx knee dislocation; with ligament and meniscal repair",22.15)]:
        c.append(mc(code,desc,S,F,O,rvu,90,True,asst=rvu>8,cosurg=rvu>16))
    
    # Tibia/Fibula 27750-27828
    tf = [
        ("27750","Closed tx tibial shaft fx; without manipulation",3.55),
        ("27752","Closed tx tibial shaft fx; with manipulation",6.25),
        ("27756","Percutaneous skeletal fixation tibial shaft fx",9.85),
        ("27758","Open tx tibial shaft fx with plate/screws",14.25),
        ("27759","Tx tibial shaft fx by intramedullary implant",13.85),
        ("27760","Closed tx medial malleolus fx; without manipulation",2.85),
        ("27762","Closed tx medial malleolus fx; with manipulation",4.55),
        ("27766","Open tx medial malleolus fx, includes internal fixation",9.55),
        ("27780","Closed tx proximal fibula or shaft fx; without manipulation",2.25),
        ("27781","Closed tx proximal fibula or shaft fx; with manipulation",3.85),
        ("27784","Open tx proximal fibula or shaft fx, includes internal fixation",8.55),
        ("27786","Closed tx distal fibular fx (lateral malleolus); without manipulation",2.55),
        ("27788","Closed tx distal fibular fx (lateral malleolus); with manipulation",4.15),
        ("27792","Open tx distal fibular fx, includes internal fixation",9.25),
        ("27808","Closed tx bimalleolar ankle fx; without manipulation",3.55),
        ("27810","Closed tx bimalleolar ankle fx; with manipulation",5.85),
        ("27814","Open tx bimalleolar ankle fx, includes internal fixation",13.55),
        ("27816","Closed tx trimalleolar ankle fx; without manipulation",3.85),
        ("27818","Closed tx trimalleolar ankle fx; with manipulation",6.25),
        ("27822","Open tx trimalleolar ankle fx; without posterior lip fixation",14.85),
        ("27823","Open tx trimalleolar ankle fx; with posterior lip fixation",16.55),
        ("27824","Closed tx pilon fx; without manipulation",4.15),
        ("27825","Closed tx pilon fx; with manipulation",7.55),
        ("27826","Open tx pilon fx; fibula only",13.25),
        ("27827","Open tx pilon fx; tibia only",17.85),
        ("27828","Open tx pilon fx; tibia and fibula",20.55),
        ("27830","Closed tx proximal tibiofibular dislocation; without anesthesia",2.85),
        ("27831","Closed tx proximal tibiofibular dislocation; requiring anesthesia",4.25),
        ("27832","Open tx proximal tibiofibular dislocation",8.55),
        ("27840","Closed tx ankle dislocation; without anesthesia",3.55),
        ("27842","Closed tx ankle dislocation; requiring anesthesia",5.85),
        ("27846","Open tx ankle dislocation; without internal fixation",9.55),
        ("27848","Open tx ankle dislocation; with internal fixation",12.85),
    ]
    for code,desc,rvu in tf:
        c.append(mc(code,desc,S,F,O,rvu,90,True,asst=rvu>8,cosurg=rvu>16))
    
    # Foot 28400-28675
    foot = [
        ("28400","Closed tx calcaneal fx; without manipulation",2.85),
        ("28405","Closed tx calcaneal fx; with manipulation",5.15),
        ("28406","Percutaneous skeletal fixation calcaneal fx",9.55),
        ("28415","Open tx calcaneal fx, includes internal fixation",15.25),
        ("28420","Closed tx talus fx; without manipulation",2.95),
        ("28430","Closed tx talus fx; with manipulation",5.35),
        ("28435","Open tx talus fx, includes internal fixation",13.85),
        ("28436","Percutaneous skeletal fixation talus fx",9.25),
        ("28440","Closed tx tarsal bone fx (excl talus/calcaneus); without manipulation",2.15),
        ("28445","Open tx talus fx with bone graft",14.55),
        ("28446","Open tx tarsal bone fx (excl talus/calcaneus)",10.55),
        ("28450","Closed tx tarsal bone dislocation; without anesthesia",2.55),
        ("28455","Closed tx tarsal bone dislocation; requiring anesthesia",4.15),
        ("28456","Percutaneous skeletal fixation tarsal bone dislocation",6.85),
        ("28465","Open tx tarsal bone dislocation, includes internal fixation",10.25),
        ("28470","Closed tx metatarsal fx; without manipulation, each",1.85),
        ("28475","Closed tx metatarsal fx; with manipulation, each",3.25),
        ("28476","Percutaneous skeletal fixation metatarsal fx",5.55),
        ("28485","Open tx metatarsal fx, includes internal fixation, each",7.85),
        ("28490","Closed tx great toe phalanx fx; without manipulation",1.55),
        ("28495","Closed tx great toe phalanx fx; with manipulation",2.65),
        ("28496","Percutaneous skeletal fixation great toe phalanx fx",4.55),
        ("28505","Open tx great toe phalanx fx, includes internal fixation",6.25),
        ("28510","Closed tx phalanx fx, other than great toe; without manipulation",1.25),
        ("28515","Closed tx phalanx fx, other than great toe; with manipulation",2.35),
        ("28525","Open tx phalanx fx, other than great toe",5.85),
        ("28530","Closed tx sesamoid fx",1.55),
        ("28531","Open tx sesamoid fx",5.25),
        ("28540","Closed tx tarsal dislocation; without anesthesia",2.55),
        ("28545","Closed tx tarsal dislocation; requiring anesthesia",4.25),
        ("28555","Open tx tarsal dislocation, includes internal fixation",10.85),
        ("28570","Closed tx talonavicular dislocation; without anesthesia",3.15),
        ("28575","Closed tx talonavicular dislocation; requiring anesthesia",4.85),
        ("28585","Open tx talonavicular dislocation",11.25),
        ("28600","Closed tx tarsometatarsal dislocation; without anesthesia",2.85),
        ("28605","Closed tx tarsometatarsal dislocation; requiring anesthesia",4.55),
        ("28606","Percutaneous skeletal fixation tarsometatarsal dislocation",7.85),
        ("28615","Open tx tarsometatarsal dislocation (Lisfranc)",11.55),
        ("28630","Closed tx MTP dislocation; without anesthesia",2.15),
        ("28635","Closed tx MTP dislocation; requiring anesthesia",3.55),
        ("28645","Open tx MTP dislocation, includes internal fixation",7.55),
        ("28660","Closed tx IP joint dislocation, foot; without anesthesia",1.85),
        ("28665","Closed tx IP joint dislocation, foot; requiring anesthesia",2.85),
        ("28675","Open tx IP joint dislocation, foot",6.25),
    ]
    for code,desc,rvu in foot:
        c.append(mc(code,desc,S,F,O,rvu,90,True,asst=rvu>8))
    
    # Spine fractures
    spine_fx = [
        ("22310","Closed tx vertebral body fx, with casting/bracing",3.85),
        ("22315","Closed tx vertebral fx with manipulation and casting/bracing",6.25),
        ("22318","Open tx odontoid fx, anterior approach",22.55),
        ("22319","Open tx odontoid fx, posterior approach",20.85),
        ("22325","Open tx vertebral fx, posterior approach; lumbar",18.25),
        ("22326","Open tx vertebral fx, posterior approach; cervical",20.55),
        ("22327","Open tx vertebral fx, posterior approach; thoracic",19.25),
        ("22328","Open tx vertebral fx, each additional segment",5.55),
    ]
    for code,desc,rvu in spine_fx:
        addon = code == "22328"
        c.append(mc(code,desc,S,F,O,rvu,90,False,addon=addon,asst=rvu>8,cosurg=rvu>16))

    # === 2. CASTING/STRAPPING (~100 codes) ===
    SC = "casting"
    casts = [
        ("29000","Application of halo type body cast",3.25),("29010","Application of Risser jacket",2.85),
        ("29015","Application of halo, cranial",4.55),("29020","Application of turnbuckle jacket",2.65),
        ("29025","Application of body cast, shoulder to hips, Minerva type",3.55),
        ("29035","Application of body cast, shoulder to hips, including 1 thigh",3.25),
        ("29040","Application of body cast, including both thighs",3.85),
        ("29044","Application of body cast, including 1 thigh",3.15),
        ("29046","Application of body cast, including both thighs",3.55),
        ("29049","Application of figure-of-eight",1.25),("29055","Application of shoulder spica",2.85),
        ("29058","Application of plaster Velpeau",1.55),
        ("29065","Application of long arm cast (shoulder to hand)",1.85),
        ("29075","Application of short arm cast (forearm to hand)",1.55),
        ("29085","Application of hand and lower forearm cast",1.35),
        ("29086","Application of finger cast",0.85),
        ("29105","Application of long arm splint",1.35),
        ("29125","Application of short arm splint; static",1.15),
        ("29126","Application of short arm splint; dynamic",1.25),
        ("29130","Application of finger splint; static",0.55),
        ("29131","Application of finger splint; dynamic",0.65),
        ("29200","Strapping of chest",0.85),("29240","Strapping of shoulder (Velpeau)",0.75),
        ("29260","Strapping of elbow or wrist",0.65),("29280","Strapping of hand or finger",0.55),
        ("29305","Application of hip spica cast; 1 leg",2.85),
        ("29325","Application of hip spica cast; both legs",3.55),
        ("29345","Application of long leg cast (thigh to toes)",2.15),
        ("29355","Application of long leg cast brace",2.35),
        ("29358","Application of long leg cast brace for proximal tibia fx",2.55),
        ("29365","Application of cylinder cast (thigh to ankle)",1.85),
        ("29405","Application of short leg cast (below knee to toes)",1.65),
        ("29425","Application of short leg walking cast",1.55),
        ("29435","Application of PTB cast",1.85),("29440","Adding walker to cast",0.55),
        ("29445","Application of rigid total contact leg cast",2.25),
        ("29450","Application of clubfoot cast with molding",2.55),
        ("29505","Application of long leg splint",1.55),("29515","Application of short leg splint",1.25),
        ("29520","Strapping of hip",0.85),("29530","Strapping of knee",0.75),
        ("29540","Strapping of ankle and/or foot",0.65),("29550","Strapping of toes",0.45),
        ("29580","Application of Unna boot",0.75),
        ("29581","Application of multi-layer compression; leg below knee",0.85),
        ("29582","Application of multi-layer compression; thigh and leg",1.05),
        ("29583","Application of multi-layer compression; upper arm and forearm",0.85),
        ("29584","Application of multi-layer compression; upper arm, forearm, hand, fingers",1.15),
        ("29700","Removal/bivalving; gauntlet, boot or body cast",0.85),
        ("29705","Removal/bivalving; full arm or full leg cast",0.75),
        ("29710","Removal/bivalving; shoulder or hip spica",1.15),
        ("29720","Repair of spica, body cast or jacket",0.65),
        ("29730","Windowing of cast",0.55),("29740","Wedging of cast",0.65),
        ("29750","Wedging of clubfoot cast",0.75),
    ]
    for code,desc,rvu in casts:
        bil = code not in ("29000","29010","29015","29020","29025","29200","29700","29710","29720","29730")
        sub = "strapping" if "Strapping" in desc or "Unna" in desc or "compression" in desc else "casting"
        c.append(mc(code,desc,S,sub,O,rvu,0,bil))

    # === 3. ARTHROSCOPY (~55 codes) ===
    SA = "arthroscopy"
    arthro = [
        # Shoulder
        ("29805","Arthroscopy, shoulder, diagnostic",5.85),
        ("29806","Arthroscopy, shoulder; capsulorrhaphy",14.55),
        ("29807","Arthroscopy, shoulder; repair of SLAP lesion",12.85),
        ("29819","Arthroscopy, shoulder; removal of loose body",8.55),
        ("29820","Arthroscopy, shoulder; synovectomy, partial",7.85),
        ("29821","Arthroscopy, shoulder; synovectomy, complete",9.25),
        ("29822","Arthroscopy, shoulder; debridement, limited",7.55),
        ("29823","Arthroscopy, shoulder; debridement, extensive",8.85),
        ("29824","Arthroscopy, shoulder; distal claviculectomy (Mumford)",9.55),
        ("29825","Arthroscopy, shoulder; lysis of adhesions",8.25),
        ("29826","Arthroscopy, shoulder; subacromial decompression",9.85),
        ("29827","Arthroscopy, shoulder; rotator cuff repair",15.55),
        ("29828","Arthroscopy, shoulder; biceps tenodesis",10.55),
        # Elbow
        ("29830","Arthroscopy, elbow, diagnostic",5.55),
        ("29834","Arthroscopy, elbow; removal of loose body",7.85),
        ("29835","Arthroscopy, elbow; synovectomy, partial",7.25),
        ("29836","Arthroscopy, elbow; synovectomy, complete",8.55),
        ("29837","Arthroscopy, elbow; debridement, limited",7.15),
        ("29838","Arthroscopy, elbow; debridement, extensive",8.25),
        # Wrist
        ("29840","Arthroscopy, wrist, diagnostic",5.25),
        ("29843","Arthroscopy, wrist; lavage and drainage",7.55),
        ("29844","Arthroscopy, wrist; synovectomy, partial",7.15),
        ("29845","Arthroscopy, wrist; synovectomy, complete",8.25),
        ("29846","Arthroscopy, wrist; TFCC excision/repair",8.85),
        ("29847","Arthroscopy, wrist; internal fixation for fracture",10.25),
        ("29848","Endoscopic carpal tunnel release",6.55),
        # Hip
        ("29860","Arthroscopy, hip, diagnostic",7.55),
        ("29861","Arthroscopy, hip; removal of loose body",9.85),
        ("29862","Arthroscopy, hip; chondroplasty/labral resection",10.55),
        ("29863","Arthroscopy, hip; femoroplasty (cam lesion)",11.85),
        ("29914","Arthroscopy, hip; femoroplasty",12.25),
        ("29915","Arthroscopy, hip; acetabuloplasty (pincer lesion)",12.85),
        ("29916","Arthroscopy, hip; labral repair",13.55),
        # Knee
        ("29870","Arthroscopy, knee, diagnostic",4.85),
        ("29871","Arthroscopy, knee; lavage and drainage",6.55),
        ("29873","Arthroscopy, knee; lateral release",6.85),
        ("29874","Arthroscopy, knee; removal of loose body",6.25),
        ("29875","Arthroscopy, knee; synovectomy, limited",6.55),
        ("29876","Arthroscopy, knee; synovectomy, major",8.25),
        ("29877","Arthroscopy, knee; chondroplasty",6.85),
        ("29879","Arthroscopy, knee; abrasion arthroplasty/microfracture",7.55),
        ("29880","Arthroscopy, knee; meniscectomy, medial AND lateral",7.85),
        ("29881","Arthroscopy, knee; meniscectomy, medial OR lateral",6.85),
        ("29882","Arthroscopy, knee; meniscus repair, medial OR lateral",8.55),
        ("29883","Arthroscopy, knee; meniscus repair, medial AND lateral",10.25),
        ("29884","Arthroscopy, knee; lysis of adhesions",6.55),
        ("29885","Arthroscopy, knee; drilling for OCD with bone graft",9.25),
        ("29886","Arthroscopy, knee; drilling for intact OCD",7.85),
        ("29887","Arthroscopy, knee; drilling for OCD with internal fixation",9.55),
        ("29888","Arthroscopic ACL reconstruction",15.85),
        ("29889","Arthroscopic PCL reconstruction",16.55),
        # Ankle
        ("29891","Arthroscopy, ankle; excision of osteochondral defect",9.55),
        ("29892","Arthroscopic repair of OCD lesion, talar dome",11.25),
        ("29893","Endoscopic plantar fasciotomy",6.55),
        ("29894","Arthroscopy, ankle; removal of loose body",7.25),
        ("29895","Arthroscopy, ankle; synovectomy, partial",7.55),
        ("29897","Arthroscopy, ankle; debridement, limited",7.15),
        ("29898","Arthroscopy, ankle; debridement, extensive",8.25),
    ]
    for code,desc,rvu in arthro:
        bil = code not in ("29860","29861","29862","29863","29914","29915","29916")
        c.append(mc(code,desc,S,SA,O,rvu,90,bil,asst=rvu>12))

    # === 4. INTERVENTIONAL CARDIOLOGY (~100 codes) ===
    # PCI
    pci = [
        ("92920","Percutaneous coronary angioplasty; single vessel",12.55,False),
        ("92921","Percutaneous coronary angioplasty; each additional branch",3.85,True),
        ("92924","Percutaneous coronary atherectomy; single vessel",13.25,False),
        ("92925","Percutaneous coronary atherectomy; each additional branch",4.15,True),
        ("92928","Percutaneous intracoronary stent; single vessel",14.85,False),
        ("92929","Percutaneous intracoronary stent; each additional branch",4.55,True),
        ("92933","Percutaneous coronary atherectomy with stent; single vessel",15.55,False),
        ("92934","Percutaneous coronary atherectomy with stent; each additional branch",4.85,True),
        ("92937","Percutaneous revascularization of bypass graft; single vessel",15.85,False),
        ("92938","Percutaneous revascularization of bypass graft; each additional branch",5.15,True),
        ("92941","Percutaneous revascularization of acute total occlusion during AMI",17.55,False),
        ("92943","Percutaneous revascularization of chronic total occlusion; single vessel",18.25,False),
        ("92944","Percutaneous revascularization of chronic total occlusion; each additional",5.55,True),
    ]
    for code,desc,rvu,addon in pci:
        c.append(mc(code,desc,S,"interventional_cardiology","cardiology",rvu,0,False,addon=addon,asst=not addon))
    
    # Electrophysiology
    ep = [
        ("93600","Bundle of His recording",3.25,False),("93602","Intra-atrial recording",2.85,False),
        ("93603","Right ventricular recording",2.55,False),
        ("93609","Intracardiac mapping of tachycardia",5.85,False),
        ("93610","Intra-atrial pacing",2.55,False),("93612","Intraventricular pacing",2.55,False),
        ("93613","Intracardiac 3D mapping",6.25,True),
        ("93615","Esophageal recording of atrial electrogram",1.85,False),
        ("93616","Esophageal recording with pacing",2.25,False),
        ("93618","Induction of arrhythmia by electrical pacing",3.55,False),
        ("93619","Comprehensive EP evaluation without left atrial pacing",8.55,False),
        ("93620","Comprehensive EP evaluation with left atrial pacing",10.25,False),
        ("93621","EP evaluation with right atrial and ventricular pacing",2.55,True),
        ("93622","EP evaluation with left atrial pacing from coronary sinus",3.15,True),
        ("93623","Programmed stimulation after IV drug infusion",2.15,True),
        ("93624","EP follow-up study to test therapy effectiveness",5.85,False),
        ("93631","Intraoperative epicardial/endocardial mapping",7.25,False),
        ("93640","EP evaluation of pacing defibrillator leads; with testing",2.85,False),
        ("93641","EP evaluation of pacing defibrillator leads; with arrhythmia induction",3.55,False),
        ("93642","EP evaluation of pacing defibrillator leads; with DFT evaluation",4.25,False),
        ("93644","EP evaluation of subcutaneous ICD",3.85,False),
        ("93650","Intracardiac catheter ablation of AV node function",8.85,False),
        ("93653","Comprehensive EP evaluation with ablation of SVT",15.55,False),
        ("93654","Comprehensive EP evaluation with ablation of VT",18.25,False),
        ("93655","Intracardiac ablation of distinct arrhythmia mechanism",5.55,True),
        ("93656","Comprehensive EP with pulmonary vein isolation for AFib",20.55,False),
        ("93657","Additional linear/focal ablation for AFib",6.55,True),
        ("93660","Tilt table evaluation",2.55,False),
        ("93662","Intracardiac echocardiography during intervention",3.85,True),
    ]
    for code,desc,rvu,addon in ep:
        cat = S if rvu > 12 else "Medicine"
        c.append(mc(code,desc,cat,"electrophysiology","cardiology",rvu,0,False,addon=addon,asst=rvu>12))
    
    # Pacemaker/ICD
    pm = [
        ("33206","Insertion of permanent pacemaker; atrial",7.55),
        ("33207","Insertion of permanent pacemaker; ventricular",7.85),
        ("33208","Insertion of permanent pacemaker; atrial and ventricular",9.25),
        ("33210","Insertion of temporary transvenous single chamber pacemaker",3.55),
        ("33211","Insertion of temporary transvenous dual chamber pacemaker",4.25),
        ("33212","Insertion of pacemaker pulse generator; single lead",5.55),
        ("33213","Insertion of pacemaker pulse generator; dual leads",5.85),
        ("33214","Upgrade pacemaker single to dual chamber",8.25),
        ("33215","Repositioning of pacemaker/ICD electrode",5.25),
        ("33216","Insertion of single transvenous electrode",5.85),
        ("33217","Insertion of 2 transvenous electrodes",7.25),
        ("33218","Repair of single transvenous electrode",5.55),
        ("33220","Repair of 2 transvenous electrodes",7.15),
        ("33221","Insertion of pacemaker pulse generator; multiple leads",6.25),
        ("33222","Relocation of skin pocket for pacemaker",5.15),
        ("33223","Relocation of skin pocket for ICD",5.85),
        ("33224","Insertion of LV pacing electrode with existing device",8.55),
        ("33225","Insertion of LV pacing electrode at time of device insertion",5.25),
        ("33226","Repositioning of LV electrode",5.55),
        ("33227","Replacement of pacemaker generator; single lead",4.85),
        ("33228","Replacement of pacemaker generator; dual lead",5.15),
        ("33229","Replacement of pacemaker generator; multiple lead",5.55),
        ("33230","Insertion of ICD pulse generator; dual leads",7.25),
        ("33231","Insertion of ICD pulse generator; multiple leads",7.55),
        ("33233","Removal of pacemaker pulse generator only",4.25),
        ("33234","Removal of pacemaker electrode; single lead",6.55),
        ("33235","Removal of pacemaker electrodes; dual lead",7.85),
        ("33236","Removal of epicardial pacemaker by thoracotomy; single lead",12.55),
        ("33237","Removal of epicardial pacemaker by thoracotomy; dual lead",14.25),
        ("33238","Removal of transvenous electrodes by thoracotomy",15.55),
        ("33240","Insertion of ICD pulse generator; single lead",6.85),
        ("33241","Removal of ICD pulse generator only",4.85),
        ("33243","Removal of ICD electrodes; by thoracotomy",16.55),
        ("33244","Removal of ICD electrodes; by transvenous extraction",12.85),
        ("33249","Insertion/replacement of ICD system with transvenous leads",12.55),
        ("33262","Replacement of ICD generator; single lead",6.25),
        ("33263","Replacement of ICD generator; dual lead",6.55),
        ("33264","Replacement of ICD generator; multiple lead",6.85),
        ("33270","Insertion of subcutaneous ICD system",10.55),
        ("33271","Insertion of subcutaneous ICD electrode",5.85),
        ("33272","Removal of subcutaneous ICD electrode",5.25),
        ("33273","Repositioning of subcutaneous ICD electrode",5.55),
        ("33274","Insertion of permanent leadless pacemaker",8.55),
        ("33275","Transcatheter removal of leadless pacemaker",7.25),
    ]
    for code,desc,rvu in pm:
        addon = code == "33225"
        c.append(mc(code,desc,S,"pacemaker_icd","cardiology",rvu,90,False,addon=addon,asst=rvu>8))

    # === 5. RADIOLOGY (~200 codes) ===
    R = "Radiology"
    # Skull/Head
    skull = [
        ("70100","XR mandible; partial",0.55),("70110","XR mandible; complete",0.65),
        ("70120","XR mastoids; less than 3 views",0.55),("70130","XR mastoids; complete",0.65),
        ("70140","XR facial bones; less than 3 views",0.50),("70150","XR facial bones; complete",0.60),
        ("70160","XR nasal bones, complete",0.45),("70200","XR orbits, complete",0.55),
        ("70210","XR sinuses, paranasal; partial",0.45),("70220","XR sinuses, paranasal; complete",0.55),
        ("70250","XR skull; less than 4 views",0.55),("70260","XR skull; complete",0.65),
    ]
    for code,desc,rvu in skull:
        c.append(mc(code,desc,R,"xray","radiology",rvu,0,False))
    
    # Spine XR
    spine_xr = [
        ("72010","XR spine, entire survey",0.75),("72020","XR spine, single view",0.35),
        ("72040","XR c-spine; 2-3 views",0.50),("72050","XR c-spine; 4-5 views",0.60),
        ("72052","XR c-spine; 6+ views",0.70),("72070","XR t-spine; 2 views",0.50),
        ("72072","XR t-spine; 3 views",0.55),("72074","XR t-spine; 4+ views",0.60),
        ("72080","XR thoracolumbar; 2 views",0.50),("72100","XR l-spine; 2-3 views",0.50),
        ("72110","XR l-spine; 4+ views",0.60),
        ("72114","XR l-spine; complete with bending views",0.70),
        ("72120","XR l-spine; bending views only",0.50),
    ]
    for code,desc,rvu in spine_xr:
        c.append(mc(code,desc,R,"xray","radiology",rvu,0,False))
    
    # Pelvis XR
    for code,desc,rvu in [("72170","XR pelvis; 1-2 views",0.45),("72190","XR pelvis; complete",0.55),
        ("72200","XR sacroiliac joints; partial",0.40),("72202","XR sacroiliac joints; 3+ views",0.50),
        ("72220","XR sacrum and coccyx",0.45)]:
        c.append(mc(code,desc,R,"xray","radiology",rvu,0,False))
    
    # Upper extremity XR
    ue_xr = [
        ("73000","XR clavicle, complete",0.40),("73010","XR scapula, complete",0.45),
        ("73020","XR shoulder; 1 view",0.35),("73030","XR shoulder; complete, 2+ views",0.45),
        ("73050","XR acromioclavicular joints, bilateral",0.50),
        ("73060","XR humerus, 2+ views",0.40),("73070","XR elbow; 2 views",0.35),
        ("73080","XR elbow; complete, 3+ views",0.45),("73090","XR forearm, 2 views",0.35),
        ("73100","XR wrist; 2 views",0.35),("73110","XR wrist; complete, 3+ views",0.45),
        ("73120","XR hand; 2 views",0.35),("73130","XR hand; complete, 3+ views",0.45),
        ("73140","XR finger(s), 2+ views",0.30),
    ]
    for code,desc,rvu in ue_xr:
        c.append(mc(code,desc,R,"xray","radiology",rvu,0,True))
    
    # Lower extremity XR
    le_xr = [
        ("73500","XR hip, unilateral; 1 view",0.35),
        ("73501","XR hip, unilateral; 2-3 views",0.45),
        ("73502","XR hip, unilateral; 4+ views",0.55),
        ("73521","XR hips, bilateral; 2 views",0.45),
        ("73522","XR hips, bilateral; 3-4 views",0.55),
        ("73523","XR hips, bilateral; 5+ views",0.65),
        ("73551","XR femur; 1 view",0.35),("73552","XR femur; 2+ views",0.45),
        ("73560","XR knee; 1-2 views",0.35),("73562","XR knee; 3 views",0.45),
        ("73564","XR knee; complete, 4+ views",0.55),
        ("73565","XR knees, bilateral, standing",0.50),
        ("73590","XR tibia and fibula; 2 views",0.35),
        ("73592","XR lower extremity, infant",0.35),
        ("73600","XR ankle; 2 views",0.35),("73610","XR ankle; complete, 3+ views",0.45),
        ("73620","XR foot; 2 views",0.35),("73630","XR foot; complete, 3+ views",0.45),
        ("73650","XR calcaneus; 2+ views",0.40),("73660","XR toes; 2+ views",0.30),
    ]
    for code,desc,rvu in le_xr:
        c.append(mc(code,desc,R,"xray","radiology",rvu,0,True))
    
    # Chest XR
    chest_xr = [
        ("71045","XR chest; single view",0.30),("71046","XR chest; 2 views",0.40),
        ("71047","XR chest; 3 views",0.45),("71048","XR chest; 4+ views",0.50),
    ]
    for code,desc,rvu in chest_xr:
        c.append(mc(code,desc,R,"xray","radiology",rvu,0,False))
    
    # Abdomen XR
    abd_xr = [
        ("74018","XR abdomen; 1 view",0.30),("74019","XR abdomen; 2 views",0.35),
        ("74021","XR abdomen; 3+ views",0.40),
        ("74022","XR abdomen; complete acute abdomen series",0.50),
    ]
    for code,desc,rvu in abd_xr:
        c.append(mc(code,desc,R,"xray","radiology",rvu,0,False))
    
    # Fluoroscopy
    fluoro = [
        ("76000","Fluoroscopy, up to 1 hour physician/QHP time",1.15),
        ("76001","Fluoroscopy, physician/QHP time more than 1 hour",1.85),
        ("76010","Radiologic examination from nose to rectum for foreign body",0.55),
        ("76080","Radiologic examination, abscess fistula or sinus tract study",1.25),
        ("76098","Radiological examination, surgical specimen",0.35),
        ("76100","Radiologic examination, single plane body section",0.65),
        ("76101","Radiologic examination, complex motion body section; unilateral",0.85),
        ("76102","Radiologic examination, complex motion body section; bilateral",1.05),
        ("76120","Cineradiography/videoradiography, except where specifically included",0.55),
        ("76125","Cineradiography/videoradiography to complement routine examination",0.35),
        ("76140","Consultation on X-ray examination made elsewhere",0.85),
        ("76376","3D rendering with interpretation and reporting of CT/MRI; not requiring image postprocessing on independent workstation",0.35),
        ("76377","3D rendering with interpretation and reporting of CT/MRI; requiring image postprocessing on independent workstation",0.55),
        ("76380","Computed tomography, limited or localized follow-up study",0.65),
        ("76390","Magnetic resonance spectroscopy",1.15),
    ]
    for code,desc,rvu in fluoro:
        c.append(mc(code,desc,R,"fluoroscopy","radiology",rvu,0,False))
    
    # Bone density
    for code,desc,rvu in [
        ("77080","Dual-energy X-ray absorptiometry (DXA), bone density study; axial skeleton",0.35),
        ("77081","DXA bone density study; appendicular skeleton",0.25),
        ("77085","DXA bone density study; axial skeleton including vertebral fracture assessment",0.55),
        ("77086","Vertebral fracture assessment via DXA",0.25)]:
        c.append(mc(code,desc,R,"bone_density","radiology",rvu,0,False))
    
    # Radiation therapy
    rt = [
        ("77261","Therapeutic radiology treatment planning; simple",1.55),
        ("77262","Therapeutic radiology treatment planning; intermediate",2.55),
        ("77263","Therapeutic radiology treatment planning; complex",3.85),
        ("77280","Therapeutic radiology simulation-aided field setting; simple",1.25),
        ("77285","Therapeutic radiology simulation-aided field setting; intermediate",1.85),
        ("77290","Therapeutic radiology simulation-aided field setting; complex",2.55),
        ("77295","Therapeutic radiology simulation; 3-dimensional",3.25),
        ("77299","Unlisted procedure, therapeutic radiology clinical treatment planning",0.00),
        ("77300","Basic radiation dosimetry calculation",0.55),
        ("77301","Intensity modulated radiation therapy plan",7.55),
        ("77306","Teletherapy isodose plan; simple",1.25),
        ("77307","Teletherapy isodose plan; complex",2.15),
        ("77316","Brachytherapy isodose plan; simple",1.55),
        ("77317","Brachytherapy isodose plan; intermediate",2.55),
        ("77318","Brachytherapy isodose plan; complex",3.85),
        ("77321","Special teletherapy port plan",0.85),
        ("77331","Special dosimetry (TLD, microdosimetry, etc.)",0.55),
        ("77332","Treatment devices, design and construction; simple",0.45),
        ("77333","Treatment devices, design and construction; intermediate",0.85),
        ("77334","Treatment devices, design and construction; complex",1.55),
        ("77336","Continuing medical physics consultation",0.85),
        ("77338","Multi-leaf collimator (MLC) device(s) for IMRT",0.65),
        ("77370","Special medical radiation physics consultation",1.55),
        ("77371","Radiation treatment delivery, stereotactic radiosurgery (SRS), complete course of treatment of cranial lesion(s); per session",7.85),
        ("77372","Radiation treatment delivery, SRS, complete course; linear accelerator based",7.55),
        ("77373","Stereotactic body radiation therapy, treatment delivery, per fraction",6.85),
        ("77385","Intensity modulated radiation treatment delivery; simple",0.85),
        ("77386","Intensity modulated radiation treatment delivery; complex",1.25),
        ("77387","Guidance for localization of target volume for delivery of radiation treatment",0.55),
        ("77401","Radiation treatment delivery, superficial and/or ortho voltage",0.35),
        ("77402","Radiation treatment delivery, >= 1 MeV; simple",0.55),
        ("77407","Radiation treatment delivery, >= 1 MeV; intermediate",0.65),
        ("77412","Radiation treatment delivery, >= 1 MeV; complex",0.75),
        ("77417","Therapeutic radiology port image(s)",0.15),
        ("77427","Radiation treatment management, 5 treatments",2.85),
        ("77431","Radiation therapy management with complete course of therapy consisting of 1 or 2 fractions only",1.85),
        ("77432","Stereotactic radiation treatment management of cranial lesion(s)",5.55),
        ("77435","Stereotactic body radiation therapy treatment management, per treatment course",5.25),
        ("77520","Proton treatment delivery; simple, without compensation",0.85),
        ("77522","Proton treatment delivery; simple, with compensation",1.15),
        ("77523","Proton treatment delivery; intermediate",1.55),
        ("77525","Proton treatment delivery; complex",1.85),
        ("77600","Hyperthermia, externally generated; superficial",1.25),
        ("77605","Hyperthermia, externally generated; deep",1.85),
        ("77610","Hyperthermia generated by interstitial probe(s); 5 or fewer interstitial applicators",2.55),
        ("77615","Hyperthermia generated by interstitial probe(s); more than 5 applicators",3.25),
        ("77620","Hyperthermia generated by intracavitary probe(s)",2.55),
        ("77750","Infusion or instillation of radioelement solution",1.55),
        ("77761","Intracavitary radiation source application; simple",3.55),
        ("77762","Intracavitary radiation source application; intermediate",5.55),
        ("77763","Intracavitary radiation source application; complex",7.25),
        ("77767","Remote afterloading high dose rate radionuclide skin surface brachytherapy; 1 channel",3.85),
        ("77768","Remote afterloading high dose rate brachytherapy; 2+ channels",5.55),
        ("77770","Remote afterloading high dose rate radionuclide interstitial or intracavitary brachytherapy; 1 channel",4.85),
        ("77771","Remote afterloading HDR brachytherapy; 2-12 channels",6.55),
        ("77772","Remote afterloading HDR brachytherapy; over 12 channels",8.25),
        ("77789","Surface application of low dose rate radionuclide source",1.55),
        ("77790","Supervision, handling, loading of radiation source",0.55),
        ("77799","Unlisted procedure, clinical brachytherapy",0.00),
    ]
    for code,desc,rvu in rt:
        c.append(mc(code,desc,R,"radiation_therapy","radiation_oncology",rvu,0,False))

    # === 6. DERMATOLOGY (~150 codes) ===
    D = "dermatology"
    # Destruction benign/premalignant/malignant 17000-17286
    derm_dest = [
        ("17000","Destruction premalignant lesions; first lesion",1.05),
        ("17003","Destruction premalignant lesions; 2-14, each additional",0.15),
        ("17004","Destruction premalignant lesions; 15 or more",4.85),
        ("17106","Destruction of cutaneous vascular proliferative lesions; less than 10 sq cm",2.55),
        ("17107","Destruction of cutaneous vascular proliferative lesions; 10-50 sq cm",3.85),
        ("17108","Destruction of cutaneous vascular proliferative lesions; over 50 sq cm",5.25),
        ("17110","Destruction of flat warts, molluscum, or milia; up to 14 lesions",1.22),
        ("17111","Destruction of flat warts, molluscum, or milia; 15 or more lesions",1.88),
        ("17250","Chemical cauterization of granulation tissue",0.45),
        ("17260","Destruction, malignant lesion, trunk, arms, legs; lesion diameter 0.5 cm or less",1.55),
        ("17261","Destruction, malignant lesion, trunk, arms, legs; 0.6-1.0 cm",1.85),
        ("17262","Destruction, malignant lesion, trunk, arms, legs; 1.1-2.0 cm",2.25),
        ("17263","Destruction, malignant lesion, trunk, arms, legs; 2.1-3.0 cm",2.65),
        ("17264","Destruction, malignant lesion, trunk, arms, legs; 3.1-4.0 cm",3.15),
        ("17266","Destruction, malignant lesion, trunk, arms, legs; over 4.0 cm",3.85),
        ("17270","Destruction, malignant lesion, scalp, neck, hands, feet, genitalia; 0.5 cm or less",1.75),
        ("17271","Destruction, malignant lesion, scalp, neck, hands, feet, genitalia; 0.6-1.0 cm",2.05),
        ("17272","Destruction, malignant lesion, scalp, neck, hands, feet, genitalia; 1.1-2.0 cm",2.55),
        ("17273","Destruction, malignant lesion, scalp, neck, hands, feet, genitalia; 2.1-3.0 cm",2.95),
        ("17274","Destruction, malignant lesion, scalp, neck, hands, feet, genitalia; 3.1-4.0 cm",3.45),
        ("17276","Destruction, malignant lesion, scalp, neck, hands, feet, genitalia; over 4.0 cm",4.15),
        ("17280","Destruction, malignant lesion, face, ears, eyelids, nose, lips, mucous membrane; 0.5 cm or less",1.95),
        ("17281","Destruction, malignant lesion, face, ears, eyelids, nose, lips; 0.6-1.0 cm",2.35),
        ("17282","Destruction, malignant lesion, face, ears, eyelids, nose, lips; 1.1-2.0 cm",2.85),
        ("17283","Destruction, malignant lesion, face, ears, eyelids, nose, lips; 2.1-3.0 cm",3.35),
        ("17284","Destruction, malignant lesion, face, ears, eyelids, nose, lips; 3.1-4.0 cm",3.85),
        ("17286","Destruction, malignant lesion, face, ears, eyelids, nose, lips; over 4.0 cm",4.55),
    ]
    for code,desc,rvu in derm_dest:
        addon = code == "17003"
        c.append(mc(code,desc,S,"destruction",D,rvu,10,False,addon=addon))
    
    # Destruction benign lesions
    derm_benign = [
        ("17000","Destruction premalignant lesion, first",1.05),  # already added above, skip dupes at merge
        ("11200","Removal of skin tags, up to and including 15",1.12),
        ("11201","Removal of skin tags, each additional 10",0.35),
    ]
    for code,desc,rvu in derm_benign:
        addon = code == "11201"
        c.append(mc(code,desc,S,"skin_tags",D,rvu,10,False,addon=addon))
    
    # Shaving of lesions 11300-11313
    shave = [
        ("11300","Shaving of epidermal or dermal lesion, trunk, arms, legs; 0.5 cm or less",0.75),
        ("11301","Shaving of lesion, trunk, arms, legs; 0.6-1.0 cm",0.95),
        ("11302","Shaving of lesion, trunk, arms, legs; 1.1-2.0 cm",1.15),
        ("11303","Shaving of lesion, trunk, arms, legs; over 2.0 cm",1.45),
        ("11305","Shaving of lesion, scalp, neck, hands, feet, genitalia; 0.5 cm or less",0.85),
        ("11306","Shaving of lesion, scalp, neck, hands, feet, genitalia; 0.6-1.0 cm",1.05),
        ("11307","Shaving of lesion, scalp, neck, hands, feet, genitalia; 1.1-2.0 cm",1.25),
        ("11308","Shaving of lesion, scalp, neck, hands, feet, genitalia; over 2.0 cm",1.55),
        ("11310","Shaving of lesion, face, ears, eyelids, nose, lips, mucous membrane; 0.5 cm or less",0.95),
        ("11311","Shaving of lesion, face, ears, eyelids, nose, lips; 0.6-1.0 cm",1.15),
        ("11312","Shaving of lesion, face, ears, eyelids, nose, lips; 1.1-2.0 cm",1.35),
        ("11313","Shaving of lesion, face, ears, eyelids, nose, lips; over 2.0 cm",1.65),
    ]
    for code,desc,rvu in shave:
        c.append(mc(code,desc,S,"shaving",D,rvu,10,False))
    
    # Mohs surgery 17311-17315
    mohs = [
        ("17311","Mohs micrographic technique, head, neck, hands, feet, genitalia; first stage, up to 5 tissue blocks",8.85),
        ("17312","Mohs micrographic technique, head, neck, hands, feet, genitalia; each additional stage, up to 5 tissue blocks",4.55),
        ("17313","Mohs micrographic technique, trunk, arms, legs; first stage, up to 5 tissue blocks",7.55),
        ("17314","Mohs micrographic technique, trunk, arms, legs; each additional stage, up to 5 tissue blocks",3.85),
        ("17315","Mohs micrographic technique, each additional block after 5, any stage",0.55),
    ]
    for code,desc,rvu in mohs:
        addon = code in ("17312","17314","17315")
        c.append(mc(code,desc,S,"mohs_surgery",D,rvu,0,False,addon=addon))
    
    # Phototherapy/Photodynamic therapy
    photo = [
        ("96900","Actinotherapy (ultraviolet light)",0.25),
        ("96902","Microscopic examination of hairs plucked or clipped by the examiner",0.55),
        ("96904","Whole body integumentary photography",0.85),
        ("96910","Photochemotherapy; tar and ultraviolet B (Goeckerman treatment) or petrolatum and UVB",0.85),
        ("96912","Photochemotherapy; psoralens and ultraviolet A (PUVA)",0.85),
        ("96913","Photochemotherapy (Goeckerman and/or PUVA) for severe photoresponsive dermatoses requiring at least 4-8 hours of care",1.55),
        ("96920","Laser treatment for inflammatory skin disease; total area less than 250 sq cm",1.55),
        ("96921","Laser treatment for inflammatory skin disease; 250-500 sq cm",2.25),
        ("96922","Laser treatment for inflammatory skin disease; over 500 sq cm",2.85),
        ("96999","Unlisted special dermatological service or procedure",0.00),
    ]
    for code,desc,rvu in photo:
        c.append(mc(code,desc,"Medicine","phototherapy",D,rvu,0,False))
    
    # Excision benign/malignant lesions (common derm codes)
    excision = [
        ("11400","Excision, benign lesion including margins, trunk, arms, legs; 0.5 cm or less",1.35),
        ("11401","Excision, benign lesion, trunk, arms, legs; 0.6-1.0 cm",1.75),
        ("11402","Excision, benign lesion, trunk, arms, legs; 1.1-2.0 cm",2.15),
        ("11403","Excision, benign lesion, trunk, arms, legs; 2.1-3.0 cm",2.55),
        ("11404","Excision, benign lesion, trunk, arms, legs; 3.1-4.0 cm",2.95),
        ("11406","Excision, benign lesion, trunk, arms, legs; over 4.0 cm",3.55),
        ("11420","Excision, benign lesion, scalp, neck, hands, feet, genitalia; 0.5 cm or less",1.55),
        ("11421","Excision, benign lesion, scalp, neck, hands, feet, genitalia; 0.6-1.0 cm",1.95),
        ("11422","Excision, benign lesion, scalp, neck, hands, feet, genitalia; 1.1-2.0 cm",2.35),
        ("11423","Excision, benign lesion, scalp, neck, hands, feet, genitalia; 2.1-3.0 cm",2.75),
        ("11424","Excision, benign lesion, scalp, neck, hands, feet, genitalia; 3.1-4.0 cm",3.25),
        ("11426","Excision, benign lesion, scalp, neck, hands, feet, genitalia; over 4.0 cm",3.85),
        ("11440","Excision, benign lesion, face, ears, eyelids, nose, lips, mucous membrane; 0.5 cm or less",1.75),
        ("11441","Excision, benign lesion, face, ears, eyelids, nose, lips; 0.6-1.0 cm",2.25),
        ("11442","Excision, benign lesion, face, ears, eyelids, nose, lips; 1.1-2.0 cm",2.65),
        ("11443","Excision, benign lesion, face, ears, eyelids, nose, lips; 2.1-3.0 cm",3.15),
        ("11444","Excision, benign lesion, face, ears, eyelids, nose, lips; 3.1-4.0 cm",3.55),
        ("11446","Excision, benign lesion, face, ears, eyelids, nose, lips; over 4.0 cm",4.25),
        ("11600","Excision, malignant lesion, trunk, arms, legs; 0.5 cm or less",1.85),
        ("11601","Excision, malignant lesion, trunk, arms, legs; 0.6-1.0 cm",2.25),
        ("11602","Excision, malignant lesion, trunk, arms, legs; 1.1-2.0 cm",2.65),
        ("11603","Excision, malignant lesion, trunk, arms, legs; 2.1-3.0 cm",3.15),
        ("11604","Excision, malignant lesion, trunk, arms, legs; 3.1-4.0 cm",3.55),
        ("11606","Excision, malignant lesion, trunk, arms, legs; over 4.0 cm",4.25),
        ("11620","Excision, malignant lesion, scalp, neck, hands, feet, genitalia; 0.5 cm or less",2.05),
        ("11621","Excision, malignant lesion, scalp, neck, hands, feet, genitalia; 0.6-1.0 cm",2.55),
        ("11622","Excision, malignant lesion, scalp, neck, hands, feet, genitalia; 1.1-2.0 cm",2.95),
        ("11623","Excision, malignant lesion, scalp, neck, hands, feet, genitalia; 2.1-3.0 cm",3.45),
        ("11624","Excision, malignant lesion, scalp, neck, hands, feet, genitalia; 3.1-4.0 cm",3.85),
        ("11626","Excision, malignant lesion, scalp, neck, hands, feet, genitalia; over 4.0 cm",4.55),
        ("11640","Excision, malignant lesion, face, ears, eyelids, nose, lips; 0.5 cm or less",2.35),
        ("11641","Excision, malignant lesion, face, ears, eyelids, nose, lips; 0.6-1.0 cm",2.85),
        ("11642","Excision, malignant lesion, face, ears, eyelids, nose, lips; 1.1-2.0 cm",3.35),
        ("11643","Excision, malignant lesion, face, ears, eyelids, nose, lips; 2.1-3.0 cm",3.85),
        ("11644","Excision, malignant lesion, face, ears, eyelids, nose, lips; 3.1-4.0 cm",4.35),
        ("11646","Excision, malignant lesion, face, ears, eyelids, nose, lips; over 4.0 cm",5.15),
    ]
    for code,desc,rvu in excision:
        c.append(mc(code,desc,S,"excision",D,rvu,10,False))
    
    # Biopsy codes
    biopsy = [
        ("11102","Tangential biopsy of skin; first lesion",1.05),
        ("11103","Tangential biopsy of skin; each separate/additional lesion",0.45),
        ("11104","Punch biopsy of skin; first lesion",1.15),
        ("11105","Punch biopsy of skin; each separate/additional lesion",0.55),
        ("11106","Incisional biopsy of skin; first lesion",1.55),
        ("11107","Incisional biopsy of skin; each separate/additional lesion",0.65),
    ]
    for code,desc,rvu in biopsy:
        addon = code in ("11103","11105","11107")
        c.append(mc(code,desc,S,"biopsy",D,rvu,0,False,addon=addon))

    # === 7. PULMONARY (~80 codes) ===
    P = "pulmonary"
    # Bronchoscopy 31615-31654
    bronch = [
        ("31615","Tracheobronchoscopy through established tracheostomy stoma",2.85),
        ("31622","Bronchoscopy, rigid or flexible; diagnostic, with cell washing",3.55),
        ("31623","Bronchoscopy; with brushing or protected brushings",3.85),
        ("31624","Bronchoscopy; with bronchial alveolar lavage",3.75),
        ("31625","Bronchoscopy; with bronchial or endobronchial biopsy(s), single or multiple sites",4.25),
        ("31626","Bronchoscopy; with placement of fiducial markers",4.55),
        ("31627","Bronchoscopy; with computer-assisted, image-guided navigation",3.15),
        ("31628","Bronchoscopy; with transbronchial lung biopsy(s), single lobe",5.25),
        ("31629","Bronchoscopy; with transbronchial needle aspiration biopsy(s), trachea, main stem and/or lobar bronchus(i)",4.85),
        ("31630","Bronchoscopy; with tracheal/bronchial dilation or closed reduction of fracture",5.55),
        ("31631","Bronchoscopy; with tracheal dilation and placement of tracheal stent",6.85),
        ("31632","Bronchoscopy; with transbronchial lung biopsy(s), each additional lobe",1.55),
        ("31633","Bronchoscopy; with transbronchial needle aspiration biopsy(s), each additional lobe",1.25),
        ("31634","Bronchoscopy; with balloon occlusion, with assessment of air leak, when performed",4.55),
        ("31635","Bronchoscopy; with removal of foreign body",5.25),
        ("31636","Bronchoscopy; with placement of bronchial stent(s), includes tracheal/bronchial dilation",7.55),
        ("31637","Bronchoscopy; each additional major bronchus stented",2.55),
        ("31638","Bronchoscopy; with revision of tracheal or bronchial stent inserted at previous session",6.55),
        ("31640","Bronchoscopy; with excision of tumor",6.25),
        ("31641","Bronchoscopy; with destruction of tumor or relief of stenosis by any method other than excision",6.55),
        ("31643","Bronchoscopy; with placement of catheter(s) for intracavitary radioelement application",5.25),
        ("31645","Bronchoscopy; with therapeutic aspiration of tracheobronchial tree, initial",3.25),
        ("31646","Bronchoscopy; with therapeutic aspiration, subsequent",2.85),
        ("31647","Bronchoscopy; with balloon occlusion",4.25),
        ("31648","Bronchoscopy; with removal of bronchial valve(s), initial",5.55),
        ("31649","Bronchoscopy; with removal of bronchial valve(s), each additional lobe",2.25),
        ("31651","Bronchoscopy; with balloon occlusion, with assessment of air leak",4.85),
        ("31652","Bronchoscopy; with endobronchial ultrasound (EBUS) guided transtracheal and/or transbronchial sampling, 1-2 nodes",6.55),
        ("31653","Bronchoscopy; with EBUS guided sampling, 3 or more nodes",7.55),
        ("31654","Bronchoscopy; with transendoscopic endobronchial ultrasound (EBUS) during bronchoscopic diagnostic or therapeutic intervention(s) for peripheral lesion(s)",5.85),
    ]
    for code,desc,rvu in bronch:
        addon = code in ("31632","31633","31637","31649","31627")
        c.append(mc(code,desc,S,"bronchoscopy",P,rvu,0,False,addon=addon))
    
    # PFT codes 94010-94799
    pft = [
        ("94010","Spirometry, including graphic record, total and timed vital capacity, expiratory flow rate measurement(s)",0.55),
        ("94011","Spirometry with forced expiratory maneuvers, for children through 2 years",0.65),
        ("94012","Measurement of spirometric forced expiratory flows in an infant or child through 2 years of age",0.65),
        ("94013","Measurement of lung volumes in an infant or child through 2 years of age",0.85),
        ("94014","Patient-initiated spirometric recording per 30-day period of time",0.15),
        ("94015","Patient-initiated spirometric recording per 30-day period; recording only",0.10),
        ("94016","Patient-initiated spirometric recording per 30-day period; review and interpretation only",0.15),
        ("94060","Bronchodilation responsiveness, spirometry as in 94010, pre and post bronchodilator administration",0.75),
        ("94070","Bronchospasm provocation evaluation, multiple spirometric determinations after allergen, cold air, methacholine",1.25),
        ("94150","Vital capacity, total",0.25),
        ("94200","Maximum breathing capacity, maximal voluntary ventilation",0.25),
        ("94250","Expired gas collection, quantitative, single procedure",0.15),
        ("94375","Respiratory flow volume loop",0.25),
        ("94400","Breathing response to CO2 (CO2 response curve)",0.55),
        ("94450","Breathing response to hypoxia (hypoxia response curve)",0.55),
        ("94452","High altitude simulation test (HAST)",0.85),
        ("94453","High altitude simulation test with supplemental oxygen titration",1.05),
        ("94610","Intrapulmonary surfactant administration by physician or other qualified health care professional through endotracheal tube",1.85),
        ("94617","Exercise test for bronchospasm, including pre and post spirometry and pulse oximetry",1.55),
        ("94618","Pulmonary stress testing (eg, 6-minute walk test), including measurement of heart rate, oximetry, and oxygen titration",0.55),
        ("94621","Cardiopulmonary exercise testing, including measurements of minute ventilation, CO2 production, O2 uptake, and electrocardiographic recordings",2.85),
        ("94640","Pressurized or nonpressurized inhalation treatment for acute airway obstruction",0.25),
        ("94642","Aerosol inhalation of pentamidine for pneumocystis carinii pneumonia treatment/prophylaxis",0.25),
        ("94644","Continuous inhalation treatment with aerosol medication for acute airway obstruction; first hour",0.55),
        ("94645","Continuous inhalation treatment; each additional hour",0.25),
        ("94660","Continuous positive airway pressure ventilation (CPAP), initiation and management",1.55),
        ("94662","Continuous negative pressure ventilation (CNP), initiation and management",1.55),
        ("94664","Demonstration and/or evaluation of patient utilization of an aerosol generator, nebulizer, metered dose inhaler or IPPB device",0.25),
        ("94667","Manipulation chest wall, such as cupping, percussing, and vibration to facilitate lung function; initial demonstration and/or evaluation",0.35),
        ("94668","Manipulation chest wall; subsequent",0.25),
        ("94669","Mechanical chest wall oscillation to facilitate lung function",0.25),
        ("94680","Oxygen uptake, expired gas analysis; rest and exercise, direct, simple",0.85),
        ("94681","Oxygen uptake, expired gas analysis; including CO2 output, percentage oxygen extracted",1.15),
        ("94690","Oxygen uptake, expired gas analysis; rest, indirect",0.55),
        ("94726","Plethysmography for determination of lung volumes and, when performed, airway resistance",0.55),
        ("94727","Gas dilution or washout for determination of lung volumes and, when performed, distribution of ventilation and closing volumes",0.55),
        ("94728","Airway resistance by impulse oscillometry",0.55),
        ("94729","Diffusing capacity (eg, carbon monoxide, membrane) (DLCO)",0.55),
        ("94750","Pulmonary compliance study",0.55),
        ("94760","Noninvasive ear or pulse oximetry for oxygen saturation; single determination",0.10),
        ("94761","Noninvasive ear or pulse oximetry; multiple determinations",0.15),
        ("94762","Noninvasive ear or pulse oximetry; by continuous overnight monitoring",0.15),
        ("94770","Carbon dioxide, expired gas determination by infrared analyzer",0.15),
        ("94772","Circadian respiratory pattern recording (pediatric pneumogram), 12-24 hour continuous recording",0.85),
        ("94774","Pediatric home apnea monitoring event recording including respiratory rate, pattern and heart rate per 30-day period; complete system",0.55),
        ("94775","Pediatric home apnea monitoring; recording only",0.25),
        ("94776","Pediatric home apnea monitoring; review and interpretation only",0.35),
        ("94777","Pediatric home apnea monitoring; physician review and interpretation only",0.35),
        ("94780","Car seat/bed testing for airway integrity, neonate, with continual nursing observation and continuous recording of pulse oximetry, oxygen saturation, and heart rate, over 60 minutes",0.35),
        ("94781","Car seat/bed testing; each additional full 60 minutes",0.15),
        ("94799","Unlisted pulmonary service or procedure",0.00),
    ]
    for code,desc,rvu in pft:
        addon = code in ("94645","94781")
        c.append(mc(code,desc,"Medicine","pulmonary_function",P,rvu,0,False,addon=addon))
    
    # Chest tube / Thoracentesis
    chest_proc = [
        ("32551","Tube thoracostomy, includes connection to drainage system; includes imaging guidance",4.55),
        ("32552","Removal of indwelling tunneled pleural catheter with cuff",2.25),
        ("32553","Placement of interstitial device(s) for radiation therapy guidance, percutaneous, intrathoracic",4.85),
        ("32554","Thoracentesis, needle or catheter, aspiration of the pleural space; without imaging guidance",2.25),
        ("32555","Thoracentesis, needle or catheter, aspiration of the pleural space; with imaging guidance",2.55),
        ("32556","Pleural drainage, percutaneous, with insertion of indwelling catheter; without imaging guidance",3.85),
        ("32557","Pleural drainage, percutaneous, with insertion of indwelling catheter; with imaging guidance",4.15),
    ]
    for code,desc,rvu in chest_proc:
        c.append(mc(code,desc,S,"thoracic_procedures",P,rvu,0,False))

    # === 8. PSYCHIATRY/BEHAVIORAL (~50 codes) ===
    PSY = "psychiatry"
    psych = [
        ("90785","Interactive complexity (add-on to primary procedure)",1.05,True),
        ("90791","Psychiatric diagnostic evaluation",5.55,False),
        ("90792","Psychiatric diagnostic evaluation with medical services",6.25,False),
        ("90832","Psychotherapy, 30 minutes with patient",2.45,False),
        ("90833","Psychotherapy, 30 minutes with patient when performed with E/M service",1.55,True),
        ("90834","Psychotherapy, 45 minutes with patient",3.25,False),
        ("90836","Psychotherapy, 45 minutes with patient when performed with E/M service",2.25,True),
        ("90837","Psychotherapy, 60 minutes with patient",4.25,False),
        ("90838","Psychotherapy, 60 minutes with patient when performed with E/M service",3.15,True),
        ("90839","Psychotherapy for crisis; first 60 minutes",5.55,False),
        ("90840","Psychotherapy for crisis; each additional 30 minutes",2.85,True),
        ("90845","Psychoanalysis",4.55,False),
        ("90846","Family psychotherapy without the patient present, 50 minutes",3.55,False),
        ("90847","Family psychotherapy with the patient present, 50 minutes",3.85,False),
        ("90849","Multiple-family group psychotherapy",1.55,False),
        ("90853","Group psychotherapy (other than of a multiple-family group)",1.25,False),
        ("90863","Pharmacologic management, including prescription and review of medication, when performed with psychotherapy",0.00,True),
        ("90865","Narcosynthesis for psychiatric diagnostic and therapeutic purposes",3.55,False),
        ("90867","Therapeutic repetitive transcranial magnetic stimulation (TMS) treatment; initial, including cortical mapping, motor threshold determination, delivery and management",4.55,False),
        ("90868","TMS treatment; subsequent delivery and management, per session",2.25,False),
        ("90869","TMS treatment; subsequent motor threshold re-determination with delivery and management",3.15,False),
        ("90870","Electroconvulsive therapy",3.85,False),
        ("90875","Individual psychophysiological therapy with biofeedback training by any modality, 30 minutes",1.55,False),
        ("90876","Individual psychophysiological therapy with biofeedback training by any modality, 45 minutes",2.25,False),
        ("90880","Hypnotherapy",2.55,False),
        ("90882","Environmental intervention for medical management purposes on a psychiatric patient's behalf",1.25,False),
        ("90885","Psychiatric evaluation of hospital records, other psychiatric reports, psychometric and/or projective tests",1.55,False),
        ("90887","Interpretation or explanation of results of psychiatric, other medical examinations and procedures to family or other responsible persons",1.25,False),
        ("90889","Preparation of report of patient's psychiatric status, history, treatment, or progress for other individuals, agencies, or insurance carriers",1.55,False),
        ("96130","Psychological testing evaluation services by physician or other qualified health care professional; first hour",4.55,False),
        ("96131","Psychological testing evaluation services; each additional hour",3.85,True),
        ("96132","Neuropsychological testing evaluation services by physician or other qualified health care professional; first hour",5.25,False),
        ("96133","Neuropsychological testing evaluation services; each additional hour",4.55,True),
        ("96136","Psychological or neuropsychological test administration and scoring by physician; first 30 minutes",1.55,False),
        ("96137","Psychological or neuropsychological test administration and scoring; each additional 30 minutes",1.25,True),
        ("96138","Psychological or neuropsychological test administration and scoring by technician; first 30 minutes",0.55,False),
        ("96139","Psychological or neuropsychological test administration and scoring by technician; each additional 30 minutes",0.45,True),
    ]
    for code,desc,rvu,addon in psych:
        c.append(mc(code,desc,"Medicine","psychotherapy" if "90" == code[:2] else "testing",PSY,rvu,0,False,addon=addon))

    # === 9. PHYSICAL MEDICINE (~80 codes) ===
    PM = "physical_medicine"
    pt_ot = [
        ("97010","Application of hot or cold packs",0.00),
        ("97012","Application of mechanical traction",0.25),
        ("97014","Application of electrical stimulation (unattended)",0.25),
        ("97016","Vasopneumatic devices",0.15),
        ("97018","Paraffin bath",0.15),
        ("97022","Whirlpool",0.15),
        ("97024","Diathermy",0.15),
        ("97026","Infrared",0.10),
        ("97028","Ultraviolet",0.15),
        ("97032","Application of electrical stimulation, each 15 minutes",0.45),
        ("97033","Application of iontophoresis, each 15 minutes",0.45),
        ("97034","Contrast baths, each 15 minutes",0.25),
        ("97035","Application of ultrasound, each 15 minutes",0.35),
        ("97036","Application of Hubbard tank, each 15 minutes",0.55),
        ("97039","Unlisted modality",0.00),
        ("97110","Therapeutic procedure, 1 or more areas, each 15 minutes; therapeutic exercises",1.05),
        ("97112","Therapeutic procedure; neuromuscular reeducation",1.05),
        ("97113","Therapeutic procedure; aquatic therapy with therapeutic exercises",1.05),
        ("97116","Therapeutic procedure; gait training",0.95),
        ("97124","Therapeutic procedure; massage, including effleurage, petrissage and/or tapotement",0.85),
        ("97129","Therapeutic interventions that focus on cognitive function; initial 15 minutes",1.25),
        ("97130","Therapeutic interventions that focus on cognitive function; each additional 15 minutes",1.05),
        ("97139","Unlisted therapeutic procedure",0.00),
        ("97140","Manual therapy techniques; 1 or more regions, each 15 minutes",0.85),
        ("97150","Therapeutic procedure(s), group (2 or more individuals)",0.55),
        ("97161","Physical therapy evaluation: low complexity",2.05),
        ("97162","Physical therapy evaluation: moderate complexity",2.55),
        ("97163","Physical therapy evaluation: high complexity",3.15),
        ("97164","Physical therapy re-evaluation",1.55),
        ("97165","Occupational therapy evaluation: low complexity",2.05),
        ("97166","Occupational therapy evaluation: moderate complexity",2.55),
        ("97167","Occupational therapy evaluation: high complexity",3.15),
        ("97168","Occupational therapy re-evaluation",1.55),
        ("97169","Athletic training evaluation: low complexity",2.05),
        ("97170","Athletic training evaluation: moderate complexity",2.55),
        ("97171","Athletic training evaluation: high complexity",3.15),
        ("97172","Athletic training re-evaluation",1.55),
        ("97530","Therapeutic activities, direct patient contact, each 15 minutes",1.05),
        ("97533","Sensory integrative techniques, each 15 minutes",0.95),
        ("97535","Self-care/home management training, each 15 minutes",0.95),
        ("97537","Community/work reintegration training, each 15 minutes",0.95),
        ("97542","Wheelchair management, each 15 minutes",0.95),
        ("97545","Work hardening/conditioning; initial 2 hours",3.55),
        ("97546","Work hardening/conditioning; each additional hour",1.55),
        ("97597","Debridement, open wound; first 20 sq cm",2.25),
        ("97598","Debridement, open wound; each additional 20 sq cm",0.85),
        ("97602","Removal of devitalized tissue from wound(s), non-selective debridement",0.25),
        ("97605","Negative pressure wound therapy; first 50 sq cm",1.55),
        ("97606","Negative pressure wound therapy; each additional 50 sq cm",0.55),
        ("97607","Negative pressure wound therapy using disposable, non-durable device; including provision of exudate management collection system, per session",0.55),
        ("97608","Negative pressure wound therapy using disposable device; each additional 50 sq cm",0.25),
        ("97610","Low frequency, non-contact, non-thermal ultrasound, including topical application(s)",0.55),
        ("97750","Physical performance test or measurement, each 15 minutes",0.55),
        ("97755","Assistive technology assessment, each 15 minutes",0.85),
        ("97760","Orthotic(s) management and training, initial encounter, each 15 minutes",0.65),
        ("97761","Prosthetic(s) training, initial encounter, each 15 minutes",0.65),
        ("97763","Orthotic/prosthetic management, subsequent encounter, each 15 minutes",0.55),
        ("97799","Unlisted physical medicine/rehabilitation service or procedure",0.00),
    ]
    for code,desc,rvu in pt_ot:
        addon = code in ("97130","97546","97598","97606","97608")
        c.append(mc(code,desc,"Medicine","physical_therapy",PM,rvu,0,False,addon=addon))
    
    # Chiropractic
    chiro = [
        ("98940","Chiropractic manipulative treatment (CMT); spinal, 1-2 regions",1.05),
        ("98941","CMT; spinal, 3-4 regions",1.55),
        ("98942","CMT; spinal, 5 regions",2.05),
        ("98943","CMT; extraspinal, 1 or more regions",0.65),
    ]
    for code,desc,rvu in chiro:
        c.append(mc(code,desc,"Medicine","chiropractic",PM,rvu,0,False))
    
    # Acupuncture
    acu = [
        ("97810","Acupuncture, 1 or more needles; without electrical stimulation, initial 15 minutes",1.25),
        ("97811","Acupuncture; without electrical stimulation, each additional 15 minutes",0.85),
        ("97813","Acupuncture; with electrical stimulation, initial 15 minutes",1.35),
        ("97814","Acupuncture; with electrical stimulation, each additional 15 minutes",0.95),
    ]
    for code,desc,rvu in acu:
        addon = code in ("97811","97814")
        c.append(mc(code,desc,"Medicine","acupuncture",PM,rvu,0,False,addon=addon))
    
    # Biofeedback
    for code,desc,rvu in [
        ("90901","Biofeedback training by any modality",1.25),
        ("90912","Biofeedback training, perineal muscles, anorectal or urethral sphincter; initial 15 minutes",1.55),
        ("90913","Biofeedback training, perineal muscles; each additional 15 minutes",0.85)]:
        addon = code == "90913"
        c.append(mc(code,desc,"Medicine","biofeedback",PM,rvu,0,False,addon=addon))

    # === 10. NERVE BLOCKS/INJECTIONS (~100 codes) ===
    NB = "pain_management"
    # Epidural codes
    epidural = [
        ("62320","Injection(s), of diagnostic or therapeutic substance(s), not including neurolytic substances, including needle or catheter placement; cervical or thoracic, without imaging guidance",2.25),
        ("62321","Injection(s), cervical or thoracic; with imaging guidance (fluoroscopy or CT)",2.85),
        ("62322","Injection(s), lumbar or sacral (caudal); without imaging guidance",1.85),
        ("62323","Injection(s), lumbar or sacral (caudal); with imaging guidance (fluoroscopy or CT)",2.45),
        ("62324","Injection(s), including indwelling catheter placement, continuous infusion or intermittent bolus; cervical or thoracic, without imaging guidance",3.55),
        ("62325","Injection(s), including indwelling catheter placement; cervical or thoracic, with imaging guidance",4.15),
        ("62326","Injection(s), including indwelling catheter placement; lumbar or sacral (caudal), without imaging guidance",3.15),
        ("62327","Injection(s), including indwelling catheter placement; lumbar or sacral (caudal), with imaging guidance",3.75),
        ("62350","Implantation, revision or repositioning of tunneled intrathecal or epidural catheter for long-term medication administration via an external pump or implantable reservoir/infusion pump; without laminectomy",6.85),
        ("62351","Implantation, revision or repositioning of tunneled catheter; with laminectomy",10.55),
        ("62355","Removal of previously implanted intrathecal or epidural catheter",2.55),
        ("62360","Implantation or replacement of device for intrathecal or epidural drug infusion; subcutaneous reservoir",4.55),
        ("62361","Implantation or replacement of device; non-programmable pump",5.85),
        ("62362","Implantation or replacement of device; programmable pump, including preparation of pump",7.25),
        ("62365","Removal of subcutaneous reservoir or pump, previously implanted intrathecal or epidural infusion device",3.85),
        ("62367","Electronic analysis of programmable, implanted pump for intrathecal or epidural drug infusion; without reprogramming or refill",0.55),
        ("62368","Electronic analysis of programmable pump; with reprogramming",0.85),
        ("62369","Electronic analysis of programmable pump; with reprogramming and refill",1.15),
        ("62370","Electronic analysis of programmable pump; with reprogramming and refill requiring skill of physician",1.45),
    ]
    for code,desc,rvu in epidural:
        c.append(mc(code,desc,S,"epidural",NB,rvu,0,False))
    
    # Facet joint codes
    facet = [
        ("64490","Injection(s), diagnostic or therapeutic agent, paravertebral facet (zygapophyseal) joint (or nerves innervating that joint) with image guidance; cervical or thoracic, single level",2.55),
        ("64491","Injection(s), paravertebral facet; cervical or thoracic, second level",1.25),
        ("64492","Injection(s), paravertebral facet; cervical or thoracic, third and any additional level(s)",0.85),
        ("64493","Injection(s), diagnostic or therapeutic agent, paravertebral facet joint; lumbar or sacral, single level",2.25),
        ("64494","Injection(s), paravertebral facet; lumbar or sacral, second level",1.15),
        ("64495","Injection(s), paravertebral facet; lumbar or sacral, third and any additional level(s)",0.75),
        ("64633","Destruction by neurolytic agent, paravertebral facet joint nerve(s), with imaging guidance; cervical or thoracic, single facet joint",4.55),
        ("64634","Destruction by neurolytic agent; cervical or thoracic, each additional facet joint",1.85),
        ("64635","Destruction by neurolytic agent, paravertebral facet joint nerve(s); lumbar or sacral, single facet joint",4.25),
        ("64636","Destruction by neurolytic agent; lumbar or sacral, each additional facet joint",1.65),
    ]
    for code,desc,rvu in facet:
        addon = code in ("64491","64492","64494","64495","64634","64636")
        c.append(mc(code,desc,S,"facet_joint",NB,rvu,0,False,addon=addon))
    
    # Trigger point injections
    for code,desc,rvu in [
        ("20552","Injection(s); single or multiple trigger point(s), 1 or 2 muscle(s)",1.25),
        ("20553","Injection(s); single or multiple trigger point(s), 3 or more muscle(s)",1.55)]:
        c.append(mc(code,desc,S,"trigger_point",NB,rvu,0,False))
    
    # Joint/Bursa injections
    joint_inj = [
        ("20600","Arthrocentesis, aspiration and/or injection, small joint or bursa; without ultrasound guidance",1.05),
        ("20604","Arthrocentesis, aspiration and/or injection, small joint or bursa; with ultrasound guidance",1.35),
        ("20605","Arthrocentesis, aspiration and/or injection, intermediate joint or bursa; without ultrasound guidance",1.15),
        ("20606","Arthrocentesis, aspiration and/or injection, intermediate joint or bursa; with ultrasound guidance",1.45),
        ("20610","Arthrocentesis, aspiration and/or injection, major joint or bursa; without ultrasound guidance",1.55),
        ("20611","Arthrocentesis, aspiration and/or injection, major joint or bursa; with ultrasound guidance",1.85),
    ]
    for code,desc,rvu in joint_inj:
        c.append(mc(code,desc,S,"joint_injection",NB,rvu,0,True))
    
    # Nerve blocks - peripheral
    nerve_blocks = [
        ("64400","Injection, anesthetic agent; trigeminal nerve, any division or branch",1.55),
        ("64405","Injection, anesthetic agent; greater occipital nerve",1.25),
        ("64408","Injection, anesthetic agent; vagus nerve",1.55),
        ("64415","Injection, anesthetic agent; brachial plexus, single",2.25),
        ("64416","Injection, anesthetic agent; brachial plexus, continuous infusion by catheter",3.55),
        ("64417","Injection, anesthetic agent; axillary nerve",1.85),
        ("64418","Injection, anesthetic agent; suprascapular nerve",1.55),
        ("64420","Injection, anesthetic agent; intercostal nerve, single",1.25),
        ("64421","Injection, anesthetic agent; intercostal nerves, multiple, regional block",2.55),
        ("64425","Injection, anesthetic agent; ilioinguinal, iliohypogastric nerves",1.55),
        ("64430","Injection, anesthetic agent; pudendal nerve",1.55),
        ("64435","Injection, anesthetic agent; paracervical (uterine) nerve",1.85),
        ("64445","Injection, anesthetic agent; sciatic nerve, single",2.25),
        ("64446","Injection, anesthetic agent; sciatic nerve, continuous infusion by catheter",3.55),
        ("64447","Injection, anesthetic agent; femoral nerve, single",2.05),
        ("64448","Injection, anesthetic agent; femoral nerve, continuous infusion by catheter",3.25),
        ("64449","Injection, anesthetic agent; lumbar plexus, posterior approach, continuous infusion by catheter",3.85),
        ("64450","Injection, anesthetic agent; other peripheral nerve or branch",1.25),
        ("64451","Injection(s), anesthetic agent(s) and/or steroid; nerves innervating the sacroiliac joint, with image guidance",2.55),
        ("64454","Injection(s), anesthetic agent(s) and/or steroid; genicular nerve branches, including imaging guidance, when performed",2.25),
        ("64455","Injection(s), anesthetic agent and/or steroid; plantar common digital nerve(s)",1.25),
        ("64461","Paravertebral block (PVB); thoracic; single injection site",2.15),
        ("64462","Paravertebral block (PVB); thoracic; second injection site",1.15),
        ("64463","Paravertebral block (PVB); thoracic; continuous infusion by catheter",3.55),
    ]
    for code,desc,rvu in nerve_blocks:
        addon = code in ("64462",)
        c.append(mc(code,desc,S,"nerve_block",NB,rvu,0,False,addon=addon))
    
    # Sympathetic blocks
    symp = [
        ("64505","Injection, anesthetic agent; sphenopalatine ganglion",1.55),
        ("64508","Injection, anesthetic agent; carotid sinus (separate procedure)",1.85),
        ("64510","Injection, anesthetic agent; stellate ganglion (cervical sympathetic)",2.25),
        ("64517","Injection, anesthetic agent; superior hypogastric plexus",3.55),
        ("64520","Injection, anesthetic agent; lumbar or thoracic (paravertebral sympathetic)",2.55),
        ("64530","Injection, anesthetic agent; celiac plexus, with or without radiologic monitoring",3.85),
    ]
    for code,desc,rvu in symp:
        c.append(mc(code,desc,S,"sympathetic_block",NB,rvu,0,False))
    
    # Neurolytic blocks
    neurolytic = [
        ("64600","Destruction by neurolytic agent, trigeminal nerve; supraorbital, infraorbital, mental, or inferior alveolar branch",3.55),
        ("64605","Destruction by neurolytic agent, trigeminal nerve; second and third division branches at foramen ovale",5.55),
        ("64610","Destruction by neurolytic agent, trigeminal nerve; second and third division branches at foramen ovale under radiologic monitoring",6.25),
        ("64620","Destruction by neurolytic agent, intercostal nerve",2.55),
        ("64624","Destruction by neurolytic agent, genicular nerve branches including imaging guidance",4.55),
        ("64625","Radiofrequency ablation, nerves innervating the sacroiliac joint, with image guidance",5.25),
        ("64628","Destruction by neurolytic agent, other peripheral nerve or branch; single",2.85),
        ("64629","Destruction by neurolytic agent, other peripheral nerve or branch; each additional",1.55),
        ("64640","Destruction by neurolytic agent; other peripheral nerve or branch",2.55),
        ("64680","Destruction by neurolytic agent, with or without radiologic monitoring; celiac plexus",4.85),
        ("64681","Destruction by neurolytic agent, with or without radiologic monitoring; superior hypogastric plexus",4.55),
    ]
    for code,desc,rvu in neurolytic:
        addon = code == "64629"
        c.append(mc(code,desc,S,"neurolytic",NB,rvu,0,False,addon=addon))
    
    # Spinal cord stimulator
    scs = [
        ("63650","Percutaneous implantation of neurostimulator electrode array, epidural",6.55),
        ("63655","Laminectomy for implantation of neurostimulator electrodes, plate/paddle, epidural",12.25),
        ("63661","Removal of spinal neurostimulator electrode percutaneous array(s), including fluoroscopy, when performed",3.85),
        ("63662","Removal of spinal neurostimulator electrode plate/paddle(s), including fluoroscopy, when performed, by laminotomy or laminectomy",10.55),
        ("63663","Revision including replacement of spinal neurostimulator electrode percutaneous array(s)",5.55),
        ("63664","Revision including replacement of spinal neurostimulator electrode plate/paddle(s)",11.85),
        ("63685","Insertion or replacement of spinal neurostimulator pulse generator or receiver",4.85),
        ("63688","Revision or removal of implanted spinal neurostimulator pulse generator or receiver",3.55),
    ]
    for code,desc,rvu in scs:
        c.append(mc(code,desc,S,"neurostimulator",NB,rvu,90,False,asst=rvu>8))
    
    # Sacroiliac joint injections
    for code,desc,rvu in [
        ("27096","Injection procedure for sacroiliac joint, anesthetic/steroid, with image guidance including fluoroscopy or CT",2.55)]:
        c.append(mc(code,desc,S,"si_joint",NB,rvu,0,False))

    return c


def main():
    print(f"Loading database from {DB_PATH}...")
    with open(DB_PATH, "r") as f:
        db = json.load(f)
    
    original_count = len(db)
    print(f"Original count: {original_count}")
    
    new_codes = gen_all()
    print(f"Generated {len(new_codes)} new codes")
    
    added = 0
    skipped = 0
    for entry in new_codes:
        code = entry["code"]
        if code not in db:
            db[code] = entry
            added += 1
        else:
            skipped += 1
    
    final_count = len(db)
    print(f"Added: {added}, Skipped (already exist): {skipped}")
    print(f"Final count: {final_count}")
    
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2)
    
    # Verify
    with open(DB_PATH, "r") as f:
        verify = json.load(f)
    print(f"Verification: JSON valid, {len(verify)} entries")
    
    # Category breakdown
    cats = {}
    for v in verify.values():
        sub = v.get("subcategory") or "none"
        cats[sub] = cats.get(sub, 0) + 1
    
    print("\nSubcategory breakdown of NEW codes:")
    for sub in sorted(cats.keys()):
        print(f"  {sub}: {cats[sub]}")

if __name__ == "__main__":
    main()
