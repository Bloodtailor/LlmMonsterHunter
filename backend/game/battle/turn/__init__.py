# The battle turn, phase by phase - the logic behind battle_turn in
# registered_workflows.py:
#   context       TurnContext: the state everyone shares + tiny lookups
#   actions       resolving one attack/ability/defend/item turn
#   negotiation   mid-battle talk and what the adjudicator's decision does
#   player_phase  resolving the player's input (a turn or a talk reply)
#   director      who acts next: LLM choice inside Python guardrails
#   ending        outcome text, persistence, memories, keepsakes, defeat
#   run           the orchestrator battle_turn delegates to
#   housekeeping  the queued battle-log condensing workflow body
#
# Step names, action_resolved payloads, and response shapes are a
# frontend contract (see docs/architecture.md) - they must not drift.
