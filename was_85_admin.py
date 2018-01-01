#================================================================================================================================
# SCRIPT : This script is the main script for property file based Websphere Application Server enviornment creation.
#          Part of WASDEV setup.
# USAGE  : wsadmin -lang jython was_85_admin.py [country name].[application name].[environment name]
#          Example: ./wsadmin.sh -lang jython -f was_85_admin.py "ind.test.dev"
# AUTHOR : Middleware Engineering
# DATED  : 01 January, 2015
# VERSION: 1.0
#================================================================================================================================
###########################################################################################################################################
# IMPORT
import os
import socket
import time
import sys
import re
import java
from java.util import Properties
from java.io import FileInputStream
from   java.util.logging  import Logger, FileHandler, SimpleFormatter
import javax.management.ObjectName as ObjectName

###########################################################################################################################################
# GLOBAL DECLARATION
global AdminConfig
global AdminControl
global AdminApp
global was_host 
global property_file
global logger
global log_file
global cell
global cell_id
global mail_status
global mod_mapping
global global_cluster_list
global global_datasource_auth_alias_list
global global_datasource_provider_list
global global_vhost_list
global global_threadpool_map
global global_domain_list

###########################################################################################################################################
# UTILITY FUNCTION SECTION
def notify_error(messege) :
        global mail_status
        AdminTask.restoreCheckpoint(['-checkpointName', 'full2'])
        if mail_status == 0 :
            url_called =  'https://mail.send.endpoint.com:443/sendmail'
            url_called =  url_called + 'San.Muk@gmail.com&alert_type=DEPLOYMENT&env_type=APPLICATION&env=' + environment_detail + '&remark=' + messege
            url_called =  url_called + '&status=FAILED&server=' + was_host
            unix_command = 'wget -q --spider --no-check-certificate "' + url_called + '"'
            os.system(unix_command)
        #
        mail_status = 1
        sys.exit(1)
#

def check_valid_value(input_value) :
        if input_value == None or input_value == '' :
                return 'True'
        else :
                return
        #
#

def splitlist(s) :
    if s[0] != '[' or s[-1] != ']':
        raise "Invalid string: %s" % s
    #
    return s[1:-1].split(' ')
#

def splitlines(s) :
    rv = [s]
    if '\r' in s:
        rv = s.split('\r\n')
    elif '\n' in s:
        rv = s.split('\n')
    #
    if rv[-1] == '':
        rv = rv[:-1]
    #
    return rv
#

def customscript() :
    logger.info('Inside : customscript')
    try :
        scpt_list = search_property_list('was.customtask.script.name_r_')
        for scpt in scpt_list :
            logger.info('Executing script: ' + scpt)
            scpt_index = search_property_index('was.customtask.script.name_r_', scpt)
            path = search_property('was.customtask.script.path_r_' + scpt_index)
            arg = search_property('was.customtask.script.argument_o_' + scpt_index)
            command_str = ''
            if arg != None or arg != '' :
                command_str = path + ' ' + arg
            else :
                command_str = path
            #
            os.system(command_str)
        #
        logger.info('Exiting : customscript')
    except :
        logger.severe('ERROR: Cannot complete customscript Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in customscript methord.')
        sys.exit(1)
    #
#

def initiatelog(log_file_location) :
    try :
        curTime = time.localtime()
        log_file_name = 'was_85_admin_' + str(curTime[0]) + '_' + str(curTime[1]) + '_' + str(curTime[2]) + '.log'
        log_file = FileHandler(os.path.join(log_file_location, log_file_name))
        log_file.setFormatter(SimpleFormatter())
        logger.addHandler(log_file)
        logger.info('Initiated Websphere Deployment on server ' + was_host)
        logger.info('Exiting : initiatelog')
        return 0
    except :
        print "ERROR: Cannot initiate logging. Setup failed to initiate."
        print str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1])
        notify_error('Fatal error detected in initiatelog methord.')
        sys.exit(1)
    #
#

def loadproperty(property_file_cluster) :
    logger.info('Inside : loadproperty . Argument : ' + property_file_cluster)
    try :
        logger.info('Property file : ' + property_file_cluster)
        property_file.load(FileInputStream(property_file_cluster))
        logger.info('Property file loaded successfully.')
        logger.info('Exiting : loadproperty')
    except :
        logger.severe('Error loading property file. Execution will be halted')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in loadproperty methord.')
        sys.exit(1)
    #
#

def search_property_list(property_string) :
    logger.info('Inside : search_property_list. Argument : ' + property_string)
    tmp_list = []
    try :
        counter = 1
        prop_str = property_string + str(counter)
        prop_val = property_file.getProperty(prop_str)
        logger.info('Property: ' + prop_str + ' Value: ' + str(prop_val))
        while prop_val != None :
            tmp_list.append(str(prop_val))
            counter = counter + 1
            prop_str = property_string + str(counter)
            prop_val = property_file.getProperty(prop_str)
            logger.info('Property: ' + prop_str + ' Value: ' + str(prop_val))
        #
        logger.info('Exiting : search_property_list.')
        return tmp_list
    except :
        logger.severe('Error searching property in property file.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in search_property_list methord.')
        sys.exit(1)
    #
#

def search_property_index(property_string, property_value) :
    logger.info('Inside : search_property_index. Argument : ' + property_string + '. ' + property_value)
    tmp_list = []
    try :
        counter = 1
        prop_str = property_string + str(counter)
        prop_val = property_file.getProperty(prop_str)
        logger.info('Property: ' + prop_str + ' Value: ' + str(prop_val))
        while prop_val != None :
            if prop_val == property_value :
                logger.info('Property found. Exiting : search_property_index')
                return str(counter)
            #
            counter = counter + 1
            prop_str = property_string + str(counter)
            prop_val = property_file.getProperty(prop_str)
        #
        logger.info('Cannot match a property with string: ' + property_string + ' and value: ' + property_value)
        logger.info('Exiting : search_property_index')
        return None
    except :
        logger.severe('Error searching property in property file.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in search_property_index methord.')
        sys.exit(1)
    #
#

def search_property(property_string) :
    logger.info('Inside : search_property. Argument : ' + property_string)
    try :
        prop_val = property_file.getProperty(property_string)
        logger.info('Property: ' + property_string + ' Value: ' + str(prop_val))
        logger.info('Exiting : search_property')
        return prop_val
    except :
        logger.severe('Error searching property in property file.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in search_property methord.')
        sys.exit(1)
    #
#

def check_element_in_list(list_passed, element_passed) :
    logger.info('Inside : check_element_in_list. Argument : ' + str(list_passed) + ', ' + element_passed)
    try :
        for list_element in list_passed :
            if list_element.find(element_passed) != -1 :
                logger.info('Found: ' + list_element)
                return 1
            #
        #
        logger.info('Exiting : check_element_in_list')
        return 0
    except :
        logger.severe('Error searching element in the list.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in check_element_in_list methord.')
        sys.exit(1)
    #
#

def check_config_in_configid_list(config_list, name, param=None) :
    logger.info('Inside : check_config_in_configid_list. Argument : ' + str(config_list) + ', ' + name)
    try :
        for conf in config_list :
            if param == None :
                config_name = AdminConfig.showAttribute(conf, 'name')
            else :
                config_name = AdminConfig.showAttribute(conf, param)
            #
            if config_name == name :
                return conf
            #
        #
        logger.info('Exiting : check_config_in_configid_list')
        return ''
    except :
        logger.severe('Error searching element in the Configuration list.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in check_config_in_configid_list methord.')
        sys.exit(1)
    #
#

###########################################################################################################################################
# CORE FUNCTIONALITY
def setJ2eeResourceProperty(parent, propName, propType, propValue) :
    logger.info('Inside : setJ2eeResourceProperty. Argument : ' + parent  + ', ' + propName  + ', ' + propType  + ', ' + propValue)
    try :
        propSet = AdminConfig.showAttribute(parent, 'propertySet')
        if propSet == None or propSet == '' :
            propSet = AdminConfig.create('J2EEResourcePropertySet' , parent, "")
        #
        name = ["name" , propName]
        type = ["type" , propType]
        required = ["required" , "true"]
        value = ["value" , propValue]
        attrs = [name , type , required , value]
        return_value = AdminConfig.create('J2EEResourceProperty' , propSet , attrs)
        logger.info(return_value)
        logger.info('Exiting : setJ2eeResourceProperty')
    except :
        logger.severe('Error setting resource property. Execution will be haulted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in setJ2eeResourceProperty methord.')
        sys.exit(1)
    #
#

def setWebSphereVariable(name, value, clusterName) :
    logger.info('Inside : setWebSphereVariable. Argument : ' + name + ' . ' + value + ' . ' + clusterName)
    try :
        clusterid = check_config_in_configid_list(global_cluster_list, clusterName)
        map = AdminConfig.list('VariableMap', clusterid)
        attrs = []
        attrs.append( [ 'symbolicName', name ] )
        attrs.append( [ 'value', value ] )
        object=AdminConfig.create('VariableSubstitutionEntry', map, attrs)
        logger.info('Exiting : setWebSphereVariable')
        return object
    except :
        logger.severe('Error setting Websphere Variable. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in setWebSphereVariable methord.')
        sys.exit(1)
    #
#

def stop_cluster(cluster_name) :
    logger.info('Inside : stop_cluster. Argument : ' + cluster_name)
    try :
        try :
            dummy = AdminTask.getDynamicClusterServerType(cluster_name)
        except :
            logger.info('Cluster ' + cluster_name + ' does not exist.')
            return
        #
        logger.info('Stopping Cluster.')
        AdminTask.setDynamicClusterOperationalMode(cluster_name, '[-operationalMode manual]')
	cluster_object = AdminControl.completeObjectName('type=Cluster,name=%s,*' % (cluster_name))
        state = AdminControl.getAttribute( cluster_object, 'state' )
        if state != 'websphere.cluster.partial.stop' and state != 'websphere.cluster.stopped' :
            AdminControl.invoke(cluster_object, 'stop')
        #
        time.sleep( 300 )
        state = AdminControl.getAttribute( cluster_object, 'state' )
        if state != 'websphere.cluster.stopped' :
            raise Exception('Cluster ' + cluster_name + ' cannot be stopped. Please stop and manually and retrigger the script.')
        #
        logger.info('Exiting : stop_cluster.')
    except :
        logger.severe('Error stopping CLUSTER.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in stop_cluster methord.')
        sys.exit(1)
    #
#

def start_cluster(cluster_name) :
    logger.info('Inside : start_cluster. Argument : ' + cluster_name)
    try :
        try :
            dummy = AdminTask.getDynamicClusterServerType(cluster_name)
        except :
            logger.info('Cluster ' + cluster_name + ' does not exist.')
            notify_error('Deployment complete but configured CLUSTER not found.')
            return
        #
        cluster_index = search_property_index('was.cluster.dynamic.name_r_', cluster_name)
        op_mode_req_ret = search_property('was.cluster.dynamic.operationalmode_o_' + str(cluster_index))
        op_mode_req = str(op_mode_req_ret)
        op_mode_prs = AdminTask.getDynamicClusterOperationalMode(cluster_name)
        logger.info('Present Operational Mode: ' + op_mode_prs + ' Required Operational Mode: ' + op_mode_req)
        if op_mode_prs != op_mode_req :
            logger.info('Setting CLUSTER correct Operational Mode.')
            tmp_tuple = '[-operationalMode ' + op_mode_req + ']'
            result_output = AdminTask.setDynamicClusterOperationalMode(cluster_name, tmp_tuple)
            logger.info(result_output)
        #
        logger.info('Exiting : start_cluster')
    except :
        logger.severe('Error starting CLUSTER.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in start_cluster methord.')
        sys.exit(1)
    #
#

def create_auth_alias() :
    logger.info('Inside : create_auth_alias')
    try :
        auth_alias_list = search_property_list('was.jdbc.auth.name_r_')
        for auth_alias in auth_alias_list :
            logger.info('Starting to craete Auth Alias: ' + auth_alias)
            alias_index = search_property_index('was.jdbc.auth.name_r_', auth_alias)
            alias_user = search_property('was.jdbc.auth.user_r_' + alias_index)
            alias_password = search_property('was.jdbc.auth.password_r_' + alias_index)
            logger.info('Property retrived. Name: ' + auth_alias + ' User: ' + alias_user + ' Password: ' + alias_password)
            if auth_alias == None or auth_alias == '' or alias_user == None or alias_user == '' or alias_password == None or alias_password == '' :
                raise Exception('Required property not defined.')
            else :
                alias_attr = ["alias", auth_alias]
                desc_attr = ["description", 'Alias - '+auth_alias]
                userid_attr = ["userId", alias_user]
                password_attr = ["password", alias_password]
                attrs = [alias_attr, desc_attr, userid_attr, password_attr]
                sec = AdminConfig.getid('/Cell:%s/Security:/' % cell)
                appauthdata = AdminConfig.create("JAASAuthData", sec, attrs)
                global_datasource_auth_alias_list.append(appauthdata)
                logger.info(appauthdata)
            #
            logger.info('Completed creation of Alias: ' + auth_alias)
        #
        logger.info('Exiting : create_auth_alias')
    except :
        logger.severe('Error creating Auth Alias. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in create_auth_alias methord.')
        sys.exit(1)
    #
#

