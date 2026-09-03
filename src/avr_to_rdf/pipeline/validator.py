"""Validation logic for AVR data."""

import re
from typing import Any, Dict, List, Tuple


class ValidationError:
    """Represents a validation error."""
    
    def __init__(self, field: str, value: Any, error: str, severity: str = "error"):
        self.field = field
        self.value = value
        self.error = error
        self.severity = severity  # error, warning
    
    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.field}: {self.error} (value: {self.value})"


class AVRValidator:
    """Validates AVR records against schema and custom rules."""
    
    # Required fields
    REQUIRED_FIELDS = {
        "antibody_hubmap_id",
        "clonality",
        "host",
        "recommended",
    }
    
    # Field patterns for validation
    PATTERNS = {
        "hgnc_id": r"^HGNC:\d+$",
        "uniprot_accession_number": r"^([OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2})$",
        "rrid": r"^AB_\d+$",
        "organ_uberon_id": r"^UBERON:\d{7}$",
        "protocol_doi": r"^10\.\d{4,}/\S+$",
        "manuscript_doi": r"^10\.\d{4,}/\S+$",
    }
    
    # Enum values
    ENUMS = {
        "clonality": {"monoclonal", "polyclonal"},
        "host": {"Mouse", "Rabbit", "Goat", "Human", "Chicken", "Sheep"},
        "recommended": {True, False, "Yes", "No"},
        "recombinant": {True, False, "Yes", "No"},
        "senescence_specific": {True, False, "Yes", "No"},
    }
    
    def __init__(self):
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
    
    def validate_antibody(self, antibody: Dict[str, Any]) -> bool:
        """
        Validate an antibody record.
        
        Args:
            antibody: Antibody data to validate
            
        Returns:
            True if valid, False if errors found
        """
        self.errors.clear()
        self.warnings.clear()
        
        # Check required fields
        self._check_required_fields(antibody)
        
        # Check patterns
        self._check_patterns(antibody)
        
        # Check enum values
        self._check_enums(antibody)
        
        # Check logical consistency
        self._check_consistency(antibody)
        
        return len(self.errors) == 0
    
    def _check_required_fields(self, antibody: Dict[str, Any]) -> None:
        """Check that all required fields are present and non-empty."""
        for field in self.REQUIRED_FIELDS:
            value = antibody.get(field)
            if value is None or value == "":
                self.errors.append(ValidationError(
                    field,
                    value,
                    f"Required field is missing or empty"
                ))
    
    def _check_patterns(self, antibody: Dict[str, Any]) -> None:
        """Check fields against regex patterns."""
        for field, pattern in self.PATTERNS.items():
            value = antibody.get(field)
            if value and value != "":
                if not re.match(pattern, str(value)):
                    self.warnings.append(ValidationError(
                        field,
                        value,
                        f"Value does not match expected pattern: {pattern}",
                        severity="warning"
                    ))
        author_orcids = antibody.get("author_orcids")
        if author_orcids:
            values = author_orcids if isinstance(author_orcids, list) else [author_orcids]
            for orcid in values:
                if not re.match(r"^https://orcid\.org/\d{4}-\d{4}-\d{4}-\d{3}[0-9X]$", str(orcid)):
                    self.warnings.append(ValidationError(
                        "author_orcids",
                        orcid,
                        "Value does not match expected ORCID IRI pattern",
                        severity="warning"
                    ))
    
    def _check_enums(self, antibody: Dict[str, Any]) -> None:
        """Check that enum fields have valid values."""
        for field, valid_values in self.ENUMS.items():
            value = antibody.get(field)
            if value is None or value == "":
                continue
            normalized = value
            if isinstance(value, str):
                stripped = value.strip()
                lowered = stripped.lower()
                if lowered in {"yes", "true", "y", "1"}:
                    normalized = True
                elif lowered in {"no", "false", "n", "0"}:
                    normalized = False
                else:
                    normalized = stripped
            if normalized not in valid_values:
                self.errors.append(ValidationError(
                    field,
                    value,
                    f"Invalid value. Expected one of: {', '.join(sorted(str(v) for v in valid_values))}"
                ))
    
    def _check_consistency(self, antibody: Dict[str, Any]) -> None:
        """Check logical consistency between fields."""
        # Monoclonal antibodies should have clone_id
        if antibody.get("clonality") == "monoclonal" and not antibody.get("clone_id"):
            self.warnings.append(ValidationError(
                "clone_id",
                None,
                "Monoclonal antibody should have a clone_id",
                severity="warning"
            ))
        
        # Target information should be consistent
        target_symbol = antibody.get("target_symbol")
        hgnc_id = antibody.get("hgnc_id")
        uniprot = antibody.get("uniprot_accession_number")
        
        if target_symbol and not hgnc_id:
            self.warnings.append(ValidationError(
                "hgnc_id",
                None,
                "Should have HGNC ID when target symbol is provided",
                severity="warning"
            ))
    
    def get_report(self) -> Dict[str, Any]:
        """
        Get validation report.
        
        Returns:
            Dictionary with error and warning counts and details
        """
        return {
            "valid": len(self.errors) == 0,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": [str(e) for e in self.errors],
            "warnings": [str(w) for w in self.warnings],
        }


def validate_collection(antibodies: List[Dict[str, Any]]) -> Tuple[int, int, List[str]]:
    """
    Validate a collection of antibodies.
    
    Args:
        antibodies: List of antibody records
        
    Returns:
        Tuple of (valid_count, invalid_count, error_messages)
    """
    validator = AVRValidator()
    valid_count = 0
    invalid_count = 0
    error_messages = []
    
    for i, antibody in enumerate(antibodies):
        if validator.validate_antibody(antibody):
            valid_count += 1
        else:
            invalid_count += 1
            antibody_id = antibody.get("antibody_hubmap_id", f"record_{i}")
            error_msg = f"\nAntibody {antibody_id}:"
            report = validator.get_report()
            error_msg += "\n  " + "\n  ".join(report["errors"])
            error_messages.append(error_msg)
    
    return valid_count, invalid_count, error_messages
