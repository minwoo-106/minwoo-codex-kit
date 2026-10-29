"""Check useful properties and ensure the generator can reject an actual defect."""
import json
from hypothesis import find, given, settings, strategies as st

values = st.lists(st.integers())
counterexample = find(values, lambda xs: list(filter(bool, xs)) != xs,
                      settings=settings(max_examples=500, database=None, derandomize=True))
assert counterexample == [0], counterexample

@settings(max_examples=500, database=None, derandomize=True)
@given(values)
def round_trip(xs):
    assert json.loads(json.dumps(xs)) == xs

round_trip()
print("PASS Hypothesis: broken round-trip minimized to [0]; correct property passed (500 examples)")
