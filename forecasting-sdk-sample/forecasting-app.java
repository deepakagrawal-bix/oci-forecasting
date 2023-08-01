package org.ocasfc;

import com.oracle.bmc.ConfigFileReader;
import com.oracle.bmc.aiforecasting.Forecast;
import com.oracle.bmc.aiforecasting.ForecastClient;
//import com.oracle.bmc.aiforecasting.model.ConfidenceInterval;
import com.oracle.bmc.aiforecasting.model.*;
//import com.oracle.bmc.aiforecasting.model.ForecastFrequency;
import com.oracle.bmc.aiforecasting.requests.CreateDataAssetRequest;
import com.oracle.bmc.aiforecasting.requests.CreateForecastRequest;
import com.oracle.bmc.aiforecasting.requests.CreateProjectRequest;
import com.oracle.bmc.aiforecasting.requests.DeleteDataAssetRequest;
import com.oracle.bmc.aiforecasting.requests.UpdateForecastRequest;
import com.oracle.bmc.aiforecasting.requests.DeleteForecastRequest;
import com.oracle.bmc.aiforecasting.requests.CancelForecastRequest;
import com.oracle.bmc.aiforecasting.requests.DeleteProjectRequest;
import com.oracle.bmc.aiforecasting.requests.GetForecastRequest;
import com.oracle.bmc.aiforecasting.requests.GetForecastContentRequest;
import com.oracle.bmc.aiforecasting.requests.GetExplanationContentRequest;
import com.oracle.bmc.aiforecasting.requests.GetFittedSeriesContentRequest;
import com.oracle.bmc.aiforecasting.requests.GetInputSeriesRequest;
import com.oracle.bmc.aiforecasting.requests.GetResultContentRequest;
import com.oracle.bmc.aiforecasting.responses.CreateDataAssetResponse;
import com.oracle.bmc.aiforecasting.responses.CreateForecastResponse;
import com.oracle.bmc.aiforecasting.responses.CreateProjectResponse;
import com.oracle.bmc.aiforecasting.responses.GetForecastResponse;
import com.oracle.bmc.aiforecasting.responses.GetForecastContentResponse;
import com.oracle.bmc.aiforecasting.responses.GetExplanationContentResponse;
import com.oracle.bmc.aiforecasting.responses.GetFittedSeriesContentResponse;
import com.oracle.bmc.aiforecasting.responses.GetInputSeriesResponse;
import com.oracle.bmc.aiforecasting.responses.GetResultContentResponse;
import com.oracle.bmc.aiforecasting.responses.UpdateForecastResponse;
import com.oracle.bmc.aiforecasting.responses.DeleteForecastResponse;
import com.oracle.bmc.aiforecasting.responses.DeleteDataAssetResponse;
import com.oracle.bmc.aiforecasting.responses.DeleteProjectResponse;
import com.oracle.bmc.aiforecasting.responses.CancelForecastResponse;
import com.oracle.bmc.auth.AuthenticationDetailsProvider;
import com.oracle.bmc.auth.ConfigFileAuthenticationDetailsProvider;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import java.util.Arrays;

public class Application {

    private static final String compartmentId = "ocid1.tenancy.oc1..aaaaaaaaonxo6xgq5hmmbqmxqthumokfzgkdz6nje5g3mfoqq37azuuui3ea";

