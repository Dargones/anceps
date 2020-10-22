from tqdm import tqdm
from src.scan.meter import Meter
from src.scan.scansion import Scansion
from collections import defaultdict
import warnings


def analyse(data):
    """
    Analyze the scanned data and record various statistics such as elision occurrence
    :param data:
    :return: a dictionary with various statistical measurements
    """
    print("Analysis in progress...")
    stats = defaultdict(dict)
    dummy_func = lambda *args: None  # function used if look up of a function fails
    for verse in tqdm(data.values()):
        meter = Meter.METERS[verse["meter"]]
        decomposition = meter.decompose(Scansion(verse["scansion"]), turn_off_assertions=True)
        if len(decomposition) != 1:
            warnings.warn("Multiple ways to decompose a scansion!")
        decomposition = decomposition[0]
        record_global(decomposition, verse, stats["global"])  # record global statistics
        globals().get("record_" + meter.name, dummy_func)(decomposition, verse, stats[meter.name])
    for key in stats:
        globals().get("finalize_" + key, dummy_func)(stats[key])
    return stats


def record_trimeterDATI(decomposition, verse, stats):
    return record_trimeter(decomposition, verse, stats)


def record_trimeterCORRER(decomposition, verse, stats):
    return record_trimeter(decomposition, verse, stats)


def record_trimeter(decomposition, verse, stats):
    """
    Function called to record statistics about a verse of trimeter
    :param decomposition:   decomposition of verse into six feet
    :param verse:           verse dictionary
    :param stats:           dictionary to fill with statistics
    :return:                None
    """
    if len(stats) == 0:
        stats["resolution"] = Distribution("foot_")
        stats["patterns"] = Distribution("")
    stats["patterns"].add(verse["pattern"], 1)
    for i, foot in enumerate(decomposition):
        stats["resolution"].add(i, len(foot.pattern) - 2)


def finalize_trimeterDATI(stats):
    return finalize_trimeter(stats)


def finalize_trimeterCORRER(stats):
    return finalize_trimeter(stats)


def finalize_trimeter(stats):
    """
    Function called after all the statistics about trimeter was recorded
    :param stats:           dictionary to fill with statistics
    :return:                None
    """
    stats["patterns"].calculate_frequencies()
    stats["patterns"] = stats["patterns"].data
    stats["resolution"].calculate_frequencies(stats["patterns"]["counts"]["total"])
    stats["resolution"] = stats["resolution"].data


def record_global(decomposition, verse, stats):
    """
    Function called to record global statistics about a verse in the text
    :param decomposition:   decomposition of verse into six feet
    :param verse:           verse dictionary
    :param stats:           dictionary to fill with statistics
    :return:                None
    """
    if len(stats) == 0:
        stats["elision"] = Distribution("foot_")
        stats["method"] = defaultdict(int)
    stats["method"][verse["method"]] += 1
    for i, foot in enumerate(decomposition):
        stats["elision"].add(i, foot.count_elisions())


def finalize_global(stats):
    """
    Function called after all the global statistics about the text was recorded
    :param stats:           dictionary to fill with statistics
    :return:                None
    """
    total = sum([stats["method"][x] for x in stats["method"].keys()
                 if x.split(" ")[0] not in ["total", "failed"]])
    stats["elision"].calculate_frequencies(total)
    stats["elision"] = stats["elision"].data


class Distribution:
    """A class to store simple frequency data (elision rates, resolution rates, etc.)"""

    def __init__(self, prefix):
        """
        Initialize a Distribution object with a dictionary that stores integer counts
        :param prefix: prefix to use for all keys (e.g. "foot_")
        """
        self.data = {"counts": defaultdict(int)}
        self.prefix = prefix

    def add(self, key, amount):
        """
        Add a certain amount to an integer counter
        :param key:     a key by which the counter is identified
        :param amount:  amount to add
        :return:
        """
        assert(key != "total")
        self.data["counts"][key] += amount
        self.data["counts"]["total"] += amount

    def calculate_frequencies(self, total=None):
        """
        Calculate frequencies from raw counts.
        The "total" frequency is calcuulated as self.data["counts"]["total"]/total
        :param total: the denominator to use when calculating frequency for total
        :return:
        """
        self.data["frequencies"] = {}
        for key in self.data["counts"]:
            self.data["frequencies"][key] = self.data["counts"][key] / self.data["counts"]["total"]
        if total:
            self.data["frequencies"]["total"] = self.data["counts"]["total"] / total
