from scubaduck import hello


def test_hello() -> None:
    """Verify hello() returns the expected greeting."""
    assert hello() == "Hello from scubaduck!"
