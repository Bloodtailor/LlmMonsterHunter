// The deck. One entry per narrated section; `keys` are the screenshot
// keyframes shown while that section's audio plays. `at` is a FRACTION
// of the section's audio duration (0..1) so timing survives any edit to
// the narration. Every image is a real, unstaged screenshot from the
// played session.
const DECK = [
  {
    n: '01',
    eyebrow: 'The session',
    title: 'This time, somebody played it',
    audio: 'audio/01.mp3',
    keys: [
      { img: 'shots/01_title.png', at: 0, cap: 'A fresh save. The old world is about to be erased.' },
      { img: 'shots/02_settings_images.png', at: 0.45, cap: 'Painting on — Gemini paints everything this session.' },
      { img: 'shots/03_new_game_confirm.png', at: 0.75, cap: 'The game makes you mean it.' },
    ],
  },
  {
    n: '02',
    eyebrow: 'Character creation',
    title: 'Making Maren',
    audio: 'audio/02.mp3',
    keys: [
      { img: 'shots/04_wizard_what_are_you.png', at: 0, cap: 'Step 1 of 7 — four archetypes and a box where your words win.' },
      { img: 'shots/05_wizard_origin.png', at: 0.38, cap: 'By step 3 the options know her by name.' },
      { img: 'shots/06_wizard_wish.png', at: 0.62, cap: 'The wish that will shape the whole story.' },
      { img: 'shots/07_wizard_role.png', at: 0.85, cap: 'Combat role is a fixed word-ladder — code owns these.' },
    ],
  },
  {
    n: '03',
    eyebrow: 'Image generation',
    title: 'The portrait',
    audio: 'audio/03.mp3',
    keys: [
      { img: 'shots/08_wizard_appearance.png', at: 0, cap: 'Step 7 writes an artist’s brief, not a stat block.' },
      { img: 'shots/09_portrait_painting.png', at: 0.35, cap: 'Twenty seconds of Gemini.' },
      { img: 'shots/10_portrait_full.png', at: 0.55, cap: 'The brief, honored line for line.' },
    ],
  },
  {
    n: '04',
    eyebrow: 'The guided first run',
    title: 'A wish, and a door',
    audio: 'audio/04.mp3',
    keys: [
      { img: 'shots/11_wish_and_door.png', at: 0, cap: 'Prose assembled from every wizard answer.' },
      { img: 'shots/13_goal_glade.png', at: 0.42, cap: 'A goal appears and stays: leave with a companion.' },
      { img: 'shots/12_paths.png', at: 0.7, cap: 'Every path is written on the spot.' },
    ],
  },
  {
    n: '05',
    eyebrow: 'First contact',
    title: 'Luminel makes an entrance',
    audio: 'audio/05.mp3',
    keys: [
      { img: 'shots/14_luminel_card.png', at: 0, cap: 'Card art paints itself while the prose still streams.' },
      { img: 'shots/15_exchange.png', at: 0.35, cap: '“Would you remember me when the dawn comes?”' },
      { img: 'shots/16_companion.png', at: 0.75, cap: 'Recruited by meaning what we said.' },
    ],
  },
  {
    n: '06',
    eyebrow: 'Combat',
    title: 'The lullaby fight',
    audio: 'audio/06.mp3',
    keys: [
      { img: 'shots/17_confrontation.png', at: 0, cap: '“Stop fighting it, you’re so safe, you’re so safe…”' },
      { img: 'shots/18_battle_party.png', at: 0.22, cap: 'Maren fights beside a companion that will not take orders yet.' },
      { img: 'shots/19_custom_action.png', at: 0.42, cap: 'Describe what you attempt. The referee decides.' },
      { img: 'shots/20_lantern_ruling.png', at: 0.6, cap: 'The referee improvises a synergy nobody scripted.' },
      { img: 'shots/21_victory_cocatok.png', at: 0.82, cap: 'Victory without a killing blow — and a token to prove it.' },
    ],
  },
  {
    n: '07',
    eyebrow: 'Progression',
    title: 'Growth you can read',
    audio: 'audio/07.mp3',
    keys: [
      { img: 'shots/40_surface_run1.png', at: 0, cap: 'Back to the surface — with a reward that fits the goal.' },
      { img: 'shots/22_party_home.png', at: 0.4, cap: 'Stats up, ability rewritten, bond deepened.' },
      { img: 'shots/26_sanctuary.png', at: 0.72, cap: 'Even the monster we spared keeps a memory of yielding.' },
    ],
  },
  {
    n: '08',
    eyebrow: 'Home base',
    title: 'The altar and the campfire',
    audio: 'audio/08.mp3',
    keys: [
      { img: 'shots/23_campfire.png', at: 0, cap: 'The Merrow Bell, named and entrusted.' },
      { img: 'shots/24_evolution_streaming.png', at: 0.38, cap: 'The story tells itself…' },
      { img: 'shots/25_evolved_card.png', at: 0.62, cap: 'Same soul, new sky: reference-image regeneration.' },
    ],
  },
  {
    n: '09',
    eyebrow: 'Run two',
    title: 'The reef that tested us back',
    audio: 'audio/09.mp3',
    keys: [
      { img: 'shots/30_notices2.png', at: 0, cap: 'Danger comes as a word, not a number.' },
      { img: 'shots/31_camp.png', at: 0.18, cap: 'Camp: tea warmed on a beacon-fey’s antennae.' },
      { img: 'shots/32_sneak.png', at: 0.34, cap: 'A beacon that knows when not to shine.' },
      { img: 'shots/33_kelyx.png', at: 0.48, cap: 'Kelyx trades passage for a beautiful story.' },
      { img: 'shots/34_lumenisca.png', at: 0.63, cap: 'The tenders of the keel ask their one question.' },
      { img: 'shots/35_beauty_answer.png', at: 0.76, cap: 'Her honest answer becomes canon.' },
      { img: 'shots/36_leviathans_wake.png', at: 0.9, cap: 'A heartbeat that isn’t hers.' },
    ],
  },
  {
    n: '10',
    eyebrow: 'Resilience',
    title: 'The crash that became canon',
    audio: 'audio/10.mp3',
    keys: [
      { img: 'shots/29_scar.png', at: 0, cap: 'A forced reboot, absorbed into the fiction.' },
      { img: 'shots/38_chronicle.png', at: 0.6, cap: 'The chronicle numbering respects the ghost run.' },
    ],
  },
  {
    n: '11',
    eyebrow: 'The ledger',
    title: 'What broke, and what it cost',
    audio: 'audio/11.mp3',
    keys: [
      { img: 'shots/39_bug_cocatok.png', at: 0, cap: 'The vanishing victory token — minted, then hidden by a click.' },
      { img: 'shots/41_fix_counter.png', at: 0.45, cap: 'The fix: a visible limit, and errors that speak.' },
      { img: 'shots/42_fix_title.png', at: 0.75, cap: 'First impressions repaired: the game greets you, not the debug tools.' },
    ],
  },
  {
    n: '12',
    eyebrow: 'The verdict',
    title: 'Mercy is a build',
    audio: 'audio/12.mp3',
    keys: [
      { img: 'shots/10_portrait_full.png', at: 0, cap: 'A person invented in seven questions.' },
      { img: 'shots/25_evolved_card.png', at: 0.3, cap: 'A companion that remembers why it changed.' },
      { img: 'shots/38_chronicle.png', at: 0.55, cap: 'A chronicle that reads like someone meant it.' },
      { img: 'shots/01_title.png', at: 0.85, cap: 'Fully playable today.' },
    ],
  },
];
