# Dungeon Run Database Model
# One row per dungeon run - the anchor that lets monster memories say
# WHEN something happened ("run 3"). A run opens when the party enters
# the dungeon and closes with a result when the run ends.
# Data storage only - run lifecycle decisions live in the game layer.

from datetime import datetime
from .base import BaseModel
from sqlalchemy import Column, Integer, String, Text, DateTime

# The ways a run can end (result stays NULL while the run is active)
RUN_RESULTS = ('victory_exit', 'defeat', 'abandoned')

class DungeonRun(BaseModel):
    """
    Dungeon run model - one record per journey into the dungeon

    - run_number counts up over the whole save (1, 2, 3, ...)
    - created_at doubles as the start time; ended_at is set on close
    - result: NULL while active, then victory_exit | defeat | abandoned
    - summary: one line of what the run amounted to
    """

    __tablename__ = 'dungeon_runs'

    run_number = Column(Integer, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    result = Column(String(20), nullable=True)
    summary = Column(Text, nullable=True)

    def to_dict(self):
        result = super().to_dict()
        result.update({
            'run_number': self.run_number,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'result': self.result,
            'summary': self.summary
        })
        return result

    @classmethod
    def begin(cls):
        """
        Open a new run. Any run still marked active is a leftover from a
        crash or restart - close it as 'abandoned' first so there is only
        ever one active run.

        Returns:
            DungeonRun: the new active run, or None on database error
        """
        try:
            for dangling in cls.query.filter(cls.result.is_(None)).all():
                dangling.result = 'abandoned'
                dangling.ended_at = datetime.utcnow()
                dangling.save()

            last = cls.query.order_by(cls.run_number.desc()).first()
            run = cls(run_number=(last.run_number + 1) if last else 1)
            return run if run.save() else None
        except Exception as e:
            print(f"❌ Error beginning dungeon run: {e}")
            return None

    @classmethod
    def get_active(cls):
        """The currently open run (result is NULL), or None"""
        try:
            return cls.query.filter(cls.result.is_(None)).order_by(cls.run_number.desc()).first()
        except Exception as e:
            print(f"❌ Error fetching active dungeon run: {e}")
            return None

    @classmethod
    def get_by_id(cls, run_id):
        try:
            return cls.query.get(run_id)
        except Exception as e:
            print(f"❌ Error fetching dungeon run {run_id}: {e}")
            return None

    @classmethod
    def close(cls, result: str, summary: str = None):
        """
        Close the active run with a result. Safe to call when no run is
        active (returns None quietly - e.g. sanctuary test battles).

        Args:
            result: one of RUN_RESULTS
            summary: optional one-line story of the run

        Returns:
            DungeonRun: the closed run, or None
        """
        if result not in RUN_RESULTS:
            print(f"❌ Unknown run result '{result}' - not closing run")
            return None
        run = cls.get_active()
        if not run:
            return None
        run.result = result
        run.ended_at = datetime.utcnow()
        if summary:
            run.summary = str(summary)[:2000]
        run.save()
        return run

    def __repr__(self):
        return f"<DungeonRun(id={self.id}, number={self.run_number}, result={self.result or 'active'})>"
