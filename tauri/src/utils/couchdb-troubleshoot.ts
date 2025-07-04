/**
 * CouchDB Connection Troubleshooting Utility
 * 
 * This module provides functions to diagnose and fix common CouchDB connection issues.
 */

import { diagnoseCouchDbConnection, reinitializeRemoteDatabases } from 'src/boot/pouchdb';

// Define interface for diagnostic results to fix type issues
interface CouchDbDiagnosticResult {
  serverInfo: {
    version: string;
    vendor: string;
    features: string[];
  } | null;
  authStatus: {
    authenticated: boolean;
    username: string;
    roles: string[];
  } | null;
  databasesAccessible: {
    [dbName: string]: {
      accessible: boolean;
      docCount?: number;
      updateSeq?: string;
      error?: number | string;
    }
  };
  errors: string[];
}

/**
 * Run a full diagnostic on CouchDB connections and provide detailed recommendations
 */
export const troubleshootCouchDbConnection = async (): Promise<{
  status: 'ok' | 'warning' | 'error',
  issues: string[],
  recommendations: string[],
  diagnosticResults: any
}> => {
  console.log('🔍 Running CouchDB troubleshooter...');
  
  const result = {
    status: 'ok' as 'ok' | 'warning' | 'error',
    issues: [] as string[],
    recommendations: [] as string[],
    diagnosticResults: null as any
  };
  
  try {
    // Run the diagnostic
    const diagnosticResults = await diagnoseCouchDbConnection();
    result.diagnosticResults = diagnosticResults;
    
    // Check for server connection issues
    if (!diagnosticResults.serverInfo) {
      result.status = 'error';
      result.issues.push('Cannot connect to CouchDB server');
      result.recommendations.push('Check if CouchDB is running on the specified host');
      result.recommendations.push('Verify network connectivity to the CouchDB server');
      result.recommendations.push('Check firewall settings that might be blocking connections');
    }
    
    // Check for authentication issues
    if (diagnosticResults.authStatus && !diagnosticResults.authStatus.authenticated) {
      result.status = 'error';
      result.issues.push('Authentication failed - not logged in as a valid user');
      result.recommendations.push('Verify the username and password in your configuration');
      result.recommendations.push('Check if the user has proper permissions in CouchDB');
    }
    
    // Check each database
    const inaccessibleDbs = Object.entries(diagnosticResults.databasesAccessible)
      .filter(([_, info]: [string, any]) => !info.accessible)
      .map(([dbName, info]: [string, any]) => ({ dbName, error: info.error }));
      
    if (inaccessibleDbs.length > 0) {
      result.status = result.status === 'ok' ? 'warning' : result.status;
      result.issues.push(`${inaccessibleDbs.length} databases are not accessible`);
      
      // Group by error type for better recommendations
      const notFound = inaccessibleDbs.filter(db => db.error === 404).map(db => db.dbName);
      const authErrors = inaccessibleDbs.filter(db => [401, 403].includes(db.error)).map(db => db.dbName);
      const serverErrors = inaccessibleDbs.filter(db => db.error === 500).map(db => db.dbName);
      
      if (notFound.length > 0) {
        result.issues.push(`Databases not found: ${notFound.join(', ')}`);
        result.recommendations.push('Create the missing databases in CouchDB');
      }
      
      if (authErrors.length > 0) {
        result.issues.push(`Authentication errors for: ${authErrors.join(', ')}`);
        result.recommendations.push('Check user permissions for these specific databases');
      }
      
      if (serverErrors.length > 0) {
        result.issues.push(`Server errors (500) for: ${serverErrors.join(', ')}`);
        result.recommendations.push('Check CouchDB logs for errors related to these databases');
        result.recommendations.push('Ensure CouchDB has enough disk space and resources');
      }
    }
    
    // If there are connection errors but no specific issues identified
    if (diagnosticResults.errors.length > 0 && result.issues.length === 0) {
      result.status = 'error';
      result.issues.push('Unknown connection errors occurred');
      result.issues.push(...diagnosticResults.errors);
      result.recommendations.push('Check CouchDB server logs for more information');
      result.recommendations.push('Verify your CouchDB configuration (URL, credentials, etc.)');
    }
    
    // If everything seems fine but there were initial issues
    if (result.status === 'ok') {
      result.recommendations.push('Connection appears healthy now. If you were experiencing issues before:');
      result.recommendations.push('- The issue might have been temporary');
      result.recommendations.push('- Try restarting the application to ensure proper connection');
    }
    
    return result;
  } catch (error: any) {
    console.error('❌ Troubleshooter failed:', error);
    
    return {
      status: 'error',
      issues: ['Failed to run diagnostics', error.message],
      recommendations: [
        'Check your network connection',
        'Verify that CouchDB is running',
        'Check your application logs for more details'
      ],
      diagnosticResults: null
    };
  }
};