def create_jdbc_variable() :
    logger.info('Inside : create_jdbc_variable')
    try :
        jdbc_var_scope_list = search_property_list('was.jdbc.scope_r_')
        for jdbc_var_scope in jdbc_var_scope_list :
            cluster_index = search_property_index('was.cluster.dynamic.name_r_', jdbc_var_scope)
            if cluster_index == None :
                raise Exception('Scope defined for Cluster which is not found in property file. Scope can be Cluster which are created for this environment.')
            else :
                logger.info('Starting to craete JDBC Variable for scope: ' + jdbc_var_scope)
                jdbc_var_index = search_property_index('was.jdbc.scope_r_', jdbc_var_scope)
                jdbc_var_type = search_property('was.jdbc.provider.type_r_' + jdbc_var_index)
                ds_variable_list = search_property_list('was.jdbc.provider.variable_name_r_' + jdbc_var_index + '_')
                for ds_variable in ds_variable_list :
                    ds_variable_str = 'was.jdbc.provider.variable_name_r_' + jdbc_var_index + '_'
                    ds_variable_index = search_property_index(ds_variable_str, ds_variable)
                    ds_variable_str = 'was.jdbc.provider.variable_value_r_' + jdbc_var_index + '_'
                    ds_variable_value = search_property(ds_variable_str + ds_variable_index)
                    if ds_variable == None or ds_variable == '' or ds_variable_value == None or ds_variable_value == '' :
                        raise Exception('Property not correctly defined. Check property indexed: ' + jdbc_var_index + '_' + ds_variable_index)
                    #
                    logger.info('Creating Websphere Variable. Scope: ' + jdbc_var_scope + ' Name: ' + ds_variable + ' Value: ' + ds_variable_value)
                    ret_value = setWebSphereVariable(ds_variable, ds_variable_value, jdbc_var_scope)
                    logger.info(ret_value)
                #
            #
            logger.info('Done creating Websphere Variable for Scope: ' + jdbc_var_scope)
        #
        logger.info('Exiting : create_jdbc_variable')
    except :
        logger.severe('Error creating resource variable. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in create_jdbc_variable methord.')
        sys.exit(1)
    #
#

def create_datasource_provider() :
    logger.info('Initialize : create_datasource_provider')
    try :
        jdbc_var_scope_list = search_property_list('was.jdbc.scope_r_')
        for jdbc_var_scope in jdbc_var_scope_list :
            cluster_index = search_property_index('was.cluster.dynamic.name_r_', jdbc_var_scope)
            if cluster_index == None :
                raise Exception('Scope defined for Cluster which is not found in property file. Scope can be Cluster which are created for this environment.')
            else :
                logger.info('Starting to craete Datasource Provider for scope: ' + jdbc_var_scope)
                jdbc_var_index = search_property_index('was.jdbc.scope_r_', jdbc_var_scope)
                jdbc_var_type = search_property('was.jdbc.provider.type_r_' + jdbc_var_index)
                ds_provider_name = search_property('was.jdbc.provider.name_r_' + jdbc_var_index)
                ds_provider_class = search_property('was.jdbc.provider.class_r_' + jdbc_var_index)
                ds_provider_driver = search_property('was.jdbc.provider.driver_r_' + jdbc_var_index)
                if check_valid_value(ds_provider_name) or check_valid_value(ds_provider_class) or check_valid_value(ds_provider_driver) :
                    raise Exception('Required property not defined for Datasource Provider of index: ' + jdbc_var_index)
                else :
                    logger.info('Creating Datasource Provider. Name:%s ImplementationClass:%s Driver:%s' % (ds_provider_name, ds_provider_class, ds_provider_driver))
                    attrs = []
                    attrs.append( [ 'name', ds_provider_name ] )
                    attrs.append( [ 'classpath', ds_provider_driver ] )
                    attrs.append( [ 'nativepath', ''  ] )
                    attrs.append( [ 'implementationClassName', ds_provider_class ] )
                    if jdbc_var_type == 'oracle' :
                        attrs.append( [ 'description', 'Oracle Datasource Provider' ] )
                        attrs.append( [ 'providerType', 'Oracle' ] )
                    elif jdbc_var_type == 'db2' :
                        attrs.append( [ 'description', 'DB2 JDBC Driver Provider' ] )
                        attrs.append( [ 'providerType', 'DB2' ] )
                    else :
                        raise Exception('Only Oracle and DB2 Implementation present curretly.')
                    #
                    cluster_id = AdminConfig.getid( '/Cell:%s/ServerCluster:%s/' % (cell, jdbc_var_scope))
                    ret_value = AdminConfig.create('JDBCProvider', cluster_id, attrs)
                    global_datasource_provider_list.append(ret_value)
                    logger.info(ret_value)
                #
            #
            logger.info('Done Creating Datasource Provider for scope: ' + jdbc_var_scope)
        #
        logger.info('Exiting : create_datasource_provider')
    except :
        logger.severe('Error Datasource Provider. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in create_datasource_provider methord.')
        sys.exit(1)
    #
#

def create_datasource() :
    logger.info('Initialize : create_datasource')
    try :
        jdbc_var_scope_list = search_property_list('was.jdbc.scope_r_')
        for jdbc_var_scope in jdbc_var_scope_list :
            cluster_index = search_property_index('was.cluster.dynamic.name_r_', jdbc_var_scope)
            if cluster_index == None :
                raise Exception('Scope defined for Cluster which is not found in property file. Scope can be Cluster which are created for this environment.')
            else :
                logger.info('Starting to craete Datasource for scope: ' + jdbc_var_scope)
                jdbc_ds_index = search_property_index('was.jdbc.scope_r_', jdbc_var_scope)
                jdbc_ds_provider = search_property('was.jdbc.provider.name_r_' + jdbc_ds_index)
                jdbc_ds_type = search_property('was.jdbc.provider.type_r_' + jdbc_ds_index)
                ds_list = search_property_list('was.jdbc.datasource.name_r_' + jdbc_ds_index + '_')
                for ds_name in ds_list :
                    ds_index = search_property_index('was.jdbc.datasource.name_r_' + jdbc_ds_index + '_', ds_name)
                    ds_jndi = search_property('was.jdbc.datasource.jndi_r_' + jdbc_ds_index + '_' + ds_index)
                    ds_auth = search_property('was.jdbc.datasource.authalias_r_' + jdbc_ds_index + '_' + ds_index)
                    ds_auth_list = search_property_list('was.jdbc.auth.name_r_')
                    ds_auth_status = check_element_in_list(ds_auth_list, ds_auth)
                    if ds_auth_status == 0 :
                        raise Exception('The Auth Alias name specified for Datasource ' + ds_name + ' not defined for this environment.')
                    #
                    ds_helper = search_property('was.jdbc.datasource.helperClass_r_' + jdbc_ds_index + '_' + ds_index)
                    ds_stmt_cache = search_property('was.jdbc.datasource.stmentcachesize_o_' + jdbc_ds_index + '_' + ds_index)
                    if ds_stmt_cache == None or ds_stmt_cache == '' :
                        ds_stmt_cache = 10
                    #
                    if ds_jndi == None or ds_jndi == '' or ds_auth == None or ds_auth == '' or ds_helper == None or ds_helper == '' :
                        raise Exception('All required property not present for Datasource ' + ds_name)
                    #
                    mapping = []
                    mapping.append( [ 'authDataAlias', ds_auth ] )
                    mapping.append( [ 'mappingConfigAlias', 'DefaultPrincipalMapping' ] )
                    attrs = []
                    attrs.append( [ 'name', ds_name ] )
                    attrs.append( [ 'description', 'Datasource ' + ds_name ] )
                    attrs.append( [ 'jndiName', ds_jndi ] )
                    attrs.append( [ 'statementCacheSize', ds_stmt_cache ] )
                    attrs.append( [ 'authDataAlias', ds_auth ] )
                    attrs.append( [ 'datasourceHelperClassname', ds_helper ] )
                    attrs.append( [ 'mapping', mapping ] )
                    provider_id = check_config_in_configid_list(global_datasource_provider_list, jdbc_ds_provider)
                    ds_provider_type = AdminConfig.showAttribute(provider_id,  'providerType')
                    if ds_provider_type.find('XA') != -1 :
                        xa_alias = search_property('was.jdbc.datasource.xarecoveryalias_r_' + jdbc_ds_index + '_' + ds_index)
                        if xa_alias == None or xa_alias == '' :
                            raise Exception('XA Recovery alias is a required attribute for XA Datasource. It is not defined in property file.')
                        #
                        attrs.append(['xaRecoveryAuthAlias', xa_alias])
                    #
                    logger.info('Creating Datasource ' + ds_name)
                    ds_obj = AdminConfig.create('DataSource', provider_id, attrs) 
                    logger.info(ds_obj)
                    if jdbc_ds_type == 'oracle' :
                        logger.info('Creating Oracle Datasource ' + ds_name + ' Property Set.')
                        ds_url = search_property('was.jdbc.datasource.url_r_' + jdbc_ds_index + '_' + ds_index)
                        if ds_url == None or ds_url == '' :
                            raise Exception('Property URL is required for Oracle Datasource. It seems missing.')
                        #
                        setJ2eeResourceProperty(ds_obj, 'URL', 'java.lang.String', ds_url)
                    elif jdbc_ds_type == 'db2' :
                        logger.info('Creating DB2 Datasource ' + ds_name + ' Property Set.')
                        ds_dbname = search_property('was.jdbc.datasource.dbname_r_' + jdbc_ds_index + '_' + ds_index)
                        ds_srv = search_property('was.jdbc.datasource.servername_r_' + jdbc_ds_index + '_' + ds_index)
                        ds_prt = search_property('was.jdbc.datasource.port_r_' + jdbc_ds_index + '_' + ds_index)
                        ds_drvtyp = search_property('was.jdbc.datasource.drivertype_r_' + jdbc_ds_index + '_' + ds_index)
                        setJ2eeResourceProperty(ds_obj, 'databaseName', 'java.lang.String', ds_dbname)
                        setJ2eeResourceProperty(ds_obj, 'serverName',   'java.lang.String', ds_srv)
                        setJ2eeResourceProperty(ds_obj, 'portNumber',   'java.lang.Integer', ds_prt)
                        setJ2eeResourceProperty(ds_obj, 'driverType',   'java.lang.Integer', ds_drvtyp)
                    else :
                        raise Exception('Only Oracle and DB2 Implementation present curretly.')
                    #
                    logger.info('Datasource ' + ds_name + ' creation complete.')
                    set_connection_pool(ds_obj, jdbc_ds_index, ds_index)
                #
            #
            logger.info('Completed Datasource creation for Cluster ' + jdbc_var_scope)
        #
        logger.info('Exiting : create_datasource')
    except :
        logger.severe('Error creating Datasource. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in create_datasource methord.')
        sys.exit(1)
    #
#

def set_connection_pool(datasource, scope_index, datasource_index) :
    logger.info('Initialize : set_connection_pool. Arguments: ' + datasource + ' . ' + scope_index + ' . ' + datasource_index)
    try :
        con_pool_id = AdminConfig.showAttribute(datasource, 'connectionPool')
        if con_pool_id == '' :
            raise Exception('Connection pool id cannot be retrived for Datasource. Check Datasource configured correctly.')
        #
        ds_conn_timeout = search_property('was.jdbc.datasource.connectiontimeout_o_' + scope_index + '_' + datasource_index)
        if ds_conn_timeout == None or ds_conn_timeout == '' :
            ds_conn_timeout = 180
        #
        ds_conn_min = search_property('was.jdbc.datasource.minconnections_o_' + scope_index + '_' + datasource_index)
        if ds_conn_min == None or ds_conn_min == '' :
            ds_conn_min = 10
        #
        ds_conn_max = search_property('was.jdbc.datasource.maxconnections_o_' + scope_index + '_' + datasource_index)
        if ds_conn_max == None or ds_conn_max == '' :
            ds_conn_max = 40
        #
        attrs = []
        attrs.append( [ 'connectionTimeout', ds_conn_timeout ] )
        attrs.append( [ 'minConnections', ds_conn_min ] )
        attrs.append( [ 'maxConnections', ds_conn_max ] )
        AdminConfig.modify(con_pool_id, attrs)
        logger.info('Modified Datasource Connection pool.')
        logger.info('Exiting : set_connection_pool')
    except :
        logger.severe('Error setting connection pool for Datasource. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in set_connection_pool methord.')
        sys.exit(1)
    #
#

def getVirtualHostByName( virtualhostname ) :
    logger.info('Initialize : getVirtualHostByName')
    try :
        hosts = AdminConfig.list( 'VirtualHost' )
        hostlist = splitlines(hosts)
        for host_id in hostlist:
            name = AdminConfig.showAttribute( host_id, "name" )
            if name == virtualhostname:
                logger.info('Virtual Host found.')
                logger.info('Exiting : getVirtualHostByName')
                return host_id
            #
        #
        logger.info('Virtual Host not found.')
        logger.info('Exiting : getVirtualHostByName')
        return None
    except :
        logger.severe('Error finding Virtual Host. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in getVirtualHostByName methord.')
        sys.exit(1)
    #
#

def create_coregroup() :
    logger.info('Initialize : create_coregroup')
    try :
        coregroup_list = search_property_list('was.coregroup.name_r_')
        for cg in coregroup_list :
            status = AdminTask.doesCoreGroupExist('[-coreGroupName %s]' % (cg))
            if status == 'true' :
                logger.info('Core Group ' + cg + ' exist. Thus no action required.')
            elif status == 'false' :
                ret_value = AdminTask.createCoreGroup('[-coreGroupName %s]' % (cg))
                logger.info(ret_value)
                fstatus = AdminTask.doesCoreGroupExist('[-coreGroupName %s]' % (cg))
                if fstatus == 'true' :
                    logger.info('CoreGroup ' + cg + ' created successfully.')
                else :
                    raise Exception('Coregroup cannot be created.')
                #
            else :
                raise Exception('Coregroup ' + cg + ' Status returned is unknown.')
            #
        #
        logger.info('Core Group Configuration Completed.')
        logger.info('Exiting : create_coregroup')
    except :
        logger.severe('Error configuring Core Group. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in create_coregroup methord.')
        sys.exit(1)
    #
#

