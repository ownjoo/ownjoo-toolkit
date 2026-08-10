"""User acceptance tests for all output and formatting utilities.

These tests demonstrate and verify that console output utilities produce
visually correct formatted output.
"""

import io
import unittest

from oj_toolkit import (
    Box,
    Color,
    ColoredText,
    Output,
    Table,
    progress_bar,
    status_badge,
    status_line,
)


class TestBasicColoredOutput(unittest.TestCase):
    """Verify basic colored output displays correctly."""

    def test_output_single_colors(self):
        """Test basic single color output."""
        output = io.StringIO()
        o = Output(stdout=output)
        o.out_red("Red text")
        o.out_green("Green text")
        o.out_yellow("Yellow text")
        o.out_blue("Blue text")

        result = output.getvalue()
        # Should contain color codes and text
        self.assertIn(Color.RED, result)
        self.assertIn(Color.GREEN, result)
        self.assertIn(Color.YELLOW, result)
        self.assertIn(Color.BLUE, result)
        self.assertIn("Red text", result)
        self.assertIn("Green text", result)

    def test_output_combined_colors(self):
        """Test combined colors and styles."""
        output = io.StringIO()
        o = Output(stdout=output)
        o.out_colored("Bold Red", color=Color.BOLD + Color.RED)
        o.out_colored("Dim Yellow", color=Color.DIM + Color.YELLOW)

        result = output.getvalue()
        self.assertIn(Color.BOLD, result)
        self.assertIn(Color.RED, result)
        self.assertIn(Color.DIM, result)
        self.assertIn(Color.YELLOW, result)
        self.assertIn("Bold Red", result)
        self.assertIn("Dim Yellow", result)

    def test_output_colored_shorthand_methods(self):
        """Verify shorthand color methods work correctly."""
        output = io.StringIO()
        o = Output(stdout=output)
        o.out_red("Error")
        o.out_green("Success")

        result = output.getvalue()
        self.assertIn(Color.RED, result)
        self.assertIn(Color.GREEN, result)


class TestColoredTextChaining(unittest.TestCase):
    """Verify ColoredText chainable builder produces correct output."""

    def test_colored_text_basic_chain(self):
        """Test basic color chaining."""
        colored = ColoredText().red("ERROR: ").green("fixed").add(" ✓")
        result = str(colored)

        # Should contain color codes for both red and green
        self.assertIn(Color.RED, result)
        self.assertIn(Color.GREEN, result)
        self.assertIn("ERROR: ", result)
        self.assertIn("fixed", result)

    def test_colored_text_complex_chain(self):
        """Test complex multi-segment coloring."""
        colored = (
            ColoredText()
            .bold("Build: ")
            .green("OK")
            .add(" | ")
            .bold("Tests: ")
            .green("OK")
            .add(" | ")
            .bold("Deploy: ")
            .red("FAILED")
        )
        result = str(colored)

        # Should have multiple color segments
        self.assertIn("Build:", result)
        self.assertIn("Tests:", result)
        self.assertIn("Deploy:", result)
        self.assertIn(Color.BOLD, result)
        self.assertIn(Color.GREEN, result)
        self.assertIn(Color.RED, result)

    def test_colored_text_output_to_stream(self):
        """Test ColoredText output to stream."""
        output = io.StringIO()
        colored = ColoredText(stdout=output).red("Error").add(": ").yellow("failed")
        colored.out()

        result = output.getvalue()
        self.assertIn(Color.RED, result)
        self.assertIn(Color.YELLOW, result)