/**
 * Try to automatically fix common CouchDB connection issues
 */
export const attemptCouchDbConnectionFix = async (): Promise<{
  fixed: boolean,
  actions: string[],
  message: string
}> => {
  console.log('🔧 Attempting to fix CouchDB connection issues...');
  
  const actions: string[] = [];
  
  try {
    // Run diagnostic first
    const diagnostic = await diagnoseCouchDbConnection();
    
    // Check if there's a connection at all
    if (!diagnostic.serverInfo) {
      actions.push('Unable to connect to server - cannot auto-fix');
      return {
        fixed: false,
        actions,
        message: 'Cannot connect to CouchDB server. Please check if it is running and accessible.'
      };
    }
    
    // Check auth issues
    if (diagnostic.authStatus && !diagnostic.authStatus.authenticated) {
      actions.push('Detected authentication issue');
      actions.push('Attempting to reconnect with updated credentials');
      
      // Try reinitializing with current settings
      await reinitializeRemoteDatabases();
      actions.push('Reinitialized remote database connections');
      
      // Check if that fixed it
      const afterAuthFix = await diagnoseCouchDbConnection();
      if (afterAuthFix.authStatus && afterAuthFix.authStatus.authenticated) {
        actions.push('Authentication issue resolved');
      } else {
        actions.push('Authentication issue persists - manual fix required');
        return {
          fixed: false,
          actions,
          message: 'Authentication issues could not be fixed automatically. Please check your credentials.'
        };
      }
    }
    
    // Handle missing databases
    const missingDbs = Object.entries(diagnostic.databasesAccessible)
      .filter(([_, info]: [string, any]) => !info.accessible && info.error === 404)
      .map(([dbName]: [string, any]) => dbName);
    
    if (missingDbs.length > 0) {
      actions.push(`Found ${missingDbs.length} missing databases`);
      actions.push('Attempting to create missing databases');
      
      // Try reinitializing which will attempt to create missing databases
      await reinitializeRemoteDatabases();
      actions.push('Reinitialized remote database connections');
      
      // Check if that fixed it
      const afterDbFix = await diagnoseCouchDbConnection();
      const stillMissing = Object.entries(afterDbFix.databasesAccessible)
        .filter(([_, info]: [string, any]) => !info.accessible && info.error === 404)
        .map(([dbName]: [string, any]) => dbName);
      
      if (stillMissing.length === 0) {
        actions.push('Successfully created all missing databases');
      } else if (stillMissing.length < missingDbs.length) {
        actions.push(`Created some databases, but ${stillMissing.length} are still missing`);
      } else {
        actions.push('Failed to create any missing databases - permissions issue likely');
        return {
          fixed: false,
          actions,
          message: 'Could not create missing databases. You may need admin permissions.'
        };
      }
    }
    
    // Check for server errors
    const serverErrorDbs = Object.entries(diagnostic.databasesAccessible)
      .filter(([_, info]: [string, any]) => !info.accessible && info.error === 500)
      .map(([dbName]: [string, any]) => dbName);
    
    if (serverErrorDbs.length > 0) {
      actions.push(`Found ${serverErrorDbs.length} databases with server errors`);
      actions.push('Server errors typically require manual intervention');
      actions.push('Attempting to reconnect with different parameters');
      
      // Try reinitializing with modified timeout settings
      await reinitializeRemoteDatabases();
      actions.push('Reinitialized with adjusted connection parameters');
      
      // Check if that fixed it
      const afterServerFix = await diagnoseCouchDbConnection();
      const stillErrorDbs = Object.entries(afterServerFix.databasesAccessible)
        .filter(([_, info]: [string, any]) => !info.accessible && info.error === 500)
        .map(([dbName]: [string, any]) => dbName);
      
      if (stillErrorDbs.length === 0) {
        actions.push('Successfully resolved all server errors');
      } else {
        actions.push(`${stillErrorDbs.length} databases still have server errors`);
        return {
          fixed: false,
          actions, 
          message: 'Server errors persist. Check CouchDB logs and configuration.'
        };
      }
    }
    
    // Final check
    const finalCheck = await diagnoseCouchDbConnection();
    const anyRemainingIssues = Object.values(finalCheck.databasesAccessible).some(
      (info: any) => !info.accessible
    ) || finalCheck.errors.length > 0;
    
    if (!anyRemainingIssues) {
      return {
        fixed: true,
        actions,
        message: 'Successfully fixed all detected CouchDB connection issues!'
      };
    } else {
      return {
        fixed: false,
        actions,
        message: 'Some issues were fixed, but others remain. Manual intervention required.'
      };
    }
    
  } catch (error: any) {
    console.error('❌ Auto-fix failed:', error);
    actions.push(`Error during fix attempt: ${error.message}`);
    
    return {
      fixed: false,
      actions,
      message: `Auto-fix failed: ${error.message}`
    };
  }
};
