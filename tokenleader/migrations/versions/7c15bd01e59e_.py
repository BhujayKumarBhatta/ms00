"""empty message

Revision ID: 7c15bd01e59e
Revises: 
Create Date: 2019-10-24 16:57:23.659460

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7c15bd01e59e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('department',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('creation_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('is_active', sa.Enum('N', 'Y'), server_default='Y', nullable=False),
    sa.Column('created_by', sa.String(length=24), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_department_name'), 'department', ['name'], unique=True)
    op.create_table('organization',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('orgtype', sa.String(length=64), nullable=True),
    sa.Column('creation_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('is_active', sa.Enum('N', 'Y'), server_default='Y', nullable=False),
    sa.Column('auth_backend', sa.String(length=64), nullable=True),
    sa.Column('created_by', sa.String(length=24), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organization_name'), 'organization', ['name'], unique=True)
    op.create_table('orgunit',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('creation_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('is_active', sa.Enum('N', 'Y'), server_default='Y', nullable=False),
    sa.Column('created_by', sa.String(length=24), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_orgunit_name'), 'orgunit', ['name'], unique=True)
    op.create_table('otp',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('otp', sa.String(length=64), nullable=False),
    sa.Column('creation_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('delivery_method', sa.String(length=4), nullable=True),
    sa.Column('is_active', sa.Enum('N', 'Y'), server_default='Y', nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_otp_otp'), 'otp', ['otp'], unique=True)
    op.create_table('role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('rolename', sa.String(length=64), nullable=False),
    sa.Column('creation_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('is_active', sa.Enum('N', 'Y'), server_default='Y', nullable=False),
    sa.Column('created_by', sa.String(length=24), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_role_rolename'), 'role', ['rolename'], unique=True)
    op.create_table('service_catalog',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('endpoint_url_internal', sa.String(length=256), nullable=True),
    sa.Column('endpoint_url_external', sa.String(length=256), nullable=True),
    sa.Column('endpoint_url_admin', sa.String(length=256), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_service_catalog_endpoint_url_admin'), 'service_catalog', ['endpoint_url_admin'], unique=True)
    op.create_index(op.f('ix_service_catalog_endpoint_url_external'), 'service_catalog', ['endpoint_url_external'], unique=True)
    op.create_index(op.f('ix_service_catalog_endpoint_url_internal'), 'service_catalog', ['endpoint_url_internal'], unique=True)
    op.create_index(op.f('ix_service_catalog_name'), 'service_catalog', ['name'], unique=True)
    op.create_table('workfunctioncontext',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('creation_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('is_active', sa.Enum('N', 'Y'), server_default='Y', nullable=False),
    sa.Column('org_id', sa.Integer(), nullable=False),
    sa.Column('orgunit_id', sa.Integer(), nullable=False),
    sa.Column('department_id', sa.Integer(), nullable=False),
    sa.Column('created_by', sa.String(length=24), nullable=True),
    sa.ForeignKeyConstraint(['department_id'], ['department.id'], ),
    sa.ForeignKeyConstraint(['org_id'], ['organization.id'], ),
    sa.ForeignKeyConstraint(['orgunit_id'], ['orgunit.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workfunctioncontext_name'), 'workfunctioncontext', ['name'], unique=True)
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('creation_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('otp_mode', sa.String(length=20), nullable=True),
    sa.Column('allowemaillogin', sa.Enum('N', 'Y'), server_default='N', nullable=False),
    sa.Column('is_active', sa.Enum('N', 'Y'), server_default='Y', nullable=False),
    sa.Column('wfc_id', sa.Integer(), nullable=False),
    sa.Column('otp_id', sa.Integer(), nullable=True),
    sa.Column('created_by', sa.String(length=24), nullable=True),
    sa.ForeignKeyConstraint(['otp_id'], ['otp.id'], ),
    sa.ForeignKeyConstraint(['wfc_id'], ['workfunctioncontext.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('roles_n_user_map',
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('role_id', 'user_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('roles_n_user_map')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_workfunctioncontext_name'), table_name='workfunctioncontext')
    op.drop_table('workfunctioncontext')
    op.drop_index(op.f('ix_service_catalog_name'), table_name='service_catalog')
    op.drop_index(op.f('ix_service_catalog_endpoint_url_internal'), table_name='service_catalog')
    op.drop_index(op.f('ix_service_catalog_endpoint_url_external'), table_name='service_catalog')
    op.drop_index(op.f('ix_service_catalog_endpoint_url_admin'), table_name='service_catalog')
    op.drop_table('service_catalog')
    op.drop_index(op.f('ix_role_rolename'), table_name='role')
    op.drop_table('role')
    op.drop_index(op.f('ix_otp_otp'), table_name='otp')
    op.drop_table('otp')
    op.drop_index(op.f('ix_orgunit_name'), table_name='orgunit')
    op.drop_table('orgunit')
    op.drop_index(op.f('ix_organization_name'), table_name='organization')
    op.drop_table('organization')
    op.drop_index(op.f('ix_department_name'), table_name='department')
    op.drop_table('department')
    # ### end Alembic commands ###
