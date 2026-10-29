# v157 craft / delve data scope — actual official API field probe

Developer-side read-only probe; no new item DB, no Native stats, no effect
certification, and no runtime linkage. This **does not** repeat raid/dungeon
collection. Blizzard authenticated field discovery is primary, v057 historical
51 candidates only aid overlap reports.

- Blizzard `profession/index` → Tailoring → exactly named Midnight skill tier
  → bounded recipe references → at most 3 recipe detail outputs.
- API ceilings: OAuth 1 + 6 Blizzard Game Data GET. Missing `crafted_item`
  is UNKNOWN, never 'not craftable'.
- One Tailoring profession is an intentional source-data sample, not claim of
  all crafted equipment or season-total recipe inventory.
- Reuse existing v046 exact variant static cache and v058 lazy-craft work where
  applicable. Newly fetched item IDs are not trusted SimC L by themselves.
- Delve sources are not boss loot lists: Bountiful reward chests, maps, Great
  Vault and reward merchants may differ. Official season notices show tiers
  and content but don't expose a confirmed one-stop public REST 'Delve all
  dropped items' index. Delve acquisition evidence remains UNCERTAIN until
  specific source data or actual API response supports IDs.
- 10 WCL raid/lair bosses discovered is an acquisition *scope*. One boss's
  16 loot IDs already checked in v156; the other 9 have not yet been hydrated.
  Do not confuse scope discovery and full drop-ID harvest.
- User-directed provenance authority: Blizzard live official drop/result IDs
  first, SimC data/effects/stats next, older v047/v057/WEQUIP information
  reference-only for comparison, never overwrite observed official IDs.

## Follow-up official item-identity check (no repeated profession traversal)

The first authenticated v157 run discovered Tailoring profession 197, its
Midnight skill tier 2918, 92 recipe references, and recipe IDs 52181/52173/52174.
Those three individual recipe details did **not** expose crafted output
item IDs. To avoid another six-call traversal, the follow-up uses three
`item/{id}` endpoints for old v057 item IDs 239656, 239652, 239653.
Matching official item names confirms item identity, not that a particular
recipe crafts it. Neither result provides an exact CHMV L or SimC effect.
