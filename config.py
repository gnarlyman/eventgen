import json

from lib.eventgenlib import *

from lib.gen import Case, LineGen

CONFIG = {
	### Splunk Config ###
	'index' 			: 'vap',
	'sourcetype' 		: 'adrouter_audit_message',
	'host' 				: 'localhost',
	'splunk_rest_port'	: '8089',
	'splunk_tx_port'	: '9999',

	### Test Cases ###
    'cases': {
        'FW/PlReq/PlResp' : {   
            'data':read_file('samples/test_case_1.log', lines=True),
            'values':json.loads(read_file('fields/test_case_1.json')),
            'callback':Case,
            'functions' : {
                'session':[randhex,20], # arg can be (foo, [], {})
                'session2':[randhex,20],
                'assetID':[randhex,16],
                'messageId':randid,
            },
        },
        'FW/PSN/PSA' : {
            'data':read_file('samples/test_case_2.log', lines=True),
            'values':json.loads(read_file('fields/test_case_2.json')),
            'callback':Case,
            'functions' : {
                'session':[randhex,20],
                'assetID':[randhex,16],
                'messageId':randid,
            },
        },
        'CA/PlReq/PlResp' : {   
            'data':read_file('samples/test_case_3.log', lines=True),
            'values':json.loads(read_file('fields/test_case_1.json')),
            'callback':Case,
            'functions' : {
                'session':[randhex,20], 
                'session2':[randhex,20],
                'assetID':[randhex,16],
                'messageId':randid,
            },
        },
        'CA/PSN/PSA' : {
            'data':read_file('samples/test_case_4.log', lines=True),
            'values':json.loads(read_file('fields/test_case_2.json')),
            'callback':Case,
            'functions' : {
                'session':[randhex,20],
                'assetID':[randhex,16],
                'messageId':randid,
            },
        },
    },

    # LineGen configuration
    'linegen' : {
        'ba.log' : {
            'disabled':False,
            'file':'samples/ba.log',
            'callback':LineGen,
            'function':genLines_BA,
            'output':'output/ba.log',
        },
        'jboss.log' : {
            'disabled':True,
            'file':'samples/jboss.all.log',
            'callback':LineGen,
            'function':genLines_Jboss,
            'output':'output/jboss.log',
        },
        'executive-process.log' : {
            'disabled':True,
            'file':'samples/executive-process.log',
            'callback':LineGen,
            'function':genLines_ExecProcess,
            'output':'output/executive-process.log',
        },
        'conductor.log' : {
            'disabled':True,
            'file':'samples/conductor.all.log',
            'callback':LineGen,
            'function':genLines_Conductor,
            'output':'output/conductor.log',
        },
        'aspera-scp-transfer.log' : {
            'disabled':False,
            'file':'samples/aspera-scp-transfer.all.log',
            'callback':LineGen,
            'function':genLines_AsperaSCPTransfer,
            'output':'output/aspera-scp-transfer.log',
        },
        'PMG.log' : {
            'disabled':False,
            'file':'samples/PMG.all.log',
            'callback':LineGen,
            'function':genLines_PMG,
            'output':'output/PMG.log',
        },
        'PMG_EVENTS.log' : {
            'disabled':False,
            'file':'samples/PMG_EVENTS.all.log',
            'callback':LineGen,
            'function':genLines_PMG_EVENTS,
            'output':'output/PMG_EVENTS.log',
        },
    },
}
