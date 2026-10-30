#!/usr/bin/env python3
"""v188 UI-only display labels and source-verified embellishment categories.

Keep SimC's original tokens and existing immutable user-input contract.
Do not infer weapon/jewelry embellishment compatibility from the simulator:
SimulationCraft accepts embellishment= without checking crafting recipe rules.
"""
from __future__ import annotations

# Source: WoW Midnight Sunfire Silk and Arcanoweave Lining recipe usability,
# documented "most unembellished armor". No claim for jewelry or weapons.
ARMOR_SLOTS=frozenset(("head","shoulders","back","chest","wrists",
                       "hands","waist","legs","feet"))
KNOWN_EMBELLISHMENTS={
 "arcanoweave_lining":{
   "name":"비전직조 안감 (Arcanoweave Lining)",
   "effect":"주문·능력 사용 시 아군과 자신의 주능력치 증가 효과 발동",
   "category":"armor",
   "slots":tuple(sorted(ARMOR_SLOTS))},
 "sunfire_silk_lining":{
   "name":"태양불꽃 비단 안감 (Sunfire Silk Lining)",
   "effect":"지속 치유·피해로 주능력치 중첩 증가(15초, 최대 5중첩)",
   "category":"armor",
   "slots":tuple(sorted(ARMOR_SLOTS))},
}
# Presentation metadata only. Unknown numeric magnitudes are not invented.
CONSUMABLE_LABELS={
 "food":{
  "source_default":"전문화 기본 음식 (원본 설정 유지)",
  "harandar_celebration":"하란다르 축하 잔치 · 주능력치 +50",
  "silvermoon_parade":"실버문 행진 잔치 · 주능력치 +50",
  "royal_roast":"왕실 구이 (Royal Roast) · 주능력치 +65",
  "blooming_feast":"만개한 잔치 (Blooming Feast) · 가장 높은 보조능력치 +65",
  "disabled":"음식 효과 사용 안 함"},
 "potion":{
  "source_default":"전문화 기본 물약 (원본 설정 유지)",
  "potion_of_recklessness_2":"무모함의 물약 (2등급) · 30초간 최고 보조능력치 증가, 최저 보조능력치 일부 감소",
  "lights_potential_2":"빛의 잠재력 (2등급) · 30초간 주능력치 증가",
  "liquid_luster_2":"액체 광택 (Liquid Luster, 2등급) · 효과 상세 미확인",
  "disabled":"물약 사용 안 함"},
 "augmentation":{
  "source_default":"전문화 기본 증강룬 (원본 설정 유지)",
  "void_touched":"공허에 물든 증강룬 · 일정 시간 주능력치 증가",
  "void_touched_augment_rune":"공허에 물든 증강룬 (전체 SimC 토큰) · 일정 시간 주능력치 증가",
  "disabled":"증강룬 사용 안 함"},
 "diamond_id":{
  "0":"전문화 기본 다이아몬드 (원본 설정 유지)",
  "240983":"해독할 수 없는 에버송 다이아몬드 · 주능력치 +32",
  "240967":"강력한 에버송 다이아몬드 · 주능력치 +23, 서로 다른 색 보석당 치명타 효과 +0.15%"}
}
def labels():
    """Only return displayed strings for already source-whitelisted tokens."""
    import v108_native_consumable_inputs as runtime
    result={}
    for key in ("food","potion","augmentation"):
        allowed={"source_default",*runtime.SUPPORTED[key]}
        assert set(CONSUMABLE_LABELS[key])==allowed,(key,allowed)
        result[key]={k:CONSUMABLE_LABELS[key][k] for k in sorted(allowed)}
    allowed={"0",*(str(x) for x in runtime.DIAMONDS)}
    assert set(CONSUMABLE_LABELS["diamond_id"])==allowed
    result["diamond_id"]=dict(CONSUMABLE_LABELS["diamond_id"])
    return result

def public_embellishments():
    return {token:dict(metadata) for token,metadata in KNOWN_EMBELLISHMENTS.items()}

def check_embellishment(token,slot,need):
    entry=KNOWN_EMBELLISHMENTS.get(token)
    need(entry is not None,"CURRENT_SEASON_UNKNOWN_EMBELLISHMENT_TOKEN")
    need(slot in entry["slots"],
         "CURRENT_SEASON_EMBELLISHMENT_WRONG_EQUIPMENT_CATEGORY:"+slot)
    return entry
