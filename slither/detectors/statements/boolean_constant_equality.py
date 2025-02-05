"""
Module detecting misuse of Boolean constants
"""

from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification
from slither.slithir.operations import (
    Binary,
    BinaryType,
)
from slither.slithir.variables import Constant
from slither.utils.swc_mapping import SWCID


class BooleanEquality(AbstractDetector):
    """
    Boolean constant equality
    """

    ARGUMENT = "boolean-equal"
    HELP = "Comparison to boolean constant"
    IMPACT = DetectorClassification.INFORMATIONAL
    CONFIDENCE = DetectorClassification.HIGH

    WIKI = "https://github.com/crytic/slither/wiki/Detector-Documentation#boolean-equality"

    WIKI_TITLE = "Boolean equality"
    WIKI_DESCRIPTION = """Detects the comparison to boolean constants."""

    # region wiki_exploit_scenario
    WIKI_EXPLOIT_SCENARIO = """
```solidity
contract A {
	function f(bool x) public {
		// ...
        if (x == true) { // bad!
           // ...
        }
		// ...
	}
}
```
Boolean constants can be used directly and do not need to be compare to `true` or `false`."""
    # endregion wiki_exploit_scenario

    WIKI_RECOMMENDATION = """Remove the equality to the boolean constant."""

    SWCID = SWCID.NONE

    @staticmethod
    def _detect_boolean_equality(contract):

        # Create our result set.
        results = []

        # Loop for each function and modifier.
        # pylint: disable=too-many-nested-blocks
        for function in contract.functions_and_modifiers_declared:
            f_results = set()

            # Loop for every node in this function, looking for boolean constants
            for node in function.nodes:
                for ir in node.irs:
                    if isinstance(ir, Binary):
                        if ir.type in [BinaryType.EQUAL, BinaryType.NOT_EQUAL]:
                            for r in ir.read:
                                if isinstance(r, Constant):
                                    if isinstance(r.value, bool):
                                        f_results.add(node)
                results.append((function, f_results))

        # Return the resulting set of nodes with improper uses of Boolean constants
        return results

    def _detect(self):
        """
        Detect Boolean constant misuses
        """
        results = []
        for contract in self.contracts:
            boolean_constant_misuses = self._detect_boolean_equality(contract)
            for (func, nodes) in boolean_constant_misuses:
                for node in nodes:
                    info = [
                        func,
                        " compares to a boolean constant:\n\t-",
                        node,
                        "\n",
                    ]
                    info += f"\nSWCID: {self.SWCID} \n"
                    info += f"IMPACT: {self.IMPACT} \n"
                    res = self.generate_result(info)
                    results.append(res)

        return results
