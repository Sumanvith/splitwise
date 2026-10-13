from fastapi import APIRouter

from app.core.dependencies import DbSession, GroupMemberDep
from app.schemas.settlement import BalanceRead
from app.services import settlement_service

router = APIRouter(prefix="/groups/{group_id}", tags=["settlements"])


@router.get("/balances", response_model=BalanceRead)
async def get_balances(group_id: int, db: DbSession, _: GroupMemberDep):
    return await settlement_service.get_balances(db, group_id)
