"""Tests for StochasticSequencer's constructor validation of stochastic config files."""

from pathlib import Path
from types import SimpleNamespace

import pytest

from temoa.extensions.stochastics.stochastic_sequencer import StochasticSequencer


def _config(stochastic_config: Path | None) -> SimpleNamespace:
    """A minimal stand-in for TemoaConfig with just the attribute the sequencer reads."""
    return SimpleNamespace(stochastic_config=stochastic_config)


def test_missing_stochastic_config_raises() -> None:
    with pytest.raises(ValueError, match="requires a 'stochastic_config'"):
        StochasticSequencer(_config(None))  # type: ignore[arg-type]


def test_nonexistent_stochastic_config_path_raises(tmp_path: Path) -> None:
    missing = tmp_path / 'does_not_exist.toml'
    with pytest.raises(ValueError, match='not found'):
        StochasticSequencer(_config(missing))  # type: ignore[arg-type]


def test_stochastic_config_path_is_directory_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match='is not a file'):
        StochasticSequencer(_config(tmp_path))  # type: ignore[arg-type]


def test_invalid_toml_content_raises_wrapped_error(tmp_path: Path) -> None:
    bad_toml = tmp_path / 'stoch.toml'
    bad_toml.write_text('not valid = toml = content [[[')

    with pytest.raises(ValueError, match='Error parsing stochastic config'):
        StochasticSequencer(_config(bad_toml))  # type: ignore[arg-type]


def test_valid_stochastic_config_loads_successfully(tmp_path: Path) -> None:
    good_toml = tmp_path / 'stoch.toml'
    good_toml.write_text(
        """
        [scenarios]
        base = 0.5
        high = 0.5
        """
    )

    sequencer = StochasticSequencer(_config(good_toml))  # type: ignore[arg-type]

    assert sequencer.stoch_config.scenarios == {'base': 0.5, 'high': 0.5}
    assert sequencer.objective_value is None
