# Dungeon workflow handlers - the logic behind registered_workflows.py.
#
# One module per event or action, so no file outgrows a read-through:
#   run_lifecycle    enter the dungeon, fresh paths onward, log condensing
#   paths            choose_path validation + event dispatch
#   exit_run         the exit path: ceremony, run close, leaving
#   reunion          a remembered monster returns (choose_path event)
#   explore          arrive and look around (choose_path event)
#   treasure         a hidden item discovery (choose_path event)
#   dialogue_event   a monster stops the party with a question (choose_path event)
#   battle_event     hostiles attack on arrival (choose_path event)
#   talk             the party speaks; the monster decides the outcome
#   stealth          sneaking past and surprise attacks
#   camp             resting, restores, and campfire growth
#   items_abilities  out-of-battle ability/item use + shared target logic
#   encounter_battle starting battles against monsters that already exist
#
# Every handler advances the shared WorkflowStep - step names and
# progress-data keys are a frontend contract (see docs/architecture.md).
