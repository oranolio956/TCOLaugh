/**
 * Enhanced Recon Results Formatter
 * Formats the enhanced recon results for better display
 */

function formatReconResults(data) {
    if (!data || !data.found_on || data.found_on.length === 0) {
        return "No platforms found for this username.";
    }
    
    let output = `Found on ${data.total_found || data.found_on.length} platform(s):\n\n`;
    
    data.found_on.forEach((result, index) => {
        output += `${index + 1}. ${result.site}\n`;
        output += `   URL: ${result.url}\n`;
        
        if (result.confidence !== undefined) {
            const confidencePercent = Math.round(result.confidence * 100);
            output += `   Confidence: ${confidencePercent}%`;
            
            // Confidence indicator
            if (result.confidence >= 0.9) {
                output += " ⭐⭐⭐ (Very High)";
            } else if (result.confidence >= 0.7) {
                output += " ⭐⭐ (High)";
            } else {
                output += " ⭐ (Medium)";
            }
            output += "\n";
        }
        
        if (result.methods_used && result.methods_used.length > 0) {
            output += `   Detection Methods: ${result.methods_used.join(", ")}\n`;
        } else if (result.method) {
            output += `   Detection Method: ${result.method}\n`;
        }
        
        if (result.response_time_ms !== undefined) {
            output += `   Response Time: ${result.response_time_ms}ms\n`;
        }
        
        if (result.status_code) {
            output += `   Status Code: ${result.status_code}\n`;
        }
        
        if (result.details) {
            // Truncate long details
            const details = result.details.length > 100 
                ? result.details.substring(0, 100) + "..." 
                : result.details;
            output += `   Details: ${details}\n`;
        }
        
        output += "\n";
    });
    
    if (data.scan_timestamp) {
        const scanDate = new Date(data.scan_timestamp * 1000);
        output += `\nScan completed: ${scanDate.toLocaleString()}`;
    }
    
    return output;
}

function formatReconResultsJSON(data) {
    // Pretty JSON with enhanced formatting
    return JSON.stringify(data, null, 2);
}