def delete_nodegroup() :
    logger.info('Initialize : delete_nodegroup')
    try :
        nodegroup_list = search_property_list('was.nodegroup.name_r_')
        for ng in nodegroup_list :
            ng_index = search_property_index('was.nodegroup.name_r_', ng)
            status = AdminNodeGroupManagement.checkIfNodeGroupExists(ng)
            if status == 'true' :
                logger.info('Node Group ' + ng + ' exist. It would be removed.')
                ng_member_list = AdminNodeGroupManagement.listNodeGroupMembers(ng)
                req_ng_mem_list = search_property_list('was.nodegroup.member_r_' + ng_index + '_')
                for ng_member in ng_member_list :
                    presc = check_element_in_list(req_ng_mem_list, ng_member)
                    if presc == 1 :
                        logger.info('Node Group ' + ng + ' member ' + ng_member + ' found in configuration and will not be removed.')
                    else :
                        logger.info('Node Group ' + ng + ' removing member ' + ng_member)
                        AdminNodeGroupManagement.deleteNodeGroupMember(ng, ng_member)
                    #
                #
            else :
                logger.info('Node Group ' + ng + ' doesnot exist.')
            #
        #
        logger.info('Exiting : delete_nodegroup')
    except :
        logger.severe('Error clearing Node Group. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in delete_nodegroup methord.')
        sys.exit(1)
    #
#

def create_nodegroup() :
    logger.info('Initialize : create_nodegroup')
    try :
        nodegroup_list = search_property_list('was.nodegroup.name_r_')
        for ng in nodegroup_list :
            ng_index = search_property_index('was.nodegroup.name_r_', ng)
            status = AdminNodeGroupManagement.checkIfNodeGroupExists(ng)
            if status == 'true' :
                logger.info('Node Group ' + ng + ' already exist.')
            else :
                logger.info('Creating Node Group ' + ng)
                ret_value = AdminNodeGroupManagement.createNodeGroup(ng)
                logger.info(ret_value)
            #
            logger.info('Adding member to Node Group.')
            node_list = search_property_list('was.nodegroup.member_r_' + ng_index + '_')
            ng_member_list = AdminNodeGroupManagement.listNodeGroupMembers(ng)
            for node in node_list :
                presc = check_element_in_list(ng_member_list, node)
                if presc == 1 :
                    logger.info('Node ' + node + ' already member of Node Group ' + ng + '. No action required.')
                else :
                    status = AdminNodeManagement.doesNodeExist(node)
                    if status == 'false' :
                        raise Exception('Node ' + node + ' doesnot exist. You need to create the node before it can be added to NodeGroup.')
                    #
                    logger.info('Node ' + node + ' will be added to the NodeGroup ' + ng)
                    ret_value = AdminTask.addNodeGroupMember(ng, ["-nodeName", node])
                    logger.info(ret_value)
                #
            #
            logger.info('Completed NodeGroup ' + ng + ' creation.')
        #
        logger.info('Exiting : create_nodegroup')
    except :
        logger.severe('Error configuring Node Group. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in create_nodegroup methord.')
        sys.exit(1)
    #
#

def create_application_cluster(clusterName) :
    logger.info('Initialize : create_application_cluster. Parameter: ' + clusterName)
    try :
        cluster_index = search_property_index('was.cluster.dynamic.name_r_', clusterName)
        membership = search_property('was.cluster.dynamic.membership_r_' + cluster_index)
        operationalmode = search_property('was.cluster.dynamic.operationalmode_r_' + cluster_index)
        mininstances = search_property('was.cluster.dynamic.mininstances_r_' + cluster_index)
        maxinstances = search_property('was.cluster.dynamic.maxinstances_r_' + cluster_index)
        serverinactivitytime = search_property('was.cluster.dynamic.serverinactivitytime_r_' + cluster_index)
        numverticalinstancese = search_property('was.cluster.dynamic.numverticalinstances_r_' + cluster_index)
        coregroup = search_property('was.cluster.dynamic.coregroup_r_' + cluster_index)
        templatename = search_property('was.cluster.dynamic.templatename_r_' + cluster_index)
        recreate = search_property('was.cluster.dynamic.forcerecreate_r_' + cluster_index)
        if check_valid_value(membership) or check_valid_value(membership) or check_valid_value(operationalmode) or check_valid_value(mininstances) or check_valid_value(maxinstances) or check_valid_value(serverinactivitytime) or check_valid_value(numverticalinstancese) or check_valid_value(coregroup) or check_valid_value(templatename) or check_valid_value(recreate) :
            raise Exception('Required property missing for Application Cluster ' + clusterName + ' property defined.')
        else :
            logger.info('All requireed inputs provided.')
            cluster_id = AdminConfig.getid('/DynamicCluster:' + clusterName)
            if cluster_id != '' :
                logger.info('Dynamic Cluster ' + clusterName + ' present in repository. Property will be reapplied.')
                AdminTask.setDynamicClusterMembershipPolicy(clusterName, '[-membershipPolicy "node_nodegroup = \'' + membership + '\'"]')
                AdminTask.setDynamicClusterOperationalMode(clusterName, '[-operationalMode ' + operationalmode + ']')
                AdminTask.setDynamicClusterMinInstances(clusterName, '[-minInstances ' + str(mininstances) + ']')
                AdminTask.setDynamicClusterMaxInstances(clusterName, '[-maxInstances ' + str(maxinstances) + ']')
                AdminTask.setDynamicClusterVerticalInstances(clusterName, '[-numVerticalInstances ' + str(numverticalinstancese) + ']')
                AdminConfig.modify(cluster_id, [['serverInactivityTime', serverinactivitytime]])
                global_cluster_list.append(cluster_id)
                localCluster = cluster_id
            else :
                logger.info('Dynamic Cluster ' + clusterName + ' not present in repository. It will be created.')
                localCluster = AdminTask.createDynamicCluster(clusterName, '[-membershipPolicy "node_nodegroup = \'' + membership + '\'" -dynamicClusterProperties "[[operationalMode ' + operationalmode + '][minInstances ' + str(mininstances) + '][maxInstances ' + str(maxinstances) + '][numVerticalInstances ' + str(numverticalinstancese) + '][serverInactivityTime ' + str(serverinactivitytime) + ']]" -clusterProperties "[[preferLocal false][createDomain false][templateName ' + templatename + '][coreGroup ' + coregroup + ']]"]')
                logger.info(localCluster)
                global_cluster_list.append(localCluster)
                createapplicationmapping(clusterName)
            #
            update_servertemplete_for_server(localCluster, cluster_index)
            configure_app_jvm(localCluster, cluster_index)
        #
        logger.info('Exiting : create_application_cluster')
    except :
        logger.severe('Error creating Application Cluster. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in create_application_cluster methord.')
        sys.exit(1)
    #
#

def update_servertemplete_for_server(cluster_id, cluster_index) :
    logger.info('Initialize : update_servertemplete_for_server. Parameter: ' + cluster_id + ' . ' + cluster_index)
    try :
        server_id = AdminConfig.list('Server', cluster_id)
        if len(server_id) == 0 :
            raise Exception('Cannot get server templete configuration id for Cluster ' + cluster_id)
        #
        logger.info('Appling JVM configurations.')
        genericargument = search_property('was.cluster.dynamic.member.jvm.genericargument_o_' + cluster_index)
        minheap = search_property('was.cluster.dynamic.member.jvm.minheap_o_' + cluster_index)
        maxheap = search_property('was.cluster.dynamic.member.jvm.maxheap_o_' + cluster_index)
        verboseclassloading = search_property('was.cluster.dynamic.member.jvm.verboseclassloading_o_' + cluster_index)
        verbosegc = search_property('was.cluster.dynamic.member.jvm.verbosegc_o_' + cluster_index)
        disablejit = search_property('was.cluster.dynamic.member.jvm.disablejit_o_' + cluster_index)
        if minheap == None or minheap == '' :
            minheap = 512
        if maxheap == None or maxheap == '' :
            maxheap = 1024
        if verboseclassloading == None or verboseclassloading == '' :
            verboseclassloading = 'false'
        if verbosegc == None or verbosegc == '' :
            verbosegc = 'true'
        if disablejit == None or disablejit == '' :
            disablejit = 'false'
        if genericargument == None or genericargument == '' :
            genericargument = '-Xverbosegclog:${SERVER_LOG_ROOT}/gc.log,10,10000'
        else :
            genericargument = '-Xverbosegclog:${SERVER_LOG_ROOT}/gc.log,10,10000 ' + genericargument
        #
        AdminTask.setJVMProperties(server_id, '[-verboseModeClass ' + verboseclassloading + ' -verboseModeGarbageCollection ' + verbosegc + ' -verboseModeJNI false -initialHeapSize ' + str(minheap) + ' -maximumHeapSize ' + str(maxheap) + ' -runHProf false -hprofArguments -debugMode false -debugArgs "-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=7777" -executableJarFileName -genericJvmArguments "' + genericargument + '" -disableJIT ' + disablejit + ']')
        logger.info('Done configuring JVM.')
        logger.info('Appling Environment Entry.')
        prop_list = splitlines(AdminConfig.list('Property', server_id))
        entry_list = search_property_list('was.cluster.dynamic.member.jvm.environmententry.name_r_' + cluster_index + '_')
        for en_nm in entry_list :
            en_ind = search_property_index('was.cluster.dynamic.member.jvm.environmententry.name_r_' + cluster_index + '_', en_nm)
            en_val = search_property('was.cluster.dynamic.member.jvm.environmententry.value_r_' + cluster_index + '_' + en_ind)
            prop_id = check_config_in_configid_list(prop_list, en_nm)
            jvm_def = AdminConfig.list('JavaProcessDef', server_id)
            if prop_id == '' :
                logger.info('Setting Name ' + en_nm + ' with value ' + en_val + '.')
                attrs = []
                attrs.append( [ 'name', en_nm ] )
                attrs.append( [ 'value', en_val ] )
                ret_value = AdminConfig.create('Property', jvm_def, attrs)
            else :
                logger.info('Property present thus setting value ' + en_val + ' for ' + en_nm)
                ret_value = AdminConfig.modify(prop_id, [['value', en_val]])
            #
            logger.info(ret_value)
        #
        logger.info('Done appling Environment Entry.')
        logger.info('Appling PMI Setting.')
        pmi_status = search_property('was.cluster.dynamic.member.monitoring.status_r_' + cluster_index)
        pmi_level = search_property('was.cluster.dynamic.member.monitoring.pmilevel_o_' + cluster_index)
        pmi_couter = search_property('was.cluster.dynamic.member.monitoring.seqcounter_o_' + cluster_index)
        if pmi_status == None or pmi_status == '' :
            logger.info('No PMI Setting change requested. Default setting prevails.')
        else :
            if pmi_level == None or pmi_level == '' :
                pmi_level = 'basic'
            if pmi_couter == None or pmi_couter == '' :
                pmi_couter = 'false'
            #
            pmi_id = AdminConfig.list('PMIService', server_id)
            if len(pmi_id) == 0 :
                raise Exception('PMI Configuration cannot be retrived for Server ' + server_id)
            #
            AdminConfig.modify(pmi_id, '[[synchronizedUpdate ' + pmi_couter + '] [enable ' + pmi_status + '] [statisticSet ' + pmi_level + ']]')
            logger.info('Done configuring PMI Setting.')
        #
        logger.info('Exiting : update_servertemplete_for_server')
    except :
        logger.severe('Error updating Cluster server templete. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in update_servertemplete_for_server methord.')
        sys.exit(1)
    #
#

