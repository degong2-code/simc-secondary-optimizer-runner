"""Source-observed color IDs, shared between preview and product build.

Only physical Midnight gem IDs already observed in pinned source profiles.
The fallback target-334 four-color choices are identical to v101's earlier
seven-spec contract. No gem effect or proc simulation.
"""
SOURCE_GEM_COLOR={
    240908:"garnet",240906:"garnet",
    240900:"amethyst",240898:"amethyst",
    240918:"lapis",
    240892:"peridot",240890:"peridot",
    # Other gem IDs remain unclassified; a color-required profile replaces
    # them via the already source-observed fallback IDs below.
}
FOUR_COLOR_GEMS={
    "garnet":240908,"amethyst":240900,
    "lapis":240918,"peridot":240892}
