"""
Tests for bulk test-case parser.

"""
import textwrap

from tests import case



class ParseBulkTest(case.TestCase):
    """Tests for BulkParser."""
    @property
    def parser(self):
        from moztrap.model.library.bulk import BulkParser
        return BulkParser


    def test_success(self):
        """Test successful parsing."""
        self.assertEqual(
            self.parser().parse(
                textwrap.dedent("""
                 Test that bulk parsing works
                As a testcase administrator
                Given that I've loaded the bulk-input screen
                When I type a sonnet in the textarea
                And I sing my sonnet aloud
                Then my sonnet should be parsed
                And when I click the submit button
                Then testcases should be created
                And
                When I am done
                Then I feel satisfied

                  tEst that a second testcase works
                 With any old description
                  whEn I do this thing
                Over here
                tHen I see that thing
                Over there
                """)
                ),
            [
                {
                    "name": "Test that bulk parsing works",
                    "description": (
                        "As a testcase administrator\n"
                        "Given that I've loaded the bulk-input screen"
                        ),
                    "steps": [
                        {
                            "instruction": (
                                "When I type a sonnet in the textarea\n"
                                "And I sing my sonnet aloud"
                                ),
                            "expected": "Then my sonnet should be parsed",
                            },
                        {
                            "instruction": "And when I click the submit button",
                            "expected": "Then testcases should be created",
                            },
                        {
                            "instruction": "When I am done",
                            "expected": "Then I feel satisfied",
                            },
                        ]
                    },
                {
                    "name": "tEst that a second testcase works",
                    "description": "With any old description",
                    "steps": [
                        {
                            "instruction": (
                                "whEn I do this thing\n"
                                "Over here"
                                ),
                            "expected": (
                                "tHen I see that thing\n"
                                "Over there"
                                ),
                            },
                        ],
                    },
                ]
            )


    def test_beginning_junk(self):
        """Unexpected junk at start causes error."""
        self.assertEqual(
            self.parser().parse(
                textwrap.dedent("""
                This is not the beginning of a test case.
                Nor is this.
                """)
                ),
            [
                {
                    "error": (
                        "Expected 'Test that ...', not "
                        "'This is not the beginning of a test case.'"
                        ),
                    },
                ]
            )


    def test_no_description(self):
        """No description is ok."""
        self.assertEqual(
            self.parser().parse(
                textwrap.dedent("""
                Test That a perfectly good name
                When followed by another keyword
                Then may work out just fine
                """)
                ),
            [
                {
                    "name": "Test That a perfectly good name",
                    "description": "",
                    "steps": [
                        {
                            "instruction": "When followed by another keyword",
                            "expected": "Then may work out just fine",
                            }
                        ],
                    },
                ]
            )


    def test_and_in_expected_result(self):
        """'And' can occur in the midst of an expected result."""
        self.assertEqual(
            self.parser().parse(
                textwrap.dedent("""
                test That the word And
                Yes, that word
                When I place it in a result
                then it works
                And
                is included in the result
                """)
                ),
            [
                {
                    "name": "test That the word And",
                    "description": "Yes, that word",
                    "steps": [
                        {
                            "instruction": "When I place it in a result",
                            "expected": (
                                "then it works\n"
                                "And\n"
                                "is included in the result"
                                ),
                            },
                        ]
                    },
                ]
            )


    def test_early_end_begin(self):
        """Unexpected end of input causes error."""
        self.assertEqual(
            self.parser().parse(
                textwrap.dedent("""
                """)
                ),
            [
                {
                    "error": (
                        "Unexpected end of input, looking for 'Test That '"
                        ),
                    },
                ]
            )


    def test_early_end_pre_description(self):
        """Unexpected end of input after name causes error."""
        self.assertEqual(
            self.parser().parse(
                textwrap.dedent("""
                Test That a perfectly good name
                """)
                ),
            [
                {
                    "name": "Test That a perfectly good name",
                    "error": (
                        "Unexpected end of input, looking for 'When ' or 'And When '"
                        ),
                    },
                ]
            )


    def test_early_end_description(self):
        """Unexpected end of input in description causes error."""
        self.assertEqual(
            self.parser().parse(
                textwrap.dedent("""
                Test That a perfectly good name
                With some description
                """)
                ),
            [
                {
                    "name": "Test That a perfectly good name",
                    "description": "With some description",
                    "error": (
                        "Unexpected end of input, looking for 'When ' or 'And When '"
                        ),
                    },
                ]
            )


    def test_early_end_after_and(self):
        """Unexpected end of input after 'and' is ok."""
        self.assertEqual(
            self.parser().parse(
                textwrap.dedent("""
                Test That a perfectly good name
                And a good description
                When insufficiently assisted
                Then may not
                And
                """)
                ),
            [
                {
                    "name": "Test That a perfectly good name",
                    "description": "And a good description",
                    "steps": [
                        {
                            "instruction": "When insufficiently assisted",
                            "expected": "Then may not",
                            },
                        ],
                    "error": (
                        "Unexpected end of input, looking for 'When '"
                        ),
                    },
                ]
            )


    def test_unmatched_when_then(self):
        """Unexpected end of input in the midst of a step causes error."""
        self.assertEqual(
            self.parser().parse(
                textwrap.dedent("""
                Test that this case is good
                when ever you are
                tesT that this case is better
                when it's there
                 Test that bulk parsing works
                When I type a sonnet in the textarea
                And I sing my sonnet aloud
                And when I click the submit button
                When I am done
                Then I feel satisfied
                wHen nothing happens

                  tEst that another testcase works
                 With any old description
                  whEn I do this thing
                """)
                ),
            [
                {
                    "name": "Test that this case is good",
                    "description": "",
                    "steps": [
                        {
                            "instruction": (
                                "when ever you are"
                                ),
                            },
                        ]
                    },
                {
                    "name": "tesT that this case is better",
                    "description": "",
                    "steps": [
                        {
                            "instruction": (
                                "when it's there"
                                ),
                            },
                        ]
                    },
                {
                    "name": "Test that bulk parsing works",
                    "description": "",
                    "steps": [
                        {
                            "instruction": (
                                "When I type a sonnet in the textarea\n"
                                "And I sing my sonnet aloud"
                                ),
                            },
                        {
                            "instruction": "And when I click the submit button",
                            },
                        {
                            "instruction": "When I am done",
                            "expected": "Then I feel satisfied",
                            },
                        {
                            "instruction": "wHen nothing happens",
                            },
                        ]
                    },
                {
                    "name": "tEst that another testcase works",
                    "description": "With any old description",
                    "steps": [
                        {
                            "instruction": (
                                "whEn I do this thing"
                                ),
                            },
                        ],
                    },
                ]
            )


    def test_overlong_name_in_first_case(self):
        """Overlong name causes error."""
        self.assertEqual(
            self.parser().parse(
                textwrap.dedent("""
                Test That a super long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long name
                When the name is overlong
                Then causes error
                """)
                ),
            [
                {
                    "error": (
                        "Title should have at most 200 chracters, '"
                        "Test That a super long long long long long long lo"
                        "...'"
                        ),
                    },
                ]
            )


    def test_overlong_name_in_another_case(self):
        """Overlong name causes error."""
        self.assertEqual(
            self.parser().parse(
                textwrap.dedent("""
                Test that a perfectly good name
                when ever you are
                Test That a super long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long name
                When the name is overlong
                Then causes error
                """)
                ),
            [
                {
                    "name": "Test that a perfectly good name",
                    "description": "",
                    "steps": [
                        {
                            "instruction": (
                                "when ever you are"
                                ),
                            },
                        ]
                    },
                {
                    "error": (
                        "Title should have at most 200 chracters, '"
                        "Test That a super long long long long long long lo"
                        "...'"
                        ),
                    },
                ]
            )
