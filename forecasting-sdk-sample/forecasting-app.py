import time
from oci.ai_forecasting.forecast_client import ForecastClient
from oci.ai_forecasting.models import DataSourceDataAsset, FcDataSourceDataAsset, \
    ForecastCreationDetails, Forecast, CreateProjectDetails, DataSourceDetails, DataSourceDetailsObjectStorage, \
    CreateDataAssetDetails,UpdateForecastDetails
from oci.ai_forecasting.models.create_forecast_details import CreateForecastDetails
from oci.ai_forecasting.models.model_details import ModelDetails
from oci.ai_forecasting.models.schema import Schema
from oci.config import from_file

# change the config file location
config = from_file("/Users/rommonda/.oci/config")

compartment_id = "ocid1.compartment.oc1..aaaaaaaaa6b6bypmwsy5z3mhwdfdnc4mlt35xn5solpepqd6slplonok7lvq"
forecast_client = ForecastClient(
    config,
    service_endpoint="https://forecasting-int.aiservice.us-ashburn-1.oci.oraclecloud.com",
)

# CREATE PROJECT
print("-*-*-*-PROJECT-*-*-*-")

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

# GET PROJECT
get_proj = forecast_client.get_project(project_id=project_id)
print("----Get Project---")
print(get_proj.data)
time.sleep(5)

# CREATE DATA ASSET
print("-*-*-*-DATA ASSET-*-*-*-")
dDetails = DataSourceDetails(data_source_type="ORACLE_OBJECT_STORAGE")

dObjDetails = DataSourceDetailsObjectStorage(
    namespace="axebztqviz4z",
    bucket_name="testautomation",
    object_name="rossmann_10x500_primary.csv",
)

da_details = CreateDataAssetDetails(
    display_name="PythonSDKTestDataAsset",
    description="SDK Test DataAsset",
    compartment_id=compartment_id,
    project_id=project_id,
    data_source_details=dObjDetails,
)
create_res = forecast_client.create_data_asset(create_data_asset_details=da_details)
print("----Creating DataAsset----")
print(create_res.data)
time.sleep(5)
da_id = create_res.data.id

# GET DATAASSET
get_da = forecast_client.get_data_asset(data_asset_id=da_id)
print("----Reading DataAsset----")
print(get_da.data)
time.sleep(5)

# CREATE FORECAST
print("-*-*-*-Forecast-*-*-*-")

primaryFcDataSource = FcDataSourceDataAsset(
    data_asset_id=da_id,
    column_schema=[Schema(column_name="date", data_type=Schema.DATA_TYPE_DATE),
                   Schema(column_name="Sales", data_type=Schema.DATA_TYPE_INT),
                   Schema(column_name="Store", data_type=Schema.DATA_TYPE_STRING)],
    is_data_grouped=True,
    data_frequency="1DAY",
    ts_col_name="date",
    ts_col_format="yyyy-MM-dd HH:mm:ss"
)

dataSourceDataAsset = DataSourceDataAsset(
    primary_data_source=primaryFcDataSource
)

forecastCreationDetails = ForecastCreationDetails(
    data_source_details=dataSourceDataAsset,
    model_details=ModelDetails(models = ["SMA", "DMA"]),
    forecast_frequency="1WEEK",
    forecast_technique=ForecastCreationDetails.FORECAST_TECHNIQUE_ROCV,
    is_forecast_explanation_required=True,
    confidence_interval=95,
    target_variables = ["Sales"],
    forecast_horizon = 14,
    error_measure = ForecastCreationDetails.ERROR_MEASURE_RMSE,
    are_csv_result_files_required=True
)
createForecastDetails = CreateForecastDetails(
    display_name="PythonSDKTestForecast",
    description="PythonSDKTestForecast description",
    compartment_id=compartment_id,
    project_id=project_id,
    forecast_creation_details=forecastCreationDetails,
)

print("----Creating Forecast----")
create_res = forecast_client.create_forecast(create_forecast_details=createForecastDetails)
print(create_res.data)
time.sleep(5)
forecast_id = create_res.data.id

# GET FORECAST
get_forecast = forecast_client.get_forecast(forecast_id=forecast_id)
print("----Get Forecast----")
print(get_forecast.data)
time.sleep(5)
while get_forecast.data.lifecycle_state == Forecast.LIFECYCLE_STATE_CREATING:
    get_forecast = forecast_client.get_forecast(forecast_id=forecast_id)
    time.sleep(5)
    print("Status: "+ get_forecast.data.lifecycle_state)

# UPDATE FORECAST
print("----Updating Forecast----")

update_details = UpdateForecastDetails(
    display_name="Updated Forecast",
    description="Updated Forecast Description through SDK"
)

update_res = forecast_client.update_forecast(forecast_id=forecast_id,update_forecast_details=update_details)
print(update_res.data)

get_forecast = forecast_client.get_forecast(forecast_id=forecast_id)
time.sleep(1)
while get_forecast.data.lifecycle_state == Forecast.LIFECYCLE_STATE_UPDATING:
    get_forecast = forecast_client.get_forecast(forecast_id=forecast_id)
    time.sleep(1)
    print("Status: "+ get_forecast.data.lifecycle_state)

# GET RESULTS OF FORECAST
print("----Get STATUS of Forecast----")
get_forecast = forecast_client.get_forecast(forecast_id=forecast_id)
print(get_forecast.data)

print("----Get Forecast Result Content of Forecast----")
forecast_content = forecast_client.get_forecast_content(forecast_id=forecast_id,series_id=None)
print(forecast_content.data)

print("----Get Explanation Content of Forecast----")
explanation_content = forecast_client.get_explanation_content(forecast_id=forecast_id,series_id=None)
print(explanation_content.data)

print("----Get FittedSeries Content of Forecast----")
fittedSeries = forecast_client.get_fitted_series_content(forecast_id=forecast_id,series_id=None)
print(fittedSeries.data)

print("----Get InputSeries Content of Forecast----")
inputSeries = forecast_client.get_input_series(forecast_id=forecast_id,series_id=None)
print(inputSeries.data)

print("----Download Result CSV as ZIP----")
res = forecast_client.get_result_content(forecast_id=forecast_id)
file = open('response.zip', 'wb')
file.write(res.data.content)
file.close()

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

# DELETE DATA ASSET
delete_da = forecast_client.delete_data_asset(data_asset_id=da_id)
print("----DELETING DATA ASSET----")
if delete_da.status == 204:
    print("----DataAsset Deleted Successfully----")
else:
    print("----DataAsset Deletion Failed----")
    print(delete_da.data)
time.sleep(5)

# DELETE PROJECT
print("----DELETING PROJECT----")
delete_project = forecast_client.delete_project(project_id=project_id)
if delete_project.status == 204:
    print("----Project Deleted Successfully----")
else:
    print("----Project Deletion Failed----")
    print(delete_project.data)