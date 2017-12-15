'use strict'

const fs = require('fs')
const mime = require('mime')
const request = require('request')
const async = require('async')
const chalk = require('chalk')
const trunc = require('unicode-byte-truncate')
const sanitize = require('sanitize-filename')

var numDownloaded = 0;
var globalNum;
var afterValue;

const defaultOptions = {
  sub: 'pics',
  cat: 'hot',
  num: '3',
  key: null
}

/*
 * Exports module to be called by cli.js, which is our executable
 */
module.exports = (options) => {
  const {sub, cat, num, key} = Object.assign(defaultOptions, options)
  let url = [
    'http://www.reddit.com/r/',
    sub, '/', (key !== null ? 'search' : cat), '.json', '?limit=', num
  ].join('')

  globalNum = num;

  if(key !== null) {
    url += '&q=' + key + '&restrict_sr=on&sort=' + cat + '&t=all&after=';
  }

  console.log(url);

  getPosts(url, getImage)
}

/*
 * GETs JSON data, then calls getImage on each post
 * Use try/catch since Reddit sends an HTML error page instead of JSON if server is under load
 */
function getPosts (url) {
  request(url, (err, res, body) => {
    if (err) return console.log(err)
    try {
      const parsed = JSON.parse(body)
      async.parallel(
        parsed.data.children.map(link => callback => getImage(link, callback)),
        (err, results) => {
          if (err) return console.log(err)

          // Continue searching until all requested images found
          if(numDownloaded < globalNum) {
            url = replaceUrlParam(url, 'after', afterValue);

            getPosts(url, getImage)
          }

          console.log('All downloads complete')
          console.log(`Downloaded ${results.filter(res => res).length} out of ${results.length} links`)
        })
    } catch (err) {
      console.log(err.message)
    }
  })
}

/*
 * Check if there is a reddit preview of the image then download from that url
 */
function getImage (post, callback) {
  if (!post.data.preview) {
    console.log(post.data.url, chalk.red('No image found'))
    return callback(null, null)
  }
  const url = post.data.preview.images[0].source.url

  // Set after value for queries > 100
  afterValue = post.data.name;

  // truncate to 251 so we have 4 bytes for the file extension
  const filename = trunc(sanitize(post.data.title, {replacement: '_'}), 251)
  
  // Uncomment to allow gifs to be searched
  // const redditImageRegex = /https?:\/\/i\.redditmedia\.com\/.*\.(jpg|png|gif)/

  // Only desire still images no gifs
  const redditImageRegex = /https?:\/\/i\.redditmedia\.com\/.*\.(jpg|png)/

  if (url.match(redditImageRegex)) {
    const match = url.match(redditImageRegex)
    const ext = '.' + match[1]
    downloadImage(url, filename + ext, callback)
  } else {
    console.log(url, chalk.red(' Unrecognized image url'))
    callback(null, null)
  }
}

// Modified to save directly to an images folder. This should not be used as a global npm
function downloadImage (url, filename, callback) {
  request(url)
  .pipe(fs.createWriteStream('./images/' + filename))
  .on('close', () => {
    console.log(url, chalk.green(' downloaded successfully'))

    // Increase numDownloaded to keep track of how many images have been downloaded
    numDownloaded++;

    callback(null, filename)
  })
}

// Found from https://stackoverflow.com/questions/7171099/how-to-replace-url-parameter-with-javascript-jquery
function replaceUrlParam(url, paramName, paramValue) {
  if (paramValue == null)
    paramValue = '';
  var pattern = new RegExp('\\b(' + paramName + '=).*?(&|$)')
  if (url.search(pattern) >= 0) {
    return url.replace(pattern, '$1' + paramValue + '$2');
  }
  url = url.replace(/\?$/, '');
  return url + (url.indexOf('?') > 0 ? '&' : '?') + paramName + '=' + paramValue
}