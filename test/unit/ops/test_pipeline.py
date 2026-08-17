"""Integration test: a full pipeline stitched together from most of the ops classes.

This is deliberately not one isolated behavior per test method like the rest of
test/unit/ops/ -- it exercises a realistic end-to-end chain (the "enclosure with
blades" scenario used throughout the ops README) so the composed pipeline reads as a
sentence, and so a change to one op's contract that breaks composition with its
neighbors shows up here even if every op's own unit tests still pass in isolation.
"""

import unittest

from oj_toolkit.ops import (
    And,
    Broadcast,
    Eq,
    Exists,
    Extract,
    Fanout,
    Filter,
    FlatMap,
    GroupBy,
    Gt,
    In,
    Iter,
    Join,
    Map,
    MapField,
    Merge,
    Not,
    Or,
    Sequence,
    When,
    Zip,
)


class TestFullPipeline(unittest.TestCase):
    """Runs a full ops pipeline end to end and checks the final shape."""

    # pylint: disable-next=too-many-locals
    def test_should_produce_flagged_report_grouped_by_facility(self):
        # each pipeline stage gets its own named local on purpose -- that's the
        # readability property this test exists to check, not accidental complexity.
        # setup: a stream of enclosures, each holding a list of child blades --
        # raw and messy on purpose (mixed-case/whitespace status) to give the
        # normalization stage something real to do.
        enclosures = [
            {
                "enclosure_id": "encl-1",
                "location": "dc-east",
                "blades": [
                    {"serial": "b1", "cpu": 92, "status": "  OK  "},
                    {"serial": "b2", "cpu": 40, "status": "ok"},
                    {"serial": "b3", "cpu": 95, "status": "decommissioned"},
                ],
            },
            {
                "enclosure_id": "encl-2",
                "location": "dc-west",
                "blades": [{"serial": "b4", "cpu": 88, "status": "warn"}],
            },
        ]
        facilities = [
            {"code": "dc-east", "name": "East Campus"},
            {"code": "dc-west", "name": "West Campus"},
        ]
        reviewers = ["inspector-1", "inspector-2", "inspector-3"]

        # Each stage is named for what it does to the record it's handed. Item-level
        # ops (conditions, When, Fanout/Merge) nest into a single expression -- that's
        # the "chainable" part. Stream-level stages are sequential Python calls, one
        # per line, because Filter/FlatMap/Join/GroupBy change cardinality and can't
        # be lifted through Iter (see the ops README's "Recipes" section).

        # 1. one enclosure record -> N blade records, each carrying its parent's fields
        expand_blades = FlatMap(
            op=Broadcast(
                children_path="blades",
                fields={"enclosure_id": "enclosure_id", "location": "location"},
            )
        )

        # 2. trim/lowercase the noisy status field before anything compares against it
        normalize_status = Iter(
            fn=MapField(key="status", fn=Sequence(ops=[Map(fn=str.strip), Map(fn=str.lower)]))
        )

        # 3. drop anything that isn't actively in service
        keep_in_service = Filter(
            condition=Or(ops=[Eq(input="status", value="ok"), Eq(input="status", value="warn")])
        )

        # 4. tag hot-and-healthy blades -- guard the comparison with Exists first
        flag_hot = Iter(
            fn=When(
                condition=And(ops=[Exists(input="cpu"), Gt(input="cpu", value=80)]),
                then=Map(fn=lambda blade: {**blade, "alert": True}),
                otherwise=Map(fn=lambda blade: {**blade, "alert": False}),
            )
        )

        # 5. reshape into a flat summary record, merging two Fanouts into one dict
        summarize = Iter(
            fn=Merge(
                ops=[
                    Fanout(serial=Extract(path="serial"), location=Extract(path="location")),
                    Fanout(status=Extract(path="status"), alert=Extract(path="alert")),
                ]
            )
        )

        # 6. enrich with the facility's display name
        enrich_facility = Join(right=facilities, on="location", right_on="code")

        # 7. pair each surviving record with a reviewer, then flatten the pair back into a dict
        assign_reviewer = Zip(others=[reviewers])
        attach_reviewer = Iter(fn=Map(fn=lambda pair: {**pair[0], "reviewed_by": pair[1]}))

        # 8. finally, roll everything up by facility name
        group_by_facility = GroupBy(key="name")

        expected = {
            "East Campus": [
                {
                    "serial": "b1",
                    "location": "dc-east",
                    "status": "ok",
                    "alert": True,
                    "code": "dc-east",
                    "name": "East Campus",
                    "reviewed_by": "inspector-1",
                },
                {
                    "serial": "b2",
                    "location": "dc-east",
                    "status": "ok",
                    "alert": False,
                    "code": "dc-east",
                    "name": "East Campus",
                    "reviewed_by": "inspector-2",
                },
            ],
            "West Campus": [
                {
                    "serial": "b4",
                    "location": "dc-west",
                    "status": "warn",
                    "alert": True,
                    "code": "dc-west",
                    "name": "West Campus",
                    "reviewed_by": "inspector-3",
                },
            ],
        }

        # execute -- the pipeline itself: one stage's output feeds the next stage's input
        blades = expand_blades(enclosures)
        blades = normalize_status(blades)
        blades = keep_in_service(blades)
        blades = flag_hot(blades)
        summaries = summarize(blades)
        enriched = enrich_facility(summaries)
        reviewed = attach_reviewer(assign_reviewer(enriched))
        actual = group_by_facility(reviewed)

        # assess
        self.assertEqual(expected, actual)

        # b3 (decommissioned) never makes it past keep_in_service, so it's absent
        # from every downstream stage rather than merely un-flagged.
        all_serials = {blade["serial"] for facility in actual.values() for blade in facility}
        self.assertNotIn("b3", all_serials)

        # teardown

    def test_condition_tree_reads_back_as_a_readable_repr(self):
        # setup: the same guard condition used by flag_hot above, in isolation --
        # confirms the nested item-level "sentence" is legible on its own, not just
        # when it's working correctly buried inside a larger pipeline.
        is_hot_and_measured = And(ops=[Exists(input="cpu"), Gt(input="cpu", value=80)])

        # execute
        actual = repr(is_hot_and_measured)

        # assess
        self.assertTrue(actual.startswith("And(ops=["))
        self.assertIn("Exists(input='cpu'", actual)
        self.assertIn("Gt(input='cpu', value=80", actual)
        self.assertTrue(is_hot_and_measured({"cpu": 92}))
        self.assertFalse(is_hot_and_measured({"cpu": 10}))
        self.assertFalse(is_hot_and_measured({}))

        # teardown

    def test_not_and_in_negate_and_reuse_conditions_declaratively(self):
        # setup: build the same "in service" condition two ways -- once with a
        # positive In() check, once with a negated Not(In(...)) -- to confirm the
        # negation composes cleanly rather than needing a bespoke NotIn op.
        currently_in_service = In(input="status", value=["ok", "warn"])
        not_in_service = Not(op=currently_in_service)

        # execute / assess
        self.assertTrue(currently_in_service({"status": "ok"}))
        self.assertFalse(not_in_service({"status": "ok"}))
        self.assertFalse(currently_in_service({"status": "decommissioned"}))
        self.assertTrue(not_in_service({"status": "decommissioned"}))

        # teardown


if __name__ == "__main__":
    unittest.main()