class TestTableFormatting(unittest.TestCase):
    """Verify table formatting displays correctly."""

    def test_table_with_headers(self):
        """Test table renders with proper headers."""
        table = Table(headers=["Name", "Status"], columns=2, style="ascii")
        table.add_row("Task 1", "OK")
        table.add_row("Task 2", "FAILED")

        result = str(table)

        # Should contain borders
        self.assertIn("+", result)
        self.assertIn("-", result)
        # Should contain headers and data
        self.assertIn("Name", result)
        self.assertIn("Status", result)
        self.assertIn("Task 1", result)
        self.assertIn("Task 2", result)
        # Should have at least 3 lines (header, separator, data rows)
        lines = result.split("\n")
        self.assertGreater(len([line for line in lines if line.strip()]), 2)

    def test_table_dict_input_detection(self):
        """Test table auto-detects dict input and extracts headers."""
        data = [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}]
        table = Table(style="ascii")
        table.add_rows(data)

        result = str(table)

        # Should auto-detect and use dict keys as headers
        self.assertIn("id", result)
        self.assertIn("name", result)
        self.assertIn("Alice", result)
        self.assertIn("Bob", result)

    def test_table_tuple_input(self):
        """Test table with tuple input."""
        table = Table(style="ascii")
        table.add_rows([("Task 1", "OK"), ("Task 2", "ERROR")])

        result = str(table)

        self.assertIn("Task 1", result)
        self.assertIn("OK", result)
        self.assertIn("ERROR", result)

    def test_table_alignment_and_padding(self):
        """Test table respects alignment and padding."""
        table = Table(headers=["Col1", "Col2"], columns=2, style="ascii", padding=2)
        table.add_row("A", "B")

        result = str(table)

        # More padding = wider table
        lines = result.split("\n")
        # Border line should be reasonably wide
        self.assertGreater(len(lines[0]), 10)

    def test_table_with_colored_content(self):
        """Test table can contain colored text."""
        table = Table(headers=["Task", "Status"], columns=2, style="ascii")
        table.add_row("Build", status_badge("OK", "ok"))
        table.add_row("Deploy", status_badge("FAILED", "error"))

        result = str(table)

        # Should have table structure
        self.assertIn("+", result)
        self.assertIn("Task", result)
        self.assertIn("Status", result)
        # Should have colored badges
        self.assertIn("[OK]", result)
        self.assertIn("[ERROR]", result)


class TestBoxFormatting(unittest.TestCase):
    """Verify box formatting displays correctly."""

    def test_box_basic_rendering(self):
        """Test box renders with borders."""
        box = Box(style="ascii")
        box.add_line("Hello")
        box.add_line("World")

        result = str(box)

        # Should have borders
        self.assertIn("+", result)
        self.assertIn("-", result)
        # Should contain content
        self.assertIn("Hello", result)
        self.assertIn("World", result)
        # Should have multiple lines
        lines = [line for line in result.split("\n") if line.strip()]
        self.assertGreaterEqual(len(lines), 4)  # Top border, 2 content, bottom border

    def test_box_with_padding(self):
        """Test box respects padding."""
        box_no_pad = Box(style="ascii", padding=0)
        box_no_pad.add_line("X")
        result_no_pad = str(box_no_pad)

        box_pad = Box(style="ascii", padding=2)
        box_pad.add_line("X")
        result_pad = str(box_pad)

        # With padding should be wider
        self.assertGreater(
            len(result_pad.split("\n", maxsplit=1)[0]), len(result_no_pad.split("\n", maxsplit=1)[0])
        )

    def test_box_with_fixed_width(self):
        """Test box with fixed width."""
        box = Box(style="ascii", width=40)
        box.add_line("Content")

        result = str(box)
        lines = result.split("\n")

        # All lines should be approximately the specified width
        for line in lines:
            if line.strip():
                self.assertGreater(len(line), 35)
                self.assertLess(len(line), 45)

    def test_box_with_colored_content(self):
        """Test box can contain colored text."""
        box = Box(style="ascii")
        box.add_line(status_line("Status", "OK", color=Color.GREEN))
        box.add_line(status_line("Error", "None", color=Color.RED))

        result = str(box)

        # Should have box structure
        self.assertIn("+", result)
        # Should have colored content
        self.assertIn(Color.GREEN, result)
        self.assertIn(Color.RED, result)


class TestStatusIndicators(unittest.TestCase):
    """Verify status indicators format correctly."""

    def test_status_line_formatting(self):
        """Test status_line produces correct format."""
        result = status_line("Server", "Running")

        # Should contain both label and value with separator
        self.assertIn("Server", result)
        self.assertIn("Running", result)
        self.assertIn(": ", result)
        self.assertEqual(result, "Server: Running")

    def test_status_line_with_color(self):
        """Test status_line applies color to value."""
        result = status_line("Status", "OK", color=Color.GREEN)

        # Should contain color codes and reset
        self.assertIn(Color.GREEN, result)
        self.assertIn(Color.RESET, result)
        self.assertIn("Status", result)
        self.assertIn("OK", result)

    def test_status_badge_colors(self):
        """Test status badges use correct semantic colors."""
        ok_badge = status_badge("Ready", "ok")
        error_badge = status_badge("Failed", "error")
        warning_badge = status_badge("Partial", "warning")
        info_badge = status_badge("Info", "info")

        # Should contain badges with correct colors
        self.assertIn("[OK]", ok_badge)
        self.assertIn(Color.GREEN, ok_badge)

        self.assertIn("[ERROR]", error_badge)
        self.assertIn(Color.RED, error_badge)

        self.assertIn("[WARNING]", warning_badge)
        self.assertIn(Color.YELLOW, warning_badge)

        self.assertIn("[INFO]", info_badge)
        self.assertIn(Color.CYAN, info_badge)

    def test_progress_bar_display(self):
        """Test progress bar formats correctly."""
        # Test various percentages
        bar_0 = progress_bar(0, width=10)
        bar_50 = progress_bar(50, width=10)
        bar_100 = progress_bar(100, width=10)

        # All should contain percentage
        self.assertIn("0%", bar_0)
        self.assertIn("50%", bar_50)
        self.assertIn("100%", bar_100)

        # Should show progress visually
        # 0% should have more empty
        # 100% should have more filled
        self.assertIn("█", bar_100)

    def test_progress_bar_with_label(self):
        """Test progress bar with label."""
        p_bar = progress_bar(75, width=20, label="Download")

        self.assertIn("Download", p_bar)
        self.assertIn("75%", p_bar)

    def test_progress_bar_custom_characters(self):
        """Test progress bar with custom fill/empty characters."""
        p_bar = progress_bar(50, width=10, filled="=", empty="-")

        self.assertIn("=", p_bar)
        self.assertIn("-", p_bar)
        self.assertIn("50%", p_bar)


