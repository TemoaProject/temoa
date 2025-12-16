from temoa.model_checking.unit_checking.unit_propagator import UnitPropagator

extract_capacity_unit_func = UnitPropagator._extract_capacity_unit


def test_extract_simple() -> None:
    """Test extracting a simple capacity unit."""
    assert extract_capacity_unit_func('Mdollar/GW') == 'GW'


def test_extract_complex_utopia() -> None:
    """Test extracting from a complex unit string like 'Mdollar / (PJ^2 / GW)'."""
    assert extract_capacity_unit_func('Mdollar / (PJ^2 / GW)') == 'GW'


def test_extract_complex_fixed() -> None:
    """Test extracting from a complex unit string with a time component."""
    assert extract_capacity_unit_func('Mdollar / (PJ^2 / GW / year)') == 'GW'


def test_extract_MW() -> None:  # noqa: N802
    """Test extracting 'MW' as a capacity unit."""
    assert extract_capacity_unit_func('Mdollar / (MW)') == 'MW'


def test_extract_kW() -> None:  # noqa: N802
    """Test extracting 'kW' as a capacity unit."""
    assert extract_capacity_unit_func('Mdollar / (kW)') == 'kW'


def test_extract_gigawatt() -> None:
    """Test extracting 'gigawatt' as a capacity unit."""
    assert extract_capacity_unit_func('Mdollar / (gigawatt)') == 'gigawatt'


def test_extract_megawatt() -> None:
    """Test extracting 'megawatt' as a capacity unit."""
    assert extract_capacity_unit_func('Mdollar / (megawatt)') == 'megawatt'


def test_extract_kilowatt() -> None:
    """Test extracting 'kilowatt' as a capacity unit."""
    assert extract_capacity_unit_func('Mdollar / (kilowatt)') == 'kilowatt'


def test_extract_ignores_energy() -> None:
    """Test that energy units like 'GWh' are ignored."""
    assert extract_capacity_unit_func('GWh') is None


def test_extract_none() -> None:
    """Test cases where no capacity unit can be extracted."""
    assert extract_capacity_unit_func('Mdollar/PJ') is None
    assert extract_capacity_unit_func('Mdollar/kg') is None
    assert extract_capacity_unit_func('Mdollar') is None
    assert extract_capacity_unit_func('SomethingElse') is None
