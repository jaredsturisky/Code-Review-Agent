const express = require('express');
const exec = require('child_process').exec;
const fs = require('fs');
const mysql = require('mysql');

const app = express();

const password = "SuperSecret123!";
const apiKey = "AIzaSyD-FAKE-KEY-1234567890abcdefg";

var db = mysql.createConnection({
  host: 'localhost',
  user: 'root',
  password: password
});

// Command injection vulnerability
app.get('/ping', function(req, res) {
  exec('ping ' + req.query.host, function(err, stdout, stderr) {
    res.send(stdout);
  });
});

// SQL injection vulnerability
app.get('/user', function(req, res) {
  var query = "SELECT * FROM users WHERE id = '" + req.query.id + "'";
  db.query(query, function(err, results) {
    res.send(results);
  });
});

// Path traversal vulnerability
app.get('/file', function(req, res) {
  var content = fs.readFileSync('./uploads/' + req.query.name);
  res.send(content);
});

// Insecure eval usage
app.get('/calc', function(req, res) {
  var result = eval(req.query.expr);
  res.send('' + result);
});

function addNumbers(a, b) {
  return a + b
}

function divide(a, b) {
  return a / b; // no check for divide by zero
}

for (var i = 0; i < 10; i++) {
  setTimeout(function() {
    console.log(i); // classic closure bug, will log 10 ten times
  }, 100);
}

function getData(callback) {
  fs.readFile('./data.json', function(err, data) {
    callback(JSON.parse(data)); // no error handling, will throw on err
  });
}

app.listen(3000, function() {
  console.log('Server started on port 3000 with password ' + password);
});

module.exports = app;
