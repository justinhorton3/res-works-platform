"""RES Works domain package."""

from .models import ProjectManifest
from .repository import ProjectRepository
from .ingest import ingest_artifact
from .pdf_review import inventory_pdf
from .pdf_render import render_pdf_pages
from .validation import evaluate_requirement, evaluate_requirements
from .rule_catalog import load_requirements
from .reports import build_validation_report
from .geometry import validate_geometry
from .caproj import inventory_caproj
from .dxf import inventory_dxf
from .dxf_extract import extract_architectural_entities, normalize_layer
from .plan_fixture import load_plan_geometry
from .fact_mapping import facts_from_geometry

__all__ = ["ProjectManifest", "ProjectRepository", "ingest_artifact", "inventory_pdf", "render_pdf_pages", "evaluate_requirement", "evaluate_requirements", "load_requirements", "build_validation_report", "validate_geometry", "load_plan_geometry", "facts_from_geometry", "inventory_caproj", "inventory_dxf", "extract_architectural_entities", "normalize_layer"]
