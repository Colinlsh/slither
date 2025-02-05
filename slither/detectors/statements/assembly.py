"""
Module detecting usage of inline assembly
"""

from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification
from slither.core.cfg.node import NodeType
from slither.utils.swc_mapping import SWCID


class Assembly(AbstractDetector):
    """
    Detect usage of inline assembly
    """

    ARGUMENT = "assembly"
    HELP = "Assembly usage"
    IMPACT = DetectorClassification.INFORMATIONAL
    CONFIDENCE = DetectorClassification.HIGH

    WIKI = "https://github.com/crytic/slither/wiki/Detector-Documentation#assembly-usage"

    WIKI_TITLE = "Assembly usage"
    WIKI_DESCRIPTION = "The use of assembly is error-prone and should be avoided."
    WIKI_RECOMMENDATION = "Do not use `evm` assembly."
    SWCID = SWCID.SWC127

    @staticmethod
    def _contains_inline_assembly_use(node):
        """
             Check if the node contains ASSEMBLY type
        Returns:
            (bool)
        """
        return node.type == NodeType.ASSEMBLY

    def detect_assembly(self, contract):
        ret = []
        for f in contract.functions:
            if f.contract_declarer != contract:
                continue
            nodes = f.nodes
            assembly_nodes = [n for n in nodes if self._contains_inline_assembly_use(n)]
            if assembly_nodes:
                ret.append((f, assembly_nodes))
        return ret

    def _detect(self):
        """Detect the functions that use inline assembly"""
        results = []
        for c in self.contracts:
            values = self.detect_assembly(c)
            for func, nodes in values:
                info = [func, " uses assembly\n"]

                # sort the nodes to get deterministic results
                nodes.sort(key=lambda x: x.node_id)

                for node in nodes:
                    info += ["\t- ", node, "\n"]
                    
                info += f"\nSWCID: {self.SWCID} \n"
                info += f"IMPACT: {self.IMPACT} \n"
                res = self.generate_result(info)
                results.append(res)

        return results
