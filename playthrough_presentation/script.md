# The Keeper and the Beacon — a played-through review of LLM Monster Hunter

Narration script. Each `## NN — Title` section becomes `audio/NN.mp3`
via `generate_audio.py` (same pipeline as playtest_presentation). The
deck in `data.js` points each slide at its section number.

## 01 — This time, somebody played it

The last presentation was called Playtesting Without Playing. This one is the opposite. One evening, one fresh save, image generation switched on, and every shipped system touched the way a real player would touch it — by clicking on things and finding out. The save was wiped from the title screen, a new character was built from nothing, and two full expeditions went down into the dark and came back. Everything you are about to see is a real screenshot from that session. Nothing was staged, and the bugs you will hear about were found the honest way — by walking into them.

## 02 — Making Maren

Character creation is seven questions, and a language model writes the answers you choose between. Fresh ideas on every step, or write your own — the game promises your words win. The archetypes on step one were already strong: a stitched-together simulacrum of three dead lovers, a wyrmling whose hoard is the last words of the dying. We chose the lighthouse keeper who saw something rise from the deep twenty years ago and hasn't spoken since. Named her Maren Holt, in our own words, into the free-text box. From there the wizard started paying attention: the origin options knew about the lighthouse, the wish options knew about the ship the sea took. The wish we picked shapes the whole story — bring back the Merrow Bell, crew and all, and finally turn off the lamp.

## 03 — The portrait

Step seven writes an artist's brief instead of a character sheet — the exact words become the portrait prompt. Ours asked for a woman round-shouldered from leaning into storms, with a single streak of lighthouse-red through a dark braid. One click on Paint portrait, about twenty seconds of Gemini, and there she was — weathered, unblinking, the lighthouse on the cliffs behind her. The brief was honored almost line for line. You can paint another, upload your own, or walk in faceless; the game is graceful about all three. This is the moment the save stopped being data and started being a person.

## 04 — A wish, and a door

The guided first run opens with prose built from every wizard answer — the unfinished letter, the cottage door she couldn't close, the lamp still burning behind her eyes. Then a goal appears at the top of the screen and stays there: leave the dungeon with a new companion at your side. Structure and story arrive in the same breath. The dungeon deals you hand-written paths — a bellflower archway, a root-wound stair — and every room you enter is composed on the spot, streamed token by token while you watch. The pacing has a rhythm to it: read, choose, wait a few seconds while the world writes itself, read what you caused.

## 05 — Luminel makes an entrance

In the Gossamer Glade the game introduced its first monster, and it introduced it as a character, not an encounter. Luminel, a moth-fey that treats dusk as a private stage, arrived to the scent of honeysuckle applause — and its card art painted itself in the background while the prose was still streaming. Then it asked, in a borrowed voice, whether we would remember it when dawn comes. The game handed us a text box: answer honestly, bargain, flatter, deceive — the monster decides what to make of it. Maren told it the truth: I kept a lamp burning twenty years because I do not forget anyone. Not one soul. The reply came back with our own words woven into it, and a banner announced a new companion. We recruited an epic monster by meaning what we said.

## 06 — The lullaby fight

The Sighing Gallery held the game's first battle — a fern-mimic called Sighmoss whose weapon is a lullaby it genuinely believes is a favor. Combat is turn-based, refereed by the model, with code holding the numbers. Luminel, freshly recruited and still wary, acted on its own terms — the game does not hand you a new friend's obedience, and it tells you so in the fiction. Maren's turn offered attack, defend, ability, item, talk — and a custom action box that says: describe what you attempt, the referee decides. We unshuttered her storm-lantern and cut the lullaby out of the air, and the referee improvised the beam refracting through Luminel's drifting wing-scales — a synergy nobody scripted. Then, with the fern exhausted and singing to itself, the game let Maren win by talking: she promised it dawn, and it curled up and slept. Victory, no killing blow, and a collectible token minted to commemorate exactly the fight we actually had.

## 07 — Growth you can read

