## Important Order of Operations in Storm Processing Within the hurrevac_storm.py

### 1 Process Advisory Points (Calculate fields (TimeStep, etc))

**1.1 Spatial intersect to determine if inland**

**1.2 Convert MaxWindSpeed from knots to miles per hour, reduce by HurrevacVmaxFactor from settings**
    
- These reduction settings have been developed to represent an approximation on average storm intensity parameters in each quadrant versus applying the maximum value throughout.

**1.3 RadiusToHurrWindsType: Use the MaxWindSpeed in 'mph \* HurrevacVmaxFactor' to determine**

**1.4 RadiusToXWinds (34, 50, 64)**

- This classifies type of storm as hurricane, tropical storm or depression for the purpose of applying the windfield model.

**1.5 Fill in intermediate values.**

**1.6 Interim advisory RadiusToXWinds, get previous row's value**

- Interim advisories provide only the MaxWindSpeed and location, other intensity values are filled in using the previous record.

**1.7 Zero Out RadiusToXWinds**

- Based on HurrWindType.

- Only the Radius to the type of storm classified based on the previous step is used in the analysis.

**1.8 Inland can not increase in MWS**

- If current row value is greater than previous row value, set current rows value to previous rows value.

- This is a validation step to prevent the accidental increase of MaxWindSpeed inland resulting from data entry errors.

**1.9 Inland adjustment to MaxWindSpeed**

- (mph and HurrevacVmaxFactor applied) adjusted by 1.15 if inland=1 

- Note that the ARA windfield model employed by Hazus is based on points over water, so a 15% increase adjustment factor is applied to the MaxWindSpeed, for first inland point is not increased if it is determined to be intensifying (MaxWind is greater and Central Pressure is less) than the last offshore point since this represents a storm whose center is over land but should be treated as primarily over water for the purpose of windfield modelling.

### 2  Process Forecast Points (Calculate fields (TimeStep, etc))
	
**2.1 Spatial intersect to determine if inland or not**

**2.2 Convert MaxWindSpeed from knots to miles per hour, reduce by HurrevacVmaxFactor from settings**

- This classifies type of storm as hurricane, tropical storm, or depression for the purpose of applying the windfield model.

**2.3 RadiusToHurrWindsType (Use the MaxWindSpeed in mph*HurrevacVmaxFactor to determine)**

**2.4 Zero Out RadiusToXWinds**

- Based on HurrWindType.

- Only the Radius to the type of storm classified based on the previous step is used in the analysis.

**2.5 Inland can not increase in MWS**

- If current row value is greater than previous row value, set current rows value to previous rows value (this is a validation step to prevent the accidental increase of MaxWindSpeed inland resulting from data entry errors).

**2.6 Inland adjustment to MaxWindSpeed**

- (mph and HurrevacVmaxFactor applied) adjusted by 1.15 if inland=1

- Note that the ARA windfield model employed by Hazus is based on points over water, so a 15% increase adjustment factor is applied to the MaxWindSpeed, for first inland point is not increased if it is determined to be intensifying (MaxWind is greater and Central Pressure is less) than the last offshore point since this represents a storm whose center is over land but should be treated as primarily over water for the purpose of windfield modelling.

**2.7 Cleanup Forecast data frame before appending to main advisory dataframe**

### 3 Merge Forecast Points into Advisory Points

### 4 Threshold Checks and Data Conditioning (validation steps)
	
**4.1 Delete rows with 0,0 latitude, longitude values**

**4.2 MaxWindSpeed need to be 40 or higher**

- Validation fails with erroneous values or those under 40 mph.

- MaxWindspeeds under 50 mph do not influence losses.

**4.3 Radius to 34k winds needs to be 30 or higher (where the RadiusToHurrWindsType = T and RadiusTo34KWinds is 0)**

- Required at validation step.
	
### 5 Trim and format advisory dataframe 

- Optimizes analysis and shortens runtimes if points are left off head or tail of track that do not influence losses.

### 6 OptimizeTrack runs after all calculations are finished and forecast points appended to main dataframe and before loading to sql server.


## Potential Risk:
Forecast points are calculated separate from advisory points, risk is that the forecast points may increase in MWS inland if there are data entry errors from the official sources (considered low risk).