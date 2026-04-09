# AI005 Master Dataset Schema

## Core parent fields
- hazard_event_id: Parent disaster event identifier
- integration_id: Parent integration UUID from disaster dataset
- event_type: Disaster type
- severity_score: Numeric disaster severity score
- severity_level: Standardized severity label
- risk_category: Disaster risk category
- start_time: Disaster start timestamp
- duration_hours: Duration of disaster event in hours

## Location fields
- state
- region
- suburb

## Weather fields
- temperature_c
- rainfall_mm
- humidity_pct

## Impact fields
- fatalities
- injuries
- economic_loss_million
- affected_population

## Integrated scenario fields
- threat_stream: cyber or misinformation
- source_record_id: Original record ID from source dataset
- source_dataset: Source file category
- timestamp: Event timestamp from source record
- threat_type
- attack_vector
- impersonation
- target
- outcome
- success
- confidence_score
- alert_level
- misinformation_level
- social_media_spike
- cyber_frequency_level
- risk_score

## Standardization notes
- Disaster parent dataset drives the final hazard_event_id
- Severity labels are standardized to moderate, severe, extreme
- high is mapped to severe
- critical is mapped to extreme