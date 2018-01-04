#================================================================================================================================
# SCRIPT : This script is the main script for configuration for Websphere Cell. 
#          Part of WASDEV setup.
# USAGE  : wsadmin -lang jython was_85_dmgr.py [CONFIG FILE] [OPTIONAL: LOG FILE]
#          Example: ./wsadmin.sh -lang jython -f was_85_dmgr.py /DC/WAAS2.0/dmgr.conf 
# AUTHOR : Sankar Mukherjee
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
global mail_list

###########################################################################################################################################
# UTILITY FUNCTION SECTION
def notify_error(messege) :
        global mail_status
        global mail_list
        global was_host
        AdminTask.restoreCheckpoint(['-checkpointName', 'full2'])
        if mail_status == 0 :
            url_called =  'https://mail.send.endpoint.com:443/sendmail'
            url_called =  url_called + mail_list + '&alert_type=DEPLOYMENT&env_type=CELL&env=' + environment_detail + '&remark=' + messege
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

def wasvariablevalue(varnm) :
    global logger
    logger.info('Inside : wasvariablevalue. Property: '+ varnm)
    try :
        dmgr_node = AdminControl.getNode()
        variable_map = AdminConfig.getid('/Node:' + dmgr_node + '/VariableMap:/')
        variable_configId = AdminConfig.showAttribute(variable_map,'entries')
        configId_list = splitlist(variable_configId)
        for variableId in configId_list :
            if AdminConfig.showAttribute(variableId,'symbolicName') == varnm :
                return AdminConfig.showAttribute(variableId,'value')
            #
        #
        logger.info('Exiting : wasvariablevalue')
        return ''
    except :
        logger.severe('Error extracting Websphere Variable. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in wasvariablevalue.')
        sys.exit(1)
    #
# 

def initiatelog(log_file_location) :
    global was_host
    global logger
    global log_file
    try :
        curTime = time.localtime()
        log_file_name = 'was_85_dmgr_' + str(curTime[0]) + '_' + str(curTime[1]) + '_' + str(curTime[2]) + '.log'
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
    global property_file
    global logger
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
    global property_file
    global logger
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
    global property_file
    global logger
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
    global property_file
    global logger
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
    global logger
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

def check_config_in_configid_list(config_list, name, parameter=None) :
    global logger
    logger.info('Inside : check_config_in_configid_list. Argument : ' + str(config_list) + ', ' + name)
    try :
        if parameter == None :
            parameter = 'name'
        #
        for conf in config_list :
            config_name = AdminConfig.showAttribute(conf, parameter)
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