def configure_app_jvm(cluster_id, cluster_index) :
    logger.info('Initialize : configure_app_jvm. Parameter: ' + cluster_id + ' . ' + cluster_index)
    try :
        server_id = AdminConfig.list('Server', cluster_id)
        if len(server_id) == 0 :
            raise Exception('Cannot get server templete configuration id for Cluster ' + cluster_id)
        #
        logger.info('Thread Pool Configuration.')
        thread_pool_list = search_property_list('was.cluster.dynamic.member.app.threadpool.name_o_' + cluster_index + '_')
        for tp in thread_pool_list :
            logger.info('Thread Pool: ' + tp)
            def_cofig = global_threadpool_map.get(tp)
            if def_cofig == None :
                raise Exception('Thread Pool Name ' + tp + ' not a standard pool name. Only Standard Thread Pool can be configured.')
            #
            tp_index = search_property_index('was.cluster.dynamic.member.app.threadpool.name_o_' + cluster_index + '_', tp)
            min = search_property('was.cluster.dynamic.member.app.threadpool.minsize_o_' + cluster_index + '_' + tp_index)
            max = search_property('was.cluster.dynamic.member.app.threadpool.maxsize_o_' + cluster_index + '_' + tp_index)
            inacttime = search_property('was.cluster.dynamic.member.app.threadpool.inactivitytimeout_o_' + cluster_index + '_' + tp_index)
            isgrow = search_property('was.cluster.dynamic.member.app.threadpool.isgrowable_o_' + cluster_index + '_' + tp_index)
            (min_d, max_d, inacttime_d, isgrow_d) = def_cofig.split('@@@')
            if min == None or min == '' :
                min = min_d
            if max == None or max == '' :
                max = max_d
            if inacttime == None or inacttime == '' :
                inacttime = inacttime_d
            if isgrow  == None or isgrow == '' :
                isgrow = isgrow_d
            #
            tp_id_list = splitlines(AdminConfig.list('ThreadPool', server_id))
            tp_id = check_config_in_configid_list(tp_id_list, tp)
            ret_value = AdminConfig.modify(tp_id, '[[maximumSize "' + str(max) + '"] [name "' + tp + '"] [minimumSize "' + str(min) + '"] [inactivityTimeout "' + str(inacttime) + '"] [description ""] [isGrowable "' + isgrow + '"]]')
            logger.info(ret_value)
        #
        logger.info('Completed Thread Pool Configuration.')
        logger.info('Transaction  Configuration.')
        trans_service_id = AdminConfig.list('TransactionService', server_id)
        server_index_id = AdminConfig.list('ServerIndex', cluster_id)
        server_entry_id = splitlist(AdminConfig.showAttribute(server_index_id, 'serverEntries'))[0]
        if len(trans_service_id) == 0 or len(server_index_id) == 0 or len(server_entry_id) == 0 :
            raise Exception('Configuration id cannot be pulled for Transaction Configurations.')
        #
        lifetimetimeout = search_property('was.cluster.dynamic.member.app.transaction.lifetimetimeout_o_' + cluster_index)
        clientinactivitytimeout = search_property('was.cluster.dynamic.member.app.transaction.clientinactivitytimeout_o_' + cluster_index)
        propogatedorbmttranlifetimetimeout = search_property('was.cluster.dynamic.member.app.transaction.propogatedorbmttranlifetimetimeout_o_' + cluster_index)
        logdirectory = search_property('was.cluster.dynamic.member.app.transaction.logdirectory_o_' + cluster_index)
        if lifetimetimeout == None or lifetimetimeout == '' :
            lifetimetimeout = 120
        if clientinactivitytimeout == None or clientinactivitytimeout == '' :
            clientinactivitytimeout = 60
        if propogatedorbmttranlifetimetimeout == None or propogatedorbmttranlifetimetimeout == '' :
            propogatedorbmttranlifetimetimeout = 300
        if logdirectory == None or logdirectory == '' :
            logdirectory = ''
        #
        ret_value = AdminConfig.create('RecoveryLog', server_entry_id, '[[transactionLogDirectory "' + logdirectory + '"]]')
        logger.info(ret_value)
        ret_value = AdminConfig.modify(trans_service_id, '[[totalTranLifetimeTimeout "' + str(lifetimetimeout) + '"] [httpProxyPrefix ""] [LPSHeuristicCompletion "ROLLBACK"] [httpsProxyPrefix ""] [wstxURLPrefixSpecified "false"] [enableFileLocking "true"] [enable "true"] [transactionLogDirectory "' + logdirectory + '"] [enableProtocolSecurity "true"] [heuristicRetryWait "0"] [propogatedOrBMTTranLifetimeTimeout "' + str(propogatedorbmttranlifetimetimeout) + '"] [enableLoggingForHeuristicReporting "false"] [asyncResponseTimeout "30"] [clientInactivityTimeout "' + str(clientinactivitytimeout) + '"] [heuristicRetryLimit "0"] [acceptHeuristicHazard "false"]]')
        logger.info(ret_value)
        logger.info('Completed Transaction  Configuration.')
        logger.info('Session Configuration')
        sesinvtout = search_property('was.cluster.dynamic.member.app.webcontainer.sessioninvalidationtout_o_' + cluster_index)
        alwoverflw = search_property('was.cluster.dynamic.member.app.webcontainer.allowsessionoverflow_o_' + cluster_index)
        inmemses = search_property('was.cluster.dynamic.member.app.webcontainer.inmemorysession_o_' + cluster_index)
        if sesinvtout == None or sesinvtout == '' :
            sesinvtout = 10
        if alwoverflw == None or alwoverflw == '' :
            alwoverflw = 'true'
        if inmemses == None or inmemses == '' :
            inmemses = 1000
        #
        sess_mgmt_id = AdminConfig.list('TuningParams', server_id)
        if len(sess_mgmt_id)  == 0 :
            raise Exception('Configuration id cannot be pulled for Session  Configurations.')
        #
        ret_value = AdminConfig.modify(sess_mgmt_id, '[[allowOverflow "' + alwoverflw + '"] [invalidationTimeout "' + str(sesinvtout) + '"] [maxInMemorySessionCount "' + str(inmemses) + '"]]')
        logger.info(ret_value)
        logger.info('Completed Session Configuration')
        logger.info('Session Persistence Configuration')
        ses_persistent_mode = search_property('was.cluster.dynamic.member.app.session.webcontainersessionpersistencemode_r_' + cluster_index)
        if ses_persistent_mode == None or ses_persistent_mode == '' :
            logger.info('No Session Persistence configuration setting detected.')
        elif ses_persistent_mode == 'DATA_REPLICATION' :
            logger.info('Configuration requested for DATA_REPLICATION mode.')
            sesper_repdom = search_property('was.cluster.dynamic.member.app.session.installreplicationdomain_r_' + cluster_index)
            sesper_repmode = search_property('was.cluster.dynamic.member.app.session.webcontainerdatareplicationmode_r_' + cluster_index)
            sesper_repdom_id = check_config_in_configid_list(global_domain_list, sesper_repdom)
            if len(sesper_repdom_id) == 0 or sesper_repmode == None or sesper_repmode == '' :
                raise Exception('Replication Domain might not be present or you have not provided required property Replication mode.')
            #
            webcontainer = AdminConfig.list('WebContainer', server_id)
            sesmgr = splitlines(AdminConfig.list('SessionManager', webcontainer))[0]
            drssettingsobjects = splitlines(AdminConfig.list('DRSSettings', sesmgr))
            if len(drssettingsobjects) == 0 :
                AdminConfig.create('DRSSettings', sesmgr, [['messageBrokerDomainName', sesper_repdom]])
                drssettingsobjects = splitlines(AdminConfig.list('DRSSettings', sesmgr))
            #
            drs = drssettingsobjects[0]
            ret_value = AdminConfig.modify(sesmgr, '[[sessionPersistenceMode "DATA_REPLICATION"]]')
            logger.info(ret_value)
            ret_value = AdminConfig.modify(drs, '[[messageBrokerDomainName "' + sesper_repdom + '"] [dataReplicationMode "' + sesper_repmode + '"]]')
            logger.info(ret_value)
        elif ses_persistent_mode == 'DATABASE' :
            logger.info('Not currently implemented DATABASE Session Persistence.')
        else :
            raise Exception('Replication Domain type unknown.')
        #
        logger.info('Completed Session Persistence Configuration')
        logger.info('Exiting : configure_app_jvmr')
    except :
        logger.severe('Error updating Cluster server templete Thread Pool. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in configure_app_jvm methord.')
        sys.exit(1)
    #
#

def stopenvironment() :
    logger.info('Initialize : stopenvironment')
    cluster_list = []
    try :
        logger.info('Searching for defined CLUSTER.')
        cluster_list = search_property_list('was.cluster.dynamic.name_r_')
        if len(cluster_list) < 1 :
            logger.info('No CLUSTER defination found.')
        else :
            for cluster_name in cluster_list :
                stop_cluster(cluster_name)
            #
            logger.info('Done stopping all CLUSTER.')
        #
        logger.info('Exiting : stopenvironment')
    except :
        logger.severe('Error stopping CLUSTER. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in stopenvironment methord.')
        sys.exit(1)
    #
#

def startenvironment() :
    logger.info('Initialize : startenvironment')
    cluster_list = []
    try :
        logger.info('Searching for defined CLUSTER.')
        cluster_list = search_property_list('was.cluster.dynamic.name_r_')
        if len(cluster_list) < 1 :
            logger.info('No CLUSTER defination found.')
        else :
            for cluster_name in cluster_list :
                start_cluster(cluster_name)
            #
            logger.info('Done starting all CLUSTER.')
        #
        logger.info('Exiting : startenvironment')
    except :
        logger.severe('Error starting CLUSTER. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in startenvironment methord.')
        sys.exit(1)
    #
#

def deletejdbcresource() :
    logger.info('Initialize : deletejdbcresource')
    try :
        cluster_list = search_property_list('was.cluster.dynamic.name_r_')
        if len(cluster_list) < 1 :
            logger.info('No CLUSTER defination found.')
        else :
            logger.info('Clearing all Auth Alias relivent.')
            auth_alias_list = search_property_list('was.jdbc.auth.name_r_')
            resource_list = splitlines(AdminConfig.list('JAASAuthData'))
            for autItem in resource_list :
                for auth_alias in auth_alias_list :
                    auth_alias_name = AdminConfig.showAttribute(autItem, "alias")
                    if auth_alias == auth_alias_name :
                        logger.info('Found J2C Auth Alias: ' + auth_alias)
                        AdminConfig.remove(autItem)
                    #
                #
            #
            logger.info('Done deleting all J2C Auth Alias.')
            for cluster_name in cluster_list :
                cluster_index = search_property_index('was.cluster.dynamic.name_r_', cluster_name)
                cluster_type = search_property('was.cluster.dynamic.type_r_' + str(cluster_index))
                if cluster_type == 'app' :
                    logger.info('Found Application cluster ' + cluster_name + ' JDBC resource removal will be initiated for the cluster.')
                    clsuter_id = AdminConfig.getid( '/Cell:%s/ServerCluster:%s/' % (cell, cluster_name))
                    if len(clsuter_id) == 0 :
                        logger.info('Cluster ' + cluster_name + ' does not exist. Thus not action will be performed.')
                        logger.info('Exiting : deletejdbcresource')
                        return
                    #
                    resource_list = AdminConfig.list('DataSource', clsuter_id)
                    for resource_id in splitlines(resource_list) :
                        resource_name = AdminConfig.showAttribute(resource_id, 'name')
                        logger.info('Deleting Datasource: ' + resource_name)
                        AdminTask.deleteDatasource(resource_id)
                    #
                    logger.info('Done deleting all Datasource for cluster ' + cluster_name)
                    resource_list = AdminConfig.list('JDBCProvider', clsuter_id)
                    for resource_id in splitlines(resource_list) :
                        if resource_id.find('builtin_jdbcprovider') == -1 :
                            resource_name = AdminConfig.showAttribute(resource_id, 'name')
                            logger.info('Deleting Datasource Provider: ' + resource_name)
                            AdminTask.deleteJDBCProvider(resource_id)
                        #
                    #
                    logger.info('Done deleting all Datasource Provider for cluster ' + cluster_name)
                    resource_list = AdminConfig.list('VariableSubstitutionEntry', clsuter_id)
                    for resource_id in splitlines(resource_list) :
                        resource_name = AdminConfig.showAttribute(resource_id, 'symbolicName')
                        if resource_name == 'ORACLE_JDBC_DRIVER_PATH' :
                            logger.info('Found Driver Path:' + resource_name)
                            AdminConfig.remove(resource_id)
                    #
                    logger.info('Done deleting all Datasource Driver Path Variable for cluster ' + cluster_name)
                    logger.info('Deleted all JDBC resource for cluster ' + cluster_name)
            #
            logger.info('Completed deleting all JDBC resource.')
        #
        logger.info('Exiting : deletejdbcresource')
    except :
        logger.severe('Error cleaning jdbcresource. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in deletejdbcresource methord.')
        sys.exit(1)
    #
#

def createjdbcresource() :
    logger.info('Initialize : createjdbcresource')
    try :
        create_auth_alias()
        create_jdbc_variable()
        create_datasource_provider()
        create_datasource()
        logger.info('Exiting : createjdbcresource')
    except :
        logger.severe('Error creating JDBC resources.  Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in createjdbcresource methord.')
        sys.exit(1)
    #
#

def deletevhost() :
    logger.info('Initialize : deletevhost')
    try :
        vhost_list = search_property_list('was.vhost.name_r_')
        if len(vhost_list) < 1 :
            logger.info('No Virtual Host to delete.')
        else :
            for vhost in vhost_list :
                logger.info('Deleting Virtual Host: ' + vhost)
                host_id = getVirtualHostByName( vhost )
                if host_id == None:
                    logger.info('Virtual Host not present. No action taken!')
                else :
                    #ret_value = AdminConfig.remove( host_id )
                    aliases = AdminConfig.showAttribute( host_id, 'aliases' )
                    if aliases != None :
                        logger.info('No alias present to remove for Virtual Host ' + vhost)
                    else :
                        logger.info('Deleting alias for Virtual Host ' + vhost)
                        aliases = aliases[1:-1].split( ' ' )
                        for alias in aliases:
                            if alias != None and alias != '':
                                ret_value = AdminConfig.remove(alias)
                                logger.info(ret_value)
                            #
                        #
                    #
                #
            #
        #
	logger.info('Exiting : deletevhost')
    except :
        logger.severe('Error deleting Virtual Host. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in deletevhost methord.')
        sys.exit(1)
    #
#
                
def createvhost() :
    logger.info('Initialize : createvhost')
    global cell_id
    try :
        vhost_list = search_property_list('was.vhost.name_r_')
        if len(vhost_list) < 1 :
            logger.info('No Virtual Host to delete.')
	else :
            for vhost in vhost_list :		
	        vhost_id = AdminConfig.getid( '/Cell:%s/VirtualHost:%s/' % (cell, vhost))
		if len(vhost_id) == 0 :
        	    logger.info('Virtual Host ' + vhost + 'not present. Creating the same.')	
		    ret_value = AdminConfig.create('VirtualHost', cell_id, [['name', vhost]])
                    global_vhost_list.append(ret_value)
		    logger.info(ret_value)
                else :
                    global_vhost_list.append(vhost_id)
		#
                virtual_host_list = search_property_list('was.vhost.name_r_')
                host_id = check_config_in_configid_list(global_vhost_list, vhost)
                vhost_index = search_property_index('was.vhost.name_r_', vhost)
                vhost_host_list = search_property_list('was.vhost.host_r_' + vhost_index + '_')
                for host_alias in vhost_host_list :
                    logger.info('Staring adding Host Alias for host ' + host_alias)
                    host_alias_index = search_property_index('was.vhost.host_r_' + vhost_index + '_', host_alias)
                    port_alias_list = search_property_list('was.vhost.port_r_' + vhost_index + '_' + host_alias_index + '_')
                    for port_alias in port_alias_list :
                        if host_alias == None or host_alias == '' or port_alias == None or port_alias == '' :
                            raise Exception('Required property missing for VHost ' + vhost)
                        #
                        logger.info('Adding Host ' + host_alias + ' and Port ' + port_alias + ' Alias to Virtual Host ' + vhost)
                        attrs = [['hostname', host_alias], ['port', port_alias]]
                        ret_value = AdminConfig.create('HostAlias', host_id, attrs)
                        logger.info(ret_value)
                    #
                    logger.info('Completed adding Host Alias for host ' + host_alias)
                #
        #
	logger.info('Exiting : createvhost')
    except :
        logger.severe('Error create Virtual Host. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in createvhost methord.')
        sys.exit(1)
    #
#

