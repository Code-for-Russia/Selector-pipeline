from typing import Tuple

from org.codeforrussia.selector.standardizer.election_layers import ElectionLevel, ElectionLocationType, ElectionType

class ElectionAttributeRecognizer:
    def recognize(self, election_name) -> Tuple[ElectionLevel, ElectionType, ElectionLocationType]:
        """
        Recognizes election attributes from given name
        :param election_name: election name from the the protocol
        :return: tuple(election level, election type, election location type)
        """
        # TODO: add more accurate recognition; support all combinations
        lowercased_election_name = election_name.lower()
        if "депутатов государственной думы" in lowercased_election_name:
            return (ElectionLevel.FEDERAL, ElectionType.REPRESENTATIVE, None)
        elif any(all(pp in lowercased_election_name for pp in p) for p in [
            ["депутат", "город", "дум"],
            ["депутат", "город", "совет"],
            ["депутат", "город", "собран"],
        ]):
            return (ElectionLevel.MUNICIPAL, ElectionType.REPRESENTATIVE, ElectionLocationType.CITY_RURAL)
        elif any(all(pp in lowercased_election_name for pp in p) for p in [
            ["губернатор"],
            ["президент", "республик"],
            ["глав", "республик"],
            ["глав", "администрац", "област"],
        ]):
            return (ElectionLevel.REGIONAL, ElectionType.PERSONAL, None)
        elif any(all(pp in lowercased_election_name for pp in p) for p in [
            ["депутат", "совет", "республик"],
            ["депутат", "собран", "област"],
            ["депутат", "думы", "област"],
            ["депутат", "собран", "автоном", "округ"],
        ]):
            return (ElectionLevel.REGIONAL, ElectionType.REPRESENTATIVE, None)
        else:
            raise NotImplementedError(f"Cannot recognize election attributes by this election name: {election_name}")