def configuredmgr() :
    global logger
    logger.info('Initialize : configuredmgr')
    try :
        nd_list = search_property_list('was.cell.node.name_')
        for nd in nd_list :
            nd_ind = search_property_index('was.cell.node.name_', nd)
            nd_typ = search_property('was.cell.node.type_'+ nd_ind)
            nd_upd = search_property('was.cell.node.update_'+ nd_ind)
            if nd_typ == 'manager' and nd_upd == 'true' :
                logger.info('Node '+ nd +' is a Management Node. Configuring.')
                dmgrid = AdminConfig.getid('/Node:'+ nd +'/Server:dmgr/')
                if dmgrid == '' :
                    raise Exception('DMGR process cannot detected in Management Node '+ nd)
                #
                mn_hp = search_property('was.cell.dmgr.minheap_'+ nd_ind)
                mx_hp = search_property('was.cell.dmgr.maxheap_'+ nd_ind)
                if mn_hp != None and mn_hp != '' and mx_hp != None and mx_hp != '' :
                    logger.info('DMGR Heap size getting resized.')
                    AdminTask.setJVMProperties('[-nodeName '+ nd +' -serverName dmgr -initialHeapSize '+ str(mn_hp) +' -maximumHeapSize '+ str(mx_hp) +']')
                #
                envprop_list = search_property_list('was.cell.dmgr.environmententry.name_'+ nd_ind +'_')
                for envprop in envprop_list :
                    envprop_ind = search_property_index('was.cell.dmgr.environmententry.name_'+ nd_ind +'_', envprop)
                    envprop_val = search_property('was.cell.dmgr.environmententry.value_'+ nd_ind +'_'+ envprop_ind)
                    if envprop != None and envprop != '' and envprop_val != None and envprop_val != '' :
                        setenvproperty(dmgrid, envprop, envprop_val)
                    #
                #
                port_list = search_property_list('was.cell.dmgr.port.name_'+ nd_ind +'_')
                nd_id = AdminConfig.getid('/Node:'+ nd +'/')
                srventries = splitlines(AdminConfig.list( 'ServerEntry', nd_id))
                for port in port_list :
                    port_ind = search_property_index('was.cell.dmgr.port.name_'+ nd_ind +'_', port)
                    port_val = search_property('was.cell.dmgr.port.value_'+ nd_ind +'_'+ port_ind)
                    if port != None and port != '' and port_val != None and port_val != '' :
                        for srventry in srventries :
                            sname = AdminConfig.showAttribute( srventry,  'serverName' )
                            if sname == 'dmgr' :
                                endpnts = splitlist(AdminConfig.showAttribute( srventry, 'specialEndpoints' ))
                                for epnt in endpnts :
                                    epnt_nm = AdminConfig.showAttribute( epnt, 'endPointName' )
                                    if epnt_nm == port :
                                        epnt_id = AdminConfig.showAttribute( epnt, 'endPoint' )
                                        logger.info('Port '+ port +' will be configured with value '+ str(port_val))
                                        port_int = int(port_val)
                                        AdminConfig.modify( epnt_id, [['port', "%d" % port_int]] )
                                    #
                                #
                            #
                        #
                    #
                #
            #
        #
        logger.info('Exiting : configuredmgr')
    except :
        logger.severe('Error configuring DMGR. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in configuredmgr methord. ERROR: ' + str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        sys.exit(1)
    #
#

def setenvproperty (srvid, propnm, propval) :
    global logger
    logger.info('Initialize : '+ str(srvid) +' '+ propnm +' '+ propval)
    try :
        prop_list = splitlines(AdminConfig.list('Property', srvid))
        prop_id = check_config_in_configid_list(prop_list, propnm)
        jvm_def = AdminConfig.list('JavaProcessDef',  srvid)
        if prop_id == '' :
            attrs = []
            attrs.append( [ 'name', propnm ] )
            attrs.append( [ 'value', propval ] )
            logger.info('Property '+ propnm +' not present it will be created.')
            ret_value = AdminConfig.create('Property', jvm_def, attrs)
        else :
            logger.info('Property '+ propnm +' present thus setting value.')
            ret_value = AdminConfig.modify(prop_id, [['value', propval]])
        #
        logger.info(ret_value)
        logger.info('Exiting : setenvproperty')
    except :
        logger.severe('Error setting environment variable. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in setenvproperty methord. ERROR: ' + str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        sys.exit(1)
    #
#


def setcoregroupproperty(cg_id) :
    global logger
    logger.info('Initialize : setcoregroupproperty. Property: '+ cg_id)
    try :
        cg_nm = AdminConfig.showAttribute(cg_id, 'name')
        cg_ind = search_property_index('was.cell.coregroup.name_', cg_nm)
        cg_nc = search_property('was.cell.coregroup.noofcoordinator_' + cg_ind)
        if cg_nc != None and cg_nc != '' :
            logger.info('Number of coordinator will be set to ' + str(cg_nc))
            AdminConfig.modify(cg_id, [['numCoordinators',cg_nc]])
        #
        cg_prfcord_list = search_property_list('was.cell.coregroup.prefcoordinator.jvmname_' + cg_ind + '_')
        cg_pc_list = splitlist(AdminConfig.showAttribute( cg_id, "preferredCoordinatorServers" ))
        cg_msvr_list = splitlist(AdminConfig.showAttribute( cg_id, "coreGroupServers" ))
        for cg_prfcord in cg_prfcord_list :
            cg_prfcord_ind = search_property_index('was.cell.coregroup.prefcoordinator.jvmname_' + cg_ind + '_', cg_prfcord)
            cg_prfcord_nd = search_property('was.cell.coregroup.prefcoordinator.nodename_' + cg_ind + '_' + cg_prfcord_ind)
            if cg_prfcord != None and cg_prfcord != '' and cg_prfcord_nd != None and cg_prfcord_nd != '' :
                status = 0
                for cg_pc in cg_pc_list :
                    srv = AdminConfig.showAttribute(cg_pc, 'serverName')
                    nd_nm = AdminConfig.showAttribute(cg_pc, 'nodeName')
                    if srv == cg_prfcord and cg_prfcord_nd == nd_nm :
                        logger.info('The server ' + cg_prfcord + ' on Node ' + cg_prfcord_nd + ' already a member of the Core Group.')
                        status = 1
                    else :
                        for msvr in cg_msvr_list :
                            msrv = AdminConfig.showAttribute(msvr, 'serverName')
                            mnd_nm = AdminConfig.showAttribute(msvr, 'nodeName')
                            if msrv == cg_prfcord and mnd_nm == cg_prfcord_nd :
                                logger.info('Adding server ' + cg_prfcord + ' on Node ' + cg_prfcord_nd + ' as prefered coordinator.')
                                AdminConfig.modify( cg_id, [['preferredCoordinatorServers', msvr]])
                                status = 1
                            #
                        #
                    #
                #
                if status == 0 :
                    raise Exception('Could not add member server defined in configuration. Either server not a member server or server doesnot exist.')
                #
            #
        #
        logger.info('Custom property application section.')
        cg_cp_list = search_property_list('was.cell.coregroup.customproperty.name_' + cg_ind + '_')
        cg_cp_avl = splitlines(AdminConfig.list('Property', cg_id))
        for cg_cp in cg_cp_list :
            cp_ind = search_property_index('was.cell.coregroup.customproperty.name_' + cg_ind + '_', cg_cp)
            cp_val = search_property('was.cell.coregroup.customproperty.value_' + cg_ind + '_' + cg_cp)
            attrs = [[ 'name', cg_cp ], [ 'value', cp_val ]]
            cp_id = check_config_in_configid_list(cg_cp_avl, cg_cp)
            if cp_id == '' :
                logger.info('Custom property '+ cg_cp +' not present will be created.')
                AdminConfig.create('Property', cg_id, attrs)
            else :
                logger.info('Custom property '+ cg_cp +' present will be deleted and recreated.')
                AdminConfig.remove(cp_id)
                AdminConfig.create('Property', cg_id, attrs)
            #
        #
        logger.info('Exiting : setcoregroupproperty')
    except :
        logger.severe('Error configuring Core Group Property. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in setcoregroupproperty methord. ERROR: ' + str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        sys.exit(1)
    #
#

def configurecoregroup() :
    global logger
    logger.info('Initialize : configurecoregroup')
    try :
        coregroup_list = search_property_list('was.cell.coregroup.name_')
        for cg_nm in coregroup_list :
            cg_id = AdminConfig.getid('/Cell:' + cell + '/CoreGroup:' + cg_nm + '/')
            if cg_id != '' :
                logger.info('Core Group ' + cg + ' exist.')
                cg_ind = search_property_index('was.cell.coregroup.name_', cg_nm)
                cg_chk = search_property('was.cell.coregroup.update_' + cg_ind)
                if cg_chk == 'true' :
                    logger.info('Core Group ' + cg + ' property openned to be reconfigured.')
                    setcoregroupproperty(cg_id)
                #
            else :
                logger.info('Core Group ' + cg + ' does not exist it will be created.')
                ret_value = AdminTask.createCoreGroup('[-coreGroupName %s]' % (cg))
                logger.info(ret_value)
                setcoregroupproperty(ret_value)
            #
        #
        logger.info('Exiting : configurecoregroup')
    except :
        logger.severe('Error configuring Core Group. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in configurecoregroup methord. ERROR: ' + str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        sys.exit(1)
    #
#

def configurenode() :
    global logger
    logger.info('Initialize : configurenode')
    try :
        nd_lst = search_property_list('was.cell.node.name_')
        nd_pst_lst = AdminTask.listNodes()
        if len(nd_lst) != len(nd_pst_lst) :
            raise Exception('The Cell Level configuration non consistent. Number of configuration does not match.')
        #
        if nd in nd_lst :
            nd_ind = search_property_index('was.cell.node.name_', nd)
            nd_id = AdminConfig.getid('/Cell:'+ cell +'/Node:'+ nd +'/')
            if nd_id == '' :
                raise Exception('The Node '+ nd +' not present in the configuration. Inconsistent configuration detected.')
            #
            ndagent = AdminConfig.getid('/Cell:'+ cell +'/Node:'+ nd +'/Server:nodeagent/')
            if ndagent == '' :
                raise Exception('The Node configuration cannot be detected.')
            #
            nd_type = search_property('was.cell.node.type_' + nd_ind)
            chk_upd = search_property('was.cell.node.update_' + nd_ind)
            if nd_type == 'managed' and chk_upd == 'true' :
                logger.info('Nodeagent: '+ nd +' - STARTED')
                logger.info('Node agent Heap Resize.')
                mnhp = search_property('was.cell.nodeagent.minheap_' + nd_ind)
                mxhp = search_property('was.cell.nodeagent.maxheap_' + nd_ind)
                if mnhp != None and mnhp != '' and mxhp != None and mxhp != '' :
                    logger.info('Node agent configuration will be set to Initial ' + str(mnhp) + ' Maximum ' + str(mxhp))
                    AdminTask.setJVMProperties('[-nodeName '+ nd +' -serverName nodeagent -initialHeapSize '+ str(mnhp) +' -maximumHeapSize '+ str(mxhp) +']')
                #
                logger.info('Node agent Environment Entry Configuration.')
                env_nm_lst = search_property_list('was.cell.nodeagent.environmententry.name_' + nd_ind + '_')
                for env_nm in env_nm_lst :
                    env_ind = search_property_index('was.cell.nodeagent.environmententry.name_' + nd_ind + '_', env_nm)
                    env_val = search_property('was.cell.nodeagent.environmententry.value_' + nd_ind + '_' + env_ind)
                    if env_nm  != None and env_nm != '' and env_val != None and env_val  != '' :
                        setenvproperty(ndagent, env_nm, env_val)
                    #
                #
                logger.info('Node agent Port reconfiguration.')
                srventries = splitlines(AdminConfig.list( 'ServerEntry', nd_id))
                port_list = search_property_list('was.cell.nodeagent.port.name_' + nd_ind + '_')
                for port in port_list :
                    port_ind = search_property_index('was.cell.nodeagent.port.name_' + nd_ind + '_', port)
                    port_val = search_property('was.cell.nodeagent.port.value_' + nd_ind + '_' + port_ind)
                    if port != None and port != '' and port_val != None and port_val != '' :
                        for srventry in srventries :
                            sname = AdminConfig.showAttribute( srventry,  'serverName' )
                            if sname == 'nodeagent' :
                                endpnts = splitlist(AdminConfig.showAttribute( srventry, 'specialEndpoints' ))
                                for epnt in endpnts :
                                    epnt_nm = AdminConfig.showAttribute( epnt, 'endPointName' )
                                    if epnt_nm == port :
                                        epnt_id = AdminConfig.showAttribute( epnt, 'endPoint' )
                                        logger.info('Port '+ port +' will be configured with value '+ str(port_val))
                                        port_int = int(port_val)
                                        AdminConfig.modify( epnt_id, [['port', "%d" % port_int]] )
                                    #
                                #
                            #
                        #
                    #
                #
                logger.info('Node agent Core Group Assignment.')
                cr_gp = search_property('was.cell.nodeagent.coregroup.name_' + nd_ind)
                ndag_ha = AdminConfig.list('HAManagerService', ndagent)
                ndcg = AdminConfig.showAttribute(ndag_ha, 'coreGroupName')
                if cr_gp != ndcg :
                    logger.info('Nodeagent is currently assigned to different Core group thus reassignin the same.')
                    srv_mbn = AdminControl.queryNames('type=JVM,process=%s,node=%s,*' % ('nodeagent', nd))
                    if srv_mbn != '' :
                        logger.info('Nodeagent is currently running on Node ' + nd +' tring to stop the same.')
                        AdminControl.stopServer('nodeagent', nd)
                        time.sleep(30)
                    #
                    srv_mbna = AdminControl.queryNames('type=JVM,process=%s,node=%s,*' % ('nodeagent', nd))
                    if srv_mbna != '' :
                        raise Exception('The Nodeagent on node '+ nd +' cannot be stopped.')
                    #
                    commandstring = '[-source %s -target %s -nodeName %s -serverName %s]' % ( ndcg, cr_gp, nd, 'nodeagent')
                    AdminTask.moveServerToCoreGroup( commandstring )
                #
                logger.info('Nodeagent: '+ nd +' - COMPLETE')
            #
        #
        logger.info('Exiting : configurenode')
    except :
        logger.severe('Error configuring Node. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in configurenode methord. ERROR: ' + str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        sys.exit(1)
    #
#

def configurenodegroup() :
    global logger
    logger.info('Initialize : configurenodegroup')
    try :
        nodegroup_list = search_property_list('was.nodegroup.name_r_')
        for ng in nodegroup_list :
            ng_index = search_property_index('was.nodegroup.name_r_', ng)
            ng_stats = search_property('was.nodegroup.update_r_' + ng_index )
            status = AdminNodeGroupManagement.checkIfNodeGroupExists(ng)
            if status == 'true' :
                logger.info('Node Group ' + ng + ' already exist.')
            else :
                logger.info('Creating Node Group ' + ng)
                ret_value = AdminNodeGroupManagement.createNodeGroup(ng)
                ng_stats = 'true'
                logger.info(ret_value)
            #
            ng_mmb_lst = search_property_list('was.nodegroup.member_r_' + ng_index + '_')
            ng_member_list = AdminNodeGroupManagement.listNodeGroupMembers(ng)
            for ng_mmb in ng_member_list :
                stat_ck = check_element_in_list(ng_mmb_lst, ng_mmb)
                if stat_ck == 0 and ng_stats == 'true' :
                    logger.info('Node ' + ng_mmb + ' will be deleted as it is not present of Nodes to be present in Node Group.')
                    AdminNodeGroupManagement.deleteNodeGroupMember(ng, ng_member)
                #
            #
            for ng_mmb in ng_mmb_lst :
                logger.info('Checking member ' + ng_mmb + ' of Node Group.')
                stat_ck = check_element_in_list(ng_member_list, ng_mmb)
                if stat_ck == 0 and ng_stats == 'true' :
                    status = AdminNodeManagement.doesNodeExist(ng_mmb)
                    if status == 'false' :
                        raise Exception('Node ' + ng_mmb + ' doesnot exist. You need to create the node before it can be added to NodeGroup.')
                    #
                    logger.info('Adding member ' + ng_mmb + ' part of Nodegroup.')
                    ret_value = AdminTask.addNodeGroupMember(ng, ["-nodeName", ng_mmb])
                    logger.info(ret_value)
                #
            #
        #
        logger.info('Exiting : configurenodegroup')
    except :
        logger.severe('Error configuring Node Group. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in configurenodegroup methord. ERROR: ' + str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        sys.exit(1)
    #
#

def configurekeystore() :
    global logger
    logger.info('Initialize : configurekeystore')
    try :
        kystr_list = search_property_list('was.cell.keystore.name_')
        avl_kystr_list = splitlines(AdminTask.listKeyStores())
        for kystr in kystr_list :
            kystr_ind = search_property_index('was.cell.keystore.name_', kystr)
            chk_upd = search_property('was.cell.keystore.update_' + kystr_ind)
            kystr_typ = search_property('was.cell.keystore.type_' + kystr_ind)
            kystr_fl = search_property('was.cell.keystore.file_' + kystr_ind)
            kystr_psswd = search_property('was.cell.keystore.password_' + kystr_ind)
            if check_valid_value(kystr) or check_valid_value(chk_upd) or check_valid_value(kystr_typ) or check_valid_value(kystr_fl) or check_valid_value(kystr_psswd) :
                raise Exception('All required property for Keystore '+ kystr +' not present. The property file inconsistent.')
            #
            if os.path.isfile(kystr_fl) != 1 :
                raise Exception('Keystore File location '+ kystr_fl +' not present.')
            #
            check_presnt = check_config_in_configid_list(avl_kystr_list, kystr)
            if check_presnt == '' :
                logger.info('Key store '+ kystr +' not present. It will be created.')
                ret_value = AdminTask.createKeyStore('[-keyStoreName '+ kystr +' -keyStoreType '+ kystr_typ +' -keyStoreLocation '+ kystr_fl +' -keyStorePassword '+ kystr_psswd +' -keyStorePasswordVerify '+ kystr_psswd +' -keyStoreIsFileBased true -keyStoreInitAtStartup true -keyStoreReadOnly false]')
                logger.info(ret_value) 
            else :
                if chk_upd == 'true' :
                    logger.info('Key store '+ kystr +' required to be updated.')
                    ret_value = AdminTask.modifyKeyStore('-keyStoreName '+ kystr +' -keyStoreType '+ kystr_typ +' -keyStoreLocation '+ kystr_fl +' -keyStorePassword '+ kystr_psswd)
                    logger.info(ret_value)
                #
            #
        #
        logger.info('Exiting : configurekeystore')
    except :
        logger.severe('Error configuring Key Store. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in configurekeystore methord. ERROR: ' + str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        sys.exit(1)
    #
#

def configuresslconfig() :
    global logger
    logger.info('Initialize : configuresslconfig')
    try :
        keystrore_list = splitlines(AdminTask.listKeyStores())
        sslc_list = splitlines(AdminConfig.getid('/SSLConfig:/'))
        sslconf_list = search_property_list('was.cell.ssl.config.name_')
        for sslc in sslconf_list :
            sslc_ind = search_property_index('was.cell.ssl.config.name_', sslc)
            sslc_updt = search_property('was.cell.ssl.config.update_' + sslc_ind)
            sslc_trststr = search_property('was.cell.ssl.config.truststore_' + sslc_ind)
            sslc_kystr = search_property('was.cell.ssl.config.keystore_' + sslc_ind)
            sslc_clky = search_property('was.cell.ssl.config.clientkey_' + sslc_ind)
            sslc_srvky = search_property('was.cell.ssl.config.serverkey_' + sslc_ind)
            sslc_prot = search_property('was.cell.ssl.config.protocol_' + sslc_ind)
            sslc_clev =  search_property('was.cell.ssl.config.securitylevel_' + sslc_ind)
            sslc_cltauth = search_property('was.cell.ssl.config.clientauthentication_' + sslc_ind)
            if check_valid_value(sslc) or check_valid_value(sslc_updt) or check_valid_value(sslc_trststr) or check_valid_value(sslc_kystr) or check_valid_value(sslc_clky) or check_valid_value(sslc_srvky) or check_valid_value(sslc_prot) or check_valid_value(sslc_clev) or check_valid_value(sslc_cltauth) :
                raise Exception('Required property not defined for SSL Configuration index '+ str(sslc_ind))
            #
            status = check_config_in_configid_list(sslc_list, sslc, 'alias')
            if status == '' :
                logger.info('SSL Configuration '+ sslc +' not present, it will be created.')
                chk_trstr = check_config_in_configid_list(keystrore_list, sslc_trststr)
                chk_kystr = check_config_in_configid_list(keystrore_list, sslc_kystr)
                if chk_trstr == '' or chk_kystr == '' :
                    raise Exception('Key Store and Trust Store not present.')
                #
                if sslc_prot != "TLS" and sslc_prot != "TLSv1" :
                    raise Exception('SSL Protocol allowed is only TLS or TLSv1')
                #
                if sslc_clev != 'HIGH' and sslc_clev != 'MEDIUM' and sslc_clev != 'LOW' :
                    raise Exception('The cipher group allowed are HIGH, MEDIUM, LOW.')
                #
                AdminTask.createSSLConfig(['-alias', sslc, '-scopeName', '(cell):'+ cell, '-clientKeyAlias', sslc_clky, '-serverKeyAlias', sslc_srvky, '-trustStoreName', sslc_trststr, '-keyStoreName', sslc_kystr, '-clientAuthenticationSupported', sslc_cltauth, '-sslProtocol', sslc_prot, '-securityLevel', sslc_clev])
            else :
                if sslc_updt == 'true' :
                    logger.info('SSL Configuration '+ sslc +' will be updated.')
                    chk_trstr = check_config_in_configid_list(keystrore_list, sslc_trststr)
                    chk_kystr = check_config_in_configid_list(keystrore_list, sslc_kystr)
                    if chk_trstr == '' or chk_kystr == '' :
                        raise Exception('Key Store and Trust Store not present.')
                    #
                    if sslc_prot != "TLS" and sslc_prot != "TLSv1" :
                        raise Exception('SSL Protocol allowed is only TLS or TLSv1')
                    #
                    if sslc_clev != 'HIGH' and sslc_clev != 'MEDIUM' and sslc_clev != 'LOW' :
                        raise Exception('The cipher group allowed are HIGH, MEDIUM, LOW.')
                    #
                    AdminTask.modifySSLConfig(['-alias', sslc, '-scopeName', '(cell):'+ cell, '-clientKeyAlias', sslc_clky, '-serverKeyAlias', sslc_srvky, '-trustStoreName', sslc_trststr, '-keyStoreName', sslc_kystr, '-clientAuthenticationSupported', sslc_cltauth, '-sslProtocol', sslc_prot, '-securityLevel', sslc_clev])
                #
            #
        #
        logger.info('Exiting : configuresslconfig')
    except :
        logger.severe('Error configuring SSL Configuration. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in configuresslconfig methord. ERROR: ' + str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        sys.exit(1)
    #
#

def configuredynamicssloutbound() :
    global logger
    logger.info('Initialize : configuredynamicssloutbound')
    try :
        dynassl_list = search_property_list('was.cell.dynamicsslconf.name_')
        dynasslconf_list = splitlines(AdminTask.listDynamicSSLConfigSelections())
        for dynssl in dynassl_list :
            dynassl_ind = search_property_index('was.cell.dynamicsslconf.name_', dynssl)
            chk_flag = search_property('was.cell.dynamicsslconf.update_'+ dynassl_ind)
            sslconfig = search_property('was.cell.dynamicsslconf.sslconfig.name_'+ dynassl_ind)
            connstr = search_property('was.cell.dynamicsslconf.connection.string_'+ dynassl_ind)
            certalias = search_property('was.cell.dynamicsslconf.cert.alias_'+ dynassl_ind)
            desc = search_property('was.cell.dynamicsslconf.desc_'+ dynassl_ind)
            if check_valid_value(dynssl) or check_valid_value(chk_flag) or check_valid_value(sslconfig) or check_valid_value(connstr) or check_valid_value(certalias) or check_valid_value(desc) :
                raise Exception('All required property for Dynamic outbound endpoint SSL configuration indexed '+ dynassl_ind +' not present.')
            #
            check_presnt = check_config_in_configid_list(dynasslconf_list, dynssl)
            if check_presnt == '' :
                logger.info('Dynamic outbound endpoint SSL configuration '+ dynssl +' not present it will be created.')
                AdminTask.createDynamicSSLConfigSelection('[-dynSSLConfigSelectionName '+ dynssl +' -scopeName '+ '(cell):'+ cell +' -dynSSLConfigSelectionDescription '+ desc +' -dynSSLConfigSelectionInfo '+ connstr +' -sslConfigName '+ sslconfig +' -sslConfigScope '+ '(cell):'+ cell +' -certificateAlias '+ certalias +']')
            else :
                if chk_flag == 'true' :
                    logger.info('Dynamic outbound endpoint SSL configuration '+ dynssl +' will be modified.')
                    AdminTask.deleteDynamicSSLConfigSelection('-dynSSLConfigSelectionName '+ dynssl)
                    AdminTask.createDynamicSSLConfigSelection('[-dynSSLConfigSelectionName '+ dynssl +' -scopeName '+ '(cell):'+ cell +' -dynSSLConfigSelectionDescription '+ desc +' -dynSSLConfigSelectionInfo '+ connstr +' -sslConfigName '+ sslconfig +' -sslConfigScope '+ '(cell):'+ cell +' -certificateAlias '+ certalias +']')
                #
            #
        #
        logger.info('Exiting : configuredynamicssloutbound')
    except :
        logger.severe('Error configuring Dynamic SSL Outbound. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in configuredynamicssloutbound methord. ERROR: ' + str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        sys.exit(1)
    #
#

def configuresecurity() :
    global logger
    logger.info('Initialize : configuresecurity')
    try :
        chk_flag = search_property('was.cell.security.update')
        if chk_flag == 'true' :
            sec_id = AdminConfig.getid("/Security:/")
            if sec_id == '' :
                raise Exception('Cannot retrived Security configuration id.')
            #
            logger.info('Global Security Configuration requested to be altered.')
            gs = search_property('was.cell.globalsecurity.status')
            logger.info('Setting Global Security to ' + gs)
            AdminConfig.modify(sec_id, [['enabled', gs]])
            asec = search_property('was.cell.applicationsecurity.status')
            logger.info('Setting Application Security to ' + asec)
            AdminConfig.modify(sec_id, [['appEnabled', asec]])
            j2s = search_property('was.cell.java2security.status')
            logger.info('Setting Java 2 Security to ' + j2s)
            AdminConfig.modify(sec_id, [['enforceJava2Security', j2s]])
        #
        logger.info('Exiting : configuresecurity')
    except :
        logger.severe('Error configuring Security. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in configuresecurity methord. ERROR: ' + str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        sys.exit(1)
    #
#

def configurerepository() :
    global logger
    logger.info('Initialize : configurerepository')
    try :
        rp_nm_lst = search_property_list('was.cell.wim.ldap.name_')
        rp_lst_avl = AdminTask.listIdMgrRepositories()
        for rp in rp_nm_lst :
            rp_ind = search_property_index('was.cell.wim.ldap.name_', rp)
            chk_flag = search_property('was.cell.wim.ldap.update_' + rp_ind)
            rp_type = search_property('was.cell.wim.ldap.type_' + rp_ind)
            rp_loginprop = search_property('was.cell.wim.ldap.loginproperty_' + rp_ind)
            rp_sslconf = search_property('was.cell.wim.ldap.sslconfig_' + rp_ind)
            rp_hst = search_property('was.cell.wim.ldap.host_' + rp_ind)
            rp_prt = search_property('was.cell.wim.ldap.port_' + rp_ind)
            rp_busr = search_property('was.cell.wim.ldap.binduser_' + rp_ind)
            rp_bpass = search_property('was.cell.wim.ldap.bindpassword_' + rp_ind)
            rp_bentry = search_property('was.cell.wim.ldap.basedn_' + rp_ind)
            if check_valid_value(rp_type) or check_valid_value(rp_loginprop) or check_valid_value(rp_hst) or check_valid_value(rp_prt) or check_valid_value(rp_busr) or check_valid_value(rp_bpass) or check_valid_value(rp_bentry) :
                raise Exception('Required property for LDAP configuration to be added to the Fedarated repository is not present.')
            #
            if check_valid_value(rp_sslconf) :
                ssl_config = '-sslEnabled false -sslConfiguration'
            else :
                ssl_config = '-sslEnabled true -sslConfiguration '+ rp_sslconf
            #
            if rp_lst_avl.find(rp) == -1 :
                logger.info('LDAP Configuration cannot be detected. Thus creating the same.')
                AdminTask.createIdMgrLDAPRepository('[-default true -id '+ rp +' -adapterClassName com.ibm.ws.wim.adapter.ldap.LdapAdapter -ldapServerType '+ rp_type +' -sslConfiguration -certificateMapMode exactdn -supportChangeLog none -certificateFilter -loginProperties '+ rp_loginprop +']')
                #AdminTask.addIdMgrLDAPServer('[-id '+ rp +' -host '+ rp_hst +' -port '+ str(rp_prt) +' -bindDN '+ rp_busr +' -bindPassword '+ rp_bpass +' -authentication simple -ldapServerType '+ rp_type +' -certificateMapMode exactdn -certificateFilter '+ ssl_config +']')
                #AdminTask.addIdMgrRepositoryBaseEntry('[-id "'+ rp +'" -name '+ rp_bentry +' -nameInRepository  '+ rp_bentry +' ]')
            else :
                if chk_flag == 'true' :
                    logger.info('LDAP Configuration '+ rp +' requested for reconfiguration.')
                    AdminTask.updateIdMgrLDAPServer('[-id "'+ rp +'" -host '+ rp_hst +' -bindDN '+ rp_busr +' -bindPassword '+ rp_bpass +' -authentication simple -ldapServerType '+ rp_type +' -referal ignore '+ ssl_config +' -certificateMapMode exactdn -certificateFilter]')
                    AdminTask.addIdMgrRepositoryBaseEntry('[-id "'+ rp +'" -name '+ rp_bentry +' -nameInRepository  '+ rp_bentry +' ]')
                #
            #

        logger.info('Exiting : configurerepository')
    except :
        logger.severe('Error configuring User Repository. Execution will be halted.')
        logger.severe(str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        notify_error('Fatal error detected in configurerepository methord. ERROR: ' + str(sys.exc_info()[0]) + ' : ' + str(sys.exc_info()[1]))
        sys.exit(1)
    #
#

def synfullenvironment() :
    logger.info('Initialize : synfullenvironment')
    try :
        nodelist = splitlines(AdminTask.listManagedNodes())
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

###########################################################################################################################################
# MAIN SECTION
# Initiation Section
mail_status = 0
was_host = socket.gethostname()
logger  = Logger.getLogger('was_85_dmgr')
property_file = Properties()
cell_id = AdminConfig.list('Cell').split(lineSeparator)[0]
cell = AdminConfig.showAttribute(cell_id, 'name')
environment_detail=''
# Execution
if len(sys.argv) == 1 :
    environment_detail=sys.argv[0]
elif len(sys.argv) == 2 :
    environment_detail=sys.argv[0]
    log_file_location = sys.argv[1]
    initiatelog(log_file_location)
else :
    logger.severe('Incorrect usage. You need to specify argument. USAGE  : wsadmin -lang jython was_85_dmgr.py [CONFIG FILE] [OPTIONAL: LOG FILE]')
    logger.severe('Example: ./wsadmin.sh -lang jython -f was_85_dmgr.py /DC/WAAS2.0/dmgr.conf')
    sys.exit(9)
#
loadproperty(environment_detail)
check_point_list = splitlines(AdminTask.listCheckpoints())
chk_stat = check_config_in_configid_list(check_point_list, 'full2')
if chk_stat != '' :
    AdminTask.deleteCheckpoint(['-checkpointName', 'full2'])
#
AdminTask.createFullCheckpoint(['-checkpointName', 'full2'])
mail_list = 'San.Muk@gmail.com'
#runcustomscript("pre")
configuredmgr()
#configurecoregroup()
#configurenode()
#configurenodegroup()
#configurekeystore()
#configuresslconfig()
#configuredynamicssloutbound()
#configurerepository()
#configuresecurity()
AdminConfig.save()
synfullenvironment()
#runcustomscript("post")
if mail_status == 0 :
    url_called =  'https://mail.send.endpoint.com:443/sendmail'
    url_called =  url_called + mail_list + '&alert_type=DEPLOYMENT&env_type=CELL&env=' + environment_detail + '&remark=NA'
    url_called =  url_called + '&status=SUCCESS&server=' + was_host
    unix_command = 'wget -q --spider --no-check-certificate "' + url_called + '"'
    os.system(unix_command)
#