def update_odr_configuration(cluster_id, cluster_index) :
    logger.info('Initialize : update_odr_configuration')
    try :
        server_id = AdminConfig.list('Server', cluster_id)
        if len(server_id) == 0 :
            raise Exception('Cannot get server templete configuration id for Cluster ' + cluster_id)
        #
        trustproxy = search_property('was.cluster.dynamic.odrtrustedproxy_r_' + cluster_index)
        if trustproxy != None and trustproxy != '' :
            logger.info('Setting Trusted proxy for ODR. Setting: ' + trustproxy)
            proxy_id = AdminConfig.list('ProxySettings', server_id)
            if proxy_id == '' :
                logger.info('WARNING: Cannot find proxy configuration. Could not set property.')
            else :
                ret_value = AdminConfig.modify(proxy_id, [['trustedIntermediaryAddresses', trustproxy]])
                logger.info(ret_value)
                logger.info('Done setting Trusted Proxy Configuration.')
            #
        #
        logger.info('Setting all Rewrite Rule.')
        prox_id = AdminConfig.list('ProxySettings', server_id)
        if proxy_id == '' :
            logger.info('WARNING: Cannot find proxy configuration. Could not set property.')
        else :
            rw_policy_id = AdminConfig.showAttribute(proxy_id, 'rewritingPolicy')
            if rw_policy_id == None :
                rw_policy_id = AdminConfig.create('RewritingPolicy', proxy_id, "")
            #
            if rw_policy_id == '' :
                logger.info('WARNING: Cannot find Rewrite Policy Id. Could not set property.')
            else :
                odrrewrite_list = search_property_list('was.cluster.dynamic.odrrewrite_fromaddress_r_' + cluster_index + '_')
                for rw_from in odrrewrite_list :
                    logger.info('Setting Overwrite Rule for From Address: ' + rw_from)
                    rw_index = search_property_index('was.cluster.dynamic.odrrewrite_fromaddress_r_' + cluster_index + '_', rw_from)
                    rw_to = search_property('was.cluster.dynamic.odrrewrite_toaddress_r_' + cluster_index + '_' + rw_index)
                    if check_valid_value(rw_from) or check_valid_value(rw_to) :
                        raise Exception('Required property missing, for Rewrite Rule to be set both From and To address should be set.')
                    #
                    logger.info('From:'+rw_from+'---To:'+rw_to+'---ID:'+str(rw_policy_id))
                    toadd = ['toURLPattern', rw_to]
                    fmadd = ['fromURLPattern', rw_from]
                    propl = ['properties', []]
                    attrs = [fmadd, propl, toadd]
                    logger.info('-----'+str(attrs)+'------')
                    ret_value = AdminConfig.create('RewritingRule', rw_policy_id, attrs)
                    logger.info(ret_value)
                #
            #
        #
        logger.info('Done setting all Rewrite Rule.')
        logger.info('Exiting : update_odr_configuration')
    except :
        logger.severe('Error configuring ODR Cluster. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in update_odr_configuration methord.')
        sys.exit(1)
    #
#

def create_odr_cluster(clusterName) :
    logger.info('Initialize : create_odr_cluster')
    global cell_id
    try :
        cluster_index = search_property_index('was.cluster.dynamic.name_r_', clusterName)
        membership = search_property('was.cluster.dynamic.membership_r_' + cluster_index)
        operationalmode = search_property('was.cluster.dynamic.operationalmode_r_' + cluster_index)
        mininstances = search_property('was.cluster.dynamic.mininstances_r_' + cluster_index)
        maxinstances = search_property('was.cluster.dynamic.maxinstances_r_' + cluster_index)
        serverinactivitytime = search_property('was.cluster.dynamic.serverinactivitytime_r_' + cluster_index)
        numverticalinstancese = search_property('was.cluster.dynamic.numverticalinstances_r_' + cluster_index)
        coregroup = search_property('was.cluster.dynamic.coregroup_r_' + cluster_index)
        templatename = search_property('was.cluster.dynamic.templatename_r_' + cluster_index)
        recreate = search_property('was.cluster.dynamic.forcerecreate_r_' + cluster_index)
        if check_valid_value(membership) or check_valid_value(operationalmode) or check_valid_value(mininstances) or check_valid_value(maxinstances) or check_valid_value(serverinactivitytime) or check_valid_value(numverticalinstancese) or check_valid_value(coregroup) or check_valid_value(templatename) or check_valid_value(recreate) :
            raise Exception('Required property missing for Application Cluster ' + clusterName + ' property defined.')
        #
        logger.info('All requireed inputs provided.')
        cluster_id = AdminConfig.getid('/DynamicCluster:' + clusterName)
        if cluster_id != '' :
            logger.info('Dynamic Cluster ' + clusterName + ' present in repository. Property will be reapplied.')
            logger.info('Dynamic Cluster ' + clusterName + ' present in repository. Property will be reapplied.')
            AdminTask.setDynamicClusterMembershipPolicy(clusterName, '[-membershipPolicy "node_nodegroup = \'' + membership + '\'"]')
            AdminTask.setDynamicClusterOperationalMode(clusterName, '[-operationalMode ' + operationalmode + ']')
            AdminTask.setDynamicClusterMinInstances(clusterName, '[-minInstances ' + str(mininstances) + ']')
            AdminTask.setDynamicClusterMaxInstances(clusterName, '[-maxInstances ' + str(maxinstances) + ']')
            AdminTask.setDynamicClusterVerticalInstances(clusterName, '[-numVerticalInstances ' + str(numverticalinstancese) + ']')
            AdminConfig.modify(cluster_id, [['serverInactivityTime', serverinactivitytime]])
            global_cluster_list.append(cluster_id)
            localCluster = cluster_id
        else :
            logger.info('Dynamic Cluster ' + clusterName + ' not present in repository. It will be created.')
            localCluster = AdminTask.createODRDynamicCluster(clusterName, '[-membershipPolicy "node_nodegroup = \'' + membership + '\' AND node_property$com.ibm.websphere.wxdopProductShortName = \'WXDOP\'" -dynamicClusterProperties "[[operationalMode ' + operationalmode + '][minInstances ' + str(mininstances) + '][maxInstances ' + str(maxinstances) + '][numVerticalInstances ' + str(numverticalinstancese) + '][serverInactivityTime ' + str(serverinactivitytime) + ']]" -clusterProperties "[[templateName ' + templatename + '][coreGroup ' + coregroup + ']]"]')
            logger.info(localCluster)
            global_cluster_list.append(localCluster)
            logger.info('Setting APC.predictor property.')
            properties = splitlist(AdminConfig.showAttribute(cell_id, "properties"))
            propertyAllReadySet = 0
            for property in properties :
                propName = AdminConfig.showAttribute(property,"name")
                if (propName=="APC.predictor"):
                    logger.info('Property was already set')
                    propertyAllReadySet = 1
                #
            #
            if propertyAllReadySet == 0 :
                logger.info('Property was not set, setting the same.')
                AdminConfig.create('Property', cell_id, '[[name "APC.predictor"] [value "CPU"]]')
            #
        #
        update_servertemplete_for_server(localCluster, cluster_index)
        update_odr_configuration(localCluster, cluster_index)
        logger.info('Exiting : create_odr_cluster')
    except :
        logger.severe('Error create ODR Cluster.  Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in create_odr_cluster methord.')
        sys.exit(1)
    #
#

def createclusters() :
    logger.info('Initialize : createclusters')
    try :
        cluster_list = search_property_list('was.cluster.dynamic.name_r_')
        for cluster_name in cluster_list :
            cluster_index = search_property_index('was.cluster.dynamic.name_r_', cluster_name)
            cluster_type = search_property('was.cluster.dynamic.type_r_' + cluster_index)
            if cluster_type == 'app' :
                logger.info('Found Application Cluster ' + cluster_name + ' defination. Initiation of Application Cluster.')
                create_application_cluster(cluster_name)
            elif cluster_type == 'odr' :
                logger.info('Found ODR Cluster ' + cluster_name + ' defination. Initiation of ODR Cluster creation.')
                create_odr_cluster(cluster_name)
            else :
                raise Exception('Cluster ' + cluster_name + ' type defined is not supported.')
            #
        #
        logger.info('Completed creation of all Clusters.')
        logger.info('Exiting : createclusters')
    except :
        logger.severe('Error creating Cluster. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in createclusters methord.')
        sys.exit(1)
    #
#

def deleteclusters() :
    logger.info('Initialize : deleteclusters.')
    global mod_mapping
    try :
        cluster_list = search_property_list('was.cluster.dynamic.name_r_')
        for cluster_name in cluster_list :
            dcid = AdminConfig.getid("/DynamicCluster:" + cluster_name)
            cluster_index = search_property_index('was.cluster.dynamic.name_r_', cluster_name)
            recreate = search_property('was.cluster.dynamic.forcerecreate_r_' + cluster_index)
            if dcid == '' :
                logger.info('Cluster ' + cluster_name + ' not present.')
            elif recreate == 'true' :
                logger.info('Remembering Application binding if any.')
                noteapplicationmapping(cluster_name)
                logger.info('Deleting Cluster ' + cluster_name)
                ret_value = AdminTask.deleteDynamicCluster(cluster_name)
                logger.info(ret_value)
            else :
                logger.info('Cluster ' + cluster_name + ' present but will not be deleted.')
            #
        #
        logger.info('Exiting : deleteclusters')
    except :
        logger.severe('Error deleting Cluster. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in deleteclusters methord.')
        sys.exit(1)
    #
#

def createreplicationdomain() :
    logger.info('Initialize : createreplicationdomain')
    global cell_id
    try :
        repl_dom_list = search_property_list('was.cluster.dynamic.member.app.session.installreplicationdomain_r_')
        for repl_dom in repl_dom_list :
            logger.info('Creating Domain ' + repl_dom)
            repl_dom_ind = search_property_index('was.cluster.dynamic.member.app.session.installreplicationdomain_r_', repl_dom)
            repldom_repl_c = search_property('was.cluster.dynamic.member.app.session.replnumberofreplicas_o_' + repl_dom_ind)
            domain = AdminConfig.create('DataReplicationDomain', cell_id, [['name', repl_dom]])
            global_domain_list.append(domain)
            logger.info(domain)
            domainsettings = AdminConfig.create('DataReplication', domain, [['numberOfReplicas', repldom_repl_c]])
            logger.info(domainsettings)
        #
        logger.info('Exiting : createreplicationdomain')
    except :
        logger.severe('Error creating Replication Domain. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in createreplicationdomain methord.')
        sys.exit(1)
    #
#

def deletereplicationdomain() :
    logger.info('Initialize : deletereplicationdomain')
    try :
        repl_dom_list = search_property_list('was.cluster.dynamic.member.app.session.installreplicationdomain_r_')
        repl_dom_config_list = splitlines(AdminConfig.list('DataReplicationDomain'))
        for repl_dom in repl_dom_list :
            repl_dom_id = check_config_in_configid_list(repl_dom_config_list, repl_dom)
            if len(repl_dom_id) == 0 :
                logger.info('Replication Domain ' + repl_dom + ' not present in configuration.')
            else :
                AdminConfig.remove(repl_dom_id)
            #
        #
        logger.info('All Replication Domain removed.')
        logger.info('Exiting : deletereplicationdomain')
    except :
        logger.severe('Error deleting Replication Domain. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in deletereplicationdomain methord.')
        sys.exit(1)
    #
#

def noteapplicationmapping(cluster_name) :
    logger.info('Initialize : noteapplicationmapping. Parameter: ' + cluster_name)
    global mod_mapping
    try :
        cluster_index = search_property_index('was.cluster.dynamic.name_r_', cluster_name)
        logger.info('Tracking application for Cluster ' + cluster_name)
        app_list = search_property_list('was.cluster.dynamic.application.name_r_' + cluster_index + '_')
        for app in app_list :
            app_module_list = AdminApp.listModules(app, '-server').splitlines()
            attrs = []
            for app_mod in app_module_list :
                ( name, module, target ) = app_mod.split( '#' )
                if target.find(cluster_name) == -1 :
                    raise Exception('Application Module ' + name + ' not mapped to cluster ' + cluster_name)
                #
                attrs.append( [module, target] )
            #
            mod_mapping[app] = attrs
        #
        logger.info('Exiting : noteapplicationmapping')
    except :
        logger.severe('Error remembering Application Mapping. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in noteapplicationmapping methord.')
        sys.exit(1)
    #
#

def createapplicationmapping(cluster_name) :
    logger.info('Initialize : createapplicationmapping. Parameter: ' + cluster_name)
    global mod_mapping
    try :
        cluster_index = search_property_index('was.cluster.dynamic.name_r_', cluster_name)
        logger.info('Mapping application for Cluster ' + cluster_name)
        app_list = search_property_list('was.cluster.dynamic.application.name_r_' + cluster_index + '_')
        for app in app_list :
            module_config = mod_mapping.get(app)
            if module_config == None :
                logger.info('No module mapping for application ' + app)
            else :
                logger.info('Appling module mapping for application ' + app)
                str_map = '['
                for mod in module_config :
                    str_map = str_map + '[' + mod[0].split('+')[0] + ' ' + mod[0].split('+')[0] + ',' + mod[0].split('+')[1] + ' ' +  mod[1] + ']'
                #
                str_map = str_map + ']'
                ret_value = AdminApp.edit(app, '[ -MapModulesToServers ' + str_map + ']')
                logger.info(ret_value)
            #
        #
        logger.info('Exiting : createapplicationmapping')
    except :
        logger.severe('Error configure Application Mapping. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in createapplicationmapping methord.')
        sys.exit(1)
    #
#

