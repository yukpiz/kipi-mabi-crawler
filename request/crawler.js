// # export AWS_PROFILE=lambda

var async = require('async');
var request = require('request');
var cheerio = require('cheerio');
var aws = require('aws-sdk');

var local = false;

var base_url = 'http://mabinogi.nexon.co.jp/community';
var free_board = 'freeBoardList.asp';
var player_boards = {
	'playerBoardList.asp': ['ma', 'ru', 'ta'],
};
var trade_boards = {
	'tradeBoardList.asp': ['ma', 'ru', 'ta'],
};

exports.lambda_handler = (event, context) => {
	initialize(event, context);

	//Request Free Board.

	//Request Player Boards.

	//Request Trade Boards.
	Object.keys(trade_boards).forEach(b => {
		trade_boards[b].forEach(s => {
			var url = base_url + '/' + b + '?sv=' + s;
			request.get(url, {timeout: 20000}, (err, res, body) => {
				async.waterfall([
					(callback) => {
						console.log('REQUEST URL => ' + url);
						$ = cheerio.load(body, {decodeEntities: false});
						detail_urls = [];
						$('[class^="list-head"] ~ tr ').each(function() {
							detail_url = base_url + $(this).find('[class^="list-title"] > p > a').prop('href');
							detail_urls.push(detail_url);
						});
						callback(null, detail_urls);
					},
					(urls, callback) => {
						var dynamodb = new aws.DynamoDB({region: 'ap-northeast-1'});
						async.each(urls, (url) => {
							console.log('INSERT URL => ' + url);
							var params = {
								TableName: 'kipi-mabi-urls',
								Item: {
									'url': {'S': url},
									'type': {'S': 'trade'},
									'server': {'S': s},
								},
							};
							dynamodb.putItem(params, (err, data) => {
								if (err) {
									console.log(err);
								}
							});
						});
						callback(null);
					},
				]);
			});
		});
	});
}

var initialize = (event, context) => {
	console.log('=== KIPI WEB CRAWLER ==========');
	console.log('Function: DETAIL URL CRAWLER');
	local = context == null
	if (local) {
		console.log('Mode: Local Test');
	} else {
		console.log('Mode: Lambda Scheduling');
	}
};

// Call function for localhost.
exports.lambda_handler(null, null);
