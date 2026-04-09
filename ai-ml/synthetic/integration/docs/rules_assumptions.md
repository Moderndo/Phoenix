# AI005 Rules and Assumptions

1. The disaster dataset is the parent source for the integrated dataset.
2. Final hazard_event_id values come from the disaster parent dataset.
3. Cyber and misinformation rows are linked to parent disaster events.
4. Severity labels are standardized:
   - moderate -> moderate
   - severe -> severe
   - extreme -> extreme
   - high -> severe
   - critical -> extreme
   - minor -> minor is retained in the parent dataset but excluded from standardized scenario matching if needed.
5. threat_stream identifies the source scenario type:
   - cyber
   - misinformation
6. For cyber rows, original generated hazard_event_id values are preserved as source_record_id context only if needed, but parent hazard_event_id is used in the final master file.
7. For misinformation rows, hazard_event_id is already compatible with disaster parent IDs.
8. Latitude and longitude from misinformation data are not used in the final master schema because the parent disaster dataset does not use them.
9. Parent disaster location fields are the canonical location fields for final outputs.