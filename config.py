import json

from lib.eventgenlib import read_file, randhex, randid, genLines_BA

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
            'file':'samples/ba.log',
            'callback':LineGen,
            'function':genLines_BA,
        },
        'jboss.all.log' : {
            'file':'samples/ba.log',
            'callback':LineGen,
            'function':genLines_BA,
        }
    },
}
