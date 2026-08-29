# Arkansas Residential Code and Requirement Sources

## Purpose

This document defines the initial source registry for new residential
construction and remodeling in Benton and Washington counties, Arkansas. It is
an implementation source map, not legal advice and not a substitute for an
AHJ determination.

**Verification snapshot:** 2026-08-29

RES Works must determine the exact authority having jurisdiction (AHJ) from
the parcel address before selecting rules. “Benton County” and “Washington
County” are not sufficient by themselves: incorporated cities may administer
their own permits, inspections, zoning, and local amendments.

## Governing hierarchy

1. Federal requirements when applicable.
2. Arkansas statutes and administrative rules.
3. The 2021 Arkansas Fire Prevention Code (AFPC), including Arkansas
   amendments.
4. Arkansas discipline-specific codes and energy requirements.
5. County requirements for an unincorporated parcel.
6. City ordinances, adopted codes, permits, and amendments for an incorporated
   parcel.
7. Floodplain, septic, utility, subdivision, easement, covenant, and other
   site-specific requirements.
8. Project-specific professional design, when required.

The most restrictive applicable requirement should not be assumed
automatically. Conflicts must be surfaced for AHJ or professional review.

## Statewide code registry

| Domain | Initial source / edition | Authority | RES Works treatment |
| --- | --- | --- | --- |
| Residential building and life safety | 2021 AFPC Volume III, based on the 2021 IRC with Arkansas amendments | Arkansas State Police / State Fire Marshal | Primary residential rule source; never copy full code text into the repo |
| Building code when IRC scope does not apply | 2021 AFPC Volume II, based on the 2021 IBC with Arkansas amendments | Arkansas State Police / State Fire Marshal | Route scope decision to IBC profile |
| Fire code | 2021 AFPC Volume I, based on the 2021 IFC with Arkansas amendments | Arkansas State Police / State Fire Marshal | Apply to fire/life-safety conditions within scope |
| Plumbing | 2018 Arkansas Plumbing Code | Arkansas Department of Health | Separate plumbing profile and licensed-trade review |
| Fuel gas | 2018 Arkansas Fuel Gas Code | Arkansas Department of Health | Separate gas profile and licensed-trade review |
| Energy | 2014 Arkansas Energy Code, based on 2009 IECC with Arkansas supplements/amendments | Arkansas Energy Office / ADEQ | Separate energy compliance workflow; verify current amendments before production use |
| Electrical | 2020 NEC as identified by Benton County; confirm AHJ/state administration for each project | Arkansas electrical authority / local AHJ | Do not infer from building-code profile; require jurisdiction confirmation |
| Mechanical | 2021 IMC as identified by Benton County; confirm AHJ for each project | Local AHJ / state licensing authority | Separate HVAC/mechanical profile |
| Accessibility | Project/use dependent; residential one- and two-family requirements differ from commercial/covered facilities | AFPC and applicable federal/state requirements | Never apply ADA as a blanket residential rule; classify occupancy and funding/use |
| Private sewage | Arkansas Department of Health and county requirements | ADH / county health authority | Require septic permit/PFO or public-sewer confirmation when applicable |
| Floodplain | NFIP requirements plus local flood-damage-prevention ordinance | County or city floodplain administrator | Require flood-zone and FIRM evidence before approval |

Primary sources:

