"""Player API router."""

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.repositories.player_repository import PlayerRepositoryImpl
from app.core.config import get_settings
from app.db.session import get_db_session
from app.models.player import PlayerModel
from app.schemas.player import PlayerRegisterRequest, PlayerRegisterResponse, PlayerResponse
from app.services.auth import AuthService
from app.use_cases.register_player import DuplicatePlayerError, RegisterPlayerUseCase

logger = structlog.get_logger()
router = APIRouter(prefix="/players", tags=["players"])


def get_player_repository(
    session: AsyncSession = Depends(get_db_session),
) -> PlayerRepositoryImpl:
    """
    Dependency for getting player repository.

    Args:
        session: Database session

    Returns:
        Player repository instance
    """
    return PlayerRepositoryImpl(session=session)


def get_register_player_use_case(
    repository: PlayerRepositoryImpl = Depends(get_player_repository),
) -> RegisterPlayerUseCase:
    """
    Dependency for getting register player use case.

    Args:
        repository: Player repository

    Returns:
        Register player use case instance
    """
    return RegisterPlayerUseCase(repository=repository)


def get_auth_service() -> AuthService:
    """
    Dependency for getting auth service.

    Returns:
        Auth service instance
    """
    return AuthService(settings=get_settings())


@router.post(
    "/register",
    response_model=PlayerRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new player",
    description="Register a new player account and receive a JWT access token.",
    responses={
        201: {"description": "Player registered successfully"},
        409: {"description": "Username or email already exists"},
        422: {"description": "Validation error"},
    },
)
async def register_player(
    request: PlayerRegisterRequest,
    use_case: RegisterPlayerUseCase = Depends(get_register_player_use_case),
    auth_service: AuthService = Depends(get_auth_service),
    session: AsyncSession = Depends(get_db_session),
) -> PlayerRegisterResponse:
    """
    Register a new player.

    Args:
        request: Registration request data
        use_case: Register player use case
        auth_service: Authentication service

    Returns:
        Player registration response with JWT token

    Raises:
        HTTPException: If registration fails
    """
    logger.info("player_registration_attempt", username=request.username, email=request.email)

    try:
        # Register player
        player = await use_case.execute(
            username=request.username,
            email=request.email,
            password=request.password,
            country=request.country,
            initial_resources=request.initial_resources,
        )

        # Generate JWT token
        access_token = auth_service.create_access_token(player_id=str(player.id))

        logger.info(
            "player_registered_successfully",
            player_id=str(player.id),
            username=player.username.value,
        )

        # Get created_at from database (refresh to get DB-generated timestamp)
        stmt = select(PlayerModel).where(PlayerModel.id == player.id)
        result = await session.execute(stmt)
        db_player = result.scalar_one()
        created_at = db_player.created_at

        # Return response
        return PlayerRegisterResponse(
            player=PlayerResponse(
                id=player.id,
                username=player.username.value,
                email=player.email.value,
                country=player.country,
                created_at=created_at,
            ),
            access_token=access_token,
        )

    except DuplicatePlayerError as e:
        logger.warning("player_registration_failed_duplicate", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e
    except ValueError as e:
        logger.warning("player_registration_failed_validation", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error("player_registration_failed_unexpected", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration.",
        ) from e
