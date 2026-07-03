# Chest Wall Reconstruction Clinical Validation

Status: PASS

## Reference Case Selected vs Payable

{
  "selected_cpts": [
    "21811",
    "64420",
    "64620",
    "32551"
  ],
  "payable_cpts": [
    "21811",
    "64420",
    "64620"
  ],
  "excluded_cpts": [
    "32551"
  ],
  "selected_work_rvu": 17.35,
  "expected_payable_work_rvu": 12.46,
  "expected_medicare_payment_total_rvu_basis": 876.44
}

## S27.33 ICD-10 Family

Total descendants: 13
Billable children: 9
Billable codes: S27331A, S27331D, S27331S, S27332A, S27332D, S27332S, S27339A, S27339D, S27339S

## Case Matrix

### reference_left_10th_rib_nonunion_with_cryo_and_port_chest_tube
Supported CPTs: 21811, 32551, 64420, 64620
Unsupported CPTs: 21812, 21813, 32110, 32320, 32651, 36620, 64421, 64461
ICD-10: S22.32XK
Flags: 32551_routine_drainage_bundle_risk, additional_intercostal_block_levels_require_64421_review, arterial_line_not_supported_by_surgeon_narrative, cryoablation_maps_to_64620_not_64421

### simple_rib_plating
Supported CPTs: 21811
Unsupported CPTs: 21812, 21813, 32110, 32320, 32651, 64461
ICD-10: none
Flags: none

### flail_chest_seven_rib_fixation
Supported CPTs: 21813
Unsupported CPTs: 32110, 32320, 32651, 64461
ICD-10: S22.5XXA
Flags: none

### lung_laceration_repair
Supported CPTs: none
Unsupported CPTs: 32110, 32320, 32651, 64461
ICD-10: S27.0XXA, S27.331A
Flags: none

### vats_converted_to_thoracotomy_decortication
Supported CPTs: 32651
Unsupported CPTs: 32110, 64461
ICD-10: none
Flags: none

### chest_tube_before_thoracotomy
Supported CPTs: 32551
Unsupported CPTs: 32110, 32320, 32651, 64461
ICD-10: S27.0XXA
Flags: none

### chest_tube_through_thoracotomy_field
Supported CPTs: 32551
Unsupported CPTs: 32110, 32320, 32651, 64461
ICD-10: none
Flags: 32551_routine_drainage_bundle_risk

### multiple_intercostal_nerve_blocks
Supported CPTs: 64420
Unsupported CPTs: 32110, 32320, 32651, 64461
ICD-10: none
Flags: additional_intercostal_block_levels_require_64421_review

### cryoablation_multiple_intercostal_nerves
Supported CPTs: 64620
Unsupported CPTs: 32110, 32320, 32651, 64421, 64461
ICD-10: none
Flags: cryoablation_maps_to_64620_not_64421

