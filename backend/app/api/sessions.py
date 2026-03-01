"""Session import and listing endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.session import ImportSession
from app.models.hand import Hand
from app.models.player import HandPlayer
from app.models.action import Action
from app.parser.splitter import split_hands
from app.parser.ggpoker_parser import GGPokerParser
from app.parser.rush_cash import compute_stats
from app.schemas.hand import SessionOut

router = APIRouter(prefix="/sessions", tags=["sessions"])
_parser = GGPokerParser()


@router.get("/", response_model=list[SessionOut])
def list_sessions(db: Session = Depends(get_db)):
    return db.query(ImportSession).order_by(ImportSession.imported_at.desc()).all()


@router.get("/{session_id}", response_model=SessionOut)
def get_session(session_id: str, db: Session = Depends(get_db)):
    sess = db.get(ImportSession, session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    return sess


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: str, db: Session = Depends(get_db)):
    sess = db.get(ImportSession, session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(sess)
    db.commit()


@router.post("/import", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
async def import_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename or not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are supported")

    raw = await file.read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")

    hand_texts = split_hands(text)
    if not hand_texts:
        raise HTTPException(status_code=422, detail="No valid hands found in file")

    import_session = ImportSession(filename=file.filename)
    db.add(import_session)
    db.flush()  # get id before inserting children

    imported = 0
    hero_name: str | None = None

    for hand_text in hand_texts:
        parsed = _parser.parse(hand_text)
        if not parsed:
            continue

        # Skip duplicates
        exists = db.query(Hand).filter_by(ggpoker_hand_id=parsed.ggpoker_hand_id).first()
        if exists:
            continue

        compute_stats(parsed)

        if hero_name is None and parsed.hero_name:
            hero_name = parsed.hero_name

        hand = Hand(
            session_id=import_session.id,
            ggpoker_hand_id=parsed.ggpoker_hand_id,
            table_name=parsed.table_name,
            game_type=parsed.game_type,
            stakes_sb=parsed.stakes_sb,
            stakes_bb=parsed.stakes_bb,
            played_at=parsed.played_at,
            button_seat=parsed.button_seat,
            hero_seat=parsed.hero_seat,
            num_players=parsed.num_players,
            hero_position=parsed.hero_position,
            hero_cards=parsed.hero_cards,
            is_fast_fold=parsed.is_fast_fold,
            hero_vpip=parsed.hero_vpip,
            hero_pfr=parsed.hero_pfr,
            hero_had_3bet_opportunity=parsed.hero_had_3bet_opportunity,
            hero_3bet=parsed.hero_3bet,
            hero_saw_flop=parsed.hero_saw_flop,
            hero_went_to_showdown=parsed.hero_went_to_showdown,
            hero_won_at_showdown=parsed.hero_won_at_showdown,
            hero_bet_raise_count=parsed.hero_bet_raise_count,
            hero_call_count=parsed.hero_call_count,
            hero_profit_bb=parsed.hero_profit_bb,
            rake_bb=parsed.rake_chips / parsed.stakes_bb if parsed.stakes_bb else 0.0,
            flop_cards=parsed.flop_cards,
            turn_card=parsed.turn_card,
            river_card=parsed.river_card,
            run_it_twice=parsed.run_it_twice,
        )
        db.add(hand)
        db.flush()

        for p in parsed.players:
            db.add(HandPlayer(
                hand_id=hand.id,
                seat=p.seat,
                name=p.name,
                stack_bb=p.stack_chips / parsed.stakes_bb if parsed.stakes_bb else 0.0,
                is_hero=p.name == parsed.hero_name,
                hole_cards=p.hole_cards,
                profit_bb=0.0,  # refined calculation not yet available
            ))

        for a in parsed.actions:
            db.add(Action(
                hand_id=hand.id,
                player_name=a.player_name,
                street=a.street,
                sequence=a.sequence,
                action_type=a.action_type,
                amount_bb=a.amount_chips / parsed.stakes_bb if (a.amount_chips and parsed.stakes_bb) else None,
                is_all_in=a.is_all_in,
            ))

        imported += 1

    import_session.hero_name = hero_name
    import_session.hand_count = imported
    db.commit()
    db.refresh(import_session)
    return import_session
