# ICD-10 Procedure Family Architecture

## Data Flow

    CPT line
      -> CPT_PROCEDURE_FAMILY[cpt]
      -> PROCEDURE_FAMILIES[family].indications
      -> CLINICAL_INDICATION_GROUPS[indication].codes
      -> ICD10_ROWS / ICD10_BY_CODE metadata
      -> Common indications UI + CPT-card search ranking
      -> Diagnosis pointer map + export surfaces

## Current Family Map

    Tracheostomy Family
      -> Respiratory failure
      -> Ventilator dependence
      -> Airway obstruction
      -> Tracheal obstruction

    Gastrostomy Family
      -> Dysphagia
      -> Malnutrition
      -> Feeding difficulty
      -> Aspiration risk

    Colectomy Family
      -> Diverticulitis
      -> Colon cancer
      -> Volvulus
      -> Ischemic bowel
      -> Perforation
      -> Obstruction

    Hernia Family
      -> Inguinal hernia
      -> Femoral hernia
      -> Ventral hernia
      -> Incarcerated hernia
      -> Strangulated hernia

## Maintenance Pattern

    Add a new CPT:
      1. Add CPT_PROCEDURE_FAMILY['code']='family'
      2. Only add CPT_ICD10_ADDITIONS when the CPT needs diagnoses beyond family inheritance
      3. Add/adjust CLINICAL_INDICATION_GROUPS once when a concept should apply across multiple CPTs
