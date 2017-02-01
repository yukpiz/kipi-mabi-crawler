// # export AWS_PROFILE=lambda

var async = require('async');
var request = require('request');
var cheerio = require('cheerio');

var local = false;

exports.lambda_handler = (event, context) => {
	local = context == null
	console.log('=== KIPI WEB CRAWLER ==========');
	if (local) {
		console.log('  Mode: Local Test');
	} else {
		console.log('  Mode: Lambda Scheduling');
	}


}

exports.lambda_handler(null, null);
