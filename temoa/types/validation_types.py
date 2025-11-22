"""
Validation result type definitions for Temoa energy model.

This module provides type definitions for validation results, errors, and warnings
used in model checking and data validation throughout the Temoa codebase.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ValidationSeverity(str, Enum):
    """
    Enumeration of validation message severity levels.

    These represent the severity of validation issues found during
    model checking and data validation.
    """

    ERROR = 'error'
    """Critical error that prevents model execution."""

    WARNING = 'warning'
    """Non-critical issue that may affect results."""

    INFO = 'info'
    """Informational message about model structure."""


@dataclass(slots=True)
class ValidationError:
    """
    Represents a validation error or warning.

    This dataclass encapsulates information about a validation issue,
    including its severity, message, and location in the model.

    Attributes:
        severity: The severity level of the validation issue
        message: Human-readable description of the issue
        location: Optional location information (e.g., file, line, component)
        context: Optional additional context about the issue
                 (e.g., {'variable': 'x', 'expected': 10, 'actual': 5})
    """

    severity: ValidationSeverity
    message: str
    location: str | None = None
    context: dict[str, Any] | None = None

    def __str__(self) -> str:
        """Return a formatted string representation of the validation error."""
        parts = [f'[{self.severity.value.upper()}]', self.message]
        if self.location:
            parts.append(f'at {self.location}')
        return ' '.join(parts)


@dataclass(slots=True)
class ValidationWarning:
    """
    Represents a validation warning.

    This is a convenience type for warnings, which are non-critical validation
    issues that don't prevent model execution but may affect results.

    Attributes:
        message: Human-readable description of the warning
        location: Optional location information
        context: Optional additional context
    """

    message: str
    location: str | None = None
    context: dict[str, Any] | None = None

    def to_validation_error(self) -> ValidationError:
        """Convert this warning to a ValidationError with WARNING severity."""
        return ValidationError(
            severity=ValidationSeverity.WARNING,
            message=self.message,
            location=self.location,
            context=self.context,
        )

    def __str__(self) -> str:
        """Return a formatted string representation of the validation warning."""
        parts = ['[WARNING]', self.message]
        if self.location:
            parts.append(f'at {self.location}')
        return ' '.join(parts)


@dataclass(slots=True)
class ValidationResult:
    """
    Represents the complete result of a validation operation.

    This dataclass aggregates all validation errors and warnings found
    during a validation operation, along with summary information.

    Attributes:
        errors: List of validation errors found
        warnings: List of validation warnings found
        is_valid: Whether the validation passed (no errors)
        summary: Optional summary message
    """

    errors: list[ValidationError]
    warnings: list[ValidationWarning]
    is_valid: bool
    summary: str | None = None

    @classmethod
    def create_success(cls, summary: str | None = None) -> 'ValidationResult':
        """
        Create a successful validation result with no errors or warnings.

        Args:
            summary: Optional summary message

        Returns:
            ValidationResult indicating success
        """
        return cls(errors=[], warnings=[], is_valid=True, summary=summary)

    @classmethod
    def create_failure(
        cls,
        errors: list[ValidationError],
        warnings: list[ValidationWarning] | None = None,
        summary: str | None = None,
    ) -> 'ValidationResult':
        """
        Create a failed validation result with errors.

        Args:
            errors: List of validation errors
            warnings: Optional list of validation warnings
            summary: Optional summary message

        Returns:
            ValidationResult indicating failure
        """
        if not errors:
            raise ValueError('Failure result must contain at least one error')
        return cls(
            errors=errors,
            warnings=warnings or [],
            is_valid=False,
            summary=summary,
        )

    def add_error(
        self,
        message: str,
        location: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        """
        Add an error to this validation result.

        Args:
            message: Error message
            location: Optional location information
            context: Optional additional context
        """
        self.errors.append(
            ValidationError(
                severity=ValidationSeverity.ERROR,
                message=message,
                location=location,
                context=context,
            )
        )
        self.is_valid = False

    def add_warning(
        self,
        message: str,
        location: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        """
        Add a warning to this validation result.

        Args:
            message: Warning message
            location: Optional location information
            context: Optional additional context
        """
        self.warnings.append(ValidationWarning(message=message, location=location, context=context))

    def has_errors(self) -> bool:
        """Check if this result contains any errors."""
        return bool(self.errors)

    def has_warnings(self) -> bool:
        """Check if this result contains any warnings."""
        return bool(self.warnings)

    def error_count(self) -> int:
        """Get the number of errors in this result."""
        return len(self.errors)

    def warning_count(self) -> int:
        """Get the number of warnings in this result."""
        return len(self.warnings)

    def __str__(self) -> str:
        """Return a formatted string representation of the validation result."""
        lines = []
        if self.summary:
            lines.append(self.summary)
        lines.append(
            f'Validation {"PASSED" if self.is_valid else "FAILED"}: '
            f'{self.error_count()} errors, {self.warning_count()} warnings'
        )
        if self.errors:
            lines.append('\nErrors:')
            for error in self.errors:
                lines.append(f'  {error}')
        if self.warnings:
            lines.append('\nWarnings:')
            for warning in self.warnings:
                lines.append(f'  {warning}')
        return '\n'.join(lines)


# Export all types
# ruff: noqa: RUF022
__all__ = [
    'ValidationSeverity',
    'ValidationError',
    'ValidationWarning',
    'ValidationResult',
]
