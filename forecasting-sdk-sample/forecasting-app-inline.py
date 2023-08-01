import time
from oci.ai_forecasting.forecast_client import ForecastClient
from oci.ai_forecasting.models import DataSourceInline, FcDataSourceInline, \
    ForecastCreationDetails, Forecast, CreateProjectDetails
from oci.ai_forecasting.models.create_forecast_details import CreateForecastDetails
from oci.ai_forecasting.models.model_details import ModelDetails
from oci.ai_forecasting.models.schema import Schema
from oci.config import from_file

# change the config file location
config = from_file("~/.oci/config")

compartment_id = "ocid1.tenancy.oc1..aaaaaaaaonxo6xgq5hmmbqmxqthumokf"
forecast_client = ForecastClient(
    config,
    service_endpoint="https://forecasting-{region}.oci.oraclecloud.com",
)
print("-*-*-*-PROJECT-*-*-*-")

# CREATE CALL
proj_details = CreateProjectDetails(
    display_name="PythonSDKTestProject",
    description="PythonSDKTestProject description",
    compartment_id=compartment_id,
)

create_res = forecast_client.create_project(create_project_details=proj_details)
print("----Creating Project----")
print(create_res.data)
time.sleep(5)
project_id = create_res.data.id

# GET CALL
get_proj = forecast_client.get_project(project_id=project_id)
print("----Reading Project---")
print(get_proj.data)
time.sleep(5)

# Forecast
print("-*-*-*-Forecast-*-*-*-")
# CREATE CALL

primaryFcDataSource = FcDataSourceInline(
    column_data=[
        [
            "2019-01-05 00:00:00",
            "2019-01-12 00:00:00",
            "2019-01-19 00:00:00",
            "2019-01-26 00:00:00",
            "2019-02-02 00:00:00",
            "2019-02-09 00:00:00",
            "2019-02-16 00:00:00",
            "2019-02-23 00:00:00",
            "2019-03-02 00:00:00",
            "2019-03-09 00:00:00",
            "2019-03-16 00:00:00",
            "2019-03-23 00:00:00",
            "2019-03-30 00:00:00",
            "2019-04-06 00:00:00",
            "2019-04-13 00:00:00",
            "2019-04-20 00:00:00",
            "2019-04-27 00:00:00",
            "2019-05-04 00:00:00",
            "2019-05-11 00:00:00",
            "2019-05-18 00:00:00"
        ],
        [
            "1958",
            "2566",
            "1294",
            "8189",
            "12806",
            "5192",
            "1859",
            "2151",
            "2388",
            "1916",
            "2060",
            "2142",
            "1571",
            "1167",
            "2180",
            "1581",
            "2011",
            "2523",
            "1443",
            "2008"

        ],
        [
            "Product Group 182",
            "Product Group 182",
            "Product Group 182",
            "Product Group 182",
            "Product Group 182",
            "Product Group 182",
            "Product Group 182",
            "Product Group 182",
            "Product Group 182",
            "Product Group 182",
            "Product Group 182",
            "Product Group 182",
            "Product Group 182",
            "Product Group 182",
            "Product Group 182",
            "Product Group 182",
            "Product Group 182",
            "Product Group 182",
            "Product Group 182",
            "Product Group 182"

        ]
    ],
    column_schema=[Schema(column_name="last_day_of_week", data_type=Schema.DATA_TYPE_DATE),
                   Schema(column_name="sales", data_type=Schema.DATA_TYPE_INT),
                   Schema(column_name="category", data_type=Schema.DATA_TYPE_STRING)],
    is_data_grouped=True,
    data_frequency="1WEEK",
    ts_col_name="last_day_of_week",
    ts_col_format="yyyy-MM-dd HH:mm:ss"
)

dataSourceInline = DataSourceInline(
    primary_data_source=primaryFcDataSource
)
forecastCreationDetails = ForecastCreationDetails(
    data_source_details=dataSourceInline,
    model_details=ModelDetails(models=["SMA", "DMA"]),
    forecast_frequency="1WEEK",
    forecast_technique=ForecastCreationDetails.FORECAST_TECHNIQUE_ROCV,
    is_forecast_explanation_required=True,
    confidence_interval=95,
    target_variables=["sales"],
    forecast_horizon=4,
    error_measure=ForecastCreationDetails.ERROR_MEASURE_RMSE
)

createForecastDetails = CreateForecastDetails(
    display_name="PythonSDKTestForecast",
    description="PythonSDKTestForecast description",
    compartment_id=compartment_id,
    project_id=project_id,
    forecast_creation_details=forecastCreationDetails,
)

create_res = forecast_client.create_forecast(create_forecast_details=createForecastDetails)
print("----Creating Forecast----")
print(create_res.data)
time.sleep(5)
forecast_id = create_res.data.id

# READ CALL
get_forecast = forecast_client.get_forecast(forecast_id=forecast_id)
print("----Reading Forecast----")
print(get_forecast.data)
time.sleep(5)
while get_forecast.data.lifecycle_state == Forecast.LIFECYCLE_STATE_CREATING:
    get_forecast = forecast_client.get_forecast(forecast_id=forecast_id)
    time.sleep(5)
    print("Status: " + get_forecast.data.lifecycle_state)

# DELETE FORECAST
delete_forecast = forecast_client.delete_forecast(forecast_id=forecast_id)
print("----Deleting Forecast----")
if delete_forecast.status == 204:
    print("----Forecast Deleted Successfully----")
else:
    print("----Forecast Deletion Failed----")
    print(delete_forecast.data)
time.sleep(2)

# CREATE FORECAST "ToBeCancelled"
createForecastDetails = CreateForecastDetails(
    display_name="PythonSDKTestForecast_ToBeCancelled",
    description="PythonSDKTestForecast_ToBeCancelled",
    compartment_id=compartment_id,
    project_id=project_id,
    forecast_creation_details=forecastCreationDetails,
)

create_res = forecast_client.create_forecast(create_forecast_details=createForecastDetails)
print("----Creating ToBeCancelled Forecast----")
print(create_res.data)
time.sleep(5)
cancel_forecast_id = create_res.data.id

#CANCEL FORECAST "ToBeCancelled"
cancel_forecast = forecast_client.cancel_forecast(forecast_id=cancel_forecast_id)
print("----Cancelling Forecast----")
if cancel_forecast.status == 202:
    get_forecast=forecast_client.get_forecast(forecast_id=cancel_forecast_id)
    while get_forecast.data.lifecycle_state == Forecast.LIFECYCLE_STATE_CANCELING:
        print('Canceling ...')
        time.sleep(2)
        get_forecast=forecast_client.get_forecast(forecast_id=cancel_forecast_id)
    if get_forecast.data.lifecycle_state == Forecast.LIFECYCLE_STATE_CANCELED:
        print("----Forecast Cancelled Successfully----")
    else:
        print("----Forecast Cancellation Failed----")
else:
    print("----Forecast Cancellation Failed----")
    print(cancel_forecast.data)

# DELETE FORECAST
delete_forecast = forecast_client.delete_forecast(forecast_id=cancel_forecast_id)
print("----Deleting ToBeCancelled Forecast----")
if delete_forecast.status == 204:
    print("----Forecast Deleted Successfully----")
else:
    print("----Forecast Deletion Failed----")
    print(delete_forecast.data)
time.sleep(2)

#DELETE PROJECT
print("----DELETING PROJECT----")
delete_project = forecast_client.delete_project(project_id=project_id)
if delete_project.status == 204:
    print("----Project Deleted Successfully----")
else:
    print("----Project Deletion Failed----")
    print(delete_project.data)