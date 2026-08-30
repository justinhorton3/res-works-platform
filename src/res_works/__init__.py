"""RES Works domain package."""

from .models import AnalysisRun, ProjectManifest
from .repository import ProjectRepository
from .ingest import ingest_artifact
from .pdf_review import inventory_pdf
from .pdf_render import render_pdf_pages
from .validation import evaluate_requirement, evaluate_requirements
from .rule_catalog import load_requirements
from .reports import build_validation_report
from .geometry import validate_geometry
from .caproj import caproj_contents_report, extract_native_files, inventory_caproj
from .dxf import inventory_dxf
from .dxf_extract import extract_architectural_entities, normalize_layer, summarize_dxf_evidence
from .dxf_compare import compare_dimension_sets, compare_plan_to_dxf
from .recommendations import recommend_documentation
from .plan_fixture import load_plan_geometry
from .fact_mapping import facts_from_geometry
from .handoff import apply_decisions, build_change_set, build_chief_handoff
from .watcher import discover_exports, is_stable, observe_file
from .jurisdiction import classify_project, load_rule_profiles, resolve_rule_profile
from .final_qa import compare_pdf_evidence, unresolved_exceptions

__all__ = ["ProjectManifest", "AnalysisRun", "ProjectRepository", "ingest_artifact", "inventory_pdf", "render_pdf_pages", "evaluate_requirement", "evaluate_requirements", "load_requirements", "build_validation_report", "validate_geometry", "load_plan_geometry", "facts_from_geometry", "inventory_caproj", "extract_native_files", "caproj_contents_report", "inventory_dxf", "extract_architectural_entities", "summarize_dxf_evidence", "normalize_layer", "compare_dimension_sets", "compare_plan_to_dxf", "recommend_documentation", "apply_decisions", "build_change_set", "build_chief_handoff", "discover_exports", "is_stable", "observe_file", "classify_project", "load_rule_profiles", "resolve_rule_profile", "compare_pdf_evidence", "unresolved_exceptions"]