class TestIntegratedOutput(unittest.TestCase):
    """Test outputs working together in integrated scenarios."""

    def test_colored_text_in_table(self):
        """Test table can display colored text segments."""
        table = Table(headers=["Component", "Status"], columns=2, style="ascii")

        # Add colored status badges
        table.add_row("API", status_badge("OK", "ok"))
        table.add_row("Database", status_badge("SLOW", "warning"))
        table.add_row("Cache", status_badge("DOWN", "error"))

        result = str(table)

        # Should have table structure
        self.assertIn("+", result)
        self.assertIn("Component", result)
        # Should preserve colored content
        self.assertIn("[OK]", result)
        self.assertIn("[WARNING]", result)
        self.assertIn("[ERROR]", result)

    def test_colored_text_in_box(self):
        """Test box can display multiple colored segments."""
        box = Box(style="ascii")
        box.add_line(status_line("Build", "OK", color=Color.GREEN))
        box.add_line(status_line("Tests", "OK", color=Color.GREEN))
        box.add_line(status_line("Deploy", "FAILED", color=Color.RED))

        result = str(box)

        # Should have box borders
        self.assertIn("+", result)
        # Should have colored content
        self.assertIn(Color.GREEN, result)
        self.assertIn(Color.RED, result)
        # Should have all status lines
        self.assertIn("Build", result)
        self.assertIn("Tests", result)
        self.assertIn("Deploy", result)

    def test_output_with_colored_text_builder(self):
        """Test Output class with ColoredText builder."""
        out = io.StringIO()
        o = Output(stdout=out)

        # Use Output to create and output colored text
        segment = o.segment().red("ERROR: ").bold("critical").add(" failure")
        segment.out()

        result = out.getvalue()

        self.assertIn(Color.RED, result)
        self.assertIn(Color.BOLD, result)
        self.assertIn("ERROR: ", result)
        self.assertIn("critical", result)


class TestVisualConsistency(unittest.TestCase):
    """Test visual consistency of output formatting."""

    def test_table_borders_consistent(self):
        """Test table borders are consistent across rows."""
        table = Table(headers=["A", "B", "C"], columns=3, style="ascii")
        table.add_row("1", "2", "3")
        table.add_row("4", "5", "6")

        result = str(table)
        lines = result.split("\n")

        # Find all border lines (containing +)
        border_lines = [line for line in lines if "+" in line and "-" in line]

        # Should have at least 2 border lines (top and bottom)
        self.assertGreaterEqual(len(border_lines), 2)

        # First and last border lines should have same structure
        if len(border_lines) >= 2:
            # Same width at least
            self.assertEqual(len(border_lines[0]), len(border_lines[-1]))

    def test_box_borders_complete(self):
        """Test box has complete borders on all sides."""
        box = Box(style="ascii")
        box.add_line("Content")

        result = str(box)
        lines = result.split("\n")

        # Should have at least top, content, bottom
        self.assertGreaterEqual(len(lines), 3)

        # First line should start with + (top-left corner)
        self.assertTrue(lines[0].startswith("+"))
        # Last line should start with + (bottom-left corner)
        self.assertTrue(lines[-1].startswith("+"))

        # All content lines should have side borders
        for line in lines[1:-1]:
            if line.strip():
                self.assertTrue(line.startswith("|") or line.startswith("+"))

    def test_progress_bar_consistent_width(self):
        """Test progress bars maintain consistent visual width."""
        bars = [progress_bar(p, width=20) for p in [0, 25, 50, 75, 100]]

        # All bars should have similar overall length
        lengths = [len(b) for b in bars]
        # Should be within a few characters of each other
        self.assertLess(max(lengths) - min(lengths), 5)


if __name__ == "__main__":
    unittest.main()
