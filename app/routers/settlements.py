from fastapi import APIRouter

from app.core.dependencies import DbSession, GroupMemberDep
from app.schemas.settlement import BalanceRead, SettlementCreate, SettlementRead
from app.services import settlement_service

router = APIRouter(prefix="/groups/{group_id}", tags=["settlements"])


@router.get("/balances", response_model=BalanceRead)
async def get_balances(group_id: int, db: DbSession, _: GroupMemberDep):
    return await settlement_service.get_balances(db, group_id)


@router.post("/settlements", response_model=SettlementRead, status_code=201)
async def create_settlement(
    group_id: int, data: SettlementCreate, db: DbSession, _: GroupMemberDep
):
    return await settlement_service.create_settlement(db, group_id, data)


@router.get("/settlements", response_model=list[SettlementRead])
async def list_settlements(group_id: int, db: DbSession, _: GroupMemberDep):
    return await settlement_service.list_settlements(db, group_id)
