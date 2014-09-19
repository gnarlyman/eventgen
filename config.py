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
            'disabled':False,
            'file':'samples/jboss.all.log',
            'callback':LineGen,
            'function':genLines_General,
            'output':'output/jboss.log',
            'ts_re':'^(\d{2}\s[A-Za-z]{3}\s\d{4}\s\d{2}:\d{2}:\d{2},\d{3})',
            'ts_format':'%d %b %Y %H:%M:%S,%f',
            'freq':60,
        },
        'executive-process.log' : {
            'disabled':True,
            'file':'samples/executive-process.log',
            'callback':LineGen,
            'function':genLines_General,
            'output':'output/executive-process.log',
            'ts_re':'^(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2},\d{3})',
            'ts_format':'%Y-%m-%d %H:%M:%S,%f',
            'freq':1,
        },
        'conductor.log' : {
            'disabled':True,
            'file':'samples/conductor.all.log',
            'callback':LineGen,
            'function':genLines_General,
            'output':'output/conductor.log',
            'ts_re':'^(\d{2}\s[A-Za-z]{3}\s\d{4}\s\d{2}:\d{2}:\d{2},\d{3})',
            'ts_format':'%d %b %Y %H:%M:%S,%f',
            'freq':0.5,
        },
        'aspera-scp-transfer.log' : {
            'disabled':False,
            'file':'samples/aspera-scp-transfer.all.log',
            'callback':LineGen,
            'function':genLines_General,
            'output':'output/aspera-scp-transfer.log',
            'ts_re':'^(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})',
            'ts_format':'%Y-%m-%d %H:%M:%S',
            'freq':0.5,
            'NO-TS-STRIP':'',
        },
        'PMG.log' : {
            'disabled':False,
            'file':'samples/PMG.all.log',
            'callback':LineGen,
            'function':genLines_General,
            'output':'output/PMG.log',
            'ts_re':'^(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2},\d{3})',
            'ts_format':'%Y-%m-%d %H:%M:%S,%f',
            'freq':0.3,
        },
        'PMG_EVENTS.log' : {
            'disabled':False,
            'file':'samples/PMG_EVENTS.all.log',
            'callback':LineGen,
            'function':genLines_General,
            'output':'output/PMG_EVENTS.log',
            'ts_re':'^(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2},\d{3})',
            'ts_format':'%Y-%m-%d %H:%M:%S,%f',
            'freq':0.5,
        },
    },
}
