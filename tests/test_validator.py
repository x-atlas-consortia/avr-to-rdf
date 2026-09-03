"""Test suite for AVR to RDF converter."""

from avr_to_rdf.pipeline.validator import AVRValidator, validate_collection


class TestAVRValidator:
    """Tests for AVR validation."""
    
    def test_valid_antibody(self):
        """Test validation of a valid antibody record."""
        antibody = {
            "antibody_hubmap_id": "HBM756.VFSH.996",
            "clonality": "monoclonal",
            "host": "Mouse",
            "recommended": True,
            "target_symbol": "FUT4",
            "hgnc_id": "HGNC:4015",
            "vendor_name": "Miltenyi Biotec",
        }
        
        validator = AVRValidator()
        assert validator.validate_antibody(antibody) is True
        assert len(validator.errors) == 0
    
    def test_missing_required_field(self):
        """Test validation fails when required field is missing."""
        antibody = {
            "antibody_hubmap_id": "HBM756.VFSH.996",
            "clonality": "monoclonal",
            "host": "Mouse",
            # Missing "recommended"
        }
        
        validator = AVRValidator()
        assert validator.validate_antibody(antibody) is False
        assert len(validator.errors) > 0
    
    def test_invalid_enum_value(self):
        """Test validation fails for invalid enum values."""
        antibody = {
            "antibody_hubmap_id": "HBM756.VFSH.996",
            "clonality": "invalid_clonality",
            "host": "Mouse",
            "recommended": True,
        }
        
        validator = AVRValidator()
        assert validator.validate_antibody(antibody) is False
        errors = validator.get_report()
        assert any("clonality" in e for e in errors["errors"])
    
    def test_hgnc_id_pattern(self):
        """Test HGNC ID pattern validation."""
        antibody = {
            "antibody_hubmap_id": "HBM756.VFSH.996",
            "clonality": "monoclonal",
            "host": "Mouse",
            "recommended": True,
            "hgnc_id": "invalid-hgnc",
        }
        
        validator = AVRValidator()
        validator.validate_antibody(antibody)
        report = validator.get_report()
        # This should generate a warning (not error) for pattern mismatch
        assert len(report["warnings"]) > 0 or len(report["errors"]) > 0

    def test_uniprot_accession_pattern(self):
        """Test UniProt accession pattern validation accepts canonical accessions."""
        antibody = {
            "antibody_hubmap_id": "HBM756.VFSH.996",
            "clonality": "monoclonal",
            "host": "Mouse",
            "recommended": True,
            "clone_id": "123",
            "uniprot_accession_number": "P12345",
        }

        validator = AVRValidator()
        assert validator.validate_antibody(antibody) is True
        assert not validator.warnings

    def test_author_orcids_as_list(self):
        """Test ORCID fields validate as a split list."""
        antibody = {
            "antibody_hubmap_id": "HBM756.VFSH.996",
            "clonality": "monoclonal",
            "host": "Mouse",
            "recommended": True,
            "author_orcids": [
                "https://orcid.org/0000-0002-1297-9725",
                "https://orcid.org/0000-0001-2345-6789",
            ],
        }

        validator = AVRValidator()
        assert validator.validate_antibody(antibody) is True


class TestValidateCollection:
    """Tests for collection-level validation."""
    
    def test_validate_multiple_antibodies(self):
        """Test validating multiple antibody records."""
        antibodies = [
            {
                "antibody_hubmap_id": "HBM001",
                "clonality": "monoclonal",
                "host": "Mouse",
                "recommended": True,
            },
            {
                "antibody_hubmap_id": "HBM002",
                "clonality": "polyclonal",
                "host": "Rabbit",
                "recommended": False,
            },
            {
                "antibody_hubmap_id": "HBM003",
                # Missing required fields
                "clonality": "monoclonal",
            }
        ]
        
        valid, invalid, errors = validate_collection(antibodies)
        assert valid == 2
        assert invalid == 1
        assert len(errors) > 0
