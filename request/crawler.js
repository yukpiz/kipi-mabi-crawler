// # export AWS_PROFILE=lambda

var async = require('async');
var request = require('request');
var cheerio = require('cheerio');

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
	local = context == null
	console.log('=== KIPI WEB CRAWLER ==========');
	if (local) {
		console.log('  Mode: Local Test');
	} else {
		console.log('  Mode: Lambda Scheduling');
	}

	//Request Free Board.

	//Request Player Boards.

	//Request Trade Boards.
	Object.keys(trade_boards).forEach(b => {
		trade_boards[b].forEach(s => {
			var url = base_url + '/' + b + '?sv=' + s;
			request.get(url, {timeout: 20000}, (err, res, body) => {
				//Parse HTML for Trade board.
				async.waterfall([
					(callback) => {
						//1. Parse HTML Function.
						console.log('  ===> Parse HTML');
						console.log('    URL: ' + url);
						$ = cheerio.load(body, {decodeEntities: false});
						detail_urls = [];
						$('[class^="list-head"] ~ tr ').each(function() {
							detail_url = base_url + $(this).find('[class^="list-title"] > p > a').prop('href');
							detail_urls.push(detail_url);
						});
						callback(null, detail_urls);
					},
					(urls, callback) => {
						//2. Request Detail Article.
						console.log('  ===> Request Detail Article');
						async.each(urls, (url) => {
							request.get(url, {timeout: 20000}, (err, res, body) => {
								console.log('hogehoge');
							});
						});
						callback(null);
					},
					(callback) => {
						//Parse HTML
						callback(null);
					},
					(callback) => {
						//Insert DynamoDB
						console.log('finish');
						callback(null);
					},
				]);
			});
		});
	});
}

// Call function for localhost.
exports.lambda_handler(null, null);
