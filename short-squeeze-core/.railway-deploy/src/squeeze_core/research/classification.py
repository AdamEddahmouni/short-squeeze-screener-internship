from .models import (
    DetectionStatus,
    OutcomeLabel,
    ResearchCaseClassification,
    ResearchClassificationResult,
)


_CLASSIFICATION_TABLE = {
    (DetectionStatus.DETECTED, OutcomeLabel.SUBSTANTIAL_UPWARD_MOVE): (
        ResearchCaseClassification.TRUE_POSITIVE
    ),
    (DetectionStatus.DETECTED, OutcomeLabel.NO_SUBSTANTIAL_UPWARD_MOVE): (
        ResearchCaseClassification.FALSE_POSITIVE
    ),
    (DetectionStatus.NOT_DETECTED, OutcomeLabel.SUBSTANTIAL_UPWARD_MOVE): (
        ResearchCaseClassification.FALSE_NEGATIVE
    ),
    (DetectionStatus.NOT_DETECTED, OutcomeLabel.NO_SUBSTANTIAL_UPWARD_MOVE): (
        ResearchCaseClassification.TRUE_NEGATIVE
    ),
}


def classify_research_case(
    case_id: str,
    detection_status: DetectionStatus,
    outcome_label: OutcomeLabel,
    detection_result_id: str,
    outcome_label_result_id: str,
) -> ResearchClassificationResult:
    classification = _CLASSIFICATION_TABLE.get(
        (detection_status, outcome_label), ResearchCaseClassification.UNEVALUABLE
    )
    return ResearchClassificationResult(
        case_id=case_id,
        detection_status=detection_status,
        outcome_label=outcome_label,
        classification=classification,
        detection_result_id=detection_result_id,
        outcome_label_result_id=outcome_label_result_id,
    )


__all__ = ["classify_research_case"]