def deletedefaultmessaging() :
    logger.info('Initialize : deletedefaultmessaging')
    try :
        sib_list = search_property_list('was.sib.name_r_')
        bus_in_cell = splitlines(AdminTask.listSIBuses())
        for sib in sib_list :
            config_id = check_config_in_configid_list(bus_in_cell, sib)
            if len(config_id) == 0 :
                logger.info('Bus ' + sib + ' not defined in cell. Thus not action.')
            else :
                sib_ind = search_property_index('was.sib.name_r_', sib)
                sib_frcrecreate = search_property('was.sib.forcerecreate_r_' + sib_ind)
                if sib_frcrecreate == 'true' :
                    logger.info('Configuration detected for Bus ' + sib + ' it will be deleted.')
                    ret_value = AdminTask.deleteSIBus('[-bus ' + sib + ']')
                    logger.info(ret_value)
                else :
                    logger.info('SIB ' + sib + ' will not be deleted.')
                #
            #
        #
        logger.info('Exiting : deletedefaultmessaging')
    except :
        logger.severe('Error default messaging cleanup. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in deleteenvironment methord.')
        sys.exit(1)
    #
#

def createdefaultmessaging() :
    logger.info('Initialize : createdefaultmessaging')
    try :
        sib_list = search_property_list('was.sib.name_r_')
        bus_in_cell = splitlines(AdminTask.listSIBuses())
        for sib in sib_list :
            sib_ind = search_property_index('was.sib.name_r_', sib)
            sib_sec = search_property('was.sib.security_r_' + sib_ind)
            sib_mem = search_property('was.sib.me.name_r_' + sib_ind)
            sib_log_dir = search_property('was.sib.me.filestore.logdirectory_r_' + sib_ind)
            sib_perm_dir = search_property('was.sib.me.filestore.permanentstoredirectory_r_' + sib_ind)
            sib_tmp_dir = search_property('was.sib.me.filestore.temporarystoredirectory_r_' + sib_ind)
            sib_log_sz = search_property('was.sib.me.filestore.logsize_o_' + sib_ind)
            sib_unlmt_perm = search_property('was.sib.me.filestore.unlimitedpermanentstore_o_' + sib_ind)
            sib_min_perm = search_property('was.sib.me.filestore.minpermanentstore_o_' + sib_ind)
            sib_max_perm = search_property('was.sib.me.filestore.maxpermanentstore_o_' + sib_ind)
            sib_unlmt_temp = search_property('was.sib.me.filestore.unlimitedtemporarystore_o_' + sib_ind)
            sib_min_temp = search_property('was.sib.me.filestore.mintemporarystore_o_' + sib_ind)
            sib_max_temp = search_property('was.sib.me.filestore.maxtemporarystore_o_' + sib_ind)
            sib_frcrecreate = search_property('was.sib.forcerecreate_r_' + sib_ind)
            if check_valid_value(sib_sec) or check_valid_value(sib_mem) or check_valid_value(sib_log_dir) or check_valid_value(sib_perm_dir) or check_valid_value(sib_tmp_dir) :
                raise Exception('Required property missing for Bus ' + sib)
            #
            if check_valid_value(sib_log_sz) :
                sib_log_sz = 100
            if check_valid_value(sib_min_perm) :
                sib_min_perm = 200
            if check_valid_value(sib_max_perm) :
                sib_max_perm = 500
            if check_valid_value(sib_unlmt_perm) :
                sib_unlmt_perm = 'false'
            if check_valid_value(sib_min_temp) :
                sib_min_temp = 200
            if check_valid_value(sib_max_temp) :
                sib_max_temp = 500
            if check_valid_value(sib_unlmt_temp) :
                sib_unlmt_temp = 'false'
            #
            config_id = check_config_in_configid_list(bus_in_cell, sib)
            if len(config_id) != 0 :
                logger.info('Bus ' + sib + ' present.')
                logger.info('Property will be modified.')
                logger.info('Bus Property: ')
                ret_value = AdminConfig.modify(config_id, [['secure', sib_sec]] )
                logger.info(ret_value)
                logger.info('Bus Member Property: ')
                mem_id = AdminConfig.getid('/ServerCluster:' + sib_mem + '/SIBMessagingEngine:/')
                if len(config_id) == 0 :
                    raise Exception('Inconsistent configuration detected. There is no Bus Member ' + sib_mem + ' for Bus ' + sib)
                #
                store_id = AdminConfig.showAttribute(mem_id, 'fileStore')
                ret_value = AdminConfig.modify(store_id, [['logSize', sib_log_sz], ['logDirectory', sib_log_dir], ['minPermanentStoreSize', sib_min_perm], ['maxPermanentStoreSize', sib_max_perm], ['unlimitedPermanentStoreSize', sib_unlmt_perm], ['permanentStoreDirectory', sib_perm_dir], ['minTemporaryStoreSize', sib_min_temp], ['maxTemporaryStoreSize', sib_max_temp], ['unlimitedTemporaryStoreSize', sib_unlmt_temp], ['temporaryStoreDirectory', sib_tmp_dir]])
                logger.info(ret_value)
            else :
                logger.info('Bus Creation ' + sib)
                ret_value = AdminTask.createSIBus('[-bus ' + sib + ' -busSecurity ' + sib_sec + ' -scriptCompatibility 6.1 ]')
                logger.info(ret_value)
                logger.info('Bus Created cofiguring member.')
                ret_value = AdminTask.addSIBusMember('[-bus ' + sib + ' -cluster ' + sib_mem + ' -enableAssistance true -policyName HA -fileStore -logSize ' + str(sib_log_sz) + ' -logDirectory ' + sib_log_dir + ' -minPermanentStoreSize ' + str(sib_min_perm) + ' -maxPermanentStoreSize ' + str(sib_max_perm) + ' -unlimitedPermanentStoreSize ' + sib_unlmt_perm + ' -permanentStoreDirectory ' + sib_perm_dir + ' -minTemporaryStoreSize ' + str(sib_min_temp) + ' -maxTemporaryStoreSize ' + str(sib_max_temp) + ' -unlimitedTemporaryStoreSize ' + sib_unlmt_temp + ' -temporaryStoreDirectory ' + sib_tmp_dir + ' ]')
                logger.info(ret_value)
                logger.info('Bus member Clsuter ' + sib_mem + ' added.')
            #
            logger.info('Bus Destination')
            sib_dest_id_list_temp = AdminConfig.getid('/SIBus:%s/SIBQueue:/' % sib)
            sib_dest_id_list = splitlines(sib_dest_id_list_temp)
            sib_des_nm_list = search_property_list('was.sib.queue.name_r_' + sib_ind + '_')
            for sib_dest in sib_des_nm_list :
                sib_dest_ind = search_property_index('was.sib.queue.name_r_' + sib_ind + '_', sib_dest)
                sib_dest_mem = search_property('was.sib.queue.cluster_r_' + sib_ind + '_' + sib_dest_ind)
                sib_dest_rel = search_property('was.sib.queue.reliability_r_' + sib_ind + '_' + sib_dest_ind)               
                if check_valid_value(sib_dest_mem) or check_valid_value(sib_dest_rel) :
                    raise Exception('Required property missing for adding Bus Destination.')
                #
                logger.info('SIB: ' + sib + ' Name: ' + sib_dest + ' Reliability: ' + sib_dest_rel + ' Cluster: ' + sib_dest_mem)
                done_queue = 0
                for q_id in sib_dest_id_list :
                    q_name = AdminConfig.showAttribute(q_id, 'identifier')
                    if q_name == sib_dest :
                        logger.info('Queue already defined. Modifing the Queue.')
                        ret_value = AdminConfig.modify(q_id, [['reliability', sib_dest_rel]] )
                        logger.info(ret_value)
                        done_queue += 1
                    #
                #
                if done_queue == 0 :
                    logger.info('Creating Queue.')
                    ret_value = AdminTask.createSIBDestination('[-bus ' + sib + ' -name ' + sib_dest + ' -type Queue -reliability ' + sib_dest_rel + ' -description "" -cluster ' + sib_dest_mem + ' ]')
                    logger.info(ret_value)
                #
            #
        #
        logger.info('Exiting : createdefaultmessaging')
    except :
        logger.severe('Error default messaging creation. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in createdefaultmessaging methord.')
        sys.exit(1)
    #
#

def createjmsresourceq() :
    logger.info('Initialize : createjmsresourceq')
    try :
        queue_list = search_property_list('was.jms.queue.name_r_')
        for jmsq in queue_list :
            logger.info('Starting to process Queue ' + jmsq )
            q_index = search_property_index('was.jms.queue.name_r_', jmsq)
            q_type = search_property('was.jms.queue.type_r_' + q_index)
            if q_type == 'sib' :
                logger.info('DEFUALT MESSEGING QUEUE')
                q_jndi = search_property('was.jms.queue.jndi_r_' + q_index)
                q_clust = search_property('was.jms.queue.cluster_r_' + q_index)
                q_bus = search_property('was.jms.queue.bus_r_' + q_index)
                q_dest = search_property('was.jms.queue.destination_r_' + q_index)
                if check_valid_value(q_jndi) or check_valid_value(q_clust) or check_valid_value(q_bus) or check_valid_value(q_dest) or check_valid_value(jmsq) :
                    raise Exception('Required property missing for Queue ' + jmsq)
                #
                clusterid = check_config_in_configid_list(global_cluster_list, q_clust)
                if clusterid == '' :
                    raise Exception('Cluster ' + q_clust + ' not craeted under this configuration. Cannot refference a external scope.')
                #
                ret_value = AdminTask.createSIBJMSQueue('%s(cells/%s/clusters/%s|cluster.xml)' % (q_clust,cell,q_clust), '[-name ' + jmsq + ' -jndiName ' + q_jndi + ' -description "" -deliveryMode Application -readAhead AsConnection -busName ' + q_bus + ' -queueName ' + q_dest + ' -scopeToLocalQP false -producerBind false -producerPreferLocal true -gatherMessages false]')
                logger.info(ret_value)
            elif q_type == 'mq' :
                logger.info('MQ MESSEGING QUEUE')
                q_jndi = search_property('was.jms.queue.jndi_r_' + q_index)
                q_clust = search_property('was.jms.queue.cluster_r_' + q_index)
                q_dest = search_property('was.jms.queue.destination_r_' + q_index)
                q_qmgr  = search_property('was.jms.queue.qmgr_o_' + q_index)
                if check_valid_value(q_jndi) or check_valid_value(q_clust) or check_valid_value(q_dest) or check_valid_value(jmsq) :
                    raise Exception('Required property missing for Queue ' + jmsq)
                #
                clusterid = check_config_in_configid_list(global_cluster_list, q_clust)
                if clusterid == '' :
                    raise Exception('Cluster ' + q_clust + ' not craeted under this configuration. Cannot refference a external scope.')
                #
                params = ["-name", jmsq, "-jndiName", q_jndi, "-queueName", q_dest]
                if q_qmgr  != None and q_qmgr != '' :
                    params.append("-qmgr")
                    params.append(q_qmgr)
                #
                ret_value = AdminTask.createWMQQueue('%s(cells/%s/clusters/%s|cluster.xml)' % (q_clust,cell,q_clust), params)
                logger.info(ret_value)
            else :
                logger.info('Only Default and MQ resource are supported!!!')
            #
        #
        logger.info('Exiting : createjmsresourceq')
    except :
        logger.severe('Error creating JMS Resources Queue.  Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in createjmsresourceq methord.')
        sys.exit(1)
    #
#

def createjmsresourceqcf() :
    logger.info('Initialize : createjmsresourceqcf')
    try :
        qcf_list = search_property_list('was.jms.qcf.name_r_')
        for jmsqcf in qcf_list :
            logger.info('Starting to process QCF: ' + jmsqcf)
            qcf_index = search_property_index('was.jms.qcf.name_r_', jmsqcf)
            qcf_type = search_property('was.jms.qcf.type_r_' + qcf_index)
            if qcf_type == 'sib' :
                logger.info('DEFUALT MESSEGING QCF')
                qcf_jndi = search_property('was.jms.qcf.jndi_r_' + qcf_index)
                qcf_clust = search_property('was.jms.qcf.cluster_r_' + qcf_index)
                qcf_bus = search_property('was.jms.qcf.bus_r_' + qcf_index)
                qcf_provend = search_property('was.jms.qcf.providerendpoints_o_' + qcf_index)
                qcf_alias = search_property('was.jms.qcf.authalias_o_' + qcf_index)
                qcf_xaalias = search_property('was.jms.qcf.xarecoveryalias_o_' + qcf_index)
                if check_valid_value(jmsqcf) or check_valid_value(qcf_jndi) or check_valid_value(qcf_clust) or check_valid_value(qcf_bus) :
                    raise Exception('Required property missing for QCF: ' + jmsqcf)
                #
                clusterid = check_config_in_configid_list(global_cluster_list, qcf_clust)
                if clusterid == '' :
                    raise Exception('Cluster ' + qcf_clust + ' not craeted under this configuration. Cannot refference a external scope.')
                #
                params = ["-name", jmsqcf, "-jndiName", qcf_jndi, "-busName", qcf_bus, "-type", "queue", "-description", "QCF - "+jmsqcf]
                if qcf_provend != None and qcf_provend != '' :
                    params.append("-providerEndPoints")
                    params.append(qcf_provend)
                #
                if qcf_alias != None and qcf_alias != '' :
                    params.append("-authDataAlias")
                    params.append(qcf_alias)
                #
                if qcf_xaalias != None and qcf_xaalias != '' :
                    params.append("-xaRecoveryAuthAlias")
                    params.append(qcf_xaalias)
                #
                ret_value = AdminTask.createSIBJMSConnectionFactory('%s(cells/%s/clusters/%s|cluster.xml)' % (qcf_clust,cell,qcf_clust), params)
                logger.info(ret_value)
            elif qcf_type == 'mq' :
                logger.info('MQ MESSEGING QCF')
                qcf_jndi = search_property('was.jms.qcf.jndi_r_' + qcf_index)
                qcf_clust = search_property('was.jms.qcf.cluster_r_' + qcf_index)
                qcf_qmgr = search_property('was.jms.qcf.qmgr_r_' + qcf_index)
                qcf_qmgrhost = search_property('was.jms.qcf.qmgrhost_r_' + qcf_index)
                qcf_qmgrport = search_property('was.jms.qcf.qmgrport_r_' + qcf_index)
                qcf_alias = search_property('was.jms.qcf.authalias_o_' + qcf_index)
                qcf_xaalias = search_property('was.jms.qcf.xarecoveryalias_o_' + qcf_index)
                qcf_transp = search_property('was.jms.qcf.transport_o_' + qcf_index)
                qcf_ssl = search_property('was.jms.qcf.sslenable_r_' + qcf_index)
                qcf_sslalias = search_property('was.jms.qcf.sslalias_o_' + qcf_index)
                if check_valid_value(jmsqcf) or check_valid_value(qcf_jndi) or check_valid_value(qcf_clust) or check_valid_value(qcf_qmgr) or check_valid_value(qcf_qmgrhost) or check_valid_value(qcf_qmgrhost) or check_valid_value(qcf_qmgrport) :
                    raise Exception('Required property missing for QCF: ' + jmsqcf)
                #
                clusterid = check_config_in_configid_list(global_cluster_list, qcf_clust)
                if clusterid == '' :
                    raise Exception('Cluster ' + qcf_clust + ' not craeted under this configuration. Cannot refference a external scope.')
                #
                if qcf_transp != None and qcf_transp != '' :
                    qcf_transp = 'BINDINGS_THEN_CLIENT'
                #
                params = ["-name", jmsqcf, "-jndiName", qcf_jndi, "-type", "QCF", "-qmgrName", qcf_qmgr, "-wmqTransportType", qcf_transp, "-qmgrHostname", qcf_qmgrhost, "-qmgrPortNumber", qcf_qmgrport]
                if qcf_alias != None and qcf_alias != '' :
                    params.append("-containerAuthAlias")
                    params.append(qcf_alias)
                #
                if qcf_xaalias != None and qcf_xaalias != '' :
                    params.append("-xaRecoveryAuthAlias")
                    params.append(qcf_xaalias)
                #
                if qcf_ssl == 'true' :
                    if qcf_sslalias  != None and qcf_sslalias != '' :
                        params.append("-sslType")
                        params.append("CENTRAL")
                    else :
                        params.append("-sslType")
                        params.append("SPECIFIC")
                        params.append("-sslConfiguration")
                        params.append(qcf_sslalias)
                    #
                #
                ret_value = AdminTask.createWMQConnectionFactory('%s(cells/%s/clusters/%s|cluster.xml)' % (qcf_clust,cell,qcf_clust), params)
                logger.info(ret_value)
            else :
                logger.info('Only Default and MQ resource can be configured.')
            #
        #
        logger.info('Exiting : createjmsresourceqcf')
    except :
        logger.severe('Error creating QCF Resources.  Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in createjmsresourceqcf methord.')
        sys.exit(1)
    #
