#!/usr/bin/env python3
import json, pathlib, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

ROOT=pathlib.Path(__file__).resolve().parent
ART=ROOT/'qa_artifacts'/'icd10_inpatient_compliance'
ART.mkdir(parents=True, exist_ok=True)
URL=ROOT.joinpath('index.html').as_uri()

def driver():
    opts=Options()
    opts.add_argument('--headless=new')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-gpu')
    opts.add_argument('--allow-file-access-from-files')
    opts.add_argument('--window-size=1500,1250')
    return webdriver.Chrome(options=opts)

def snap(d,name):
    d.save_screenshot(str(ART/f'{name}.png'))

def js(d,src,*args):
    return d.execute_script(src,*args)

def require(cond,msg):
    if not cond: raise AssertionError(msg)

def add(d,code):
    js(d,"addCptDirectly(arguments[0]);",code)
    time.sleep(.1)

def main():
    d=driver()
    results={}
    try:
        d.get(URL); time.sleep(1.0)
        stats=js(d,"return {icd:ICD10_ROWS.length,billable:ICD10_ROWS.filter(x=>x.billable).length,ipo:INPATIENT_ONLY_BY_CPT.size,version:ICD10_DATASET_META.version,ipoVersion:INPATIENT_ONLY_META.version};")
        require(stats['icd']>90000,'ICD database not loaded')
        require(stats['ipo']>1000,'IPO database not loaded')
        add(d,'44625')
        data=js(d,"addDiagnosis('K5720',{lineId:caseLines[0].id}); return {dx:caseDiagnoses,ptr:caseLines[0].dxPointers,warnings:validateDiagnosesForLine(caseLines[0]),suggestions:commonDxForCpt(caseLines[0]).map(x=>x.code)};")
        require(data['ptr']==['A'],'diagnosis pointer A missing')
        require('K5720' in data['suggestions'],'colorectal suggestions missing diverticulitis')
        snap(d,'01_colorectal_dx_pointers')
        results['colorectal'] = data

        search=js(d,"return {diverticulitis:searchIcd10('diverticulitis',5).map(x=>x.code),hernia:searchIcd10('hernia',5).map(x=>x.code),gallstones:searchIcd10('gallstones',5).map(x=>x.code),abscess:searchIcd10('abscess',5).map(x=>x.code),sbo:searchIcd10('SBO',5).map(x=>x.code),bowel:searchIcd10('bowel obstruction',5).map(x=>x.code)};")
        require(search['diverticulitis'] and search['hernia'] and search['gallstones'] and search['abscess'] and search['sbo'],'ICD search failed common term')
        results['search']=search

        d.get(URL); time.sleep(1.0)
        add(d,'32096')
        ipo=js(d,"return {panel:document.getElementById('ipoCasePanel').classList.contains('show'),line:caseLines[0].cpt,ipo:!!inpatientOnlyInfoForLine(caseLines[0]),body:document.body.textContent.includes('Inpatient-Only Procedure')||document.body.textContent.includes('inpatient-only')};")
        require(ipo['panel'] and ipo['ipo'],'IPO warning missing')
        snap(d,'02_inpatient_only_warning')
        results['ipo']=ipo

        d.get(URL); time.sleep(1.0)
        add(d,'44625'); add(d,'49402'); add(d,'11043')
        js(d,"addDiagnosis('K5720',{lineId:caseLines[0].id}); addDiagnosis('K651',{lineId:caseLines[1].id}); toggleDxPointer(caseLines[2].id,'B');")
        many=js(d,"return {diagnoses:caseDiagnoses.map((d,i)=>({letter:diagnosisLetter(i),code:d.code})),pointers:caseLines.map(l=>({cpt:l.cpt,ptr:l.dxPointers||[]})),total:document.getElementById('tn').textContent};")
        require(many['pointers'][0]['ptr']==['A'],'many-to-many first pointer missing')
        require('B' in many['pointers'][2]['ptr'],'many-to-many second pointer missing')
        snap(d,'03_many_to_many_dx')
        results['manyToMany']=many

        d.get(URL); time.sleep(1.0)
        add(d,'44625')
        js(d,"addDiagnosis('K57'); toggleDxPointer(caseLines[0].id,'A');")
        validation=js(d,"return {warnings:validateDiagnosesForLine(caseLines[0]),dx:caseDiagnoses[0]};")
        require(any('non-billable' in w for w in validation['warnings']),'non-billable warning missing')
        results['nonBillable']=validation

        export_data=js(d,"return {diagnosisDataset:ICD10_DATASET_META,inpatientOnlyDataset:INPATIENT_ONLY_META,diagnoses:caseDiagnoses.map((dx,i)=>({pointer:diagnosisLetter(i),code:displayIcd(dx.code)})),lines:caseLines.map(l=>({cpt:l.cpt,diagnosisPointers:l.dxPointers||[],diagnosisValidationWarnings:validateDiagnosesForLine(l),inpatientOnly:!!inpatientOnlyInfoForLine(l)}))};")
        require(export_data['diagnoses'][0]['pointer']=='A','export diagnosis pointer missing')
        results['exportShape']=export_data

        (ART/'icd10_inpatient_validation.json').write_text(json.dumps({'status':'pass','stats':stats,'results':results},indent=2),encoding='utf-8')
        print(json.dumps({'status':'pass','stats':stats,'artifactDir':str(ART)},indent=2))
    finally:
        d.quit()

if __name__=='__main__':
    main()

