# Risk of Rain 2 — Arabic glossary

The terminology contract. Every string in `lang/` must use these renderings, so
the same concept never appears under two names. Where a choice was not obvious,
the reasoning is recorded — including the options rejected.

The guiding rule: translate the **concept as a player experiences it**, not the
English word. RoR2's writing is terse, dry and a little grim; the Arabic should
read the same way, not like a manual.

## Names that stay untranslated

Survivor and boss proper nouns keep their identity. Transliterate only when the
name is pronounceable as a name; leave alphanumeric designations alone.

| English | Arabic | Note |
|---|---|---|
| Risk of Rain 2 | Risk of Rain 2 | brand; never translated |
| MUL-T, REX, HAN-D, TC-280, SPEX | unchanged | machine designations |
| Mithrix | ميثريكس | transliterated |
| Commando | الكوماندو | established loan |
| Huntress | الصيّادة | descriptive, so translated |
| Engineer | المهندس | descriptive |
| Mercenary | المرتزق | descriptive |
| Artificer | الساحرة | "Artificer" has no Arabic cognate; she is a fire/ice mage — الساحرة conveys the role. Rejected: الحرفيّة (literal, meaningless here) |
| Acrid | أكريد | proper noun |
| Loader | الشاحنة | rejected: اللودر (transliteration reads as machinery) |
| Captain | القبطان | |
| Bandit | قاطع الطريق | rejected: الباندِت |
| Railgunner | قنّاصة المدفع | descriptive; rejected: الريلغانر |
| Void Fiend | شيطان الفراغ | |
| Drifter | الهائم | |
| Seeker | الساعية | |
| False Son | الابن الزائف | |

## Core nouns

| English | Arabic | Reasoning |
|---|---|---|
| Survivor | ناجٍ / الناجي | the game's word for a playable character |
| Item | غرض | rejected: عنصر — correct but reads as "element"; غرض is what you actually pick up |
| Equipment | عتاد | the active-use slot, distinct from غرض |
| Teleporter | جهاز الانتقال | must stay distinct from Portal |
| Portal | بوّابة | |
| Chest | صندوق | |
| Shrine | مَزار | |
| Drone | مُسيَّرة | standard Arabic for an unmanned machine; rejected: درون |
| Turret | برج آلي | |
| Boss | زعيم | |
| Elite | نخبة | |
| Monster / enemy | وحش / عدوّ | |
| Stage | مرحلة | |
| Run | جولة | a single playthrough; rejected: تشغيل |
| Artifact | أثر | |
| Lunar Coin | عملة قمرية | |
| Scrap | خُردة | |
| Void | الفراغ | |
| Lunar | قمري | |

## Stats and combat

Keep these rigidly consistent — they appear in hundreds of item descriptions.

| English | Arabic | Reasoning |
|---|---|---|
| Damage | ضرر | |
| Health | صحة | |
| Shield | دِرع | |
| Armor | تدريع | deliberately different from دِرع so the two never collide |
| Barrier | حاجز | |
| Healing | شفاء | |
| Regeneration | تجدّد | |
| Cooldown | زمن الاستعادة | rejected: التبريد (literal "cooling", meaningless) |
| Critical Strike | ضربة حرجة | |
| Crit Chance | فرصة الضربة الحرجة | |
| Attack Speed | سرعة الهجوم | |
| Movement Speed | سرعة الحركة | |
| Sprint | العَدْو | |
| Skill | مهارة | |
| Level | مستوى | |
| Experience | خبرة | |
| Gold | ذهب | |
| Stack / per stack | لكل نسخة | "(+15% per stack)" → "(+15% لكل نسخة)" — rejected: لكل تراكم (opaque) |
| Proc | تفعيل | |
| Luck | حظ | |

## Skill slots

| English | Arabic |
|---|---|
| Primary | الأساسية |
| Secondary | الثانوية |
| Utility | المساعدة |
| Special | الخاصة |

## Difficulty — do not translate literally

The difficulty names are the game's rain metaphor, not difficulty labels. Rendering
them as سهل/متوسط/صعب would destroy the joke and the title's through-line.

| English | Arabic | Note |
|---|---|---|
| Drizzle | رذاذ | light rain |
| Rainstorm | عاصفة مطريّة | |
| Monsoon | موسميّة | from الرياح الموسمية |
| Eclipse | كسوف | |
| Simulacrum | المُحاكاة | |
| Prismatic Trials | التجارب المنشورية | |

## Keywords (the game's own defined vocabulary)

These are rendered as bold keyword headers in tooltips and must match everywhere.

| English | Arabic |
|---|---|
| Poisonous | سامّ |
| Regenerative | مُتجدِّد |
| Agile | رشيق |
| Sonic Boom | دوّي صوتي |
| Weaken | إنهاك |
| Heavy | ثقيل |
| Freezing | تجميد |
| Stunning | إذهال |
| Expose | كشف |
| Shocking | صعق |
| Slayer | فتّاك |
| Hemorrhage | نزيف حادّ |
| Ignite | إشعال |
| Weak Point | نقطة ضعف |
| Active Reload | إعادة تلقيم نشطة |
| Corruption | فساد |

## Style and mechanics

- **Second person, masculine singular.** The game addresses the player directly
  ("Chance to block incoming damage"). Arabic uses the implied "you"; avoid
  inventing a subject. Prefer verbal nouns for effects: "فرصة لصدّ الضرر الوارد."
- **Numbers stay Western digits** (15%, 4m, 1.0s) — the UI mixes them with bars
  and counters, and Eastern Arabic numerals would clash.
- **Units**: m → م, s → ث. "4m" → "4م", "10s" → "10ث".
- **Markup is untouchable.** `<style=...>`, `<sprite ...>`, `{0}` and friends are
  copied verbatim; only the text between them is translated. The build refuses
  any string whose tag or placeholder set differs from the English.
- **Item names are evocative, not literal.** "Tougher Times" is about surviving a
  rough patch, not about time — "أيّام عصيبة". Translate the image.
- **Lore entries** are in-world documents (transcripts, logs, letters). Keep the
  register: clipped, bureaucratic, occasionally unsettling.