#

def createjmsactivationspec() :
    logger.info('Initialize : createjmsactivationspec')
    try :
        aspec_list = search_property_list('was.jms.activspec.name_r_')
        for aspec in aspec_list :
            logger.info('Starting to process Activation Specification: ' + aspec)
            as_index = search_property_index('was.jms.activspec.name_r_', aspec)
            as_type = search_property('was.jms.activspec.type_r_' + as_index)
            if as_type == 'sib' :
                logger.info('DEFUALT MESSEGING Activation Specification')
                as_jndi = search_property('was.jms.activspec.jndi_r_' + as_index)
                as_clust = search_property('was.jms.activspec.cluster_r_' + as_index)
                as_bus = search_property('was.jms.activspec.bus_r_' + as_index)
                as_dest = search_property('was.jms.activspec.dest_r_' + as_index)
                as_auth = search_property('was.jms.activspec.authalias_o_' + as_index)
                if check_valid_value(aspec) or check_valid_value(as_jndi) or check_valid_value(as_clust) or check_valid_value(as_bus) or check_valid_value(as_dest) :
                    raise Exception('Required property missing for Activation Specification: ' + aspec)
                #
                clusterid = check_config_in_configid_list(global_cluster_list, as_clust)
                if clusterid == '' :
                    raise Exception('Cluster ' + as_clust + ' not craeted under this configuration. Cannot refference a external scope.')
                #
                params = ["-name", aspec, "-jndiName", as_jndi, "-busName", as_bus, "-destinationJndiName", as_dest, "-destinationType", "queue"]
                if as_auth != None and as_auth != '' :
                    params.append("-containerAuthAlias")
                    params.append(as_auth)
                #
                ret_value = AdminTask.createSIBJMSActivationSpec('%s(cells/%s/clusters/%s|cluster.xml)' % (as_clust,cell,as_clust), params)
                logger.info(ret_value)
            elif as_type == 'mq' :
                logger.info('MQ MESSEGING Activation Specification')
                as_jndi = search_property('was.jms.activspec.jndi_r_' + as_index)
                as_clust = search_property('was.jms.activspec.cluster_r_' + as_index)
                as_dest = search_property('was.jms.activspec.dest_r_' + as_index)
                as_qmgr = search_property('was.jms.activspec.qmgr_r_' + as_index)
                as_qmgrhost = search_property('was.jms.activspec.qmgrhost_r_' + as_index)
                as_qmgrport = search_property('was.jms.activspec.qmgrport_r_' + as_index)
                as_transp = search_property('was.jms.activspec.transport_o_' + as_index)
                as_ssl = search_property('was.jms.activspec.sslenable_r_' + as_index)
                as_sslalias = search_property('was.jms.activspec.sslalias_o_' + as_index)
                as_auth = search_property('was.jms.activspec.authalias_o_' + as_index)
                if check_valid_value(aspec) or check_valid_value(as_jndi) or check_valid_value(as_clust) or check_valid_value(as_dest) or check_valid_value(as_qmgr) or check_valid_value(as_qmgrhost) or check_valid_value(as_qmgrport) or check_valid_value(as_ssl) :
                    raise Exception('Required property missing for Activation Specification: ' + aspec)
                #
                clusterid = check_config_in_configid_list(global_cluster_list, as_clust)
                if clusterid == '' :
                    raise Exception('Cluster ' + as_clust + ' not craeted under this configuration. Cannot refference a external scope.')
                #
                if as_transp != None and as_transp != '' :
                    as_transp = 'BINDINGS_THEN_CLIENT'
                #
                params = ["-name", aspec, "-jndiName", as_jndi, "-destinationJndiName", as_dest, "-destinationType", "javax.jms.Queue", "-qmgrName", as_qmgr, "-wmqTransportType", as_transp, "-qmgrHostname", as_qmgrhost, "-qmgrPortNumber", as_qmgrport]
                if as_auth != None and as_auth != '' :
                    params.append("-authAlias")
                    params.append(as_auth)
                #
                if as_ssl == 'true' :
                    if as_sslalias != None and qcf_sslalias != '' :
                        params.append("-sslType")
                        params.append("CENTRAL")
                    else :
                        params.append("-sslType")
                        params.append("SPECIFIC")
                        params.append("-sslConfiguration")
                        params.append(as_sslalias)
                    #
                #
                ret_value = AdminTask.createWMQActivationSpec('%s(cells/%s/clusters/%s|cluster.xml)' % (qcf_clust,cell,qcf_clust), params)
                logger.info(ret_value)
            else :
                logger.info('Only Default and MQ resource can be configured.')
            #
        #
        logger.info('Exiting : createjmsactivationspec')
    except :
        logger.severe('Error creating JMS Activation Specification.  Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in createjmsactivationspec methord.')
        sys.exit(1)
    #
#

def createjmsresource() :
    logger.info('Initialize : createjmsresource')
    try :
        createjmsresourceq()
        createjmsresourceqcf()
        createjmsactivationspec()
        logger.info('Exiting : createjmsresource')
    except :
        logger.severe('Error creating JMS Resources.  Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in createjmsresource methord.')
        sys.exit(1)
    #
#

def deletejmsresourceq() :
    logger.info('Initialize : deletejmsresourceq')
    try :
        cluster_list = search_property_list('was.cluster.dynamic.name_r_')
        if len(cluster_list) < 1 :
            logger.info('No CLUSTER defination found.')
        else :
            for cluster_name in cluster_list :
                cluster_index = search_property_index('was.cluster.dynamic.name_r_', cluster_name)
                cluster_type = search_property('was.cluster.dynamic.type_r_' + str(cluster_index))
                if cluster_type == 'app' :
                    logger.info('Found Application cluster ' + cluster_name + ' Queue removal will be initiated for the cluster.')
                    clsuter_id = AdminConfig.getid( '/Cell:%s/ServerCluster:%s/' % (cell, cluster_name))
                    if len(clsuter_id) == 0 :
                        logger.info('Cluster ' + cluster_name + ' does not exist. Thus not action will be performed.')
                    else :
                        for queue in splitlines(AdminTask.listSIBJMSQueues(clsuter_id)) :
                            logger.info('Removing ' + str(queue))
                            ret_value = AdminTask.deleteSIBJMSQueue(queue)
                            logger.info(ret_value)
                        #
                    #
                #
            #
        #
        logger.info('Exiting : deletejmsresourceq')
    except :
        logger.severe('Error deleting JMS Resources Queue. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in deletejmsresourceq methord.')
        sys.exit(1)
    #
#

def deletejmsresourceqcf() :
    logger.info('Initialize : deletejmsresourceqcf')
    try :
        cluster_list = search_property_list('was.cluster.dynamic.name_r_')
        if len(cluster_list) < 1 :
            logger.info('No CLUSTER defination found.')
        else :
            for cluster_name in cluster_list :
                cluster_index = search_property_index('was.cluster.dynamic.name_r_', cluster_name)
                cluster_type = search_property('was.cluster.dynamic.type_r_' + str(cluster_index))
                if cluster_type == 'app' :
                    logger.info('Found Application cluster ' + cluster_name + ' QCF removal will be initiated for the cluster.')
                    clsuter_id = AdminConfig.getid( '/Cell:%s/ServerCluster:%s/' % (cell, cluster_name))
                    if len(clsuter_id) == 0 :
                        logger.info('Cluster ' + cluster_name + ' does not exist. Thus not action will be performed.')
                    else :
                        for qcf in splitlines(AdminConfig.list('J2CConnectionFactory', clsuter_id)) :
                            logger.info('Removing ' + str(qcf))
                            ret_value = AdminTask.deleteSIBJMSConnectionFactory(qcf)
                            logger.info(ret_value)
                        #
                    #
                #
            #
        #
        logger.info('Exiting : deletejmsresourceqcf')
    except :
        logger.severe('Error deleting JMS QCF. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in deletejmsresourceqcf methord.')
        sys.exit(1)
    #
#

def deletejmsactivationspec() :
    logger.info('Initialize : deletejmsactivationspec')
    try :
        cluster_list = search_property_list('was.cluster.dynamic.name_r_')
        if len(cluster_list) < 1 :
            logger.info('No CLUSTER defination found.')
        else :
            for cluster_name in cluster_list :
                cluster_index = search_property_index('was.cluster.dynamic.name_r_', cluster_name)
                cluster_type = search_property('was.cluster.dynamic.type_r_' + str(cluster_index))
                if cluster_type == 'app' :
                    logger.info('Found Application cluster ' + cluster_name + ' Activation Specification removal will be initiated for the cluster.')
                    clsuter_id = AdminConfig.getid( '/Cell:%s/ServerCluster:%s/' % (cell, cluster_name))
                    if len(clsuter_id) == 0 :
                        logger.info('Cluster ' + cluster_name + ' does not exist. Thus not action will be performed.')
                    else :
                        for aspec in splitlines(AdminConfig.list('J2CActivationSpec', clsuter_id)) :
                            logger.info('Removing ' + str(aspec))
                            ret_value = AdminTask.deleteSIBJMSActivationSpec(aspec)
                            logger.info(ret_value)
                        #
                    #
                #
            #
        #
        logger.info('Exiting : deletejmsactivationspec')
    except :
        logger.severe('Error deleting JMS Activation Specification. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in deletejmsactivationspec methord.')
        sys.exit(1)
    #
#

def deletejmsresource() :
    logger.info('Initialize : deletejmsresource')
    try :
        deletejmsactivationspec()
        deletejmsresourceq()
        deletejmsresourceqcf()
        logger.info('Exiting : deletejmsresource')
    except :
        logger.severe('Error deleting JMS Resources.  Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in deletejmsresource methord.')
        sys.exit(1)
    #
#

def deletehealthpolicy() :
    logger.info('Initialize : deletehealthpolicy')
    try :
        hc_def_list = search_property_list('was.policies.health.name_r_')
        cluster_list = search_property_list('was.cluster.dynamic.name_r_')
        hc_pol_list = splitlines(AdminConfig.list('HealthClass'))
        for hc in hc_pol_list :
            hc_name = AdminConfig.showAttribute(hc, 'name')
            hc_target_list = splitlist(AdminConfig.showAttribute(hc, 'targetMemberships'))
            if len(hc_target_list) > 1 :
                raise Exception('Multiple target Health Policy is not created by the script.')
            #
            hc_target = hc_target_list[0]
            if hc_target != '' :
                hc_target_type = AdminConfig.showAttribute(hc_target, 'type')
                hc_target_name = AdminConfig.showAttribute(hc_target, 'memberString')
                if hc_target_type == '3' :
                    ispresent = check_element_in_list(cluster_list, hc_target_name)
                    if ispresent == 1 :
                        logger.info('Deleting Health POlicy: ' + hc_name)
                        ret_value = AdminConfig.remove(hc)
                        logger.info(ret_value)
                    #
                #
            else :
                del_stat = check_element_in_list(hc_def_list, hc_name)
                if del_stat == 1 :
                    logger.info('Deleting Health POlicy: ' + hc_name)
                    ret_value = AdminConfig.remove(hc)
                    logger.info(ret_value)
                #
            #
        #
        logger.info('Exiting : deletehealthpolicy')
    except :
        logger.severe('Error cleaning health policy. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in deletehealthpolicy methord.')
        sys.exit(1)
    #
#

