
monodera on pfsa-usr01-gb: .../ets_target_database/alembic/pfsa-db01-gb [ tickets/OBSPROC-31/monodera][][ v3.9.13(venv39)]
 alembic -c /work/monodera/Subaru-PFS/alembic_configs/alembic_pfsa-db01-gb.ini revision --autogenerate -m "Add columns for photometric errors in the fluxstd table"
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.ddl.postgresql] Detected sequence named 'fluxstd_fluxstd_id_seq' as owned by integer column 'fluxstd(fluxstd_id)', assuming SERIAL and omitting
INFO  [alembic.ddl.postgresql] Detected sequence named 'sky_sky_id_seq' as owned by integer column 'sky(sky_id)', assuming SERIAL and omitting
alembic/env.py:71: SAWarning: Skipped unsupported reflection of expression-based index sky_q3c_ang2ipix_idx
  context.run_migrations()
INFO  [alembic.autogenerate.compare] Detected added column 'fluxstd.psf_mag_error_g'
INFO  [alembic.autogenerate.compare] Detected added column 'fluxstd.psf_mag_error_r'
INFO  [alembic.autogenerate.compare] Detected added column 'fluxstd.psf_mag_error_i'
INFO  [alembic.autogenerate.compare] Detected added column 'fluxstd.psf_mag_error_z'
INFO  [alembic.autogenerate.compare] Detected added column 'fluxstd.psf_mag_error_y'
INFO  [alembic.autogenerate.compare] Detected added column 'fluxstd.psf_mag_error_j'
INFO  [alembic.autogenerate.compare] Detected added column 'fluxstd.psf_flux_error_g'
INFO  [alembic.autogenerate.compare] Detected added column 'fluxstd.psf_flux_error_r'
INFO  [alembic.autogenerate.compare] Detected added column 'fluxstd.psf_flux_error_i'
INFO  [alembic.autogenerate.compare] Detected added column 'fluxstd.psf_flux_error_z'
INFO  [alembic.autogenerate.compare] Detected added column 'fluxstd.psf_flux_error_y'
INFO  [alembic.autogenerate.compare] Detected added column 'fluxstd.psf_flux_error_j'
  Generating /work/monodera/Subaru-PFS/ets_target_database/alembic/pfsa-db01-gb/alembic/versions/20221020-174527_c4e16db3e7e1_add_columns_for_photometric_errors_in_.py ...  done
