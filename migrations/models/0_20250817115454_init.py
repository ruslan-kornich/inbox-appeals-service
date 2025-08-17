from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "auth_user" (
    "id" UUID NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "password_hash" VARCHAR(255) NOT NULL,
    "role" VARCHAR(5) NOT NULL DEFAULT 'USER'
);
CREATE INDEX IF NOT EXISTS "idx_auth_user_created_6a0cc9" ON "auth_user" ("created_at");
CREATE INDEX IF NOT EXISTS "idx_auth_user_email_1e0e57" ON "auth_user" ("email");
CREATE INDEX IF NOT EXISTS "idx_auth_user_role_79585d" ON "auth_user" ("role");
CREATE INDEX IF NOT EXISTS "idx_auth_user_email_779af8" ON "auth_user" ("email", "role");
COMMENT ON COLUMN "auth_user"."role" IS 'USER: USER\nSTAFF: STAFF\nADMIN: ADMIN';
COMMENT ON TABLE "auth_user" IS 'System user.';
CREATE TABLE IF NOT EXISTS "auth_citizen_profile" (
    "id" UUID NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "inn" VARCHAR(32) NOT NULL,
    "phone" VARCHAR(32) NOT NULL,
    "first_name" VARCHAR(80) NOT NULL,
    "last_name" VARCHAR(80) NOT NULL,
    "middle_name" VARCHAR(80),
    "birth_date" DATE NOT NULL,
    "user_id" UUID NOT NULL UNIQUE REFERENCES "auth_user" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_auth_citize_created_c726b6" ON "auth_citizen_profile" ("created_at");
CREATE INDEX IF NOT EXISTS "idx_auth_citize_inn_b06048" ON "auth_citizen_profile" ("inn");
CREATE INDEX IF NOT EXISTS "idx_auth_citize_phone_d22ede" ON "auth_citizen_profile" ("phone");
CREATE INDEX IF NOT EXISTS "idx_auth_citize_birth_d_e5afbd" ON "auth_citizen_profile" ("birth_date");
CREATE INDEX IF NOT EXISTS "idx_auth_citize_inn_86a661" ON "auth_citizen_profile" ("inn", "phone", "birth_date");
COMMENT ON TABLE "auth_citizen_profile" IS 'Profile data required by the spec for end-users (role=USER).';
CREATE TABLE IF NOT EXISTS "service_ticket" (
    "id" UUID NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "text" TEXT NOT NULL,
    "status" VARCHAR(11) NOT NULL DEFAULT 'NEW',
    "staff_comment" TEXT,
    "last_modified_at" TIMESTAMPTZ,
    "last_modified_by_id" UUID REFERENCES "auth_user" ("id") ON DELETE SET NULL,
    "owner_id" UUID NOT NULL REFERENCES "auth_user" ("id") ON DELETE CASCADE,
    "staff_assignee_id" UUID REFERENCES "auth_user" ("id") ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS "idx_service_tic_created_fdf180" ON "service_ticket" ("created_at");
CREATE INDEX IF NOT EXISTS "idx_service_tic_status_ffb438" ON "service_ticket" ("status");
CREATE INDEX IF NOT EXISTS "idx_service_tic_last_mo_bcb90f" ON "service_ticket" ("last_modified_at");
CREATE INDEX IF NOT EXISTS "idx_service_tic_last_mo_3737f0" ON "service_ticket" ("last_modified_by_id");
CREATE INDEX IF NOT EXISTS "idx_service_tic_owner_i_da1afd" ON "service_ticket" ("owner_id");
CREATE INDEX IF NOT EXISTS "idx_service_tic_staff_a_d6bbf4" ON "service_ticket" ("staff_assignee_id");
CREATE INDEX IF NOT EXISTS "idx_service_tic_status_db110e" ON "service_ticket" ("status", "created_at");
CREATE INDEX IF NOT EXISTS "idx_service_tic_staff_a_eb4ef6" ON "service_ticket" ("staff_assignee_id", "status");
CREATE INDEX IF NOT EXISTS "idx_service_tic_owner_i_fa4fa6" ON "service_ticket" ("owner_id", "created_at");
COMMENT ON COLUMN "service_ticket"."status" IS 'NEW: NEW\nIN_PROGRESS: IN_PROGRESS\nRESOLVED: RESOLVED\nREJECTED: REJECTED';
COMMENT ON TABLE "service_ticket" IS 'Citizen ticket (request).';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
