from dataclasses import dataclass, field
from uuid import UUID

from warehouse_atlas.common.constants import RoleName


@dataclass(frozen=True, slots=True)
class Role:
    id: UUID
    name: RoleName
    description: str


@dataclass(frozen=True, slots=True)
class ActorContext:
    user_id: UUID
    username: str
    roles: frozenset[RoleName]

    def has_role(self, role: RoleName) -> bool:
        return role in self.roles or RoleName.ADMIN in self.roles


@dataclass
class User:
    id: UUID
    username: str
    full_name: str
    password_hash: str
    is_active: bool = True
    roles: list[Role] = field(default_factory=list)