Walking out changed the party in ways the game showed us instead of telling us. Luminel's attack ticked up, its signature ability was rewritten — the thirty-foot spectacle became an intimate, single-target gift, because the story had been about learning to shine for someone instead of at them — and its bond badge moved from wary to familiar. Under the hood, every change landed as a first-person memory in the database: I poured my light into Maren Holt not once but twice. Even Sighmoss, the monster we sang to sleep, keeps a memory of yielding — it can return in a future run, and it will remember. This is the loop the whole game is built on: what happens becomes who they are.

## 08 — The altar and the campfire

Home base is where the systems compound. At the campfire, Maren told Luminel the name of the drowned ship, and the fey replayed it back in wind-chime voices and swore to carry it if her eyes ever close — a conversation the memory system quietly filed away, and one the bond ladder credited that night. At the Evolution Altar, we whispered a direction — let the performer become a keeper of light — and the game rewrote the creature to more of what it already was. Luminel Aeterna, epic to legendary, its backstory honored, its lineage recorded with our whisper quoted inside it. And the art regeneration used the old card as a reference: same creature, same pose, same branch — but the wings are constellation charts now, and the antennae burn like wicks. Before and after, unmistakably the same soul.

## 09 — The reef that tested us back

Run two started at a notice board — three hand-written expeditions with danger words instead of difficulty numbers. We answered the Glass Reef, calm, chasing a goal with a fragile clause: retrieve a scale from the Crystalline Leviathan's hide without breaking it. The reef was a themed ecosystem — every creature in it obsessed with light and being seen, which meant every negotiation was really about Maren. A prism-jelly demanded to know which of us fades when no one watches, and traded passage for a promise that the story of it would be beautiful. A crystal trilobite asked the most beautiful thing she had ever witnessed — and her honest answer, the thing that rose the night the Merrow Bell sank, was quietly canonized by the game: what she saw twenty years ago was a leviathan. The tenders gave us the scale. We never drew a weapon in the whole run — we sneaked twice, camped once over tea warmed on Luminel's antennae, and talked our way to the goal.

## 10 — The crash that became canon

Midway through the evening the machine itself failed us — an update forced a restart with a run half-finished. The game's answer is the best crash handling I have seen in an indie build: the title screen said the last expedition never came home, an unknown force overwhelmed the party mid-journey, and they woke safe at home base with the story carrying the scar. No corrupted save, no rollback, no apology dialog — the interruption was absorbed into the fiction, and the chronicle numbering respects it. Run three's chronicle exists because run two is a ghost story now. Losses in this game are narrated, not swallowed.

## 11 — What broke, and what it cost

Now the ledger. One real functional bug: the exchange text box silently eats any message over five hundred characters — the backend rejects it correctly, but the interface showed nothing, and in dev the uncaught error locked the screen. Maren's best speech died in that box. One celebration bug: clicking the victory token makes the card vanish instead of showing it claimed — the token survives in the inventory, but the moment is stolen. The prose occasionally forgot its pronouns — Maren became he for a paragraph, twice. Dev panels greet a brand-new player expanded over the title screen, and the item shelves borrow monster-collection controls that say monsters per page. All of it was fixed in the same session it was found, and the fixes are in the same commit history as this presentation. Two pacing notes survive as advice rather than bugs: encounters make you wait for card art before you may act, and the enemy card's health numbers never move — the condition badges are the truth, but the numbers read like a broken display.

## 12 — The verdict

Did it feel like a game? Yes — and more specifically, like a game with taste. Fairness held: the referee never once cheated us, costs came out of real resource ladders, the wary companion genuinely would not take orders, and every soft resolution was earned with words that fit the fiction. If anything it is too generous — three negotiations, three successes; the game should sometimes say no to a good speech. The story is the strongest system. A character invented in seven questions ended the night with a drowned ship's name carried by an evolved beacon-fey, a scale given rather than taken, and a chronicle that reads like someone meant it. The monster-catching genre asks what if creatures were friends; this build asks what if they remembered — and it answers on screen, in the art, in the stats, in the prose. It is fully playable today. It is occasionally slow, it is sometimes too kind, and it is the only game I have played where mercy is a build.
