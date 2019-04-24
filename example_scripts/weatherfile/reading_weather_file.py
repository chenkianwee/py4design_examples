from ladybug.epw import EPW
epw_data = EPW('F:\\kianwee_work\\digital_repository\\energyplus_share\\weatherfile\\SGP_Singapore.486980_IWEC.epw')
dbt = epw_data.dry_bulb_temperature
#dbt = list(dbt)
#print len(dbt) 
mth_dbt = dbt.average_monthly()

for d in mth_dbt:
    print round(d,2)