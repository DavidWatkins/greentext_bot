#!/usr/bin/env node
'use strict';
var meow = require('meow');
var reddid = require('./');

var cli = meow({
  help: [
    'Usage',
    '  reddid <subreddit> <category> <num> [keyword]',
    '  reddid pics top 3 week',
    '  reddid pics hot 5',
    ' ',
    ' [keyword] is an optional parameter that can be',
    ' It will change the call to a search call'
  ]
});

// const times = ['year', 'month', 'week', 'day', 'hour']
let [sub, cat, num, key] = cli.input

// time = times.includes(time) ? time : null

reddid({sub, cat, num, key});
