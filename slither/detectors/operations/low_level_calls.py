"""
Module detecting usage of low level calls
"""

from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification
from slither.slithir.operations import LowLevelCall
from slither.utils.swc_mapping import SWCID

class LowLevelCalls(AbstractDetector):
    """
    Detect usage of low level calls
    """

    ARGUMENT = "low-level-calls"
    HELP = "Low level calls"
    IMPACT = DetectorClassification.INFORMATIONAL
    CONFIDENCE = DetectorClassification.HIGH

    WIKI = "https://github.com/crytic/slither/wiki/Detector-Documentation#low-level-calls"

    WIKI_TITLE = "Low-level calls"
    WIKI_DESCRIPTION = "The use of low-level calls is error-prone. Low-level calls do not check for [code existence](https://solidity.readthedocs.io/en/v0.4.25/control-structures.html#error-handling-assert-require-revert-and-exceptions) or call success."
    WIKI_RECOMMENDATION = "Avoid low-level calls. Check the call success. If the call is meant for a contract, check for code existence."
    SWCID = SWCID.SWC104

    @staticmethod
    def _contains_low_level_calls(node):
        """
             Check if the node contains Low Level Calls
        Returns:
            (bool)
        """
        return any(isinstance(ir, LowLevelCall) for ir in node.irs)

    def detect_low_level_calls(self, contract):
        ret = []
        for f in [f for f in contract.functions if contract == f.contract_declarer]:
            nodes = f.nodes
            assembly_nodes = [n for n in nodes if self._contains_low_level_calls(n)]
            if assembly_nodes:
                ret.append((f, assembly_nodes))
        return ret

    def _detect(self):
        """Detect the functions that use low level calls"""
        results = []
        for c in self.contracts:
            values = self.detect_low_level_calls(c)
            for func, nodes in values:
                info = ["Low level call in ", func, ":\n"]

                # sort the nodes to get deterministic results
                nodes.sort(key=lambda x: x.node_id)

                for node in nodes:
                    info += ["\t- ", node, "\n"]
                
                info += f"\nSWCID: {self.SWCID} \n"
                info += f"IMPACT: {self.IMPACT} \n"

                res = self.generate_result(info)

                results.append(res)

        return results