    public static void main(String[] args) throws IOException {

        final ConfigFileReader.ConfigFile configFile = ConfigFileReader.parse("/Users/rommonda/.oci/config");
        final AuthenticationDetailsProvider provider = new ConfigFileAuthenticationDetailsProvider(configFile);

        /* Create forecast service client */
        ForecastClient forecastClient = new ForecastClient(provider);
        forecastClient.setEndpoint("https://forecasting-int.aiservice.us-ashburn-1.oci.oraclecloud.com");

        //Create Project
        String projectId = createProject(forecastClient);
        //Create DataAsset
        String dataAssetId = createDataAsset(forecastClient, projectId);
        //Create Forecast
        String forecastId = createForecast(forecastClient, projectId, dataAssetId);
        try {
            Thread.sleep(10000);
            System.out.println("-----Get Forecast------");
            String forecastStatus = getForecast(forecastClient, forecastId);
            while (forecastStatus.equalsIgnoreCase("CREATING")) {
                Thread.sleep(2000);
                forecastStatus = getForecast(forecastClient, forecastId);
            }
            if (forecastStatus.equalsIgnoreCase("ACTIVE")) {
                System.out.println("-----Forecast Created Successfully------");
            } else {
                System.out.println("-----Forecast Creation Failed------");
            }
            Thread.sleep(10000);

            //Updating Forecast
            System.out.println("-----Updating Forecast------");
            UpdateForecastDetails updateForecastDetails = UpdateForecastDetails.builder().displayName("Updated Forecast").description("Updated Forecast Description through SDK").build();
            UpdateForecastResponse updateForecastResponse = forecastClient.updateForecast(UpdateForecastRequest.builder().forecastId(forecastId).updateForecastDetails(updateForecastDetails).build());
            System.out.println(updateForecastResponse.getForecast().toString());
            String updateForecastStatus = getForecast(forecastClient,forecastId);
            while ( updateForecastStatus.equalsIgnoreCase("UPDATING") ) {
                Thread.sleep(2000);
                updateForecastStatus = getForecast(forecastClient, forecastId);
            }

            //Get Results of Forecast
            System.out.println("-----Get Forecast Result Content of Forecast------");
            GetForecastContentResponse getForecastContentResponse = forecastClient.getForecastContent(GetForecastContentRequest.builder().forecastId(forecastId).seriesId("1063").build());
            System.out.println(getForecastContentResponse.getForecastContent().toString());

            System.out.println("-----Get Explanation Content of Forecast------");
            GetExplanationContentResponse getExplanationContentResponse = forecastClient.getExplanationContent(GetExplanationContentRequest.builder().forecastId(forecastId).seriesId("1063").build());
            System.out.println(getExplanationContentResponse.getExplanationContent().toString());

            System.out.println("-----Get FittedSeries Content of Forecast------");
            GetFittedSeriesContentResponse getFittedSeriesContentResponse = forecastClient.getFittedSeriesContent(GetFittedSeriesContentRequest.builder().forecastId(forecastId).seriesId("1063").build());
            System.out.println(getFittedSeriesContentResponse.getFittedSeriesContent().toString());

            System.out.println("-----Get InputSeries Content of Forecast------");
            GetInputSeriesResponse getInputSeriesResponse = forecastClient.getInputSeries(GetInputSeriesRequest.builder().forecastId(forecastId).seriesId("1063").build());
            System.out.println(getInputSeriesResponse.getInputSeries().toString());

            System.out.println("----Download Result CSV as ZIP----");
            GetResultContentResponse getResultContentResponse = forecastClient.getResultContent(GetResultContentRequest.builder().forecastId(forecastId).build());
            System.out.println(getResultContentResponse.get__httpStatusCode__());
            InputStream initialStream = getResultContentResponse.getInputStream();
            File targetFile = new File("response.zip");
            System.out.println("Downloading as ZIP...");
            Files.copy(initialStream, targetFile.toPath(), StandardCopyOption.REPLACE_EXISTING);


            //Deleting Forecast
            System.out.println("-----Deleting Forecast------");
            DeleteForecastResponse deleteForecastResponse=forecastClient.deleteForecast(DeleteForecastRequest.builder().forecastId(forecastId).build());
            if (deleteForecastResponse.get__httpStatusCode__() == 204)
                System.out.println("Forecast Deleted Successfully");
            else
                System.out.println("Forecast Deletion Failed");
            Thread.sleep(10000);

            //Create ToBeCancelled Forecast
            String cancelForecastId = createForecast(forecastClient, projectId, dataAssetId);

            //Cancel ToBeCancelled Forecast
            System.out.println("-----Canceling Forecast------");
            CancelForecastResponse cancelForecastResponse = forecastClient.cancelForecast(CancelForecastRequest.builder().forecastId(cancelForecastId).build());
            if (cancelForecastResponse.get__httpStatusCode__() == 202) {
                String cancelForecastStatus = getForecast(forecastClient, cancelForecastId);
                while (cancelForecastStatus.equalsIgnoreCase("CANCELING")) {
                    System.out.println("Canceling ...");
                    Thread.sleep(2000);
                    cancelForecastStatus = getForecast(forecastClient, cancelForecastId);
                }
                if (cancelForecastStatus.equalsIgnoreCase("CANCELED"))
                    System.out.println("Forecast Canceled Successfully");
                else
                    System.out.println("Forecast Cancellation Failed");
            }
            else {
                System.out.println("Forecast Cancellation Failed");
            }

            //Deleting ToBeCancelled Forecast
            System.out.println("-----Deleting Forecast------");
            DeleteForecastResponse deleteToBeCancelledForecastResponse = forecastClient.deleteForecast(DeleteForecastRequest.builder().forecastId(cancelForecastId).build());
            if (deleteToBeCancelledForecastResponse.get__httpStatusCode__() == 204)
                System.out.println("Forecast Deleted Successfully");
            else
                System.out.println("Forecast Deletion Failed");
            Thread.sleep(10000);

            //Deleting DataAsset
            System.out.println("-----Deleting DataAsset------");
            DeleteDataAssetResponse deleteDataAssetResponse = forecastClient.deleteDataAsset(DeleteDataAssetRequest.builder().dataAssetId(dataAssetId).build());
            if (deleteDataAssetResponse.get__httpStatusCode__() == 204)
                System.out.println("DataAsset Deleted Successfully");
            else
                System.out.println("DataAsset Deletion Failed");
            Thread.sleep(10000);

            //Deleting Project
            System.out.println("-----Deleting Project------");
            DeleteProjectResponse deleteProjectResponse = forecastClient.deleteProject(DeleteProjectRequest.builder().projectId(projectId).build());
            if (deleteProjectResponse.get__httpStatusCode__() == 204)
                System.out.println("Project Deleted Successfully");
            else
                System.out.println("Project Deletion Failed");
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    public static String createProject(ForecastClient forecastClient) {
        CreateProjectDetails createProjectDetails = CreateProjectDetails.builder()
                .displayName("Testing Project From SDK " + System.currentTimeMillis())
                .description("Testing Forecasting Project from Java SDK")
                .compartmentId(compartmentId)
                .build();
        CreateProjectRequest createProjectRequest = CreateProjectRequest.builder()
                .createProjectDetails(createProjectDetails).build();
        CreateProjectResponse createProjectResponse = forecastClient.createProject(createProjectRequest);
        System.out.println("-----Creating Project------");
        System.out.println(createProjectResponse);
        System.out.println("-----Project Created------");
        return createProjectResponse.getProject().getId();
    }

    public static String createDataAsset(ForecastClient forecastClient, String projectId) {
        DataSourceDetailsObjectStorage dataSourceDetailsObjectStorage = DataSourceDetailsObjectStorage.builder()
                .objectName("rossmann_10x500_primary.csv")
                .bucketName("testautomation")
                .namespace("axebztqviz4z")
                .build();

        CreateDataAssetDetails createDataAssetDetails = CreateDataAssetDetails.builder()
                .dataSourceDetails(dataSourceDetailsObjectStorage)
                .compartmentId(compartmentId)
                .displayName("Cloud Capacity Data Asset By Java SDK")
                .projectId(projectId)
                .description("Data Asset for Java SDK testing")
                .build();

        CreateDataAssetRequest createDataAssetRequest = CreateDataAssetRequest.builder()
                .createDataAssetDetails(createDataAssetDetails).build();
        CreateDataAssetResponse createDataAssetResponse = forecastClient.createDataAsset(createDataAssetRequest);
        System.out.println("-----Creating DataAsset------");
        System.out.println(createDataAssetResponse);
        System.out.println("-----DataAsset Created------");
        return createDataAssetResponse.getDataAsset().getId();
    }

    public static String getForecast(ForecastClient forecastClient, String forecastId) {
        GetForecastRequest getForecastRequest = GetForecastRequest.builder()
                .forecastId(forecastId)
                .build();
        GetForecastResponse getForecastResponse = forecastClient.getForecast(getForecastRequest);
        System.out.println(getForecastResponse.getForecast());
        System.out.println("Status: "+getForecastResponse.getForecast().getLifecycleState().toString());
        return getForecastResponse.getForecast().getLifecycleState().toString();
    }

    public static String createForecast(ForecastClient forecastClient, String projectId, String dataAssetId) {
        System.out.println("-----Creating Forecast------");
        CreateForecastDetails createForecastDetails = CreateForecastDetails.builder()
                .forecastCreationDetails(getForecastCreationDetails(dataAssetId))
                .compartmentId(compartmentId)
                .projectId(projectId)
                .displayName("Forecast By Java SDK")
                .description("Forecast By Java SDK For Testing")
                .build();

        CreateForecastResponse createForecastResponse = forecastClient.createForecast(
                CreateForecastRequest.builder().createForecastDetails(createForecastDetails).build());
        System.out.println(createForecastResponse);
        System.out.println("-----Forecast Request Created------");
        return createForecastResponse.getForecast().getId();
    }

    private static ForecastCreationDetails getForecastCreationDetails(String dataAssetId) {
        return ForecastCreationDetails.builder()
                .dataSourceDetails(getDataSourceDetails(dataAssetId))
                .modelDetails(ModelDetails.builder().models(Arrays.asList(Models.Sma, Models.Dma)).build())
                .forecastFrequency("1DAY")
                .forecastHorizon(4)
                .forecastTechnique(ForecastTechnique.Rocv)
                .isForecastExplanationRequired(true)
                .errorMeasure(ErrorMeasure.Rmse)
                .targetVariables(Arrays.asList("Sales"))
                .confidenceInterval(95)
                .areCSVResultFilesRequired(true)
                .build();
    }

    private static ForecastDataSourceDetails getDataSourceDetails(String dataAssetId) {
        return DataSourceDataAsset.builder()
                .primaryDataSource(FcDataSourceDataAsset.builder()
                        .dataAssetId(dataAssetId)
                        .columnSchema(Arrays.asList(Schema.builder().columnName("date").dataType(DataTypes.Date).build(),
                                Schema.builder().columnName("Sales").dataType(DataTypes.Int).build(),
                                Schema.builder().columnName("Store").dataType(DataTypes.String).build()))
                        .isDataGrouped(true)
                        .dataFrequency("1DAY")
                        .tsColFormat("yyyy-MM-dd HH:mm:ss")
                        .tsColName("date")
                        .build())
                .build();
    }
}