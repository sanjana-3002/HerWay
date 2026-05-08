import Papa from 'papaparse';

// Normalize neighborhood names for matching between CSV and GeoJSON
export const normalizeNeighborhoodName = (name) => {
  if (!name) return '';
  return name
    .toUpperCase()
    .trim()
    .replace(/['']/g, "'")
    .replace(/\s+/g, ' ');
};

// Load and parse the CSV data
export const loadCSVData = async (csvUrl) => {
  try {
    const response = await fetch(csvUrl);
    const csvText = await response.text();
    
    return new Promise((resolve, reject) => {
      Papa.parse(csvText, {
        header: true,
        skipEmptyLines: true,
        dynamicTyping: true,
        complete: (results) => {
          // Create a lookup map by normalized neighborhood name
          const dataMap = {};
          results.data.forEach(row => {
            if (row.neighborhood) {
              const normalizedName = normalizeNeighborhoodName(row.neighborhood);
              dataMap[normalizedName] = {
                ...row,
                normalizedName
              };
            }
          });
          resolve({ data: results.data, dataMap });
        },
        error: (error) => {
          reject(error);
        }
      });
    });
  } catch (error) {
    console.error('Error loading CSV:', error);
    throw error;
  }
};

// Load GeoJSON data
export const loadGeoJSON = async (geoJsonUrl) => {
  try {
    const response = await fetch(geoJsonUrl);
    const geoJson = await response.json();
    return geoJson;
  } catch (error) {
    console.error('Error loading GeoJSON:', error);
    throw error;
  }
};

// Merge CSV data with GeoJSON features
export const mergeDataWithGeoJSON = (geoJson, csvDataMap) => {
  const mergedFeatures = geoJson.features.map(feature => {
    const geoName = normalizeNeighborhoodName(feature.properties.community);
    const csvData = csvDataMap[geoName];
    
    return {
      ...feature,
      properties: {
        ...feature.properties,
        csvData: csvData || null,
        hasData: !!csvData
      }
    };
  });

  return {
    ...geoJson,
    features: mergedFeatures
  };
};

// Get risk level color
export const getRiskColor = (riskLevel) => {
  if (!riskLevel) return '#CCCCCC';
  
  const risk = riskLevel.toLowerCase();
  if (risk.includes('high')) return '#E63946';
  if (risk.includes('medium')) return '#F4A261';
  if (risk.includes('low')) return '#2A9D8F';
  return '#CCCCCC';
};

// Get risk level class name
export const getRiskClass = (riskLevel) => {
  if (!riskLevel) return '';
  
  const risk = riskLevel.toLowerCase();
  if (risk.includes('high')) return 'high';
  if (risk.includes('medium')) return 'medium';
  if (risk.includes('low')) return 'low';
  return '';
};

// Format number for display
export const formatNumber = (num) => {
  if (num === null || num === undefined || isNaN(num)) return 'N/A';
  return Number(num).toLocaleString();
};

// Format percentage
export const formatPercent = (num) => {
  if (num === null || num === undefined || isNaN(num)) return 'N/A';
  return `${Number(num).toFixed(1)}%`;
};

// Format hours
export const formatHours = (num) => {
  if (num === null || num === undefined || isNaN(num)) return 'N/A';
  return `${Number(num).toFixed(1)} hrs`;
};

// Format score (0-1 to percentage or decimal)
export const formatScore = (num) => {
  if (num === null || num === undefined || isNaN(num)) return 'N/A';
  return Number(num).toFixed(3);
};