- [2021 Arkansas Fire Prevention Code rules](https://www.dps.arkansas.gov/emergency-management/adem/state-fire-marshals-office/)
- [Official Code of Arkansas Rules](https://codeofarrules.arkansas.gov/)
- [Arkansas Plumbing and Natural Gas](https://healthy.arkansas.gov/programs-services/licensing-military-member-licensure-permits-plan-reviews/plumbing-natural-gas-health-code/)
- [Arkansas Building Energy Codes](https://adeq.state.ar.us/energy/initiatives/building.aspx)
- [ICC 2021 Arkansas Fire Prevention Code library](https://shop.iccsafe.org/arkansas-fire-prevention-code-rules-2021-edition.html)

The AFPC is the adopted state framework: Volume I is fire, Volume II is
building, and Volume III is residential. The Arkansas State Police source
should control edition and amendment verification. The ICC library is the
licensed access path for the underlying copyrighted code publications.

## Benton County

### Unincorporated Benton County

Benton County Building Safety states that residential permits are required for
new construction, additions, and interior remodels of single-family homes. It
also identifies permits for new electrical, plumbing, and HVAC work. The county
FAQ identifies the codes it enforces as:

- 2021 Arkansas Fire Prevention Code, Volumes I, II, and III;
- 2021 International Mechanical Code;
- 2018 Arkansas Plumbing Code;
- 2018 Arkansas Fuel/Gas Code;
- 2020 National Electrical Code; and
- 2009 International Energy Conservation Code with 2014 Arkansas amendments.

The county also has a Group U exception for certain detached, non-living-space
structures in unincorporated areas. That exception must not be generalized to
residences, attached structures, or trade work.

Required Benton County source records:

- permit type and application;
- building-safety plan/checklist requirements;
- inspection sequence;
- zoning/planning approval where applicable;
- floodplain determination;
- septic or sewer evidence;
- driveway/road requirements where applicable; and
- local ordinances and board-of-appeals decisions affecting the parcel.

Official sources:

- [Benton County Building Safety](https://bentoncountyar.gov/building-safety/)
- [Benton County permits](https://bentoncountyar.gov/building-safety/permits/)
- [Benton County FAQ and enforced codes](https://bentoncountyar.gov/building-safety/faq/)
- [Benton County regulations](https://bentoncountyar.gov/county-planning/regulations/)

### Incorporated Benton County cities

For Bentonville, Rogers, Bella Vista, Springdale-area parcels, Lowell,
Centerton, Cave Springs, Decatur, Gravette, Gentry, Siloam Springs, and other
incorporated jurisdictions, RES Works must route the project to the city AHJ.
The county profile must not be applied automatically. The city may control:

- permit intake and plan review;
- adopted code editions and local amendments;
- zoning, setbacks, lot coverage, height, and use;
- grading, drainage, access, and right-of-way;
- utility connection and impact requirements; and
- inspections and certificates of occupancy.

## Washington County

### Unincorporated Washington County

Washington County states that it does not enforce building codes for
agricultural buildings, single-family homes, or residential accessory
structures in unincorporated areas, and that ordinary building permits and
inspections are not required for those categories. It also states that
Arkansas State Code must still be met and that other requirements may apply.

This is a jurisdictional distinction, not permission to design below the
statewide safety baseline. RES Works should report the county enforcement
status separately from code conformance status:

- `county_permit_required`: possibly false for the stated exempt categories;
- `state_code_obligation`: true unless a verified exception applies;
- `planning_requirements`: parcel/use dependent;
- `floodplain_permit`: required when applicable; and
- `septic_authorization`: required when domestic sewage will be created and
  private disposal applies.

Washington County planning requirements include, as applicable:

- zoning/use and conditional-use review;
- 911 address and additional-dwelling-unit review;
- floodplain development permit;
- septic permit through the Washington County Health Department;
- subdivision, minor subdivision, replat, or exempt-land-division review;
- large-scale-development review;
- road/access and utility easements;
- certified survey information; and
- house-moving permits.

Official sources:

- [Washington County Planning](https://www.washingtoncountyar.gov/government/departments-f-z/planning)
- [Washington County ordinances and regulations](https://www.washingtoncountyar.gov/government/departments-f-z/planning/ordinances-and-regulations)
- [Washington County applications](https://www.washingtoncountyar.gov/government/departments-f-z/planning/applications-and-information)
- [Washington County residential guidance](https://www.washingtoncountyar.gov/home/showpublisheddocument/32971/639047649262400000)

### Incorporated Washington County cities

For Fayetteville, Springdale, Farmington, Prairie Grove, West Fork,
Elkins, Greenland, Tontitown, Johnson, Lincoln, and other incorporated
jurisdictions, the city AHJ controls the permit and inspection workflow.
RES Works must obtain the city code profile instead of treating Washington
County's unincorporated policy as applicable.

## Remodeling and existing buildings

Remodeling must be classified before rule selection. At minimum, RES Works
should distinguish:

- repair or maintenance;
- alteration without change of occupancy;
- addition;
- structural alteration;
- change of use or occupancy;
- historic or locally protected property;
- work involving life-safety systems; and
- work involving electrical, plumbing, gas, or mechanical systems.

The applicable existing-building, residential, fire, energy, and trade rules
may differ from new construction. The engine must not assume that a remodel is
either fully grandfathered or fully new construction. It should return
`not_verified` until the AHJ and project scope are confirmed.

## Repository library strategy

Do not commit complete IRC, IBC, IFC, IMC, plumbing, fuel-gas, NEC, or IECC
text. These publications are copyrighted and the official sources may require
purchase or subscription.

The repository should contain:

- source URLs and authority metadata;
- edition and effective-date records;
- Arkansas amendment identifiers and links;
- local ordinance links and retrieval dates;
- normalized rule summaries authored by RES Works;
- applicability predicates;
- evidence requirements;
- review status and verification dates; and
- tests using small, original fixtures.

Recommended external libraries:

1. ICC Digital Codes / licensed ICC publications for the adopted IRC and
   Arkansas AFPC text.
2. Official Code of Arkansas Rules for state administrative rules and update
   checks.
3. County and city official ordinance/permit pages for local requirements.
4. Arkansas Department of Health sources for plumbing, fuel gas, and septic.
5. ADEQ / Arkansas Energy Office sources for energy requirements.
6. FEMA NFIP/FIRM resources for floodplain evidence.

The code engine should store a source reference and rule version, not scrape
or redistribute the full publication. A standards maintainer must review
changes before a rule becomes production-active.

## Initial implementation records

The first data model should include:

```text
JurisdictionProfile
  id, geography, incorporated_status, ahj, effective_from, effective_to

CodeSource
  id, title, discipline, edition, authority, url, copyright_status,
  retrieved_at, verification_status

RuleProfile
  id, jurisdiction_profile, code_sources, amendments, scope, revision,
  status

Requirement
  id, rule_profile, category, applicability, evidence_required,
  professional_review, printed_neutral_id
```

No rule profile should be selected until the address, incorporated status,
project type, and new-versus-remodel classification are known or explicitly
marked unknown.