def createhealthpolicy() :
    logger.info('Initialize : createhealthpolicy')
    try :
        hc_support_type_level = 'AGGRESSIVE;CONSERVATIVE;NORMAL'
        hc_support_type_map={}
        hc_support_type_map['age'] = 'AgeCondition@@@maxAge@@@ageUnits'
        hc_support_type_map['work'] = 'WorkloadCondition@@@totalRequests'
        hc_support_type_map['responsecondition'] = 'ResponseCondition@@@tt@@@tunit'
        hc_support_type_map['memorycondition'] = 'MemoryCondition@@@memoryUsed@@@timeOverThreshold@@@timeUnits'
        hc_support_type_map['memoryleak'] = 'MemoryLeakAlgorithm@@@level'
        hc_support_type_map['stuckrequest'] = 'StuckRequestCondition@@@timeoutPercent'
        hc_support_type_map['StormDrainCondition'] = 'StormDrainCondition@@@level'
        hc_list = search_property_list('was.policies.health.name_r_')
        for hc_name in hc_list :
            logger.info('Creating Health POlicy: ' + hc_name)
            hc_ind = search_property_index('was.policies.health.name_r_', hc_name)
            hc_mode_str = search_property('was.policies.health.mode_r_' + hc_ind)
            hc_type = search_property('was.policies.health.type_r_' + hc_ind)
            hc_target = search_property('was.policies.health.target_r_' + hc_ind)
            hc_targettype = search_property('was.policies.health.targettype_r_' + hc_ind)
            hc_typeparam_list = search_property_list('was.policies.health.typeparam_name_r_' + hc_ind + '_')
            actn = search_property('was.policies.health.action_r_' + hc_ind)
            if check_valid_value(hc_name) or check_valid_value(hc_mode_str) or check_valid_value(hc_type) or check_valid_value(actn) :
                raise Exception('Required property missing for adding Health Policy.')
            #
            hrmode = 3
            if hc_mode_str == 'supervised' :
                hrmode = 3
            elif hc_mode_str == 'automatic' :
                hrmode = 2
            else :
                raise Exception('The Health Policy Supervised Mode is Wrong or not Supported.')
            #
            chk_hc_typ = hc_support_type_map.get(hc_type)
            if chk_hc_typ == None :
                raise Exception('The Health Policy Type specified is Wrong or not Supported.')
            #
            hc_target_num = 3
            if hc_targettype == 'dynamiccluster' :
                hc_target_num = 3
            elif hc_targettype == 'staticcluster' :
                hc_target_num = 2
            else :
                raise Exception('The Health Policy Target Type is Wrong or not Supported.')
            #
            htype = chk_hc_typ.split('@@@')[0]
            attrs_param = []
            pm_list = hc_support_type_map.get(hc_type)
            for prm_nm in hc_typeparam_list :
                prm_ind = search_property_index('was.policies.health.typeparam_name_r_' + hc_ind + '_', prm_nm)
                prm_val = search_property('was.policies.health.typeparam_value_r_' + hc_ind + '_' + prm_ind)
                chk_prm = check_element_in_list(pm_list.split('@@@'), prm_nm)
                if chk_prm == 0 or check_valid_value(prm_val) :
                    raise Exception('The Health Policy Type Parameter provided not correct.')
                #
                if prm_nm == 'level' :
                    chk_lvl = check_element_in_list(hc_support_type_level.split(';'), prm_val)
                    if chk_lvl == 0 :
                        raise Exception('The Health Policy Type Parameter not correct.')
                    #
                    val = prm_val
                else :
                    val = int(prm_val)
                #
                attrs_param.append([prm_nm, val])
            #
            logger.info(str(attrs_param))
            stepnum = 3
            if actn == 'RESTART' :
                stepnum = 3
            elif actn == 'THREADDUMP' :
                stepnum = 2
            elif actn == 'HEAPDUMP' :
                stepnum = 1
            else :
                raise Exception('The Health Policy Action specified is Wrong or not Supported.')
            #
            hc = [['name', hc_name], ['description', ''], ['reactionMode', hrmode]]
            hc_id = AdminConfig.create('HealthClass', cell_id, hc)
            logger.info(hc_id)
            ret_value = AdminConfig.create(htype, hc_id, attrs_param, 'HealthCondition') 
            logger.info(ret_value)
            ret_value = AdminConfig.create('HealthAction', hc_id, [['actionType', actn], ['stepNum', str(stepnum)]], 'healthActions')
            logger.info(ret_value)
            ret_value = AdminConfig.create('TargetMembership', hc_id, [['memberString', hc_target], ['type', hc_target_num]], 'targetMemberships')
            logger.info(ret_value) 
        #
        logger.info('Exiting : createhealthpolicy')
    except :
        logger.severe('Error creating health policy. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in createhealthpolicy methord.')
        sys.exit(1)
    #
#

def createhealthcontroller() :
    logger.info('Initialize : createhealthcontroller')
    try :
        hc_state = search_property('was.controller.health.enable_r_1')
        if check_valid_value(hc_state) :
            logger.info('HealthController configuration not specified. No action needed.')
        else :
            hc_id = AdminConfig.getid("/HealthController:/")
            if hc_id == '' :
                raise Exception('HealthController cannot be identified.')
            #
            hc_cc = search_property('was.controller.health.controlcyclelength_o_1')
            hc_mxcon = search_property('was.controller.health.maxconsecutiverestarts_o_1')
            hc_mnrst = search_property('was.controller.health.minrestartinterval_o_1')
            hc_rstunit = search_property('was.controller.health.minrestartintervalunits_o_1')
            hc_rstto = search_property('was.controller.health.restarttimeout_o_1')
            attrs = []
            attrs.append(['enable', hc_state])
            if not check_valid_value(hc_cc) :
                attrs.append(['controlCycleLength', hc_cc])
            #
            if not check_valid_value(hc_mxcon) :
                attrs.append(['maxConsecutiveRestarts', hc_mxcon])
            #
            if not check_valid_value(hc_mnrst) :
                attrs.append(['minRestartInterval', hc_mnrst])
                if check_valid_value(hc_rstunit) :
                    hc_rstunit = 2
                #
                attrs.append(['minRestartIntervalUnits', hc_rstunit])
            #
            if not check_valid_value(hc_rstto) :
                attrs.append(['restartTimeout', hc_rstto])
            #
            logger.info('Setting Heath Controller property: ' + str(attrs))
            ret_value = AdminConfig.modify(hc_id, attrs)
            logger.info(ret_value)
        #
        logger.info('Exiting : createhealthcontroller')
    except :
        logger.severe('Error configuring Heath Controller. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in createhealthcontroller methord.')
        sys.exit(1)
    #
#

def createvariable() :
    global logger
    logger.info('Initialize : createvariable')
    try :
        varbl_lst = search_property_list('was.variable.name_r_')
        for varbl in varbl_lst :
            varbl_ind = search_property_index('was.variable.name_r_', varbl)
            varbl_scp = search_property('was.variable.scope_r_' + varbl_ind)
            varbl_val = search_property('was.variable.value_r_' + varbl_ind)
            if check_valid_value(varbl) or check_valid_value(varbl_scp) or check_valid_value(varbl_val) :
                raise Exception('Required property missing for Application Cluster scoped variables.')
            #
            map = AdminConfig.list('VariableMap', '%s(cells/%s/clusters/%s|cluster.xml)' % (varbl_scp, cell, varbl_scp))
            vars = splitlist(AdminConfig.showAttribute(map, 'entries'))
            parent = check_config_in_configid_list(vars, varbl, 'symbolicName')
            if parent == '' :
                logger.info('The Variable '+ varbl +' not scoped in '+ varbl_scp)
                attrs = []
                attrs.append( [ 'symbolicName', varbl ] )
                attrs.append( [ 'value', varbl_val ] )
                object=AdminConfig.create('VariableSubstitutionEntry', map, attrs)
                logger.info(object)
            else :
                logger.info('The Variable '+ varbl +' present in scoped in '+ varbl_scp)
                object=AdminConfig.modify(parent, [['value', varbl_val ]])
                logger.info(object)
            #
        #
        logger.info('Exiting : createvariable')
    except :
        logger.severe('Error creating creating variable. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in createvariable methord.')
        sys.exit(1)
    #
#

def deleteenvironment() :
    logger.info('Initialize : deleteenvironment')
    try :
        deletejdbcresource()
        deletejmsresource()
        deletedefaultmessaging()
        deletereplicationdomain()
        deletehealthpolicy()
        deleteclusters()
        deletevhost()
        delete_nodegroup()
        logger.info('Exiting : deleteenvironment')
    except :
        logger.severe('Error cleaning environment. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in deleteenvironment methord.')
        sys.exit(1)
    #
#

def createenvironment() :
    logger.info('Initialize : createenvironment')
    try :
        create_coregroup()
        create_nodegroup()
        createvhost()
        createreplicationdomain()
        createhealthcontroller()
        createclusters()
        createhealthpolicy()
        createdefaultmessaging()
        createvariable()
        createjmsresource()
        createjdbcresource()
        logger.info('Exiting : createenvironment')
    except :
        logger.severe('Error creating environment. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in createenvironment methord.')
        sys.exit(1)
    #
#

def synfullenvironment() :
    logger.info('Initialize : synfullenvironment')
    try :
        nodelist = AdminTask.listManagedNodes().split(lineSeparator)
        for nodename in nodelist :
            logger.info('Doing Full Resyncronization of node: ' + nodename)
            repo = AdminControl.completeObjectName('type=ConfigRepository,process=nodeagent,node='+ nodename +',*')
            result_output = AdminControl.invoke(repo, 'refreshRepositoryEpoch')
            logger.info(result_output)
            sync = AdminControl.completeObjectName('cell='+ cell +',node='+ nodename +',type=NodeSync,*')
            result_output = AdminControl.invoke(sync , 'sync')
            logger.info(result_output)
        #
        logger.info('Exiting : synfullenvironment')
    except :
        logger.severe('Error in Resyncronization')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in synfullenvironment methord.')
        sys.exit(1)
    #
#

def updateglobalplugin() :
    logger.info('Initialize : updateglobalplugin')
    try :
        dmgrn = AdminControl.getNode()
        vmaps = splitlines(AdminConfig.list('VariableMap', AdminConfig.getid( '/Cell:%s/Node:%s' % (cell, dmgrn) )))
        if len(vmaps) > 0 :
            map_id = vmaps[-1]
            entries = AdminConfig.showAttribute(map_id, 'entries')
            entries = entries[1:-1].split(' ')
            for e in entries :
                name = AdminConfig.showAttribute(e,'symbolicName')
                if name == 'USER_INSTALL_ROOT' :
                    value = AdminConfig.showAttribute(e,'value')
                    configDir = os.path.join(value, 'config')
                    plgGen = AdminControl.queryNames('type=PluginCfgGenerator,*')
                    result_output = AdminControl.invoke(plgGen, 'generate', '[%s %s %s null null null false]' % (value, configDir, cell), '[java.lang.String java.lang.String java.lang.String java.lang.String java.lang.String java.lang.String boolean]')
                    logger.info(result_output)
                    logger.info('Completed Plugin Generation.')
                    logger.info('Exiting : updateglobalplugin')
                    return
                #
            #
        # 
        logger.info('Exiting : updateglobalplugin')
    except :
        logger.severe('Error in Updating Plugin')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in updateglobalplugin methord.')
        sys.exit(1)
    #
#

###########################################################################################################################################
# MAIN SECTION
# Initiation Section
mail_status = 0
was_host = socket.gethostname()
logger  = Logger.getLogger('was_85_admin')
property_file = Properties()
cell_id = AdminConfig.list('Cell').split(lineSeparator)[0]
cell = AdminConfig.showAttribute(cell_id, 'name')
environment_detail=''
mod_mapping = {}
global_cluster_list=[]
global_datasource_auth_alias_list=[]
global_datasource_provider_list=[]
global_vhost_list=[]
global_domain_list=[]
global_threadpool_map={}
global_threadpool_map['server.startup'] = '1@@@3@@@30000@@@false'
global_threadpool_map['WebContainer'] = '50@@@100@@@60000@@@false'
global_threadpool_map['WMQJCAResourceAdapter'] = '10@@@50@@@5000@@@false'
global_threadpool_map['TCPChannel.DCS'] = '20@@@20@@@5000@@@false'
global_threadpool_map['SIBJMSRAThreadPool'] = '35@@@41@@@3500@@@false'
global_threadpool_map['SIBFAPThreadPool'] = '4@@@50@@@5000@@@false'
global_threadpool_map['SIBFAPInboundThreadPool'] = '4@@@50@@@5000@@@false'
global_threadpool_map['ORB.thread.pool'] = '10@@@50@@@3500@@@false'

# Execution
if len(sys.argv) == 1 :
    environment_detail=sys.argv[0]
elif len(sys.argv) == 2 :
    environment_detail=sys.argv[0]
    log_file_location = sys.argv[1]
    initiatelog(log_file_location)
else :
    logger.severe('Incorrect usage. You need to specify argument. USAGE  : wsadmin -lang jython was_85_admin.py [country name].[application name].[environment name]')
    logger.severe('Example: ./wsadmin.sh -lang jython -f was_85_admin.py ind.test.dev')
    sys.exit(9)
#
loadproperty(environment_detail)
check_point_list = splitlines(AdminTask.listCheckpoints())
chk_stat = check_config_in_configid_list(check_point_list, 'full2')
if chk_stat != '' :
    AdminTask.deleteCheckpoint(['-checkpointName', 'full2'])
#
AdminTask.createFullCheckpoint(['-checkpointName', 'full2'])
#stopenvironment()
deleteenvironment()
createenvironment()
AdminConfig.save()
#synfullenvironment()
#updateglobalplugin()
#startenvironment()
#AdminConfig.save()
#synfullenvironment()
if mail_status == 0 :
    url_called =  'https://mail.send.endpoint.com:443/sendmail'
    url_called =  url_called + 'San.Muk@gmail.com&alert_type=DEPLOYMENT&env_type=APPLICATION&env=' + environment_detail + '&remark='
    url_called =  url_called + '&status=SUCCESS&server=' + was_host
    unix_command = 'wget -q --spider --no-check-certificate "' + url_called + '"'
    os.system(unix_command)
#
