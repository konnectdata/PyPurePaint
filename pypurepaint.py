#!/usr/bin/env python
#
#   PureResponseClient
#   Python API wrapper for PureResponse by Pure360
#   For internal use and public release
#
#   MIT License
#   Copyright (c) 2013 Triggered Messaging Ltd
#   Authored by Mikael Kohlmyr
#

import suds
from suds.client import Client as SudsPaint

class PureResponseClient(object):
    version = '0.1'
    
    api_username    = None
    api_password    = None
    api_context     = None
    api_client      = None
    
    class API:
        RPC_ENCODED_BRANDED     = 'http://paint.pure360.com/paint.pure360.com/ctrlPaint.wsdl'
        RPC_LITERAL_BRANDED     = 'http://paint.pure360.com/paint.pure360.com/ctrlPaintLiteral.wsdl'
        RPC_ENCODED_UNBRANDED   = 'http://emailapi.co.uk/emailapi.co.uk/ctrlPaint.wsdl'
        RPC_LITERAL_UNBRANDED   = 'http://emailapi.co.uk/emailapi.co.uk/ctrlPaintLiteral.wsdl'
    
    class TYPES:
        ARRAY   = 'paintArray'
        KVP     = 'paintKeyValuePair'
        
        class KEYS:
            VALUE   = 'value'
            KEY     = 'key'
            STRING  = 'str'
            ARRAY   = 'arr'
            PAIRS   = 'pairs'
    
    class BEAN_PROCESSES:
        SEARCH          = 'search'
        STORE           = 'store'
        CREATE          = 'create'
        AUTHENTICATE    = 'login'
        INVALIDATE      = 'logout'
    
    class BEAN_CLASSES:
        CAMPAIGN_DELIVERY   = 'campaign_delivery'
        CAMPAIGN_EMAIL      = 'campaign_email'
        CAMPAIGN_LIST       = 'campaign_list'
        CAMPAIGN_ONE_TO_ONE = 'campaign_one2one'
        CONTEXT             = 'context'
    
    class BEAN_TYPES:
        ENTITY  = 'bus_entity'
        FACADE  = 'bus_facade'
        SEARCH  = 'bus_search'
    
    class FIELDS:
        USERNAME        = 'username'
        PASSWORD        = 'password'
        MESSAGE_ID      = 'messageId'
        BEAN_ID         = 'beanId'
        LIST_IDS        = 'listIds'
        DELIVERY_DATE   = 'deliveryDtTm'
        FOUND_DATA      = 'idData'
        RESULT          = 'result'
        RESULT_DATA     = 'resultData'
    
    class VALUES:
        SUCCESS                 = 'success'
    
    class EXCEPTIONS:
        VALIDATION          = 'bean_exception_validation'
    
    class ERRORS:
        GENERIC             = 'ERROR_GENERIC'
        NOT_AUTHENTICATED   = 'ERROR_NOT_AUTHENTICATED'
        AUTH_PARAMS         = 'ERROR_AUTHENTICATION_PARAMETERS'
        AUTH_PROCESS        = 'ERROR_AUTHENTICATION_PROCESS'
        LIST_NOT_FOUND      = 'ERROR_LIST_NOT_FOUND'
        LIST_NOT_SAVED      = 'ERROR_LIST_NOT_SAVED'
        CONTACT_NOT_FOUND   = 'ERROR_CONTACT_NOT_FOUND'
        CAMPAIGN_NOT_FOUND  = 'ERROR_CAMPAIGN_NOT_FOUND'
        BEAN_NOT_CREATED    = 'ERROR_BEAN_NOT_CREATED'
        COULD_NOT_DELIVER   = 'ERROR_COULD_NOT_DELIVER'
    
    def __init__(self, api_username = '', api_password = ''
        , api_version = API.RPC_LITERAL_UNBRANDED):
        
        self.api_client     = SudsPaint(api_version)
        self.api_username   = api_username
        self.api_password   = api_password
        
        if (not api_username) or (not api_password):
            raise Exception(PureResponseClient.ERRORS.AUTH_PARAMS)
    
    def api_authenticate(self):
        auth = self.api_make_request(
            PureResponseClient.BEAN_TYPES.FACADE
          , PureResponseClient.BEAN_CLASSES.CONTEXT
          , PureResponseClient.BEAN_PROCESSES.AUTHENTICATE
          , {
                PureResponseClient.FIELDS.USERNAME : self.api_username
              , PureResponseClient.FIELDS.PASSWORD : self.api_password
            }
        )
        
        if self._result_success(auth):
            self.api_context = self.response_data(
                auth
              , PureResponseClient.BEAN_TYPE_ENTITY
              , PureResponseClient.BEAN_CLASSES.CONTEXT
              , PureResponseClient.FIELDS.BEAN_ID
            )
            return self._dict_ok(self.api_context)
        elif self._result_exception(auth, PureResponseClient.EXCEPTIONS.VALIDATION):
            return self._dict_err(PureResponseClient.ERRORS.AUTH_PARAMS, auth)
        else:
            return self._dict_err(PureResponseClient.ERRORS.AUTH_PROCESS, auth)
    
    def api_invalidate(self):
        self.api_make_request(
            PureResponseClient.BEAN_TYPES.FACADE
          , PureResponseClient.BEAN_CLASS.CONTEXT
          , PureResponseClient.BEAN_PROCESSES.INVALIDATE
          , no_response = True
        )
        self.api_context = None
    
    def api_send_to_list(self, list_name, message_name):
        return False
    
    def api_send_to_contact(self, email_to, message_name, custom_data):
        return False
    
    def api_add_contact(self, list_name, contact):
        return False
    
    def api_add_contacts(self, list_name, contacts):
        return False
    
    # Direct access to PAINT. Other than converting to a dictionary
    # I will perform no error handling or wrapping
    # We're all adults here.
    def api_make_request(self, bean_type, bean_class, bean_process
      , entity_data = None, process_data = None, no_response = False):
        if self.api_context or (bean_process is PureResponseClient.BEAN_PROCESSES.AUTHENTICATE):
            api_context = self.api_context or suds.null()
            response    = self.api_client.service.handleRequest(
                            api_context
                          , bean_type + '_' + bean_class
                          , bean_process
                          , self._dict_to_ptarr(entity_data)
                          , self._dict_to_ptarr(process_data)
                        )
            if no_response:
                return True
            else:
                return self._ptarr_to_dict(response)
        else:
            return PureResponseClient.ERRORS.NOT_AUTHENTICATED
    
    def _response_data(self, response_dict, bean_type = None, bean_class = None, field = PureResponseClient.FIELDS.RESULT_DATA):
        if bean_type and bean_class:
            return response_dict[field][bean_type + '_' + bean_class]
        elif bean_type or bean_class:
            return False # raise exception?
        else:
            return response_dict[field]
    
    def _get_result(self, response):
        return self._response_data(response=response, field=PureResponseClient.FIELDS.RESULT)
    
    def _result_success(self, response):
        return self._get_result(response) is PureResponseClient.VALUES.SUCCESS
    
    def _result_exception(self, response, exception):
        return self._get_result(response) is exception
    
    def _dict_ok(self, result):
        return {'ok' : True, 'result': result}
    
    def _dict_err(self, error, meta):
        return {'ok' : False, 'result' : error, 'meta' : meta}
    
    def _dict_to_ptarr(self, dict_):
        if not dict_:
            return suds.null()
        arr_ = self.api_client.factory.create(PureResponseClient.TYPES.ARRAY)
        for key_ in dict_:
            kvp_ = self.api_client.factory.create(PureResponseClient.TYPES.KVP)
            setattr(kvp_, PureResponseClient.TYPES.KEYS.KEY, key_.encode('ascii', 'ignore'))
            val_ = getattr(kvp_, PureResponseClient.TYPES.KEYS.VALUE)
            if isinstance(dict_[key_], dict):
                setattr(val_, PureResponseClient.TYPES.KEYS.ARRAY, self._dict_to_ptarr(dict_[key_]))
            elif isinstance(dict_[key_], str) or isinstance(dict_[key_], unicode):
                setattr(val_, PureResponseClient.TYPES.KEYS.STRING, dict_[key_])
            else:
                setattr(val_, PureResponseClient.TYPES.KEYS.STRING, str(dict_[key_]))
            getattr(arr_, PureResponseClient.TYPES.KEYS.PAIRS).append(kvp_)
        return arr_
    
    def _ptarr_to_dict(self, ptarr):
        dict_ = {}
        if not hasattr(ptarr, PureResponseClient.TYPES.KEYS.PAIRS):
            return None
        for pair in getattr(ptarr, PureResponseClient.TYPES.KEYS.PAIRS):
            val_ = getattr(pair, PureResponseClient.TYPES.KEYS.VALUE)
            key_ = getattr(pair, PureResponseClient.TYPES.KEYS.KEY)
            if hasattr(val_, PureResponseClient.TYPES.KEYS.ARRAY):
                arr_ = getattr(val_, PureResponseClient.TYPES.KEYS.ARRAY)
                if not arr_:
                    dict_[key_] = {}
                else:
                    dict_[key_] = self._ptarr_to_dict(arr_)
            elif hasattr(val_, PureResponseClient.TYPES.KEYS.STRING):
                dict_[key_] = getattr(val_, PureResponseClient.TYPES.KEYS.STRING)
        return dict_
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    


