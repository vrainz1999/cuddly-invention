"""Deskripsi migrasi

Revision ID: 90f50b0fc66d
Revises: 0779eb09aed9
Create Date: 2024-10-15 22:13:13.173034

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '90f50b0fc66d'
down_revision = '0779eb09aed9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('pembayaran', schema=None) as batch_op:
        batch_op.alter_column('pendaftaran_id',
               existing_type=mysql.BIGINT(display_width=20),
               type_=sa.Integer(),
               nullable=True)
        batch_op.alter_column('biaya_administrasi',
               existing_type=mysql.FLOAT(),
               nullable=True)
        batch_op.alter_column('jasa_dokter',
               existing_type=mysql.FLOAT(),
               nullable=True)
        batch_op.alter_column('biaya_obat',
               existing_type=mysql.FLOAT(),
               nullable=True)
        batch_op.alter_column('total_bayar',
               existing_type=mysql.FLOAT(),
               nullable=True)
        batch_op.alter_column('tanggal_bayar',
               existing_type=sa.DATE(),
               nullable=True)
        batch_op.drop_constraint('pembayaran_ibfk_1', type_='foreignkey')
        batch_op.create_foreign_key(None, 'pendaftaran', ['pendaftaran_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('pembayaran', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('pembayaran_ibfk_1', 'pendaftaran', ['pendaftaran_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
        batch_op.alter_column('tanggal_bayar',
               existing_type=sa.DATE(),
               nullable=False)
        batch_op.alter_column('total_bayar',
               existing_type=mysql.FLOAT(),
               nullable=False)
        batch_op.alter_column('biaya_obat',
               existing_type=mysql.FLOAT(),
               nullable=False)
        batch_op.alter_column('jasa_dokter',
               existing_type=mysql.FLOAT(),
               nullable=False)
        batch_op.alter_column('biaya_administrasi',
               existing_type=mysql.FLOAT(),
               nullable=False)
        batch_op.alter_column('pendaftaran_id',
               existing_type=sa.Integer(),
               type_=mysql.BIGINT(display_width=20),
               nullable=False)

    # ### end Alembic commands ###
